package oidc

import (
	json "encoding/json"
	http "net/http"
)

func ReturnOidc(w http.ResponseWriter, id string, un string, ia bool) {
	w.Header().Set("Content-Type", "application/json;charset=UTF-8")
	w.Header().Set("Cache-Control", "no-store")
	w.Header().Set("Pragma", "no-cache")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&Response{
		ID: id,
		Username: un,
		Admin: ia,
	})
}