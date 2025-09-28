from __future__ import annotations
import os
import logging
import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

connection = sqlite3.connect("botdatabase.db")
cursor = connection.cursor()

class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Is the bot alive?!")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="echo", description="Echoes back your message")
    async def echo(self, interaction: discord.Interaction, text: str):
        await interaction.response.send_message(text)

    @app_commands.command(name="help", description="List of the bot's commands")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "`/ping` Checks if the bot is alive or not\n`/echo` Sends you back the same text you provided as parameter"
        )

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ch = member.guild.system_channel
        if ch:
            await ch.send(f"Welcome to the server {member.mention}!")

        cursor.execute("""CREATE TABLE IF NOT EXISTS members (guild_id INT, user_id INT)""")
        connection.commit()
        cursor.execute("""INSERT INTO members (guild_id, user_id) VALUES (?, ?)""", (member.guild.id, member.id))
        connection.commit()
        role = discord.utils.get(member.guild.roles, name="Member")
        member = member.guild.get_member(member.id)
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        ch = member.guild.system_channel
        if ch:
            await ch.send(f"{member.mention} has left :(")

async def setup(bot: commands.Bot):
    await bot.add_cog(Core(bot))
    await bot.add_cog(EventsCog(bot))