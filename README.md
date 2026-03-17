# ModMeister Discord Bot

A comprehensive Discord bot for server moderation, management, music playback, and utility features with AI integration.

## Overview

ModMeister is a Discord bot that provides powerful moderation and server management tools. It includes utilities for member management, channel and role administration, music playback via SoundCloud and Spotify, and fun commands. The bot also integrates with OpenAI's ChatGPT and Google Gemini APIs, allowing users to prompt these AI models directly from Discord.

## Features

- 🛡️ **Moderation Tools**: Kick, ban, mute, unmute, and warn members with a full warning history
- 📋 **Server Management**: Create, delete, and organize channels, categories, and roles
- 🎵 **Music Playback**: Stream SoundCloud and Spotify tracks directly in voice channels
- 🎲 **Fun Utilities**: Random number generators, text echoing, server info, and more
- 🤖 **AI Integration**: Prompt ChatGPT and Google Gemini directly in Discord
- 💾 **Data Persistence**: SQLite3 database for admins, members, and warnings
- 📊 **Process Management**: PM2 integration for reliable bot operation
- ⚙️ **Environment Configuration**: Secure configuration via environment variables

## Tech Stack

- **Discord Integration**: `discord.py[voice]` - Python Discord API wrapper with voice support
- **Music**: `yt-dlp` - Audio streaming from SoundCloud and other sources
- **Spotify**: `spotipy` - Spotify API client for track/playlist metadata
- **Voice Encryption**: `PyNaCl` - Required for Discord voice connections
- **AI Model Access**:
  - `openai` - OpenAI API client for ChatGPT prompting
  - `google-genai` - Google Gemini API client for prompting
- **Database**: SQLite3 - Lightweight relational database
- **Process Manager**: PM2 - Advanced application process manager
- **Environment**: `python-dotenv` - Environment variable management
- **Runtime**: Python 3.10+

## Requirements

### System Requirements
- Ubuntu/Debian-based Linux system (or compatible)
- Python 3.10+
- FFmpeg (`sudo apt install ffmpeg`)
- Node.js and npm (for PM2)
- Git

### Python Dependencies
```
dotenv~=0.9.9
python-dotenv~=1.1.1
discord.py[voice]
openai
google-genai
yt-dlp
spotipy
PyNaCl
```

## Installation

### Quick Setup (Automated)

Run the provided setup script:

```bash
bash scripts/setup.sh
```

### Manual Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/elotezer/ModMeister
   cd ModMeister
   ```

2. **Install FFmpeg**:
   ```bash
   sudo apt install ffmpeg
   ```

3. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   ```bash
   touch .env
   nano .env
   ```

6. **Run the bot**:
   ```bash
   python3 src/main.py
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
TOKEN=your_discord_bot_token_here
GUILD=your_guild_id_here
GPT_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
```

### Getting Tokens & API Keys

- **Discord Token**: Create an app at [Discord Developer Portal](https://discord.com/developers/applications)
- **OpenAI API Key**: Get it from [OpenAI API Keys](https://platform.openai.com/api-keys)
- **Google Gemini API Key**: Get it from [Google AI Studio](https://aistudio.google.com/)
- **Spotify Credentials**: Create an app at [Spotify for Developers](https://developer.spotify.com/dashboard) — select **Web API** only, set redirect URI to `http://localhost:8888/callback`

## Project Structure

```
ModMeister/
├── src/
│   ├── main.py              # Main bot application
│   └── cogs/
│       ├── core.py          # Core commands (ping, echo, help) + events
│       ├── user.py          # User commands (roll, AI prompts, serverinfo)
│       ├── admin.py         # Admin commands (moderation, server management)
│       └── music.py         # Music commands (play, queue, skip, etc.)
├── scripts/
│   ├── setup.sh             # Automated setup script
│   ├── start.sh             # Start the bot
│   ├── stop.sh              # Stop the bot
│   └── update.sh            # Update the bot
├── requirements.txt         # Python dependencies
├── .env                     # Environment configuration (create after setup)
├── .gitignore               # Git ignore patterns
└── README.md                # This file
```

## Commands

### Core Commands

| Command | Description | Permission |
|---|---|---|
| `/ping` | Check if the bot is alive + latency | Everyone |
| `/echo <text>` | Echo back a message | Everyone |
| `/help` | Display all bot commands | Everyone |

---

### User Commands

| Command | Description | Permission |
|---|---|---|
| `/roll <x> <y>` | Random integer between a range | Everyone |
| `/roll_f` | Random float between 0 and 1 | Everyone |
| `/serverinfo` | Display detailed server information | Everyone |
| `/gpt <prompt>` | Ask ChatGPT | Everyone |
| `/gemini <prompt>` | Ask Gemini | Everyone |

---

### Music Commands

> All playback control commands require the user to be in the same voice channel as the bot.

| Command | Description | Permission |
|---|---|---|
| `/play <link>` | Play a SoundCloud URL or Spotify track/playlist | Everyone |
| `/pause` | Pause the current track | Same voice channel |
| `/resume` | Resume the paused track | Same voice channel |
| `/skip` | Skip the current track | Same voice channel |
| `/stop` | Stop playback and disconnect | Same voice channel |
| `/queue` | Show the current queue | Everyone |
| `/nowplaying` | Show what's currently playing | Everyone |
| `/loop` | Toggle looping the current track | Same voice channel |
| `/volume <0-100>` | Set playback volume | Same voice channel |

**Supported sources:**
- SoundCloud direct URLs
- Spotify track links (`open.spotify.com/track/...`)
- Spotify playlist links (`open.spotify.com/playlist/...`) — up to 25 tracks

> **Note**: Spotify tracks are resolved to their title and artist, then streamed via SoundCloud.

---

### Admin Commands

> All admin commands require the Admin role or Server Owner unless stated otherwise.

#### Moderation

| Command | Description |
|---|---|
| `/admin kick <user> <reason>` | Kick a member |
| `/admin ban <user> <reason>` | Ban a member |
| `/admin unban <user>` | Unban a member |
| `/admin mute <user> <minutes> <reason>` | Timeout a member |
| `/admin unmute <user>` | Remove a timeout |
| `/admin warn <user> <reason>` | Issue a warning |
| `/admin warnings <user>` | View all warnings for a member |
| `/admin clear_warnings <user> [id]` | Clear all warnings or a specific one by ID |

#### Admin Management

| Command | Description | Permission |
|---|---|---|
| `/admin add <user>` | Grant admin to a user | Server Owner only |
| `/admin remove <user>` | Revoke admin from a user | Server Owner only |
| `/admin userinfo <user>` | Full profile, warnings & history of a user | Admin |

#### Roles

| Command | Description |
|---|---|
| `/admin give_role <role> [user]` | Give a role to a user or everyone |
| `/admin take_role <role> [user]` | Remove a role from a user or everyone |
| `/admin clear_roles` | Delete all non-managed roles |

#### Channels & Categories

| Command | Description |
|---|---|
| `/admin new_text_ch <name> <category>` | Create a text channel |
| `/admin del_text_ch <channel>` | Delete a text channel |
| `/admin new_voice_ch <name> <category>` | Create a voice channel |
| `/admin del_voice_ch <channel>` | Delete a voice channel |
| `/admin new_category <name>` | Create a category |
| `/admin del_category <category>` | Delete a category |
| `/admin new_private_category <name>` | Create an admin-only category |

#### Server

| Command | Description |
|---|---|
| `/admin setup_server` | Wipe and rebuild a basic server layout |
| `/admin wipe` | Delete all channels and categories |

> ⚠️ `setup_server` and `wipe` are destructive and cannot be undone.

---

## Database

ModMeister uses SQLite3 with the following tables:

### `admins`
| Column | Type | Description |
|---|---|---|
| `guild_id` | INTEGER | Discord server ID |
| `user_id` | INTEGER | Discord user ID |

### `members`
| Column | Type | Description |
|---|---|---|
| `guild_id` | INTEGER | Discord server ID |
| `user_id` | INTEGER | Discord user ID |

### `warnings`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-incrementing warning ID |
| `guild_id` | INTEGER | Discord server ID |
| `user_id` | INTEGER | Warned user ID |
| `reason` | VARCHAR(50) | Warning reason |
| `warned_by` | INTEGER | Issuing admin user ID |
| `timestamp` | DATETIME | When the warning was issued |

---

## Process Management

**Start with PM2**:
```bash
pm2 start src/main.py --interpreter ./venv/bin/python3 --name "modmeister-bot"
```

**Or use the scripts**:
```bash
bash scripts/start.sh    # Start
bash scripts/stop.sh     # Stop
bash scripts/update.sh   # Pull latest and restart
```

**PM2 commands**:
```bash
pm2 list
pm2 logs modmeister-bot
pm2 restart modmeister-bot
pm2 delete modmeister-bot
```

---

## Known Issues & Limitations

- `setup_server` and `wipe` are destructive and cannot be undone
- Private categories require an "Admin" role to exist in the server
- Spotify playback depends on SoundCloud availability of the track
- Spotify playlists are capped at 25 tracks to prevent spam
- Some commands may be affected by Discord API rate limits

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues or suggestions, open an [Issue](https://github.com/elotezer/ModMeister/issues) on GitHub and include the command used, the error received, and relevant server configuration details.

## License

This project is currently unlicensed. For licensing information, please contact the repository owner.

## Acknowledgments

- Built with [discord.py](https://discordpy.readthedocs.io/)
- Music streaming via [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Spotify integration via [spotipy](https://spotipy.readthedocs.io/)
- AI integration with [OpenAI API](https://openai.com/api/) and [Google Gemini](https://ai.google.dev/)
- Process management by [PM2](https://pm2.keymetrics.io/)

---

**Last Updated**: March 2026  
**Repository**: [elotezer/ModMeister](https://github.com/elotezer/ModMeister)  
**Author**: [@elotezer](https://github.com/elotezer)