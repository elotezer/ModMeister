#!/bin/bash
set -e

echo "[SETUP] Updating system packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nodejs npm git ffmpeg

echo "[SETUP] Installing PM2 globally..."
sudo npm install pm2 -g

echo "[SETUP] Cloning repository..."
if [ ! -d "ModMeister" ]; then
    git clone https://github.com/laszlokonyari/ModMeister
fi

cd ModMeister

echo "[SETUP] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
else
    echo "[SETUP] venv already exists, skipping..."
fi

if [ -f "requirements.txt" ]; then
    echo "[SETUP] Installing dependencies from requirements.txt..."
    ./venv/bin/pip install -r requirements.txt
else
    echo "[SETUP] Installing dependencies manually..."
    ./venv/bin/pip install dotenv~=0.9.9 python-dotenv~=1.1.1 discord.py openai google google.genai spotipy yt-dlp
fi

echo "[SETUP] Initializing .env file..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
TOKEN=your_bot_token_here
GUILD=your_guild_id_here
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
SPOTIFY_CLIENT_ID=your_spotify_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_secret_here
EOF
    echo "[SETUP] .env file created. Fill in your credentials!"
else
    echo "[SETUP] .env already exists."
fi

echo "[SETUP] Fixing permissions..."
sudo chown -R $USER:$USER .
chmod 775 .

echo "[SETUP] Starting bot and configuring PM2..."
pm2 start src/main.py --interpreter ./venv/bin/python3 --name "modmeister-bot"

sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u $USER --hp $HOME
pm2 save

echo "[SETUP] SUCCESS: Setup complete!"