#!/bin/bash
set -e

cd ~/ModMeister || exit

echo "--- Frissítés indítása: $(date) ---"

echo "Kód letöltése..."
git pull

echo "Függőségek frissítése..."
./venv/bin/pip install -r requirements.txt

echo "Bot újraindítása..."
pm2 restart modmeister-bot

echo "--- Frissítés sikeresen befejeződött! ---"
echo "Logok megtekintése: pm2 logs modmeister-bot"