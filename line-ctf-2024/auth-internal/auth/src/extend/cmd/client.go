package cmd

import (
	os "os"

	models "github.com/go-oauth2/oauth2/v4/models"
	store "github.com/go-oauth2/oauth2/v4/store"
)

func DefaultClients(cs *store.ClientStore) {
	var clis = []models.Client{
		{
			ID:     os.Getenv("EXTERNAL_ID"),
			Secret: os.Getenv("EXTERNAL_SECRET"),
			Domain: os.Getenv("EXTERNAL_DOMAIN"),
		},
		{
			ID:     os.Getenv("INTERNAL_ID"),
			Secret: os.Getenv("INTERNAL_SECRET"),
			Domain: os.Getenv("INTERNAL_DOMAIN"),
		},
	}
	for _, cli := range clis {
		cs.Set(cli.ID, &models.Client{
			ID:     cli.ID,
			Secret: cli.Secret,
			Domain: cli.Domain,
		})
	}
	os.Unsetenv("EXTERNAL_ID")
	os.Unsetenv("EXTERNAL_SECRET")
	os.Unsetenv("EXTERNAL_DOMAIN")
	os.Unsetenv("INTERNAL_ID")
	os.Unsetenv("INTERNAL_SECRET")
	os.Unsetenv("INTERNAL_DOMAIN")
}
