package src

import (
	"os"
)

func GetBackendHost() string {
	backendHost := os.Getenv("BACKEND_HOST")
	if backendHost == "" {
		backendHost = "127.0.0.1:8506"
	}
	return backendHost
}