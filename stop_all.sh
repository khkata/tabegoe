#!/bin/bash
echo "Stopping tabegoe services..."

# Stop frontend
echo "Stopping frontend..."
pkill -f "vite"

# Stop backend
echo "Stopping backend..."
cd /Users/haruka/Desktop/myApps/tabegoe/backend
docker compose down

echo "All services stopped."
