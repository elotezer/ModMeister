from discord import app_commands
from discord.ext import commands
import discord

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    admin = app_commands.Group(name="admin", description="Commands for administrators")

    @admin.command(name="ban")
    async def ban(self, interaction: discord.Interaction):
        if interaction.user != interaction.guild.owner:
            await interaction.response.send_message("Access denied.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))