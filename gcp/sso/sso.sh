source ./parse.sh

docker build -t sso-app .

docker run -p 5000:5000 \
  -e GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID" \
  -e GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET" \
  -e FLASK_SECRET_KEY="$FLASK_SECRET_KEY" \
  sso-app