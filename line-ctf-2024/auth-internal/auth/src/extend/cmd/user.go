package cmd

import (
	models "extend/models"
	store "extend/store"
	os "os"
)

func DefaultUsers(us *store.UserStore) {
	var uis = []models.User{
		{
			ID:       os.Getenv("ADMIN_UUID"),
			Username: os.Getenv("ADMIN_USERNAME"),
			Password: os.Getenv("ADMIN_PASSWORD"),
			URL:      os.Getenv("ADMIN_URL"),
			Admin:    true,
		},
	}
	for _, ui := range uis {
		us.CreateUser(ui.ID, ui.Username, ui.Password, ui.URL, ui.Admin)
	}
	os.Unsetenv("ADMIN_UUID")
	os.Unsetenv("ADMIN_USERNAME")
	os.Unsetenv("ADMIN_PASSWORD")
	os.Unsetenv("ADMIN_URL")
}
