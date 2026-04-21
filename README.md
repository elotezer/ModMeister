# ModMeister Discord Bot

A comprehensive Discord bot for server moderation, management, music playback, and utility features with AI integration.

## Overview

ModMeister is a Discord bot that provides powerful moderation and server management tools. It includes utilities for member management, channel and role administration, music playback via SoundCloud and Spotify, and fun commands. The bot also integrates with OpenAI's ChatGPT and Google Gemini APIs, allowing users to prompt these AI models directly from Discord.

**Website**: https://modmeister.konyarilaszlo.com

## Features

- 🛡️ **Moderation Tools**: Kick, ban, mute, unmute, and warn members with full warning history and tiered punishment escalation
- 📋 **Server Management**: Create, delete, and organize channels, categories, and roles
- 🎵 **Music Playback**: Stream SoundCloud and Spotify tracks directly in voice channels with queue management
- 🎲 **Fun Utilities**: Random number generators, text echoing, server info, and more
- 🤖 **AI Integration**: Prompt ChatGPT and Google Gemini directly in Discord
- 💾 **Data Persistence**: SQLite3 database for admins, members, warnings, and punishment thresholds
- 📊 **Process Management**: Fully Dockerized with automatic updates via Watchtower
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
- **Containerization**: Docker & Docker Compose
- **Environment**: `python-dotenv` - Environment variable management
- **Runtime**: Python 3.10+

## Requirements

### System Requirements
- Docker and Docker Compose

## Installation

### Quick Setup (Plug & Play)

ModMeister uses Watchtower for automatic updates. Simply run these commands on your VPS:

   ```bash
mkdir ModMeister && cd ModMeister
wget https://raw.githubusercontent.com/laszlokonyari/ModMeister/main/docker-compose.yml
touch .env botdatabase.db
nano .env

# Once your .env is configured, start the bot:
docker compose up -d
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
| `/avatar [user]` | Display a user's avatar | Everyone |
| `/roles [user]` | Display a user's roles | Everyone |
| `/serverinfo` | Display detailed server information | Everyone |
| `/gpt <prompt>` | Ask ChatGPT | Everyone |
| `/gemini <prompt>` | Ask Gemini | Everyone |
| `/invite [duration]` | Create a server invite link | Everyone |

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

#### Moderation with Punishment Escalation

The warning system includes automatic tiered escalation:

| Command | Description |
|---|---|
| `/admin warn <user> <reason>` | Issue a warning to a member |
| `/admin warnings <user>` | View all warnings for a member |
| `/admin clear_warnings <user> [id]` | Clear all warnings or a specific one by ID |
| `/admin punishment_view` | View current punishment thresholds for the server |
| `/admin punishment_set <type> <threshold> <minutes>` | Configure escalation thresholds |

**Punishment Escalation System:**
- Default thresholds: 3 warnings → mute, 6 warnings → kick, 8 warnings → ban
- Mute duration is configurable (default: 30 minutes)
- When a warning is issued, the system automatically checks if thresholds are exceeded
- If exceeded, the appropriate punishment is executed (mute → kick → ban progression)
- All punishment actions are logged and users receive notification embeds

**Example Configuration:**
```
/admin punishment_set mute 3 30        # Mute after 3 warnings for 30 minutes
/admin punishment_set kick 6 0         # Kick after 6 warnings
/admin punishment_set ban 8 0          # Ban after 8 warnings
```

---

#### Standard Moderation

| Command | Description |
|---|---|
| `/admin kick <user> <reason>` | Kick a member |
| `/admin ban <user> <reason>` | Ban a member |
| `/admin unban <user>` | Unban a member |
| `/admin mute <user> <minutes> <reason>` | Timeout a member |
| `/admin unmute <user>` | Remove a timeout |

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

### `guild_punishments`
| Column | Type | Description |
|---|---|---|
| `guild_id` | INTEGER | Discord server ID (primary key) |
| `mute_threshold` | INTEGER | Warning count to trigger mute (default: 3) |
| `kick_threshold` | INTEGER | Warning count to trigger kick (default: 6) |
| `ban_threshold` | INTEGER | Warning count to trigger ban (default: 8) |
| `mute_minutes` | INTEGER | Duration of mute in minutes (default: 30) |

---

## Docker & Automatic Updates

ModMeister is fully containerized and uses **Watchtower** for seamless, zero-downtime updates. 

When you deploy the bot using the provided `docker-compose.yml` file, it pulls the latest pre-built image from the GitHub Container Registry (`ghcr.io`). Watchtower runs alongside the bot and checks the registry every 5 minutes. 

If a new version of ModMeister is published to the `main` branch, Watchtower will automatically:
1. Download the new image
2. Gracefully shut down the old container
3. Start the new container with your existing `.env` and `botdatabase.db`
4. Clean up the old, unused images

**Useful Docker Commands:**
```bash
docker compose logs -f      # View live console logs
docker compose restart      # Manually restart the bot
docker compose down         # Stop the bot and Watchtower
docker compose up -d        # Start the bot in the background
```

---

## Recent Improvements (April 2026)

### Music Playback Fixes
- Fixed duplicate "Now Playing" embed on track start
- Improved response handling to prevent "thinking" state in Discord
- Added graceful error handling for missing FFmpeg dependency

### Script Enhancements
- Implemented relative path resolution for better cross-environment compatibility
- Added automatic git branch detection (supports both `main` and `master`)
- Enhanced error handling with rollback capability on failed updates
- Added `.env` template generation during setup
- Improved logging with keyword prefixes (`[SETUP]`, `[START]`, `[STOP]`, `[UPDATE]`)
- Fixed Windows opus library loading issue for audio playback

### Punishment System Implementation
- Added tiered warning escalation system with configurable thresholds
- Implemented `guild_punishments` database table for per-server settings
- Added `/admin punishment_view` and `/admin punishment_set` commands
- Auto-execution of punishments (mute → kick → ban) based on warning count
- User-friendly embed notifications for punishment actions

---

## Troubleshooting

### Bot Won't Start
- Ensure `.env` file exists and has `TOKEN` and `GUILD` set
- Check Python version: `python3 --version` (must be 3.10+)
- Verify virtual environment: `source venv/bin/activate`
- View logs: `pm2 logs modmeister-bot`

### Music Commands Not Working
- Verify FFmpeg is installed: `ffmpeg -version`
- On Ubuntu/Debian: `sudo apt install ffmpeg`
- On macOS: `brew install ffmpeg`
- Ensure bot has voice permissions in channels

### SoundCloud Tracks Return No Results
- Some tracks may be region-restricted or removed
- Try using direct SoundCloud URLs instead of search queries
- Spotify playlists are limited to 25 tracks to prevent spam

### Git Permission Error During Update
- If `.git/objects` has wrong ownership: `sudo chown -R $USER:$USER .git`
- Run: `bash scripts/update.sh` again

### Bot Crashes After Update
- Automatic rollback is enabled: `git reset --hard HEAD@{1}`
- Check dependencies: `pip install -r requirements.txt`
- Review error logs: `pm2 logs modmeister-bot --lines 50`

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

For issues or suggestions, open an [Issue](https://github.com/laszlokonyari/ModMeister/issues) on GitHub and include the command used, the error received, and relevant server configuration details.

## License

This project is currently unlicensed. For licensing information, please contact the repository owner.

## Acknowledgments

- Built with [discord.py](https://discordpy.readthedocs.io/)
- Music streaming via [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Spotify integration via [spotipy](https://spotipy.readthedocs.io/)
- AI integration with [OpenAI API](https://openai.com/api/) and [Google Gemini](https://ai.google.dev/)

---

**Last Updated**: April 21, 2026  
**Repository**: [laszlokonyari/ModMeister](https://github.com/laszlokonyari/ModMeister)  
**Author**: [@laszlokonyari](https://github.com/laszlokonyari)