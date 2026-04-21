from __future__ import annotations
import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD = os.getenv("GUILD")

# discord.opus.load_opus('libopus.so.0') 

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        activity = discord.Game(name="/help")
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents, activity=activity)

    async def setup_hook(self) -> None:
        for ext in ("cogs.core", "cogs.admin", "cogs.user", "cogs.music"):
            await self.load_extension(ext)

        if GUILD and GUILD.isdigit():
            guild = discord.Object(id=int(GUILD))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logging.info("Synced commands to GUILD")
        else:
            await self.tree.sync()
            logging.info("Synced global commands")

    async def on_ready(self):
        logging.info("Logged in as ModMeister")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if not TOKEN:
        raise SystemExit("Set TOKEN in your .env file first!")
    bot = Bot()
    bot.run(TOKEN)
