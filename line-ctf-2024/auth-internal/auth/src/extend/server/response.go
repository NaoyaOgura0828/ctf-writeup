package server

type LoginResponse struct {
	Type    string `json:"type"`
	Message string `json:"message"`
}

type RegisterResponse struct {
	Message string `json:"message"`
}
