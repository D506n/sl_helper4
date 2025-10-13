package main

import (
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"sl_helper/src"
	"time"
)

var (
	LogLevel = flag.String("l", "info", "Log level (debug, info, warning, error, critical)")
	DryRun   = flag.Bool("d", false, "Dry run mode")
	RawLogs  = flag.Bool("r", false, "Raw logs mode")
	NoCheck = flag.Bool("n", false, "No check mode")
)

func pingPort(host string, port string, timeout time.Duration) bool {
	address := net.JoinHostPort(host, port)
	conn, err := net.DialTimeout("tcp", address, timeout)
	if *LogLevel == "debug" {
		log.Println("Pinging port: ", address, " with timeout: ", timeout)
		log.Println("Error: ", err)
	}
	if err != nil {
		return false // 
	}
	conn.Close()
	return true // Порт открыт
}

func startProxy() {
	// Создаем прокси для бэкенда
	backendHost := src.GetBackendHost()
	apiProxy := httputil.NewSingleHostReverseProxy(&url.URL{
		Scheme: "http",
		Host:   backendHost,
	})
	apiProxy.Director = src.HTTPRequestHandler
	apiProxy.ModifyResponse = src.HTTPResponseHandler
	log.Println("Backend is running on", backendHost)
	
	// Обработчики
	http.HandleFunc("/ws/", src.WebsocketProxy)
	http.Handle("/", apiProxy)
	
	// Запуск сервера
	if !*NoCheck {
		go src.HealthCheck(*LogLevel)
	}
	log.Fatal(http.ListenAndServe(":3000", src.LoggingMiddleware(*LogLevel, http.DefaultServeMux)))
}

func main() {
	flag.Parse()
	
	// Проверяем, запущены ли мы в Docker-окружении
	dockerMode := os.Getenv("DOCKER_MODE")
	
	if dockerMode == "true" {
		// В Docker-окружении Python-приложение запущено отдельно, просто запускаем прокси
		startProxy()
	} else {
		// В обычном окружении сохраняем старую логику
		if !pingPort("localhost", "3000", time.Millisecond*500) {
			// Запуск FastAPI
			cmd := src.PythonProcess(*LogLevel, *DryRun, *RawLogs)
			defer cmd.Process.Kill()
			startProxy()
		} else {
			err := src.OpenApp()
			if err != nil {
				log.Fatal(err)
			}
		}
	}
}
