#!/bin/bash

sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nodejs npm git

sudo npm install pm2 -g

if [ ! -d "ModMeister" ]; then
    git clone https://github.com/elotezer/ModMeister
fi
cd ModMeister

python3 -m venv venv

./venv/bin/pip install --upgrade pip
./venv/bin/pip install dotenv~=0.9.9 python-dotenv~=1.1.1 discord.py openai

if [ ! -f ".env" ]; then
    touch .env
fi

pm2 start src/main.py --interpreter ./venv/bin/python3 --name "modmeister-bot"

pm2 startup | grep "sudo" | bash
pm2 save