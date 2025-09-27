from discord import app_commands
from discord.ext import commands
import discord

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
        else:
            self.admins.add(user.id)
            await interaction.response.send_message(f"{user.mention} is now an admin! 🥳")

    @admin.command(name="remove")
    async def add(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("Only the owner can remove other admins!", ephemeral=True)
        else:
            self.admins.add(user.id)
            await interaction.response.send_message(f"{user.mention} is no longer an admin! 👌")


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))