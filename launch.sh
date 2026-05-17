#!/bin/bash
# launch.sh — Google SSOを使う場合はfile://ではなくHTTP経由で開く必要があります
PORT=8080
DIR="$(cd "$(dirname "$0")" && pwd)"
URL="http://localhost:$PORT/vocab.html"

echo "Starting server at $URL"
echo "Press Ctrl+C to stop"

# Open browser after 1 second
(sleep 1 && open "$URL") &

# Start HTTP server
cd "$DIR" && python3 -m http.server $PORT
