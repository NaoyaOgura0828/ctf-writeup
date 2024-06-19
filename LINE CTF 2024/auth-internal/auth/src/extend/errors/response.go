package errors

import (
	errors "errors"
)

type Response struct {
	Error     string `json:"error"`
	ErrorDesc string `json:"error_description"`
}

var (
	ErrInvalidAccessToken     = errors.New("invalid_token")
	ErrInvalidRequest         = errors.New("invalid_request")
	ErrDuplicatedUsername     = errors.New("duplicated_username")
	ErrInvalidUserinfo        = errors.New("invalid_userinfo")
	ErrInvalidUsername        = errors.New("invalid_username")
	ErrInvalidUrl             = errors.New("invalid_url")
	ErrVerifyFailed           = errors.New("verify_failed")
	ErrTemporarilyUnavailable = errors.New("temporarily_unavailable")
	ErrServerError            = errors.New("server_error")
)

var Descriptions = map[error]string{
	ErrInvalidAccessToken:     "Access token is invalid, or is otherwise malformed",
	ErrInvalidRequest:         "The request is missing a required parameter, includes an invalid parameter value, includes a parameter more than once, or is otherwise malformed",
	ErrDuplicatedUsername:     "The request username is duplicated",
	ErrInvalidUserinfo:        "Username or password is incorrect",
	ErrInvalidUsername:        "Username length must be between 4 and 32 charachters",
	ErrInvalidUrl:             "The request is missing a url parameter, invalid url, or is otherwise malformed",
	ErrVerifyFailed:           "Temp",
	ErrTemporarilyUnavailable: "The authorization server is currently unable to handle the request due to a temporary overloading or maintenance of the server",
	ErrServerError:            "The authorization server encountered an unexpected condition that prevented it from fulfilling the request",
}
