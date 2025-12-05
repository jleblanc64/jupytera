#!/bin/bash
PROPERTIES_FILE="/home/charles/Desktop/sso2.txt"

get_value() {
    local KEY=$1
    local FILE=$2
    local VALUE=$(grep "^[[:space:]]*${KEY}=" "$FILE" | \
                  grep -v '^#' | \
                  awk -F= '{print $2}' | \
                  tr -d "\"' " | \
                  xargs)
    echo "$VALUE"
}

CLIENT_ID=$(get_value "GOOGLE_CLIENT_ID" "$PROPERTIES_FILE")
CLIENT_SECRET=$(get_value "GOOGLE_CLIENT_SECRET" "$PROPERTIES_FILE")
FLASK=$(get_value "FLASK_SECRET_KEY" "$PROPERTIES_FILE")

# The script must print 'export' statements so they can be executed by the calling shell.
export GOOGLE_CLIENT_ID=$CLIENT_ID
export GOOGLE_CLIENT_SECRET=$CLIENT_SECRET
export FLASK_SECRET_KEY=$FLASK