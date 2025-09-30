from discord import app_commands
from discord.ext import commands
import discord
import sqlite3
import random

class User(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # commands that every1 can use will be here

    @app_commands.command(name='roll', description='Roll a random whole number between a selected range')
    async def roll_int(self, interaction: discord.Interaction, x: int, y: int):
        rolled = random.randint(x, y)
        await interaction.response.send_message(f"Your random number: {rolled}")

    @app_commands.command(name='roll_f', description='Roll a random float number between 0 and 1')
    async def roll_f(self, interaction: discord.Interaction):
        rolled = random.random()
        await interaction.response.send_message(f"Your random number: {rolled:.6f}")


async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))