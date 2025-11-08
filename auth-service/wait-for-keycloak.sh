#!/bin/bash
# Wait for Keycloak to be ready before starting the auth service

set -e

KEYCLOAK_URL="${KEYCLOAK_SERVER_URL:-http://keycloak:8080}"
MAX_RETRIES=30
RETRY_INTERVAL=5

echo "Waiting for Keycloak at $KEYCLOAK_URL..."

retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    # Try to connect to Keycloak
    if python -c "import requests; requests.get('$KEYCLOAK_URL', timeout=5)" 2>/dev/null; then
        echo "✓ Keycloak is ready!"
        break
    else
        retry_count=$((retry_count + 1))
        echo "⏳ Waiting for Keycloak... (attempt $retry_count/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    fi
done

if [ $retry_count -eq $MAX_RETRIES ]; then
    echo "❌ ERROR: Keycloak did not become ready after $MAX_RETRIES attempts"
    exit 1
fi

# Start the Flask application
echo "🚀 Starting Auth Service..."
exec python run.py
