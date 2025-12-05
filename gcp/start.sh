#!/bin/bash

bash stop.sh

# --- 1. ARTIFACT REGISTRY CONFIG (Source Image) ---
AR_REGION="us-central1"
AR_REPO_NAME="hello-repo"
AR_IMAGE_NAME="minimal-go-hello"

# --- 2. CLOUD RUN CONFIG (Target Service) ---
CR_SERVICE_NAME="minimal-go-service"
CR_REGION="us-central1"
PROJECT_ID=$(gcloud config get-value project)

# --- 3. FIND THE LATEST IMAGE DIGEST BY UPDATE TIME ---
echo "1. Finding the digest of the newest image in ${AR_REPO_NAME}..."

# Full image path including the image name:
FULL_IMAGE_PATH="${AR_REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO_NAME}/${AR_IMAGE_NAME}"

# Query ALL images in the repo, filter for our specific image name,
# sort by update time (the '~' means descending order to get the newest first),
# extract the digest, and limit to the first result (the newest one).
IMAGE_DIGEST=$(gcloud artifacts docker images list "$FULL_IMAGE_PATH" \
    --project="${PROJECT_ID}" \
    --sort-by="~UPDATE_TIME" \
    --filter="IMAGE~${AR_IMAGE_NAME}" \
    --format='value(DIGEST)' \
    --limit 1 2>/dev/null)

if [ -z "$IMAGE_DIGEST" ]; then
  echo "ERROR: Could not find any image digest for ${AR_IMAGE_NAME} in ${AR_REPO_NAME}."
  echo "Please verify the image path: ${FULL_IMAGE_PATH}"
  exit 1
fi

# The fully qualified image path with the immutable digest:
DEPLOY_IMAGE_URL="${FULL_IMAGE_PATH}@${IMAGE_DIGEST}"

echo "   Found Digest: ${IMAGE_DIGEST}"
echo "   Deployment URL: ${DEPLOY_IMAGE_URL}"

# --- 4. DEPLOY TO CLOUD RUN ---
echo -e "\n2. Enabling Cloud Run API and deploying service ${CR_SERVICE_NAME}..."

gcloud services enable run.googleapis.com

# Create the service.yaml file
cat > service.yaml << EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: $CR_SERVICE_NAME # Match your service name
  annotations:
    run.googleapis.com/ingress: "all"
    run.googleapis.com/launch-stage: "GA"
  labels:
    cloud.googleapis.com/location: $CR_REGION # Match your region
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cpu-throttling: "false"
        autoscaling.knative.dev/maxScale: "1"
        autoscaling.knative.dev/minScale: "0"
        # The revision name is often a timestamp or hash, keep it generic
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
      - image: $DEPLOY_IMAGE_URL # Match your image URL
        ports:
        - containerPort: 8080 # Match your port
        resources:
          limits:
            cpu: 8000m
            memory: 4096Mi
        # 👇 This is the key part for the custom path health check
        livenessProbe:
          httpGet:
            path: /kernel_count.txt # ⬅️ SPECIFY YOUR CUSTOM PATH HERE
            port: 8080
            httpHeaders:
              - name: 'Custom-Header'
                value: 'HealthCheck' # Optional: Add headers if needed
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 10
EOF

gcloud run services replace service.yaml \
  --region "$CR_REGION"

gcloud run services add-iam-policy-binding "$CR_SERVICE_NAME" \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region="$CR_REGION"

echo -e "\nDeployment complete. Check the output above for the Service URL."