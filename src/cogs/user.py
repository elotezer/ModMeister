from discord import app_commands
from discord.ext import commands
import discord
import random
import os

from dotenv import load_dotenv
from openai import OpenAI
import dotenv

from google import genai

dotenv.load_dotenv()

GPT_KEY = os.getenv("GPT_KEY")


class User(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='roll', description='Roll a random whole number between a selected range')
    async def roll_int(self, interaction: discord.Interaction, x: int, y: int):
        rolled = random.randint(x, y)
        embed = discord.Embed(description=f"🎲  Your roll: **{rolled}**", color=0x3498db)
        embed.add_field(name="Range", value=f"`{x}` — `{y}`", inline=True)
        embed.set_footer(text=f"Rolled by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='roll_f', description='Roll a random float number between 0 and 1')
    async def roll_f(self, interaction: discord.Interaction):
        rolled = random.random()
        embed = discord.Embed(description=f"🎲  Your roll: **{rolled:.6f}**", color=0x3498db)
        embed.add_field(name="Range", value="`0.0` — `1.0`", inline=True)
        embed.set_footer(text=f"Rolled by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="gpt", description="Ask ChatGPT")
    async def gpt(self, interaction: discord.Interaction, prompt: str):
        ai_client = OpenAI(api_key=GPT_KEY)
        await interaction.response.defer(thinking=True)
        resp = ai_client.responses.create(
            model="gpt-5-mini",  # change to your preferred model
            input=prompt,
            store=True
        )
        embed = discord.Embed(
            description=resp.output_text.strip(),
            color=0x74aa9c  # ChatGPT green
        )
        embed.set_author(name="ChatGPT")
        embed.set_footer(text=f"Q: {prompt[:100]}{'...' if len(prompt) > 100 else ''}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="gemini", description="Ask Gemini")
    async def gemini(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer(thinking=True)
        client = genai.Client()
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        embed = discord.Embed(
            description=response.text.strip(),
            color=0x4285f4  # Google blue
        )
        embed.set_author(name="Gemini")
        embed.set_footer(text=f"Q: {prompt[:100]}{'...' if len(prompt) > 100 else ''}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))