# --- Stage 1: Builder ---
FROM golang:1.23-alpine AS builder

WORKDIR /app

# Copy source code
COPY main.go .

# Build the binary.
# CGO_ENABLED=0 is crucial. It ensures static linking so the binary
# doesn't depend on system libraries that don't exist in 'scratch'.
RUN CGO_ENABLED=0 GOOS=linux go build -o server main.go

# --- Stage 2: Final Minimal Image ---
FROM scratch

# Copy only the binary from the builder stage
COPY --from=builder /app/server /server

# Expose port (documentary only)
EXPOSE 8080

# Run the binary
ENTRYPOINT ["/server"]