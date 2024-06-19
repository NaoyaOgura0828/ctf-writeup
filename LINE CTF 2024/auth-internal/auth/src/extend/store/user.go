package store

import (
	errors "errors"
	models "extend/models"
	sync "sync"
)

type UserStore struct {
	sync.RWMutex
	users map[string]models.UserInfo
}

func NewUserSotre() *UserStore {
	return &UserStore{
		users: make(map[string]models.UserInfo),
	}
}

func (us *UserStore) Set(id string, ui models.UserInfo) (err error) {
	us.Lock()
	defer us.Unlock()

	us.users[id] = ui
	return
}

func (us *UserStore) CreateUser(id string, username string, password string, url string, admin bool) (err error) {
	us.Lock()
	defer us.Unlock()
	us.users[id] = &models.User{
		ID:       id,
		Username: username,
		Password: password,
		URL:      url,
		Admin:    admin,
	}
	return
}

func (us *UserStore) GetUserByUserID(uid string) (models.UserInfo, error) {
	us.Lock()
	defer us.Unlock()

	if ui, ok := us.users[uid]; ok {
		return ui, nil
	}
	return nil, errors.New("not found")
}

func (us *UserStore) GetUserByUsername(un string) (models.UserInfo, error) {
	us.Lock()
	defer us.Unlock()

	for _, ui := range us.users {
		if ui.GetUsername() == un {
			return ui, nil
		}
	}
	return nil, errors.New("not found")
}
