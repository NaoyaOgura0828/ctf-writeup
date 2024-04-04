package oidc

type Response struct {
	ID string `json:"id"`
	Username string `json:"username"`
	Admin bool	`json:"is_admin"`
}