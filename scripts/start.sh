#!/bin/bash
set -e

cd ~/ModMeister || exit

echo "--- ModMeister Bot indítása ---"
pm2 start modmeister-bot || pm2 start src/main.py --interpreter ./venv/bin/python3 --name "modmeister-bot"
pm2 save

echo "--- Bot elindítva! ---"