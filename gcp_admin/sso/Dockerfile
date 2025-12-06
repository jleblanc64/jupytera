# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# --- START GCLOUD CLI INSTALLATION ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 2. Add the Google Cloud SDK GPG key using the new 'signed-by' method.
#    This avoids the 'apt-key: not found' error entirely.
RUN curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

# 3. Add the Google Cloud SDK repository, referencing the new keyring.
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" > /etc/apt/sources.list.d/google-cloud-sdk.list

# 4. Install the gcloud CLI
RUN apt-get update && \
    apt-get install -y google-cloud-sdk
# --- END GCLOUD CLI INSTALLATION ---

# Copy the requirements file and install dependencies first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and the build script
COPY app.py .
COPY script_build.sh .
COPY script_empty_repo.sh .
COPY script_start.sh .
COPY script_stop.sh .
COPY voila voila

# Expose the port the Flask app runs on
EXPOSE 5000

# Ensure the build script is executable
RUN chmod +x script_build.sh

# Run the application
CMD ["python", "app.py"]