#!/bin/bash

# --- CONFIGURATION ---
REGION="us-central1"
REPO_NAME="hello-repo"
PROJECT_ID=$(gcloud config get-value project)

# Base URL for the Artifact Registry repository
REPO_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME"

echo "--- WARNING: DELETING ALL IMAGES IN REPOSITORY ---"
echo "Project ID: $PROJECT_ID"
echo "Repository: $REPO_NAME ($REGION)"
echo "-------------------------------------------------"

# Command to list all unique image paths in the repo.
# We explicitly check for 'IMAGE' or 'IMAGE_PATH' based on what worked earlier.
# If 'IMAGE' works, this is the most reliable version for your environment.
IMAGE_PATHS=$(gcloud artifacts docker images list "$REPO_URL" \
    --project="$PROJECT_ID" \
    --format="value(IMAGE)" \
    | sort -u) # <-- Retain sort -u to prevent multiple deletion attempts

# Re-check for emptiness after extraction and sorting
if [ -z "$IMAGE_PATHS" ]; then
    echo "ERROR: Image list extraction failed or no images were found. Exiting."
    # For debugging purposes, you can uncomment the line below to see the raw output:
    # gcloud artifacts docker images list "$REPO_URL" --project="$PROJECT_ID"
    exit 1
fi

# Iterate through each UNIQUE image path found
while IFS= read -r IMAGE_PATH; do
    if [[ -n "$IMAGE_PATH" ]]; then
        echo "Deleting image and all versions: $IMAGE_PATH"

        # Use --quiet (-q) to auto-accept the confirmation prompt for deletion.
        gcloud artifacts docker images delete "$IMAGE_PATH" \
            --delete-tags \
            --quiet

        # Check if the deletion was successful
        if [ $? -eq 0 ]; then
            echo "Successfully deleted $IMAGE_PATH."
        else
            # This error is expected on subsequent attempts after the first successful delete.
            echo "Failed to delete $IMAGE_PATH (Expected if image was just deleted). Skipping."
        fi
    fi
done <<< "$IMAGE_PATHS"

echo "--- Deletion process complete. ---"