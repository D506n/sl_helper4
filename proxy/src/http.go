package src

import (
	"net/http"
	"strings"
)

func HTTPRequestHandler(req *http.Request) {
	req.URL.Path = strings.TrimPrefix(req.URL.Path, "/api")
	req.URL.Host = GetBackendHost()
	req.URL.Scheme = "http"
	if strings.HasPrefix(req.URL.Path, "//") {
		req.URL.Path = strings.TrimPrefix(req.URL.Path, "/")
	}
}

func HTTPResponseHandler(resp *http.Response) error {
	if resp.StatusCode == http.StatusTemporaryRedirect {
		location, err := resp.Location()
		if err == nil && !strings.HasPrefix(location.Path, "/api/") {
			newPath := "/api" + location.Path
			resp.Header.Set("Location", newPath)
		}
	}
	return nil
}
