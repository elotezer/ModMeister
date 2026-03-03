# ModMeister 🤖

A comprehensive Discord bot for server moderation, management, and utility features with AI integration for text generation.

## Overview

ModMeister is a Discord bot that provides powerful moderation and server management tools. It includes utilities for member management, channel and role administration, and fun commands. The bot also integrates with OpenAI's ChatGPT and Google Gemini APIs, allowing users to prompt these AI models directly from Discord.

## Features

- 🛡️ **Moderation Tools**: Kick, ban, mute, and unmute members with ease
- 📋 **Server Management**: Create, delete, and organize channels, categories, and roles
- 🎲 **Fun Utilities**: Random number generators, text echoing, and more
- 🤖 **AI Integration**: Prompt ChatGPT and Google Gemini directly in Discord
- 💾 **Data Persistence**: SQLite3 database for storing admin roles and data
- 🔧 **Easy Setup**: Automated setup script for quick deployment
- 📊 **Process Management**: PM2 integration for reliable bot operation
- ⚙️ **Environment Configuration**: Secure configuration via environment variables

## Tech Stack

- **Discord Integration**: `discord.py` - Python Discord API wrapper
- **AI Model Access**: 
  - `openai` - OpenAI API client for ChatGPT prompting
  - `google-genai` - Google Gemini API client for prompting
- **Database**: SQLite3 - Lightweight relational database
- **Process Manager**: PM2 - Advanced application process manager
- **Environment**: `python-dotenv` - Environment variable management
- **Runtime**: Python 3.8+

## Requirements

### System Requirements
- Ubuntu/Debian-based Linux system (or compatible)
- Python 3.8+
- Node.js and npm
- Git

### Python Dependencies
```
dotenv~=0.9.9
python-dotenv~=1.1.1
discord.py
openai
google-genai
```

## Installation

### Quick Setup (Automated)

Run the provided setup script:

```bash
bash setup.sh
```

This script will:
- Update system packages
- Install Python3 venv, pip, Node.js, npm, and git
- Install PM2 globally
- Clone the repository (if not already present)
- Create a Python virtual environment
- Install all required Python packages
- Create a `.env` file for configuration
- Set up proper file permissions
- Start the bot with PM2

### Manual Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/elotezer/ModMeister
   cd ModMeister
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install dotenv~=0.9.9 python-dotenv~=1.1.1 discord.py openai google-genai
   ```

4. **Configure environment variables**:
   ```bash
   touch .env
   # Edit .env with your Discord token and API keys
   nano .env
   ```

5. **Run the bot**:
   ```bash
   python3 src/main.py
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
DISCORD_TOKEN=your_discord_bot_token_here
GPT_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### Getting Tokens & API Keys

- **Discord Token**: Create an app at [Discord Developer Portal](https://discord.com/developers/applications)
- **OpenAI API Key**: Get it from [OpenAI API Keys](https://platform.openai.com/api-keys)
- **Google Gemini API Key**: Get it from [Google AI Studio](https://aistudio.google.com/)

## Project Structure

```
ModMeister/
├── src/
│   ├── main.py              # Main bot application
│   └── cogs/
│       ├── core.py          # Core commands (ping, echo, help)
│       ├── user.py          # User commands (roll, AI prompts)
│       └── admin.py         # Admin commands (moderation, server management)
├── setup.sh                 # Automated setup script
├── start.sh                 # Start the bot
├── stop.sh                  # Stop the bot
├── update.sh                # Update the bot
├── requirements.txt         # Python dependencies
├── .env                     # Environment configuration (create after setup)
├── .gitignore               # Git ignore patterns
└── README.md                # This file
```

## Commands

### Core Commands (Available to Everyone)

#### `/ping`
Checks if the bot is alive and responsive.
```
/ping
```

#### `/echo`
Echoes back the text you provide.
```
/echo <text>
```
**Example**: `/echo Hello, World!` → Returns: "Hello, World!"

#### `/help`
Displays all available bot commands with descriptions.
```
/help
```

---

### User Commands (Available to Everyone)

#### `/roll`
Generates a random whole number between two values.
```
/roll <x> <y>
```
**Example**: `/roll 1 100` → Returns a random number between 1 and 100

#### `/roll_f`
Generates a random decimal number between 0 and 1.
```
/roll_f
```
**Example**: `/roll_f` → Returns something like "0.742958"

#### `/gpt`
Sends a prompt to ChatGPT and returns the response in Discord.
```
/gpt <prompt>
```
**Example**: `/gpt What is the capital of France?` → Returns ChatGPT's response

**Note**: Requires `GPT_KEY` to be set in `.env`

#### `/gemini`
Sends a prompt to Google Gemini and returns the response in Discord.
```
/gemini <prompt>
```
**Example**: `/gemini Explain quantum computing in simple terms` → Returns Gemini's response

**Note**: Requires `GEMINI_API_KEY` to be set in `.env`

---

### Admin Commands (Require Admin Role or Server Owner)

#### Moderation Commands

##### `/admin kick`
Kicks a member from the server.
```
/admin kick <user> <reason>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin kick @BadUser Spam` → Removes the user from the server

##### `/admin ban`
Bans a member from the server permanently.
```
/admin ban <user> <reason>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin ban @ToxicUser Harassment`

##### `/admin unban`
Unbans a previously banned member.
```
/admin unban <user>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin unban @UnbanMe`

##### `/admin mute`
Applies a timeout to a member (mutes them temporarily).
```
/admin mute <user> <minutes> <reason>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin mute @SpamUser 30 Spamming` → Mutes for 30 minutes

##### `/admin unmute`
Removes timeout from a member.
```
/admin unmute <user>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin unmute @MutedUser`

#### Admin Management Commands

##### `/admin add`
Adds a user as an admin (database entry + Admin role).
```
/admin add <user>
```
**Permissions**: Server Owner Only
**Example**: `/admin add @NewAdmin`

##### `/admin remove`
Removes admin privileges from a user.
```
/admin remove <user>
```
**Permissions**: Server Owner Only
**Example**: `/admin remove @FormerAdmin`

#### Channel Management Commands

##### `/admin new_text_ch`
Creates a new text channel in a specific category.
```
/admin new_text_ch <channel_name> <category>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin new_text_ch general Text`

##### `/admin del_text_ch`
Deletes a text channel.
```
/admin del_text_ch <channel>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin del_text_ch #old-channel`

##### `/admin new_voice_ch`
Creates a new voice channel in a specific category.
```
/admin new_voice_ch <channel_name> <category>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin new_voice_ch Gaming Voice`

##### `/admin del_voice_ch`
Deletes a voice channel.
```
/admin del_voice_ch <channel>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin del_voice_ch #voice-room`

#### Category Management Commands

##### `/admin new_category`
Creates a new category.
```
/admin new_category <name>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin new_category Projects`

##### `/admin new_private_category`
Creates a private category (only visible to admins).
```
/admin new_private_category <name>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin new_private_category Staff-Only`

##### `/admin del_category`
Deletes a category and all its channels.
```
/admin del_category <category>
```
**Permissions**: Admin role or Server Owner
**Example**: `/admin del_category Archived`

#### Role Management Commands

##### `/admin give_role`
Assigns a role to a user or everyone in the server.
```
/admin give_role <role> [user]
```
**Permissions**: Admin role or Server Owner
- If `user` is specified: Gives role to that user
- If `user` is omitted: Gives role to everyone

**Examples**: 
- `/admin give_role @Member @User` → Gives Member role to User
- `/admin give_role @Member` → Gives Member role to everyone

**Note**: Only server owner can give Admin roles

#### Server Setup Commands

##### `/admin setup_server`
Creates a complete server layout with predefined categories and channels.
```
/admin setup_server
```
**Permissions**: Admin role or Server Owner
**What it creates**:
- **About** category (read-only):
  - #welcome, #rules, #roles, #server, #channels, #leavers
- **Text** category (public):
  - #chat, #images, #videos, #music, #links, #games
- **Voice** category (public):
  - Voice Public, Voice Trio (3 user limit), Voice Duo (2 user limit), Voice AFK

**Note**: This command will delete all existing channels and categories!

##### `/admin wipe`
Deletes all categories and channels in the server (fresh start).
```
/admin wipe
```
**Permissions**: Admin role or Server Owner
**WARNING**: This is destructive and cannot be undone!

##### `/admin clear_roles`
Deletes all non-default, non-managed roles in the server.
```
/admin clear_roles
```
**Permissions**: Admin role or Server Owner
**WARNING**: Deleted roles cannot be recovered!

---

## Usage

### Starting the Bot

**Using PM2** (recommended):
```bash
pm2 start src/main.py --interpreter ./venv/bin/python3 --name "modmeister-bot"
```

**Or use the start script**:
```bash
bash start.sh
```

### Stopping the Bot

```bash
bash stop.sh
```

Or with PM2:
```bash
pm2 stop modmeister-bot
```

### Updating the Bot

```bash
bash update.sh
```

### Viewing Logs

```bash
pm2 logs modmeister-bot
```

### Process Management

```bash
pm2 list              # View all running processes
pm2 restart modmeister-bot
pm2 delete modmeister-bot
pm2 status modmeister-bot
```

## Database

ModMeister uses SQLite3 with the following tables:

### `admins` Table
Stores admin designations per guild.
```
- guild_id (INTEGER): Discord server ID
- user_id (INTEGER): Discord user ID
```

### `members` Table
Reserved for future member tracking features.
```
- guild_id (INTEGER): Discord server ID
- user_id (INTEGER): Discord user ID
```

## Development Status

⚠️ **This project is currently in active development.** Features and APIs may change. Please report any bugs or issues on the [GitHub Issues](https://github.com/elotezer/ModMeister/issues) page.

## Known Issues & Limitations

- Setup commands are destructive and cannot be undone (use with caution)
- Private categories require an "Admin" role to exist
- Some commands may have rate limiting due to Discord API constraints
- AI model access requires valid API keys and active accounts

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues, questions, or suggestions, please:
- Open an [Issue](https://github.com/elotezer/ModMeister/issues) on GitHub
- Check existing issues for solutions
- Provide detailed information about your problem including:
  - What command you ran
  - What error you received
  - Server configuration details (if relevant)

## License

This project is currently unlicensed. For licensing information, please contact the repository owner.

## Acknowledgments

- Built with [discord.py](https://discordpy.readthedocs.io/)
- AI integration with [OpenAI API](https://openai.com/api/) and [Google Gemini](https://ai.google.dev/)
- Process management by [PM2](https://pm2.keymetrics.io/)

---

**Last Updated**: March 2026

**Repository**: [elotezer/ModMeister](https://github.com/elotezer/ModMeister)

**Author**: [@elotezer](https://github.com/elotezer)
