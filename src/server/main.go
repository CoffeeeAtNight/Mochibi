package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"

	"github.com/gorilla/websocket"
)

type LlmResponse struct {
	Model    string `json:"model"`
	Response string `json:"response"`
	Done     bool   `json:"done"`
}

type LlmRequest struct {
	Model  string `json:"model"`
	Prompt string `json:"prompt"`
	Stream bool   `json:"stream"`
}

type SttResponse struct {
	Status  string         `json:"status"`
	Message string         `json:"message"`
	Data    SttReponseData `json:"data"`
}

type SttReponseData struct {
	Text string `json:"text"`
}

const (
	TEXT_MESSAGE     = 1
	BINARY_MESSAGE   = 2
	API_GATEWAY_ADDR = "http://127.0.0.1:5000/api/v1"
	LLM_API_ADDR     = "http://127.0.0.1:11434/api/generate"
)

var audioFilePath = ""
var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func main() {
	http.HandleFunc("/ws", handleWebsocketConnections)

	fmt.Println("WebSocket server started on :7777")
	if err := http.ListenAndServe(":7777", nil); err != nil {
		fmt.Printf("ListenAndServe failed: %v\n", err)
	}
}

func writeBinaryDataToFile(message []byte) (string, error) {
	filePath := fmt.Sprintf("/tmp/mochibi-%d.wav", rand.Int())
	err := ioutil.WriteFile(filePath, message, 0644)
	return filePath, err
}

func sendMessageTextToLlm(message string) string {
	body, err := json.Marshal(LlmRequest{
		Model:  "akiii/mochibi_3b:latest",
		Prompt: message,
		Stream: false,
	})
	if err != nil {
		fmt.Println("Error marshaling JSON:", err)
		panic("Could not marshal the LLM request")
	}

	request, err := http.NewRequest("POST", LLM_API_ADDR, bytes.NewBuffer(body))
	if err != nil {
		fmt.Println("Error creating HTTP request:", err)
		panic(err)
	}

	request.Header.Add("Content-Type", "application/json")

	client := &http.Client{}
	res, err := client.Do(request)
	if err != nil {
		fmt.Println("Error sending HTTP request:", err)
		panic(err)
	}

	defer res.Body.Close()

	llmResponse := &LlmResponse{}
	derr := json.NewDecoder(res.Body).Decode(llmResponse)
	if derr != nil {
		fmt.Println("Error decoding response:", derr)
		panic(derr)
	}

	if !llmResponse.Done {
		fmt.Println("LLM response not marked as done")
		panic("Error occurred while sending message to LLM")
	}
	return llmResponse.Response
}

func handleWebsocketConnections(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		fmt.Printf("Upgrade failed: %v\n", err)
		return
	}
	defer ws.Close()

	var completeMessage []byte

	fmt.Println("Client connected")

	for {
		messageType, message, err := ws.ReadMessage()
		if err != nil {
			fmt.Printf("Read failed: %v\n", err)
			break
		}
		fmt.Printf("Received message\n")

		if string(message) == "EOF" {
			fmt.Println("End of file received")
			filePath, err := writeBinaryDataToFile(completeMessage)
			if err != nil {
				fmt.Printf("Failed to write message to disk: %v\n", err)
				break
			}
			fmt.Printf("Wrote file to disk: %v\n", filePath)
			audioFilePath = filePath
			completeMessage = nil
			break
		}

		if messageType == BINARY_MESSAGE {
			completeMessage = append(completeMessage, message...)
		}

		// Echo message back to client
		if err := ws.WriteMessage(messageType, message); err != nil {
			fmt.Printf("Write failed: %v\n", err)
			break
		}
	}

	sttPostUrl := API_GATEWAY_ADDR + "/stt"
	body, err := json.Marshal(map[string]string{
		"filePath": audioFilePath,
	})
	if err != nil {
		panic("Error marshaling the body")
	}
	request, err := http.NewRequest("POST", sttPostUrl, bytes.NewBuffer(body))
	if err != nil {
		fmt.Println("Error occurred while trying to CONSTRUCT the POST request for the STT (speech-to-text) service")
		panic(err)
	}

	request.Header.Add("Content-Type", "application/json")
	client := &http.Client{}
	res, err := client.Do(request)
	if err != nil {
		fmt.Println("Error occurred while trying to SEND the POST request to STT (speech-to-text) service")
		panic(err)
	}

	defer res.Body.Close()

	sstResponse := &SttResponse{}
	derr := json.NewDecoder(res.Body).Decode(sstResponse)
	if derr != nil {
		fmt.Println("Error occurred while trying to decode the response of the STT (speech-to-text) service")
		panic(derr)
	}

	if res.StatusCode != http.StatusOK {
		panic("Error occurred while transcribing audio")
	}

	fmt.Printf("» User: %s\n\n", sstResponse.Data.Text)

	llmResponseMessage := sendMessageTextToLlm(sstResponse.Data.Text)
	fmt.Printf("» Mochibi: %s\n\n", llmResponseMessage)
}
