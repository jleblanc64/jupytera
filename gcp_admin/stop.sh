SERVICE_NAME="admin"
REGION="us-central1"

gcloud run services delete $SERVICE_NAME \
  --region $REGION \
  --quiet