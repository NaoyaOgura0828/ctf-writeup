package server

import (
	json "encoding/json"
	http "net/http"
)

func ReturnLogin(w http.ResponseWriter, t string, m string) {
	w.Header().Set("Content-Type", "application/json;charset=UTF-8")
	w.Header().Set("Cache-Control", "no-store")
	w.Header().Set("Pragma", "no-cache")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&LoginResponse{
		Type:    t,
		Message: m,
	})
}

func ReturnRegister(w http.ResponseWriter, m string) {
	w.Header().Set("Content-Type", "application/json;charset=UTF-8")
	w.Header().Set("Cache-Control", "no-store")
	w.Header().Set("Pragma", "no-cache")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&RegisterResponse{
		Message: m,
	})
}
