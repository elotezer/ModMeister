from __future__ import annotations
import os
import logging
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD = os.getenv("GUILD")

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.guilds = True
        activity = discord.Game(name="/help")
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents, activity=activity)



    async def setup_hook(self) -> None:
        await self.load_extension("cogs.core")
        await self.load_extension("cogs.admin")
        #await self.load_extension("cogs.fun")

        if GUILD and GUILD.isdigit():
            guild = discord.Object(id=int(GUILD))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

            logging.info("Synced commands to GUILD")
        else:
            await self.tree.sync()
            logging.info("Synced global commands")

    async def on_ready(self):
        logging.basicConfig(level=logging.INFO)
        logging.info("Logged is as ModMeister")
        print("Logged is as ModMeister")



if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Set DISCORD_TOKEN in your .env file first!")
    bot = Bot()
    bot.run(TOKEN)
