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
./venv/bin/pip install dotenv~=0.9.9 python-dotenv~=1.1.1 discord.py openai google google.genai

if [ ! -f ".env" ]; then
    touch .env
fi

sudo chown -R $USER:$USER $(pwd)
chmod 775 $(pwd)

pm2 start src/main.py --interpreter ./venv/bin/python3 --name "modmeister-bot"

sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u $USER --hp /home/$USER
pm2 save
