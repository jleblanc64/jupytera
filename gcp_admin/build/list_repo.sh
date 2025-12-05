#!/bin/bash

# --- CONFIGURATION ---
REGION="us-central1"
REPO_NAME="admin-repo"
PROJECT_ID=$(gcloud config get-value project)

# The Artifact Registry URL is constructed here:
FULL_REPO_PATH="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME"
gcloud artifacts docker images list "$FULL_REPO_PATH" --include-tags