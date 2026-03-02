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

    # commands that every1 can use will be here

    @app_commands.command(name='roll', description='Roll a random whole number between a selected range')
    async def roll_int(self, interaction: discord.Interaction, x: int, y: int):
        rolled = random.randint(x, y)
        await interaction.response.send_message(f"Your random number: {rolled}")

    @app_commands.command(name='roll_f', description='Roll a random float number between 0 and 1')
    async def roll_f(self, interaction: discord.Interaction):
        rolled = random.random()
        await interaction.response.send_message(f"Your random number: {rolled:.6f}")

    @app_commands.command(name="gpt", description="Ask ChatGPT")
    async def gpt(self, interaction: discord.Interaction, prompt: str):
        ai_client = OpenAI(api_key=GPT_KEY)
        await interaction.response.defer(thinking=True)
        resp = ai_client.responses.create(model="gpt-5-mini", # u can change this model to your preferred one
                                          input=prompt,
                                          store=True)
        embed = discord.Embed(
            title="**ChatGPT**",
            description=f"`{resp.output_text.strip()}`",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="gemini", description="Ask Gemini")
    async def gemini(self, interaction: discord.Interaction, prompt: str):

        await interaction.response.defer(thinking=True)

        
        client = genai.Client()
        

        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)

        embed = discord.Embed(
            title="**Gemini**",
            description=f"`{response.text.strip()}`",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Q: {prompt[:100]}...")
        await interaction.followup.send(embed=embed)
        # print(response.text)
 


async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))