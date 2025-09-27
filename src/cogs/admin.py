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
        self.admins = set()


    admin = app_commands.Group(name="admin", description="Commands for administrators")

    @admin.command(name="ban")
    async def ban(self, interaction: discord.Interaction):
        if interaction.user != interaction.guild.owner or interaction.user not in self.admins:
            await interaction.response.send_message("Access denied!", ephemeral=True)
        else:
            await interaction.response.send_message("Banned {user}")

    @admin.command(name="add")
    async def add(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("Only the owner can add other admins!", ephemeral=True)
            return
        else:
            guild_id = interaction.guild.id
            self.admins.add(user.id)
            cursor.execute("""INSERT INTO admins (guild_id, user_id) VALUES (?, ?) """, (guild_id, user.id))
            connection.commit()
            await interaction.response.send_message(f"{user.mention} is now an admin! 🥳")

    @admin.command(name="remove")
    async def add(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("Only the owner can remove other admins!", ephemeral=True)
            return
        else:
            self.admins.remove(user.id)
            await interaction.response.send_message(f"{user.mention} is no longer an admin! 👌")

    @admin.command(name="admins")
    async def admins(self, interaction: discord.Interaction):
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("Only the owner can list other admins!", ephemeral=True)
            return
        else:
            guild_id = interaction.guild.id
            cursor.execute("SELECT user_id FROM admins WHERE guild_id = ?", (guild_id,))
            admin_ids = [row[0] for row in cursor.fetchall()]

            if len(admin_ids) == 0:
                await interaction.response.send_message("No admins added yet.", ephemeral=True)
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