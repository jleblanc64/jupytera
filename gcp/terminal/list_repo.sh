#!/bin/bash

# --- CONFIGURATION ---
REGION="us-central1"
REPO_NAME="hello-repo"
PROJECT_ID=$(gcloud config get-value project)

# The Artifact Registry URL is constructed here:
FULL_REPO_PATH="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME"

echo "Listing all Docker Images and their tags in repository: $REPO_NAME ($REGION)"
echo "Project: $PROJECT_ID"
echo "Target Path: $FULL_REPO_PATH"
echo "---------------------------------------------------------"

# Note: In this old syntax, the repository path is passed directly
# as the final argument, and --include-tags is used.
gcloud artifacts docker images list "$FULL_REPO_PATH" --include-tags