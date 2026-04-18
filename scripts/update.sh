#!/bin/bash
set -e

cd ~/ModMeister || exit

echo "[UPDATE] Starting update: $(date)"

echo "[UPDATE] Checking Git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "[UPDATE] Stashing local changes..."
    git stash
fi

echo "[UPDATE] Pulling code..."
if ! git pull origin main; then
    echo "[UPDATE] Merge conflict detected. Force reset? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        git reset --hard origin/main
        git pull
    else
        echo "[UPDATE] Update cancelled. Reverting to previous version..."
        git reset --hard HEAD@{1}
        exit 1
    fi
fi

echo "[UPDATE] Installing dependencies..."
./venv/bin/pip install -r requirements.txt

echo "[UPDATE] Restarting bot..."
pm2 restart modmeister-bot

echo "[UPDATE] SUCCESS: Update complete!"
echo "[UPDATE] View logs: pm2 logs modmeister-bot"