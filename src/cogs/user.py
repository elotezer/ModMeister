from datetime import timedelta
from discord import app_commands
from discord.ext import commands
import discord
import sqlite3

class User(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # commands that every1 can use will be here
