package server

import (
	// "extend/errors"

	errors "extend/errors"
	oidc "extend/oidc"
	store "extend/store"
	utils "extend/utils"
	fmt "fmt"
	http "net/http"
	url "net/url"

	oauth2 "github.com/go-oauth2/oauth2/v4"
	oauth2Server "github.com/go-oauth2/oauth2/v4/server"
	session "github.com/go-session/session"
)

type Server struct {
	Oauth2    oauth2Server.Server
	UserStore store.UserStore
}

func NewDefaultServer(o *oauth2Server.Server, us *store.UserStore) *Server {
	return NewServer(o, us)
}

func NewServer(o *oauth2Server.Server, us *store.UserStore) *Server {
	srv := &Server{
		Oauth2:    *o,
		UserStore: *us,
	}
	return srv
}

func (s *Server) ValidationOpenidRequest(r *http.Request) (oauth2.TokenInfo, error) {
	if !(r.Method == "GET") {
		return nil, errors.ErrInvalidRequest
	}
	t, err := s.Oauth2.ValidationBearerToken(r)
	if err != nil {
		return nil, errors.ErrInvalidAccessToken
	}
	return t, nil
}

func (s *Server) ValidationRegistRequest(w http.ResponseWriter, r *http.Request) error {
	n := r.Form.Get("username")
	if len(n) < 4 || len(n) > 32 {
		return errors.ErrInvalidUsername
	}
	u, _ := url.Parse(r.Form.Get("url"))
	if u.Scheme != "http" && u.Scheme != "https" {
		return errors.ErrInvalidUrl
	}
	return nil
}

func (s *Server) HandleRegisterRequest(w http.ResponseWriter, r *http.Request) error {
	if r.Form == nil {
		if err := r.ParseForm(); err != nil {
			errors.ReturnError(w, errors.ErrInvalidRequest, errors.Descriptions[errors.ErrInvalidRequest])
			return nil
		}
	}
	if _, err := s.UserStore.GetUserByUsername(r.Form.Get("username")); err == nil {
		errors.ReturnError(w, errors.ErrDuplicatedUsername, errors.Descriptions[errors.ErrDuplicatedUsername])
		return nil
	}
	err := s.ValidationRegistRequest(w, r)
	s.UserStore.CreateUser(
		utils.GenUserID(),
		r.Form.Get("username"),
		r.Form.Get("password"),
		r.Form.Get("url"),
		false,
	)
	if err != nil {
		errors.ReturnError(w, err, errors.Descriptions[err])
		return nil
	}
	ReturnRegister(w, "register succeeded")
	return nil
}

func (s *Server) HandleLoginRequest(w http.ResponseWriter, r *http.Request) error {
	st, err := session.Start(r.Context(), w, r)
	if err != nil {
		errors.ReturnError(w, errors.ErrTemporarilyUnavailable, errors.Descriptions[errors.ErrTemporarilyUnavailable])
		return nil
	}
	if r.Form == nil {
		if err := r.ParseForm(); err != nil {
			errors.ReturnError(w, errors.ErrInvalidRequest, errors.Descriptions[errors.ErrInvalidRequest])
			return nil
		}
	}
	ui, err := s.UserStore.GetUserByUsername(r.Form.Get("username"))
	if err != nil {
		errors.ReturnError(w, errors.ErrInvalidUserinfo, errors.Descriptions[errors.ErrInvalidUserinfo])
		return nil
	}
	if ui.GetPassword() == r.Form.Get("password") {
		st.Set("UserID", ui.GetID())
		st.Set("VerifyURL", utils.GenVerifyURL(ui.GetURL()))
		st.Set("VerifyCode", utils.GenVerifyCode())
		st.Save()
		if utils.IsInternal(r) {
			st.Set("Verified", true)
			ReturnLogin(w, "internal", "login succeeded")
		} else {
			st.Set("Verified", false)
			ReturnLogin(w, "external", "login succeeded")
		}
		return nil
	}
	errors.ReturnError(w, errors.ErrInvalidUserinfo, errors.Descriptions[errors.ErrInvalidUserinfo])
	return nil
}

func (s *Server) HandleLogoutRequest(w http.ResponseWriter, r *http.Request) error {
	st, err := session.Start(r.Context(), w, r)
	if err != nil {
		errors.ReturnError(w, errors.ErrTemporarilyUnavailable, errors.Descriptions[errors.ErrTemporarilyUnavailable])
		return nil
	}
	_, ok := st.Get("UserID")
	if !ok {
		errors.ReturnError(w, errors.ErrInvalidRequest, errors.Descriptions[errors.ErrInvalidRequest])
		return nil
	}
	st.Flush()
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("logout succeeded"))
	return nil
}

func (s *Server) HandleVerifyRequest(w http.ResponseWriter, r *http.Request) error {
	st, err := session.Start(r.Context(), w, r)
	if err != nil {
		errors.ReturnError(w, errors.ErrTemporarilyUnavailable, errors.Descriptions[errors.ErrTemporarilyUnavailable])
		return nil
	}
	vu, _ := st.Get("VerifyURL")
	vc, _ := st.Get("VerifyCode")
	rs, err := utils.VerifyRequest(vu.(string))
	if err != nil {
		errors.ReturnError(w, errors.ErrInvalidUrl, errors.Descriptions[errors.ErrInvalidUrl])
		return nil
	}
	if utils.CheckVerify(rs, vc.(string)) {
		errors.ReturnError(w, errors.ErrVerifyFailed, utils.GenVerifyMessge(vc.(string), rs))
		return nil
	}
	st.Set("Verified", true)
	if v, ok := st.Get("ReturnURL"); ok {
		var rp = "?"

		for k, ps := range v.(url.Values) {
			for _, p := range ps {
				rp += fmt.Sprintf("&%s=%s", k, p)
			}
		}
		st.Delete("ReturnURL")
		w.WriteHeader(http.StatusFound)
		w.Header().Set("Location", fmt.Sprintf("/api/v1/authorize.oauth2%s", rp))
	}
	st.Save()
	return nil
}

func (s *Server) HandleOpenidRequest(w http.ResponseWriter, r *http.Request) error {
	t, err := s.ValidationOpenidRequest(r)
	if err != nil {
		errors.ReturnError(w, err, errors.Descriptions[err])
		return nil
	}
	ui, err := s.UserStore.GetUserByUserID(t.GetUserID())
	if err != nil {
		errors.ReturnError(w, errors.ErrServerError, errors.Descriptions[errors.ErrServerError])
		return nil
	}
	oidc.ReturnOidc(w, ui.GetID(), ui.GetUsername(), ui.IsAdmin())
	return nil
}

func (s *Server) HandleUserAuthroize(w http.ResponseWriter, r *http.Request) (userID string, err error) {
	st, err := session.Start(r.Context(), w, r)
	if err != nil {
		return
	}
	uid, ok := st.Get("UserID")
	if !ok {
		if r.Form == nil {
			r.ParseForm()
		}
		st.Set("ReturnURL", r.Form)
		st.Save()
		w.Header().Set("Location", "/login")
		w.WriteHeader(http.StatusFound)
		return
	}
	v, ok := st.Get("Verified")
	if !v.(bool) {
		if r.Form == nil {
			r.ParseForm()
		}
		st.Set("ReturnURL", r.Form)
		st.Save()
		w.Header().Set("Location", "/verify")
		w.WriteHeader(http.StatusFound)
		return
	}
	userID = uid.(string)
	st.Save()
	return
}
