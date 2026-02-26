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
cursor.execute("CREATE TABLE IF NOT EXISTS members (guild_id INTEGER, user_id INTEGER)")

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    admin = app_commands.Group(name="admin", description="Commands for administrators")

    @admin.command(name="kick", description="Kick a member")
    async def kick(self, interaction: discord.Interaction, user: discord.User, reason: str):
        cursor.execute("""Select 1 From admins Where guild_id = ? And user_id = ?""", (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()
        if not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to kick members! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        elif fetch:
            await user.kick(reason=reason)
            embed = discord.Embed(
                title=f"{user.display_name} has been kicked 🪽\nReason: {reason}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        elif interaction.user.id == interaction.guild.owner_id:
            await user.kick(reason=reason)
            embed = discord.Embed(
                title=f"{user.display_name} has been kicked 🪽\nReason: {reason}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

    @admin.command(name="ban", description="Ban a member")
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str):
        cursor.execute("""Select 1
                          From admins
                          Where guild_id = ?
                            And user_id = ?""", (interaction.guild_id, interaction.user.id))

        fetch = cursor.fetchone()

        if not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to ban members! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        elif fetch:
            await user.ban(reason=reason)
            embed = discord.Embed(
                title=f"{user.mention} has been banned 💥\nReason: {reason}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        elif interaction.user.id == interaction.guild.owner_id:
            await user.ban(reason=reason)
            embed = discord.Embed(
                title=f"{user.mention} has been banned 💥\nReason: {reason}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)


    @admin.command(name="unban", description="Unban a member")
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        cursor.execute("""Select 1
                          From admins
                          Where guild_id = ?
                            And user_id = ?""", (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()
        if not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to unban members! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        elif fetch:
            await interaction.guild.unban(user)
            embed = discord.Embed(
                title=f"{user.mention} has been unbanned! 🙌",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        elif interaction.user.id == interaction.guild.owner_id:
            await interaction.guild.unban(user)
            embed = discord.Embed(
                title=f"{user.mention} has been unbanned! 🙌",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

    @admin.command(name="mute", description="Mute a member for a specific minutes (Timeout)")
    async def mute(self, interaction: discord.Interaction, user: discord.User, minutes: int, reason: str):
        cursor.execute("""Select 1
                          From admins
                          Where guild_id = ?
                            And user_id = ?""", (interaction.guild_id, interaction.user.id))

        fetch = cursor.fetchone()

        if not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to mute members! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        elif fetch:
            muted_until = discord.utils.utcnow() + timedelta(minutes = minutes)
            await user.timeout(muted_until, reason = reason)
            embed = discord.Embed(
                title=f"{user.mention} has been muted for {minutes} minutes 🔇\nReason: {reason}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
            return

        elif interaction.user.id == interaction.guild.owner_id:
            muted_until = discord.utils.utcnow() + timedelta(minutes=minutes)
            await user.timeout(muted_until, reason=reason)
            embed = discord.Embed(
                title=f"{user.mention} has been muted for {minutes} minutes 🔇\nReason: {reason}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
            return

    @admin.command(name="unmute", description="Unmute a member")
    async def unmute(self, interaction: discord.Interaction, user: discord.User):
        cursor.execute("""Select 1
                          From admins
                          Where guild_id = ?
                            And user_id = ?""", (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to unmute members! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        elif fetch:
            await user.timeout(None)
            embed = discord.Embed(
                title=f"{user.name} has been unmuted ✅",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
            return

        elif interaction.guild.owner_id == interaction.user.id:
            await user.timeout(None)
            embed = discord.Embed(
                title=f"{user.name} has been unmuted ✅",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
            return


    @admin.command(name="add", description="Add an admin")
    async def add(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user != interaction.guild.owner:
            embed = discord.Embed(
                title="**[ALERT]** Only the owner can add admins! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        else:
            guild_id = interaction.guild.id
            cursor.execute("""INSERT INTO admins (guild_id, user_id) VALUES (?, ?) """, (guild_id, user.id))
            connection.commit()
            role = discord.utils.get(interaction.guild.roles, name="Admin")
            member = interaction.guild.get_member(user.id)
            try:
                await member.add_roles(role)
                embed = discord.Embed(
                    title=f"{user.name} is now an Admin! 🥳",
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=embed)
            except AttributeError:
                perms = discord.Permissions(administrator=True)
                admin_role = await interaction.guild.create_role(
                    name="Admin",
                    color=discord.Color.red(),
                    permissions=perms,         
                    hoist=True,                
                    mentionable=True           
                )
                await member.add_roles(admin_role)
                embed = discord.Embed(
                    title=f"{user.name} is now an Admin! 🥳",
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=embed)

    @admin.command(name="remove", description="Remove an admin")
    async def add(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user != interaction.guild.owner:
            embed = discord.Embed(
                title="**[ALERT]** Only the owner can remove admins! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        else:
            guild_id = interaction.guild.id
            cursor.execute("""DELETE FROM admins WHERE guild_id = ? AND user_id = ?""", (guild_id, user.id))
            connection.commit()
            role = discord.utils.get(interaction.guild.roles, name="Admin")
            member = interaction.guild.get_member(user.id)

            await member.remove_roles(role)
            embed = discord.Embed(
                title=f"{user.name} is no longer an Admin ✅",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

    @admin.command(name="new_text_ch", description="Create new text channel")
    async def new_text_ch(self, interaction: discord.Interaction, ch_name: str, ch_cat: discord.CategoryChannel):
        cursor.execute("""select 1 
                          from admins 
                          where guild_id = ? and user_id = ?""",
                       (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            await interaction.guild.create_text_channel(ch_name, category=ch_cat)
            embed = discord.Embed(
                title=f"Text channel `{ch_name}` has been created in category `{ch_cat.name}`✅",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        elif not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to create text channels! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return


    @admin.command(name="del_text_ch", description="Delete text channel")
    async def del_text_ch(self, interaction: discord.Interaction, channel: discord.TextChannel):
        cursor.execute("""select 1 
                            from admins 
                            where guild_id = ? and user_id = ?""",
                        (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            await channel.delete()
            embed = discord.Embed(
                title=f"Text channel `{channel.name}` has been deleted ✅",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        elif not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to delete text channels! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

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
            embed = discord.Embed(
                title=f"Voice channel `{ch_name}` has been created ✅",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        elif not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to create new voice channel! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

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
            embed = discord.Embed(
                title=f"Voice channel `{ch_name}` has been deleted ✅",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        elif not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to delete voice channel! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

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
            embed = discord.Embed(
                title=f"Category `{name}` has been created ✅",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        elif not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to create new category! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

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
            embed = discord.Embed(
                title=f"Category `{category.name}` has been deleted ✅",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        elif not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to delete category! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

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
            embed = discord.Embed(
                title=f"Private category `{name}` created ✅ (Admins only)",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        elif not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to create new private category! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

    @admin.command(name="give_role", description="Give role to a user (or everyone)")
    async def add_role(self, interaction: discord.Interaction, role: discord.Role, user: discord.Member | None = None):
        cursor.execute("""SELECT 1
                          FROM admins
                          WHERE guild_id = ?
                            AND user_id = ?""",
                       (interaction.guild.id, interaction.user.id))
        fetch = cursor.fetchone()

        if not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to delete category! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        if fetch and interaction.user.id != interaction.guild.owner.id and (role.name == "Admin"):
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to give Admin roles! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return

        if user:
            await user.add_roles(role)
            embed = discord.Embed(
                title=f"Giving role `{role.name}` to {user.mention}...",
                color=discord.Color.brand_green()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.defer()
            embed = discord.Embed(
                title=f"Giving role `{role.name}` to everyone...",
                color=discord.Color.brand_green()
            )
            await interaction.followup.send(embed=embed)

            for member in interaction.guild.members:
                try:
                    await member.add_roles(role)
                    embed = discord.Embed(
                        title=f"`{member.name}` receieved `{role.name}` ✅"
                    )
                    await interaction.followup.send(embed=embed)
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    continue
            embed = discord.Embed(
                title=f"Gave role `{role.name}` to everyone ✅"
            )
            await interaction.followup.send(embed=embed)
    @admin.command(name="setup_server", description="Sets up a basic server model with categories and channels")
    async def setup_server(self, interaction: discord.Interaction):
        cursor.execute("""select 1 
                          from admins 
                          where guild_id = ? and user_id = ?""",
                       (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            await interaction.response.defer(ephemeral=False)

            for channel in interaction.guild.channels:
                try:
                    if not channel.id == interaction.channel.id:
                        await channel.delete()
                except Exception as e:
                    print(f"couldnt delete channel: {channel.name} -", e)

            for category in interaction.guild.categories:
                try:
                    await category.delete()
                except Exception as e:
                    print(f"couldnt delete category: {category.name} -", e)


            # all channels in 'about' will be read only
            about = await interaction.guild.create_category(name="About")
            embed = discord.Embed(
                title=f"Category `About` has been created ✅",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
            # all channels in 'text' will be accessable by @everyone
            text = await interaction.guild.create_category(name="Text")
            embed = discord.Embed(
                title=f"Category `Text` has been created ✅",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
            # all channels in 'voice' will be accessable by @everyone (except private admin vc)
            voice = await interaction.guild.create_category(name="Voice")
            embed = discord.Embed(
                title=f"Category `Voice` has been created ✅",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)

            # @everyone read only
            overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                send_messages=False, 
                view_channel=True
            ),
            interaction.guild.me: discord.PermissionOverwrite(
                send_messages=True, 
                view_channel=True
            )
        }

            about_ch_names = ["welcome", "rules", "roles", "server", "channels", "leavers"]
            text_ch_names = ["chat", "images", "videos", "music", "links", "games"]
            voice_ch_names = ["Voice Public", "Voice Trio", "Voice Duo", "Voice AFK"]

            for name in about_ch_names:
                await interaction.guild.create_text_channel(name=name, category=about, overwrites=overwrites)
                embed = discord.Embed(
                    title=f"Text channel `{name}` has been created in category `About`✅",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed)
            for name in text_ch_names:
                await interaction.guild.create_text_channel(name=name, category=text)
                embed = discord.Embed(
                    title=f"Text channel `{name}` has been created in category `Text`✅",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed)
            for name in voice_ch_names:
                if name == "Voice Trio":
                    await interaction.guild.create_voice_channel(name=name, category=voice, user_limit=3)
                elif name == "Voice Duo":
                    await interaction.guild.create_voice_channel(name=name, category=voice, user_limit=2)
                else:
                    await interaction.guild.create_voice_channel(name=name, category=voice)
                embed = discord.Embed(
                    title=f"Text channel `{name}` has been created in category `Text`✅",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed)

            for channel in interaction.guild.channels:
                    try:
                        if channel.id == interaction.channel.id:
                            await channel.delete()
                    except Exception as e:
                        print(f"couldnt delete channel: {channel.name} -", e)
            
        elif not fetch:
            embed = discord.Embed(
                title="**[ALERT]** You don't have the permission to run a server setup! ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
    
    @admin.command(name="wipe", description="Delete every category and every channel in the server. A fresh start.")
    async def wipe(self, interaction: discord.Interaction):
        cursor.execute("""select 1 
                          from admins 
                          where guild_id = ? and user_id = ?""",
                       (interaction.guild_id, interaction.user.id))
        fetch = cursor.fetchone()

        if fetch:
            await interaction.response.defer(ephemeral=False)

            for channel in interaction.guild.channels:
                try:
                    if not channel.id == interaction.channel.id:
                        await channel.delete()
                except Exception as e:
                    print(f"couldnt delete channel: {channel.name} -", e)

            for category in interaction.guild.categories:
                try:
                    await category.delete()
                except Exception as e:
                    print(f"couldnt delete category: {category.name} -", e)

    @admin.command(name="clear_roles", description="Deletes all roles")
    async def clear_roles(self, interaction: discord.Interaction):
        cursor.execute("""select 1 from admins where guild_id = ? and user_id = ?""",
                    (interaction.guild_id, interaction.user.id))
        if not cursor.fetchone():
            await interaction.response.send_message("**[ALERT]** You don't have permission to wipe roles ❌", ephemeral=True)
            return

        await interaction.response.defer()

        deleted_count = 0
        bot_member = interaction.guild.me

        roles_to_delete = [
            role for role in interaction.guild.roles 
            if not role.is_default() 
            and not role.managed 
            and role < bot_member.top_role
        ]

        for role in reversed(roles_to_delete):
            try:
                await role.delete()
                deleted_count += 1
                await asyncio.sleep(0.2)
            except Exception:
                continue

        embed = discord.Embed(
            title="Roles wiped ✅",
            description=f"Successfully deleted: **{deleted_count}**",
            color=discord.Color.green()
        )
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))