import asyncio
from datetime import timedelta
from types import NoneType

from discord import app_commands
from discord.ext import commands
import discord
import sqlite3

connection = sqlite3.connect("botdatabase.db")
cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS admins (guild_id INTEGER, user_id INTEGER)")

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    admin = app_commands.Group(name="admin", description="Commands for administrators")

    @admin.command(name="kick", description="Kick a member")
    async def kick(self, interaction: discord.Interaction, user: discord.User, reason: str):
        cursor.execute("""Select 1 From admins Where guild_id = ? And user_id = ?""", (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()
        if not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have the permission to kick members!")
            return

        elif fetch:
            await user.kick(reason=reason)
            await interaction.response.send_message(f"{user.mention} has been kicked 🪽\nReason: {reason}")

        elif interaction.user.id == interaction.guild.owner_id:
            await user.kick(reason=reason)
            await interaction.response.send_message(f"{user.mention} has been kicked 🪽\nReason: {reason}")

    @admin.command(name="ban", description="Ban a member")
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str):
        cursor.execute("""Select 1
                          From admins
                          Where guild_id = ?
                            And user_id = ?""", (interaction.guild_id, interaction.user.id))

        fetch = cursor.fetchone()

        if not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have permission to ban members!")
            return

        elif fetch:
            await user.ban(reason=reason)
            await interaction.response.send_message(f"{user.mention} has been banned 💥\nReason: {reason}")

        elif interaction.user.id == interaction.guild.owner_id:
            await user.ban(reason=reason)
            await interaction.response.send_message(f"{user.mention} has been banned 💥\nReason: {reason}")


    @admin.command(name="unban", description="Unban a member")
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        cursor.execute("""Select 1
                          From admins
                          Where guild_id = ?
                            And user_id = ?""", (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()
        if not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have permission to unban members!")

        elif fetch:
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"{user.mention} has been unbanned! 🙌")

        elif interaction.user.id == interaction.guild.owner_id:
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"{user.mention} has been unbanned! 🙌")

    @admin.command(name="mute", description="Mute a member for a specific minutes (Timeout)")
    async def mute(self, interaction: discord.Interaction, user: discord.User, minutes: int, reason: str):
        cursor.execute("""Select 1
                          From admins
                          Where guild_id = ?
                            And user_id = ?""", (interaction.guild_id, interaction.user.id))

        fetch = cursor.fetchone()

        if not fetch:
            interaction.response.send_message("**[ALERT]** You don't have permission to mute members!")
            return

        elif fetch:
            muted_until = discord.utils.utcnow() + timedelta(minutes = minutes)
            await user.timeout(muted_until, reason = reason)
            await interaction.response.send_message(f"{user.mention} has been muted for {minutes} minutes 🔇\nReason: {reason}")
            return

        elif interaction.user.id == interaction.guild.owner_id:
            muted_until = discord.utils.utcnow() + timedelta(minutes=minutes)
            await user.timeout(muted_until, reason=reason)
            await interaction.response.send_message(f"{user.mention} has been muted for {minutes} minutes 🔇\nReason: {reason}")
            return

    @admin.command(name="unmute", description="Unmute a member")
    async def unmute(self, interaction: discord.Interaction, user: discord.User):
        cursor.execute("""Select 1
                          From admins
                          Where guild_id = ?
                            And user_id = ?""", (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if not fetch:
            interaction.response.send_message("**[ALERT]** You don't have permission to unmute members!")
            return

        elif fetch:
            await user.timeout(None)
            await interaction.response.send_message(
                f"{user.mention} has been unmuted 🔊")
            return

        elif interaction.guild.owner_id == interaction.user.id:
            await user.timeout(None)
            await interaction.response.send_message(
                f"{user.mention} has been unmuted 🔊")
            return


    @admin.command(name="add", description="Add an admin")
    async def add(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("**[ALERT]** Only the owner can add other admins!", ephemeral=True)
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
            await interaction.response.send_message("**[ALERT]** Only the owner can remove admins!", ephemeral=True)
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
        cursor.execute("""Select 1
                          From admins
                          Where guild_id = ?
                            And user_id = ?""", (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have permission to list admins!", ephemeral=True)
            return

        elif fetch or interaction.user.id == interaction.guild.owner:
            guild_id = interaction.guild.id
            cursor.execute("SELECT user_id FROM admins WHERE guild_id = ?", (guild_id,))

            admin_ids = [row[0] for row in cursor.fetchall()]

            if len(admin_ids) == 0:
                await interaction.response.send_message("**[ALERT]** No admins were added yet.", ephemeral=True)
                return

            mentions = []

            for uid in admin_ids:
                member = interaction.guild.get_member(uid)

                if member:
                    mentions.append(member.mention)

                else:
                    mentions.append(f"<@{uid}>")

            await interaction.response.send_message("List of admins: " + ", ".join(mentions), ephemeral=True)

    @admin.command(name="new_text_ch", description="Create new text channel")
    async def new_text_ch(self, interaction: discord.Interaction, ch_name: str, ch_cat: discord.CategoryChannel):
        cursor.execute("""select 1 
                          from admins 
                          where guild_id = ? and user_id = ?""",
                       (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            await interaction.guild.create_text_channel(ch_name, category=ch_cat)
            await interaction.response.send_message(f"**[Text Channel]** \"{ch_name}\" has been created ✅")
        elif not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have permission to create text channels ❌")


    @admin.command(name="del_text_ch", description="Delete text channel")
    async def del_text_ch(self, interaction: discord.Interaction, channel: discord.TextChannel):
        cursor.execute("""select 1 
                            from admins 
                            where guild_id = ? and user_id = ?""",
                        (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            await channel.delete()
            await interaction.response.send_message(f"**[Text Channel]** \"{channel.name}\" has been deleted ✅")
        elif not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have permission to delete text channels ❌")

    @admin.command(name="new_voice_ch", description="Create new voice channel")
    async def new_voice_ch(self, interaction: discord.Interaction, ch_name: str, ch_cat: discord.CategoryChannel):
        cursor.execute("""select 1
                          from admins
                          where guild_id = ?
                            and user_id = ?""",
                       (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            await interaction.guild.create_voice_channel(ch_name, category=ch_cat)
            await interaction.response.send_message(f"**[Voice Channel]** \"{ch_name}\" has been created ✅")
        elif not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have permission to create voice channels ❌")

    @admin.command(name="del_voice_ch", description="Delete voice channel")
    async def del_voice_ch(self, interaction: discord.Interaction, ch_name: discord.VoiceChannel):
        cursor.execute("""select 1
                          from admins
                          where guild_id = ?
                            and user_id = ?""",
                       (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            await ch_name.delete()
            await interaction.response.send_message(f"**[Voice Channel]** \"{ch_name}\" has been deleted ✅")
        elif not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have permission to delete voice channels ❌")

    @admin.command(name="new_category", description="Create new category")
    async def new_category(self, interaction: discord.Interaction, name: str):
        cursor.execute("""select 1
                          from admins
                          where guild_id = ?
                            and user_id = ?""",
                       (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            await interaction.guild.create_category(name=name)
            await interaction.response.send_message(f"**[Create Category]** \"{name}\" has been created ✅")
        elif not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have permission to create categories! ❌")

    @admin.command(name="del_category", description="Delete category")
    async def new_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        cursor.execute("""select 1
                          from admins
                          where guild_id = ?
                            and user_id = ?""",
                       (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            await category.delete()
            await interaction.response.send_message(f"**[Create Category]** \"{category.name}\" has been deleted ✅")
        elif not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have permission to delete categories! ❌")

    @admin.command(name="new_private_category")
    async def new_private_category(self, interaction: discord.Interaction, name: str):
        cursor.execute("""select 1
                          from admins
                          where guild_id = ?
                            and user_id = ?""",
                       (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            guild = interaction.guild
            admin_role = discord.utils.get(guild.roles, name="Admin")

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                admin_role: discord.PermissionOverwrite(view_channel=True)
            }

            await guild.create_category(name, overwrites=overwrites)
            await interaction.response.send_message(f"Private category `{name}` created ✅ (Admins only)")

        elif not fetch:
            await interaction.response.send_message(f"**[ALERT]** You don't have permission to create private category ❌")

    @admin.command(name="give_role", description="Give role to a user (or everyone)")
    async def add_role(self, interaction: discord.Interaction, role: discord.Role, user: discord.Member | None = None):
        cursor.execute("""SELECT 1
                          FROM admins
                          WHERE guild_id = ?
                            AND user_id = ?""",
                       (interaction.guild.id, interaction.user.id))
        fetch = cursor.fetchone()

        if not fetch:
            await interaction.response.send_message("**[ALERT]** You don't have permission to manage roles ❌")
            return

        if fetch and interaction.user.id != interaction.guild.owner.id and (role.name == "Admin"):
            await interaction.response.send_message("**[ALERT]** You don't have permission to give admin roles ❌")
            return

        if user:
            await user.add_roles(role)
            await interaction.response.send_message(f"**[ADMIN]** Giving role `{role.name}` to @{user.name}...")
        else:
            await interaction.response.defer()
            await interaction.followup.send(f"**[ADMIN]** Giving role `{role.name}` to everyone...")

            for member in interaction.guild.members:
                try:
                    await member.add_roles(role)
                    await interaction.followup.send(f"**[ADMIN]** `{member.name}` receieved `{role.name}` ✅")
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    continue

            await interaction.followup.send(f"**[ADMIN]** Gave role `{role.name}` to everyone ✅")


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))