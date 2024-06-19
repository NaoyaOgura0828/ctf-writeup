package models

type User struct {
	ID, Username, Password, URL	string
	Admin	bool
}

type UserInfo interface {
	GetID() string
	GetUsername() string
	GetPassword() string
	GetURL() string
	IsAdmin() bool
}

func (u *User) GetID() string {
	return u.ID
}

func (u *User) GetUsername() string {
	return u.Username
}

func (u *User) GetPassword() string {
	return u.Password
}

func (u *User) GetURL() string {
	return u.URL
}

func (u *User) IsAdmin() bool {
	return u.Admin
}