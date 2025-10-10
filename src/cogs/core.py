from __future__ import annotations
import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import textwrap

connection = sqlite3.connect("botdatabase.db")
cursor = connection.cursor()

class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Is the bot alive?!")
    async def ping(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Ping-Pong command",
            description="Pong!",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="echo", description="Echoes back your message")
    async def echo(self, interaction: discord.Interaction, text: str):
        embed = discord.Embed(
            title="Echo command",
            description=text,
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="help", description="Display all bot commands")
    async def help_command(self, interaction: discord.Interaction):
        help_text = textwrap.dedent("""\
                **Member commands**
                    `/ping` Checks if the bot is alive or not
                    `/echo` Sends you back the same text you provided as parameter
                    `/roll` Random number between a provided range
                    `/roll_f` Random number between 0 and 1
                    `/gpt` Prompt ChatGPT

                **Admin commands**
                    `/admin add` Add admin role to user
                    `/admin remove` Remove admin role from user
                    `/admin list` List of admins
                    `/admin ban` Ban a member
                    `/admin unban` Unban a member
                    `/admin mute` Mute a member for a specified minutes (Timeout)
                    `/admin unmute` Mute a member for a specified minutes (Timeout)
                    `/admin new_text_ch` Create new text channel
                    `/admin del_text_ch` Delete text channel
                    `/admin new_voice_ch` Create new voice channel
                    `/admin del_voice_ch` Delete voice channel
                    `/admin new_private_category` Create new private category
                    `/admin new_category` Create new category
                    `/admin new_private_category` Pivate category (Every new channel in this category will be private)
                    `/admin del_category` Delete category
                    `/admin give_role` Add role to a user (leave user parameter empty to give everyone)
                """)
        embed = discord.Embed(
            title="ModMeister's commands",
            description=help_text,
            color=discord.Color.red()
        )

        embed.set_footer(text="ModMeister 2025")

        await interaction.response.send_message(embed=embed)

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        ch = member.guild.system_channel
        if ch:
            embed = discord.Embed(
                title="A New Member Joined Us! 🥳🙌",
                description=f"Welcome to {member.guild.name}, {member.mention}!",
                color=discord.Color.gold()
            )
            await ch.send(embed=embed)

        cursor.execute("""CREATE TABLE IF NOT EXISTS members (guild_id INT, user_id INT)""")
        connection.commit()

        cursor.execute("""INSERT INTO members (guild_id, user_id) VALUES (?, ?)""", (member.guild.id, member.id))
        connection.commit()

        role = discord.utils.get(member.guild.roles, name="Member")
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        ch = member.guild.system_channel
        if ch:
            embed = discord.Embed(
                title="A Member Left Us! 😖🌧️",
                description=f"See you soon, {member.name}! 👋",
                color=discord.Color.dark_blue()
            )
            await ch.send(embed=embed)
        cursor.execute("""DELETE FROM members where guild_id = ? and user_id = ?""", (member.guild.id, member.id))
        connection.commit()

        admin_role = discord.utils.get(member.guild.roles, name="Admin")

        cursor.execute("SELECT 1 FROM admins WHERE guild_id = ? AND user_id = ?", (member.guild.id, member.id))
        if cursor.fetchone() is not None:
            cursor.execute("""DELETE
                              FROM admins
                              where guild_id = ?
                                and user_id = ?""", (member.guild.id, member.id))
            connection.commit()

async def setup(bot: commands.Bot):
    await bot.add_cog(Core(bot))
    await bot.add_cog(EventsCog(bot))