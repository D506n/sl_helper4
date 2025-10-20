package src

import (
	"log"
	"net/http"
	"strings"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func handleWebsocketProxy(w http.ResponseWriter, r *http.Request, connBackend *websocket.Conn) {
	connFrontend, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade failed: %v", err)
		return
	}
	defer connFrontend.Close()

	// Проксирование сообщений между фронтендом и бэкендом
	go func() {
		for {
			msgType, msg, err := connFrontend.ReadMessage()
			if err != nil {
				return
			}
			if err := connBackend.WriteMessage(msgType, msg); err != nil {
				return
			}
		}
	}()

	for {
		msgType, msg, err := connBackend.ReadMessage()
		if err != nil {
			return
		}
		if err := connFrontend.WriteMessage(msgType, msg); err != nil {
			return
		}
	}
}

func WebsocketProxy(w http.ResponseWriter, r *http.Request) {
	backendPath := strings.TrimPrefix(r.URL.Path, "/ws/")
	backendURL := "ws://" + GetBackendHost() + "/" + backendPath

	connBackend, _, err := websocket.DefaultDialer.Dial(backendURL, nil)
	if err != nil {
		log.Printf("Error connecting to backend: %v", err)
		http.Error(w, "Unable to connect to backend", http.StatusBadGateway)
		return
	}
	defer connBackend.Close()
	handleWebsocketProxy(w, r, connBackend)
}
