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
cursor.execute("""
    CREATE TABLE IF NOT EXISTS warnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER,
        user_id INTEGER,
        reason VARCHAR(50),
        warned_by INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")


def success_embed(description: str) -> discord.Embed:
    return discord.Embed(description=f"✅  {description}", color=0x2ecc71)


def error_embed(description: str) -> discord.Embed:
    return discord.Embed(description=f"🚫  {description}", color=0xe74c3c)


def info_embed(title: str, description: str = "") -> discord.Embed:
    return discord.Embed(title=title, description=description, color=0x3498db)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    admin = app_commands.Group(name="admin", description="Commands for administrators")

    def is_admin(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == interaction.guild.owner_id:
            return True
            
        cursor.execute(
            "SELECT 1 FROM admins WHERE guild_id = ? AND user_id = ?",
            (interaction.guild_id, interaction.user.id)
        )
        
        result = cursor.fetchone()
        if result is not None:
            return True
        else:
            return False

    async def send_no_permission(self, interaction: discord.Interaction, action: str):
        embed = error_embed(f"You don't have permission to {action}.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @admin.command(name="kick", description="Kick a member")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "kick members")
            return

        await user.kick(reason=reason)
        
        embed = success_embed(f"{user.mention} has been kicked.")
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="ban", description="Ban a member")
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "ban members")
            return

        await user.ban(reason=reason)
        
        embed = success_embed(f"{user.mention} has been banned.")
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="unban", description="Unban a member")
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "unban members")
            return

        await interaction.guild.unban(user)
        
        embed = success_embed(f"{user.mention} has been unbanned.")
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="mute", description="Mute a member for a specific number of minutes (Timeout)")
    async def mute(self, interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "mute members")
            return

        muted_until = discord.utils.utcnow() + timedelta(minutes=minutes)
        await user.timeout(muted_until, reason=reason)
        
        embed = success_embed(f"{user.mention} has been muted for **{minutes} minute(s)**.")
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Expires", value=discord.utils.format_dt(muted_until, style="R"), inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="unmute", description="Unmute a member")
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "unmute members")
            return

        await user.timeout(None)
        
        embed = success_embed(f"{user.mention} has been unmuted.")
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="add", description="Add an admin")
    async def add(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user.id != interaction.guild.owner_id:
            embed = error_embed("Only the server owner can add admins.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guild_id = interaction.guild.id
        cursor.execute("INSERT INTO admins (guild_id, user_id) VALUES (?, ?)", (guild_id, user.id))
        connection.commit()
        
        role = discord.utils.get(interaction.guild.roles, name="Admin")
        member = interaction.guild.get_member(user.id)
        
        if role is None:
            perms = discord.Permissions(administrator=True)
            role = await interaction.guild.create_role(
                name="Admin",
                color=discord.Color.red(),
                permissions=perms,
                hoist=True,
                mentionable=True
            )
            
        if member is not None:
            await member.add_roles(role)

        embed = success_embed(f"{user.mention} has been added as an Admin.")
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Added by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="remove", description="Remove an admin")
    async def remove(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user.id != interaction.guild.owner_id:
            embed = error_embed("Only the server owner can remove admins.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guild_id = interaction.guild.id
        cursor.execute("DELETE FROM admins WHERE guild_id = ? AND user_id = ?", (guild_id, user.id))
        connection.commit()
        
        role = discord.utils.get(interaction.guild.roles, name="Admin")
        member = interaction.guild.get_member(user.id)
        
        if role is None:
            pass
        else:
            if member is not None:
                await member.remove_roles(role)

        embed = success_embed(f"{user.mention} has been removed as an Admin.")
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Removed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="new_text_ch", description="Create a new text channel")
    async def new_text_ch(self, interaction: discord.Interaction, ch_name: str, ch_cat: discord.CategoryChannel):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "create text channels")
            return

        await interaction.guild.create_text_channel(ch_name, category=ch_cat)
        
        embed = success_embed(f"Text channel **#{ch_name}** created in **{ch_cat.name}**.")
        embed.set_footer(text=f"Created by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="del_text_ch", description="Delete a text channel")
    async def del_text_ch(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "delete text channels")
            return

        name = channel.name
        await channel.delete()
        
        embed = success_embed(f"Text channel **#{name}** has been deleted.")
        embed.set_footer(text=f"Deleted by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="new_voice_ch", description="Create a new voice channel")
    async def new_voice_ch(self, interaction: discord.Interaction, ch_name: str, ch_cat: discord.CategoryChannel):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "create voice channels")
            return

        await interaction.guild.create_voice_channel(ch_name, category=ch_cat)
        
        embed = success_embed(f"Voice channel **{ch_name}** created in **{ch_cat.name}**.")
        embed.set_footer(text=f"Created by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="del_voice_ch", description="Delete a voice channel")
    async def del_voice_ch(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "delete voice channels")
            return

        name = channel.name
        await channel.delete()
        
        embed = success_embed(f"Voice channel **{name}** has been deleted.")
        embed.set_footer(text=f"Deleted by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="new_category", description="Create a new category")
    async def new_category(self, interaction: discord.Interaction, name: str):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "create categories")
            return

        await interaction.guild.create_category(name=name)
        
        embed = success_embed(f"Category **{name}** has been created.")
        embed.set_footer(text=f"Created by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="del_category", description="Delete a category")
    async def del_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "delete categories")
            return

        name = category.name
        await category.delete()
        
        embed = success_embed(f"Category **{name}** has been deleted.")
        embed.set_footer(text=f"Deleted by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="new_private_category", description="Create a new admin-only private category")
    async def new_private_category(self, interaction: discord.Interaction, name: str):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "create private categories")
            return

        guild = interaction.guild
        admin_role = discord.utils.get(guild.roles, name="Admin")
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            admin_role: discord.PermissionOverwrite(view_channel=True)
        }

        await guild.create_category(name, overwrites=overwrites)
        
        embed = success_embed(f"Private category **{name}** has been created.\n🔒  Visible to Admins only.")
        embed.set_footer(text=f"Created by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="give_role", description="Give a role to a user (or everyone)")
    async def add_role(self, interaction: discord.Interaction, role: discord.Role, user: discord.Member | None = None):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "give roles")
            return

        if interaction.user.id != interaction.guild.owner_id:
            if role.name == "Admin":
                embed = error_embed("Only the server owner can give the Admin role.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        if user is not None:
            await user.add_roles(role)
            
            embed = success_embed(f"Gave {role.mention} to {user.mention}.")
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.defer()
            
            info = info_embed(f"Distributing {role.name}...", f"Giving **{role.name}** to all members. This may take a while.")
            await interaction.followup.send(embed=info)

            success = 0
            failed = 0
            
            for member in interaction.guild.members:
                try:
                    await member.add_roles(role)
                    success += 1
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    failed += 1
                    continue

            result_embed = success_embed(f"Finished distributing **{role.name}**.")
            result_embed.add_field(name="✅ Succeeded", value=str(success), inline=True)
            
            if failed > 0:
                result_embed.add_field(name="❌ Failed", value=str(failed), inline=True)
                
            result_embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=result_embed)

    @admin.command(name="take_role", description="Remove a role from a user (or everyone)")
    async def take_role(self, interaction: discord.Interaction, role: discord.Role, user: discord.Member | None = None):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "take roles")
            return

        if interaction.user.id != interaction.guild.owner_id:
            if role.name == "Admin":
                embed = error_embed("Only the server owner can remove the Admin role.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        if user is not None:
            await user.remove_roles(role)
            
            embed = success_embed(f"Removed {role.mention} from {user.mention}.")
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.defer()
            
            info = info_embed(f"Removing {role.name}...", f"Removing **{role.name}** from all members. This may take a while.")
            await interaction.followup.send(embed=info)

            success = 0
            failed = 0
            
            for member in interaction.guild.members:
                try:
                    await member.remove_roles(role)
                    success += 1
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    failed += 1
                    continue

            result_embed = success_embed(f"Finished removing **{role.name}**.")
            result_embed.add_field(name="✅ Succeeded", value=str(success), inline=True)
            
            if failed > 0:
                result_embed.add_field(name="❌ Failed", value=str(failed), inline=True)
                
            result_embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=result_embed)

    @admin.command(name="warn", description="Issue a warning to a member")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "warn members")
            return

        cursor.execute(
            "INSERT INTO warnings (guild_id, user_id, reason, warned_by) VALUES (?, ?, ?, ?)",
            (interaction.guild_id, user.id, reason, interaction.user.id)
        )
        connection.commit()

        cursor.execute(
            "SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?",
            (interaction.guild_id, user.id)
        )
        total_warnings = cursor.fetchone()[0]

        embed = discord.Embed(title="Warning Issued", color=0xf39c12)
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Member", value=user.mention, inline=True)
        embed.add_field(name="Total Warnings", value=str(total_warnings), inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Warned by {interaction.user} • ID: {user.id}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

        try:
            dm_embed = discord.Embed(
                title=f"⚠️ You received a warning in **{interaction.guild.name}**",
                color=0xf39c12
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Total Warnings", value=str(total_warnings), inline=True)
            dm_embed.set_footer(text=f"Issued by {interaction.user}")
            
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            pass

    @admin.command(name="warnings", description="View all warnings for a member")
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "view warnings")
            return

        cursor.execute(
            "SELECT id, reason, warned_by, timestamp FROM warnings WHERE guild_id = ? AND user_id = ? ORDER BY timestamp DESC",
            (interaction.guild_id, user.id)
        )
        rows = cursor.fetchall()

        if len(rows) == 0:
            embed = info_embed(f"No warnings for {user}", f"{user.mention} has a clean record.")
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(title=f"Warnings — {user}", color=0xf39c12)
        embed.set_thumbnail(url=user.display_avatar.url)

        for warning_id, reason, warned_by, timestamp in rows:
            embed.add_field(
                name=f"#{warning_id} • {timestamp}",
                value=f"**Reason:** {reason}\n**By:** <@{warned_by}>",
                inline=False
            )

        embed.set_footer(
            text=f"Total: {len(rows)} warning(s) • Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="clear_warnings", description="Clear warnings for a member — all or a specific one by ID")
    async def clear_warnings(self, interaction: discord.Interaction, user: discord.Member, warning_id: int | None = None):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "clear warnings")
            return

        if warning_id is not None:
            cursor.execute(
                "SELECT id FROM warnings WHERE id = ? AND guild_id = ? AND user_id = ?",
                (warning_id, interaction.guild_id, user.id)
            )
            
            result = cursor.fetchone()
            if result is None:
                embed = error_embed(f"Warning `#{warning_id}` not found for {user.mention}.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            cursor.execute("DELETE FROM warnings WHERE id = ?", (warning_id,))
            connection.commit()

            cursor.execute(
                "SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?",
                (interaction.guild_id, user.id)
            )
            remaining = cursor.fetchone()[0]

            embed = success_embed(f"Warning `#{warning_id}` removed from {user.mention}.")
            embed.add_field(name="Remaining Warnings", value=str(remaining), inline=True)
        else:
            cursor.execute(
                "SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?",
                (interaction.guild_id, user.id)
            )
            count = cursor.fetchone()[0]

            if count == 0:
                embed = error_embed(f"{user.mention} has no warnings to clear.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            cursor.execute(
                "DELETE FROM warnings WHERE guild_id = ? AND user_id = ?",
                (interaction.guild_id, user.id)
            )
            connection.commit()

            embed = success_embed(f"All **{count}** warning(s) cleared for {user.mention}.")

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @admin.command(name="userinfo", description="Display full information about a user")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "look up user info")
            return

        await interaction.response.defer()

        cursor.execute(
            "SELECT reason, warned_by, timestamp FROM warnings WHERE guild_id = ? AND user_id = ? ORDER BY timestamp DESC",
            (interaction.guild_id, user.id)
        )
        warning_rows = cursor.fetchall()
        total_warnings = len(warning_rows)

        created_at = discord.utils.format_dt(user.created_at, style="F")
        created_ago = discord.utils.format_dt(user.created_at, style="R")
        account_age_days = (discord.utils.utcnow() - user.created_at).days

        if user.joined_at is not None:
            joined_at = discord.utils.format_dt(user.joined_at, style="F")
            joined_ago = discord.utils.format_dt(user.joined_at, style="R")
        else:
            joined_at = "Unknown"
            joined_ago = ""

        rejoined_note = ""
        if user.joined_at is not None:
            days_after_creation = (user.joined_at - user.created_at).days
            if days_after_creation > 30:
                rejoined_note = f"\n⚠️ Joined {days_after_creation} days after account creation — may have left & rejoined."

        roles = []
        for r in reversed(user.roles):
            if r.name != "@everyone":
                roles.append(r.mention)
                
        roles_display = ""
        if len(roles) > 0:
            for i, role in enumerate(roles):
                if i > 0:
                    roles_display += ", "
                roles_display += role
        else:
            roles_display = "None"

        key_perms = []
        if user.guild_permissions.administrator:
            key_perms.append("Administrator")
        if user.guild_permissions.manage_guild:
            key_perms.append("Manage Server")
        if user.guild_permissions.manage_roles:
            key_perms.append("Manage Roles")
        if user.guild_permissions.manage_channels:
            key_perms.append("Manage Channels")
        if user.guild_permissions.ban_members:
            key_perms.append("Ban Members")
        if user.guild_permissions.kick_members:
            key_perms.append("Kick Members")
        if user.guild_permissions.moderate_members:
            key_perms.append("Timeout Members")
            
        perms_display = ""
        if len(key_perms) > 0:
            for i, perm in enumerate(key_perms):
                if i > 0:
                    perms_display += ", "
                perms_display += perm
        else:
            perms_display = "None"

        status_map = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🌙 Idle",
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }
        
        status = status_map.get(user.status, "Unknown")
        
        if user.activity is not None:
            activity = str(user.activity)
        else:
            activity = "None"

        timed_out = ""
        if user.timed_out_until is not None:
            if user.timed_out_until > discord.utils.utcnow():
                timed_out = discord.utils.format_dt(user.timed_out_until, style="R")

        embed_color = 0x3498db
        if user.color != discord.Color.default():
            embed_color = user.color

        embed = discord.Embed(color=embed_color)
        
        bot_emoji = ""
        if user.bot:
            bot_emoji = "🤖"
            
        embed.set_author(name=f"{user} {bot_emoji}", icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="Display Name", value=user.display_name, inline=True)
        embed.add_field(name="User ID", value=f"`{user.id}`", inline=True)
        embed.add_field(name="Status", value=status, inline=True)

        embed.add_field(
            name="Account Created",
            value=f"{created_at}\n{created_ago} — {account_age_days} days old",
            inline=False
        )
        embed.add_field(
            name="Joined Server",
            value=f"{joined_at}\n{joined_ago}{rejoined_note}",
            inline=False
        )

        if timed_out != "":
            embed.add_field(name="⏱️ Timed Out", value=f"Expires {timed_out}", inline=False)

        embed.add_field(name="Activity", value=activity, inline=True)
        embed.add_field(name="Key Permissions", value=perms_display, inline=False)
        embed.add_field(name=f"Roles ({len(roles)})", value=roles_display[:1024], inline=False)

        if total_warnings > 0:
            warnings_text = ""
            for i, row in enumerate(warning_rows[:5]):
                if i > 0:
                    warnings_text += "\n"
                warnings_text += f"`{row[2]}` — {row[0]} (by <@{row[1]}>)"
                
            if total_warnings > 5:
                warnings_text += f"\n*...and {total_warnings - 5} more*"
                
            embed.add_field(name=f"⚠️ Warnings ({total_warnings})", value=warnings_text, inline=False)
        else:
            embed.add_field(name="⚠️ Warnings", value="None", inline=False)

        embed.set_footer(
            text=f"Requested by {interaction.user} • {interaction.guild.name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.followup.send(embed=embed)

    @admin.command(name="setup_server", description="Sets up a basic server model with categories and channels")
    async def setup_server(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "run a server setup")
            return

        await interaction.response.defer(ephemeral=False)

        for channel in interaction.guild.channels:
            try:
                if channel.id != interaction.channel.id:
                    await channel.delete()
            except Exception as e:
                print(f"couldnt delete channel: {channel.name} -", e)

        for category in interaction.guild.categories:
            try:
                await category.delete()
            except Exception as e:
                print(f"couldnt delete category: {category.name} -", e)

        about = await interaction.guild.create_category(name="About")
        await interaction.followup.send(embed=success_embed("Category **About** created."))

        text = await interaction.guild.create_category(name="Text")
        await interaction.followup.send(embed=success_embed("Category **Text** created."))

        voice = await interaction.guild.create_category(name="Voice")
        await interaction.followup.send(embed=success_embed("Category **Voice** created."))

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
            await interaction.followup.send(embed=success_embed(f"**#{name}** created in **About**."))

        for name in text_ch_names:
            await interaction.guild.create_text_channel(name=name, category=text)
            await interaction.followup.send(embed=success_embed(f"**#{name}** created in **Text**."))

        for name in voice_ch_names:
            if name == "Voice Trio":
                await interaction.guild.create_voice_channel(name=name, category=voice, user_limit=3)
            elif name == "Voice Duo":
                await interaction.guild.create_voice_channel(name=name, category=voice, user_limit=2)
            else:
                await interaction.guild.create_voice_channel(name=name, category=voice)
            await interaction.followup.send(embed=success_embed(f"**{name}** created in **Voice**."))

        for channel in interaction.guild.channels:
            try:
                if channel.id == interaction.channel.id:
                    await channel.delete()
            except Exception as e:
                print(f"couldnt delete channel: {channel.name} -", e)

    @admin.command(name="wipe", description="Delete every category and every channel in the server.")
    async def wipe(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "wipe the server")
            return

        await interaction.response.defer(ephemeral=False)

        for channel in interaction.guild.channels:
            try:
                if channel.id != interaction.channel.id:
                    await channel.delete()
            except Exception as e:
                print(f"couldnt delete channel: {channel.name} -", e)

        for category in interaction.guild.categories:
            try:
                await category.delete()
            except Exception as e:
                print(f"couldnt delete category: {category.name} -", e)

        await interaction.followup.send(embed=success_embed("Server has been wiped."))

    @admin.command(name="clear_roles", description="Deletes all roles")
    async def clear_roles(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
            await self.send_no_permission(interaction, "wipe roles")
            return

        await interaction.response.defer()

        deleted_count = 0
        bot_member = interaction.guild.me

        roles_to_delete = []
        for role in interaction.guild.roles:
            if not role.is_default():
                if not role.managed:
                    if role < bot_member.top_role:
                        roles_to_delete.append(role)

        for role in reversed(roles_to_delete):
            try:
                await role.delete()
                deleted_count += 1
                await asyncio.sleep(0.2)
            except Exception:
                continue

        embed = success_embed(f"Deleted **{deleted_count}** role(s).")
        embed.set_footer(text=f"Actioned by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))