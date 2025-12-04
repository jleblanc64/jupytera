# --- STAGE 1: The Builder ---
# Use a minimal base image that includes the Go compiler
FROM golang:1.21-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the application source code
COPY main.go .

# Statically compile the Go application
# CGO_ENABLED=0 disables CGo, producing a purely static binary
# -o /hello specifies the output file name and location
RUN CGO_ENABLED=0 go build -ldflags "-s -w" -o /hello main.go

# --- STAGE 2: The Final, Minimal Image ---
# Use the "scratch" image, which is literally an empty filesystem layer
FROM scratch

# Set the entrypoint to the port that Cloud Run expects (8080)
EXPOSE 8080

# Copy the single compiled binary file from the builder stage
COPY --from=builder /hello /hello

# Set the command to run the binary when the container starts
ENTRYPOINT ["/hello"]