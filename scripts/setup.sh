#!/bin/bash
set -e

echo "--- Rendszer frissítése és csomagok telepítése ---"
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nodejs npm git

echo "--- PM2 globális telepítése ---"
sudo npm install pm2 -g

echo "--- Projekt klónozása ---"
if [ ! -d "ModMeister" ]; then
    git clone https://github.com/laszlokonyari/ModMeister
fi

cd ModMeister

echo "--- Virtuális környezet (venv) beállítása ---"
python3 -m venv venv
./venv/bin/pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo "--- Függőségek telepítése a requirements.txt-ből ---"
    ./venv/bin/pip install -r requirements.txt
else
    echo "--- Függőségek telepítése manuálisan ---"
    ./venv/bin/pip install dotenv~=0.9.9 python-dotenv~=1.1.1 discord.py openai google google.genai
fi

echo "--- Környezeti változók (.env) inicializálása ---"
if [ ! -f ".env" ]; then
    touch .env
    echo ".env fájl létrehozva. Kérlek, töltsd ki az adatokat!"
fi

echo "--- Jogosultságok javítása ---"
sudo chown -R $USER:$USER .
chmod 775 .

echo "--- Bot indítása és PM2 konfigurálása ---"
pm2 start src/main.py --interpreter ./venv/bin/python3 --name "modmeister-bot"

sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u $USER --hp $HOME
pm2 save

echo "--- Telepítés és beállítás sikeresen befejeződött! ---"