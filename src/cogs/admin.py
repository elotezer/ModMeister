from datetime import timedelta

from discord import app_commands
from discord.ext import commands
import discord
import sqlite3
import datetime

connection = sqlite3.connect("botdatabase.db")
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS admins (guild_id INTEGER, user_id INTEGER)")

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    admin = app_commands.Group(name="admin", description="Commands for administrators")

    @admin.command(name="kick", description="Kick a member")
    async def kick(self, interaction: discord.Interaction, user: discord.User, reason: str):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("You don't have the permission to kick members!")
            return
        else:
            await user.kick(reason=reason)
            await interaction.response.send_message(f"{user.mention} has been kicked 🪽\nReason: {reason}")

    @admin.command(name="ban", description="Ban a member")
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("You don't have permission to ban members!")
            return
        else:
            await user.ban(reason=reason)
            await interaction.response.send_message(f"{user.mention} has been banned 💥\nReason: {reason}")

    @admin.command(name="unban", description="Unban a member")
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("You don't have permission to unban members!")
        else:
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"{user.mention} has been unbanned! 🙌")

    @admin.command(name="mute", description="Mute a member for a specific minutes (Timeout)")
    async def mute(self, interaction: discord.Interaction, user: discord.User, minutes: int, reason: str):
        if not interaction.user.guild_permissions.moderate_members:
            interaction.response.send_message("You don't have permission to mute members!")
            return
        else:
            muted_until = discord.utils.utcnow() + timedelta(minutes = minutes)
            await user.timeout(muted_until, reason = reason)
            await interaction.response.send_message(f"{user.mention} has been muted for {minutes} minutes 🔇\nReason: {reason}")

    @admin.command(name="unmute", description="Unmute a member")
    async def unmute(self, interaction: discord.Interaction, user: discord.User):
        if not interaction.user.guild_permissions.moderate_members:
            interaction.response.send_message("You don't have permission to unmute members!")
            return
        else:
            await user.timeout(None)
            await interaction.response.send_message(
                f"{user.mention} has been unmuted 🔊")



    @admin.command(name="add", description="Add an admin")
    async def add(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("Only the owner can add other admins!", ephemeral=True)
            return
        else:
            guild_id = interaction.guild.id
            cursor.execute("""INSERT INTO admins (guild_id, user_id) VALUES (?, ?) """, (guild_id, user.id))
            connection.commit()
            role = discord.utils.get(interaction.guild.roles, name="Admin")
            member = interaction.guild.get_member(user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f"{user.mention} is now an admin! 🥳")

    @admin.command(name="remove", description="Remove an admin")
    async def add(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("Only the owner can remove admins!", ephemeral=True)
            return
        else:
            guild_id = interaction.guild.id
            cursor.execute("""DELETE FROM admins WHERE guild_id = ? AND user_id = ?""", (guild_id, user.id))
            connection.commit()
            role = discord.utils.get(interaction.guild.roles, name="Admin")
            member = interaction.guild.get_member(user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f"{user.mention} is no longer an admin! 👌")

    @admin.command(name="list", description="List admins")
    async def list(self, interaction: discord.Interaction):
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("Only the owner can list admins!", ephemeral=True)
            return
        else:
            guild_id = interaction.guild.id
            cursor.execute("SELECT user_id FROM admins WHERE guild_id = ?", (guild_id,))
            admin_ids = [row[0] for row in cursor.fetchall()]

            if len(admin_ids) == 0:
                await interaction.response.send_message("No admins were added yet.", ephemeral=True)
                return

            mentions = []
            for uid in admin_ids:
                member = interaction.guild.get_member(uid)
                if member:
                    mentions.append(member.mention)
                else:
                    mentions.append(f"<@{uid}>")

            await interaction.response.send_message("List of admins: " + ", ".join(mentions), ephemeral=True)



async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))