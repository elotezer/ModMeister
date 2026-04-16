from __future__ import annotations
import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get
import sqlite3

connection = sqlite3.connect("botdatabase.db")
cursor = connection.cursor()


class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Is the bot alive?!")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            description=f"🏓  Pong! **{latency}ms**", 
            color=0x3498db
        )
        embed.set_footer(
            text=f"Requested by {interaction.user}", 
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="echo", description="Echoes back your message")
    async def echo(self, interaction: discord.Interaction, text: str):
        embed = discord.Embed(
            description=text, 
            color=0x3498db
        )
        embed.set_footer(
            text=f"Sent by {interaction.user}", 
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Display all bot commands")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="ModMeister — Command Reference",
            color=0x3498db
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="🎲  General",
            value=(
                "`/ping` — Check if the bot is alive\n"
                "`/echo` — Echo back a message\n"
                "`/roll` — Random integer between a range\n"
                "`/roll_f` — Random float between 0 and 1\n"
                "`/serverinfo` — Display detailed server information"
            ),
            inline=False
        )

        embed.add_field(
            name="🤖  AI",
            value=(
                "`/gpt` — Ask ChatGPT\n"
                "`/gemini` — Ask Gemini"
            ),
            inline=False
        )

        embed.add_field(
            name="🔨  Moderation",
            value=(
                "`/admin kick` — Kick a member\n"
                "`/admin ban` — Ban a member\n"
                "`/admin unban` — Unban a member\n"
                "`/admin mute` — Timeout a member for a set duration\n"
                "`/admin unmute` — Remove a timeout from a member\n"
                "`/admin warn` — Issue a warning to a member\n"
                "`/admin warnings` — View all warnings for a member\n"
                "`/admin clear_warnings` — Clear all or a specific warning"
            ),
            inline=False
        )

        embed.add_field(
            name="👑  Admin Management",
            value=(
                "`/admin add` — Grant admin to a user\n"
                "`/admin remove` — Revoke admin from a user\n"
                "`/admin userinfo` — Full profile & history of a user"
            ),
            inline=False
        )

        embed.add_field(
            name="🎭  Roles",
            value=(
                "`/admin give_role` — Give a role to a user or everyone\n"
                "`/admin take_role` — Remove a role from a user or everyone\n"
                "`/admin clear_roles` — Delete all deletable roles"
            ),
            inline=False
        )

        embed.add_field(
            name="📁  Channels & Categories",
            value=(
                "`/admin new_text_ch` — Create a text channel\n"
                "`/admin del_text_ch` — Delete a text channel\n"
                "`/admin new_voice_ch` — Create a voice channel\n"
                "`/admin del_voice_ch` — Delete a voice channel\n"
                "`/admin new_category` — Create a category\n"
                "`/admin del_category` — Delete a category\n"
                "`/admin new_private_category` — Create an admin-only category"
            ),
            inline=False
        )

        embed.add_field(
            name="🎵  Music",
            value=(
                "`/play` — Play a SoundCloud or Spotify track/playlist\n"
                "`/pause` — Pause the current track\n"
                "`/resume` — Resume the paused track\n"
                "`/skip` — Skip the current track\n"
                "`/stop` — Stop playback and disconnect\n"
                "`/queue` — Show the current queue\n"
                "`/nowplaying` — Show what's currently playing\n"
                "`/loop` — Toggle looping the current track\n"
                "`/volume` — Set playback volume (0–100)"
            ),
            inline=False
        )

        embed.add_field(
            name="🛠️  Server",
            value=(
                "`/admin setup_server` — Wipe and rebuild a basic server layout\n"
                "`/admin wipe` — Delete all channels and categories"
            ),
            inline=False
        )

        embed.set_footer(text="ModMeister 2026")
        await interaction.response.send_message(embed=embed)


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        ch = get(member.guild.text_channels, name="welcome")
        
        if ch:
            embed = discord.Embed(
                description=f"👋  Welcome to **{member.guild.name}**, {member.mention}! Glad to have you here.",
                color=0xf1c40f
            )
            embed.set_author(name="New Member!", icon_url=member.display_avatar.url)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Member #{member.guild.member_count}")
            
            await ch.send(embed=embed)

        cursor.execute("CREATE TABLE IF NOT EXISTS members (guild_id INT, user_id INT)")
        connection.commit()
        
        cursor.execute("INSERT INTO members (guild_id, user_id) VALUES (?, ?)", (member.guild.id, member.id))
        connection.commit()

        role = discord.utils.get(member.guild.roles, name="Member")
        if role:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        ch = get(member.guild.text_channels, name="leavers")
        
        if not ch:
            ch = member.guild.system_channel
            
        if ch:
            embed = discord.Embed(
                description=f"👋  **{member.name}** has left the server. See you around!",
                color=0x2c3e50
            )
            embed.set_author(name="Member Left", icon_url=member.display_avatar.url)
            embed.set_thumbnail(url=member.display_avatar.url)
            
            await ch.send(embed=embed)

        cursor.execute("DELETE FROM members WHERE guild_id = ? AND user_id = ?", (member.guild.id, member.id))
        connection.commit()

        cursor.execute("SELECT 1 FROM admins WHERE guild_id = ? AND user_id = ?", (member.guild.id, member.id))
        
        if cursor.fetchone() is not None:
            cursor.execute("DELETE FROM admins WHERE guild_id = ? AND user_id = ?", (member.guild.id, member.id))
            connection.commit()


async def setup(bot: commands.Bot):
    await bot.add_cog(Core(bot))
    await bot.add_cog(EventsCog(bot))