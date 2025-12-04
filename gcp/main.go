package main

import (
    "fmt"
    "log"
    "net/http"
    "os"
)

func main() {
    // Cloud Run provides the port via the PORT environment variable
    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello World!")
    })

    log.Printf("Listening on port %s", port)
    // Start the server
    if err := http.ListenAndServe(":"+port, nil); err != nil {
        log.Fatal(err)
    }
}