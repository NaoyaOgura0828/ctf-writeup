package main

import (
	"fmt"

	gin "github.com/gin-gonic/gin"
	generates "github.com/go-oauth2/oauth2/v4/generates"
	manage "github.com/go-oauth2/oauth2/v4/manage"
	server "github.com/go-oauth2/oauth2/v4/server"
	store "github.com/go-oauth2/oauth2/v4/store"
	session "github.com/go-session/session"

	extendCmd "extend/cmd"
	extendServer "extend/server"
	extendStore "extend/store"
	http "net/http"
	"net/url"
)

func main() {
	router := gin.Default()
	manager := manage.NewDefaultManager()
	manager.SetAuthorizeCodeTokenCfg(manage.DefaultAuthorizeCodeTokenCfg)
	manager.MustTokenStorage(store.NewFileTokenStore(extendServer.TokenStore))
	manager.MapAccessGenerate(generates.NewAccessGenerate())
	clientStore := store.NewClientStore()
	userStore := extendStore.NewUserSotre()
	extendCmd.DefaultClients(clientStore)
	extendCmd.DefaultUsers(userStore)
	manager.MapClientStorage(clientStore)
	oauth2 := server.NewDefaultServer(manager)
	extend := extendServer.NewDefaultServer(oauth2, userStore)
	oauth2.SetUserAuthorizationHandler(extend.HandleUserAuthroize)

	router.LoadHTMLGlob("./static/*")
	router.GET("/login", func(c *gin.Context) {
		st, err := session.Start(c.Request.Context(), c.Writer, c.Request)
		if err != nil {
			http.Error(c.Writer, err.Error(), http.StatusInternalServerError)
			return
		}
		ru, _ := st.Get("ReturnURL")
		if ru == nil {
			http.Error(c.Writer, "invalid authentication process", http.StatusBadRequest)
			return
		}
		c.HTML(http.StatusOK, "login.tmpl", nil)
		return
	})
	router.GET("/register", func(c *gin.Context) {
		st, err := session.Start(c.Request.Context(), c.Writer, c.Request)
		if err != nil {
			http.Error(c.Writer, err.Error(), http.StatusInternalServerError)
			return
		}
		uid, _ := st.Get("UserID")
		if uid != nil {
			http.Error(c.Writer, "you have already logged in", http.StatusBadRequest)
			return
		}
		c.HTML(http.StatusOK, "register.tmpl", nil)
		return
	})
	router.GET("/verify", func(c *gin.Context) {
		st, err := session.Start(c.Request.Context(), c.Writer, c.Request)
		if err != nil {
			http.Error(c.Writer, err.Error(), http.StatusInternalServerError)
			return
		}
		uid, _ := st.Get("UserID")
		if uid == nil {
			http.Error(c.Writer, "invalid authentication process", http.StatusBadRequest)
			return
		}
		v, _ := st.Get("Verified")
		if v.(bool) {
			if ru, ok := st.Get("ReturnURL"); ok {
				var rp = "?"

				for k, ps := range ru.(url.Values) {
					for _, p := range ps {
						rp += fmt.Sprintf("&%s=%s", k, p)
					}
				}
				st.Delete("ReturnURL")
				c.Writer.WriteHeader(http.StatusFound)
				c.Writer.Header().Set("Location", fmt.Sprintf("/api/v1/authorize.oauth2%s", rp))
				return
			} else {
				http.Error(c.Writer, "invalid authentication process", http.StatusBadRequest)
				return
			}
		}
		vu, _ := st.Get("VerifyURL")
		vc, _ := st.Get("VerifyCode")
		c.HTML(http.StatusOK, "verify.tmpl", gin.H{
			"verify_url":  vu.(string),
			"verify_code": vc.(string),
		})
		return
	})

	api := router.Group("api")
	{
		v1 := api.Group("v1")
		{
			v1.POST("/login", func(c *gin.Context) {
				err := extend.HandleLoginRequest(c.Writer, c.Request)
				if err != nil {
					http.Error(c.Writer, err.Error(), http.StatusBadRequest)
				}
				return
			})
			v1.GET("/logout", func(c *gin.Context) {
				err := extend.HandleLogoutRequest(c.Writer, c.Request)
				if err != nil {
					http.Error(c.Writer, err.Error(), http.StatusBadRequest)
				}
				return
			})
			v1.POST("/register", func(c *gin.Context) {
				err := extend.HandleRegisterRequest(c.Writer, c.Request)
				if err != nil {
					http.Error(c.Writer, err.Error(), http.StatusBadRequest)
				}
				return
			})
			v1.GET("/verify", func(c *gin.Context) {
				err := extend.HandleVerifyRequest(c.Writer, c.Request)
				if err != nil {
					http.Error(c.Writer, err.Error(), http.StatusBadRequest)
				}
				return
			})
			v1.GET("/authorize.oauth2", func(c *gin.Context) {
				err := oauth2.HandleAuthorizeRequest(c.Writer, c.Request)
				if err != nil {
					http.Error(c.Writer, err.Error(), http.StatusBadRequest)
				}
				return
			})
			v1.POST("/token.oauth2", func(c *gin.Context) {
				err := oauth2.HandleTokenRequest(c.Writer, c.Request)
				if err != nil {
					http.Error(c.Writer, err.Error(), http.StatusInternalServerError)
				}
				return
			})
			v1.GET("/userinfo.openid", func(c *gin.Context) {
				err := extend.HandleOpenidRequest(c.Writer, c.Request)
				if err != nil {
					http.Error(c.Writer, err.Error(), http.StatusBadRequest)
				}
				return
			})
		}
	}
	router.Run(":80")
}
