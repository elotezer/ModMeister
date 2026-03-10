#!/bin/bash
cd ~/ModMeister
pm2 start src/main.py --interpreter ./venv/bin/python3 --name "modmeister-bot"
pm2 save