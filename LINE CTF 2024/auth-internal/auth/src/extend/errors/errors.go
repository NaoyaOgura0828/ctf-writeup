package errors

import (
	json "encoding/json"
	http "net/http"
)

func ReturnError(w http.ResponseWriter, e error, ed string) {
	w.Header().Set("Content-Type", "application/json;charset=UTF-8")
	w.Header().Set("Cache-Control", "no-store")
	w.Header().Set("Pragma", "no-cache")
	w.WriteHeader(http.StatusBadRequest)
	json.NewEncoder(w).Encode(&Response{
		Error:     e.Error(),
		ErrorDesc: ed,
	})
}
