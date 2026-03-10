#!/bin/bash

echo "--- Frissítés indítása: $(date) ---"

git pull origin master

./venv/bin/pip install -r requirements.txt

pm2 restart modmeister-bot

echo "--- Frissítés sikeresen befejeződött! ---"
echo "Logok megtekintése: pm2 logs modmeister-bot"
