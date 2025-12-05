#!/bin/bash

# --- CONFIGURATION ---
PROJECT_ID="dialog-flow-259821"
REGION="us-central1"
REPO_NAME="hello-repo"
IMAGE_NAME="minimal-go-hello"
TAG="latest"

# The destination address for the image
FULL_IMAGE_PATH="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$TAG"

gcloud config set project $PROJECT_ID
#bash script_empty_repo.sh

echo "--- Configuration ---"
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo "Target:  $FULL_IMAGE_PATH"
echo "---------------------"

# 1. Enable APIs (Artifact Registry + Cloud Build)
check_and_enable_api() {
  SERVICE_NAME=$1

  # Check if the service is in the list of enabled services
  # The output of gcloud services list is filtered by the service name.
  # If the count is 0, the API is not enabled.
  if [[ $(gcloud services list --enabled --filter="NAME=$SERVICE_NAME" --format="value(NAME)" | wc -l) -eq 0 ]]; then
    echo "   ➡️ Enabling $SERVICE_NAME..."
    gcloud services enable "$SERVICE_NAME"
  else
    echo "   ✅ $SERVICE_NAME is already enabled."
  fi
}

# --- 1. Enable APIs (Only if needed) ---
echo "1. Checking and enabling required APIs..."
check_and_enable_api artifactregistry.googleapis.com
check_and_enable_api cloudbuild.googleapis.com

# 2. Create Repository (if it doesn't exist)
echo "2. Checking for repository '$REPO_NAME'..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION --project=$PROJECT_ID > /dev/null 2>&1; then
    echo "   Repository not found. Creating..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Docker repository for Go apps"
else
    echo "   Repository exists."
fi

# 3. Submit the build to Cloud Build
# The '.' at the end specifies the current directory as the source
echo "3. Submitting build to Google Cloud Build..."
echo "   (This may take a minute as it provisions a server)"
gcloud builds submit --tag $FULL_IMAGE_PATH voila

echo "--- Success! ---"
echo "Build complete and image available at: $FULL_IMAGE_PATH"