#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR" || exit

echo "[START] Launching bot..."
pm2 start modmeister-bot || pm2 start src/main.py --interpreter "$(pwd)/venv/bin/python3" --name "modmeister-bot"

if [ $? -eq 0 ]; then
    pm2 save
    echo "[START] SUCCESS: Bot is running"
else
    echo "[START] ERROR: Failed to start bot"
    exit 1
fi