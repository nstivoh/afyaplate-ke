#!/bin/bash
set -e

echo "Verifying Database and Cache..."

# Run seed_db.py to generate cache and SQLite db if they don't exist
python scripts/seed_db.py

echo "Starting Uvicorn Server..."
exec "$@"
