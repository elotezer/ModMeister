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
            model="gpt-5-mini",
            input=prompt,
            store=True
        )
        embed = discord.Embed(
            description=resp.output_text.strip(),
            color=0x74aa9c
        )
        embed.set_author(name="ChatGPT", icon_url="https://cdn.discordapp.com/emojis/1095939132004454430.webp")
        embed.set_footer(text=f"Q: {prompt[:100]}{'...' if len(prompt) > 100 else ''}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="gemini", description="Ask Gemini")
    async def gemini(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer(thinking=True)
        client = genai.Client()
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        embed = discord.Embed(
            description=response.text.strip(),
            color=0x4285f4
        )
        embed.set_author(name="Gemini", icon_url="https://cdn.discordapp.com/emojis/1197557441210994698.webp")
        embed.set_footer(text=f"Q: {prompt[:100]}{'...' if len(prompt) > 100 else ''}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)


    @app_commands.command(name="serverinfo", description="Display detailed information about this server")
    async def serverinfo(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild = interaction.guild

        total_members = guild.member_count
        humans = sum(1 for m in guild.members if not m.bot)
        bots = sum(1 for m in guild.members if m.bot)
        online = sum(1 for m in guild.members if m.status != discord.Status.offline)

        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        forums = len([c for c in guild.channels if isinstance(c, discord.ForumChannel)])
        stage_channels = len(guild.stage_channels)
        threads = len(guild.threads)

        total_roles = len(guild.roles) - 1
        role_list = [r.mention for r in reversed(guild.roles) if r.name != "@everyone"]
        roles_display = ", ".join(role_list[:20]) + (f" *+{total_roles - 20} more*" if total_roles > 20 else "")

        total_emoji = len(guild.emojis)
        animated_emoji = sum(1 for e in guild.emojis if e.animated)
        static_emoji = total_emoji - animated_emoji
        total_stickers = len(guild.stickers)

        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count or 0
        boosters = len(guild.premium_subscribers)

        created_at = discord.utils.format_dt(guild.created_at, style="F")
        created_ago = discord.utils.format_dt(guild.created_at, style="R")

        features = [f.replace("_", " ").title() for f in guild.features] if guild.features else ["None"]

        verification_map = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium",
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest"
        }
        filter_map = {
            discord.ContentFilter.disabled: "Disabled",
            discord.ContentFilter.no_role: "No Role",
            discord.ContentFilter.all_members: "All Members"
        }
        nsfw_map = {
            discord.NSFWLevel.default: "Default",
            discord.NSFWLevel.explicit: "Explicit",
            discord.NSFWLevel.safe: "Safe",
            discord.NSFWLevel.age_restricted: "Age Restricted"
        }
        mfa_map = {
            discord.MFALevel.disabled: "Not Required",
            discord.MFALevel.require_2fa: "Required"
        }

        verification = verification_map.get(guild.verification_level, "Unknown")
        content_filter = filter_map.get(guild.explicit_content_filter, "Unknown")
        nsfw_level = nsfw_map.get(guild.nsfw_level, "Unknown")
        mfa = mfa_map.get(guild.mfa_level, "Unknown")

        embed = discord.Embed(
            color=guild.me.color if guild.me.color != discord.Color.default() else 0x3498db
        )
        embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else None)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Server ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="Created", value=f"{created_at}\n{created_ago}", inline=False)

        embed.add_field(
            name=f"Members ({total_members})",
            value=f"👤 Humans: **{humans}**\n🤖 Bots: **{bots}**\n🟢 Online: **{online}**",
            inline=True
        )

        embed.add_field(
            name=f"Channels ({text_channels + voice_channels + stage_channels + forums})",
            value=(
                f"💬 Text: **{text_channels}**\n"
                f"🔊 Voice: **{voice_channels}**\n"
                f"📁 Categories: **{categories}**\n"
                + (f"🧵 Threads: **{threads}**\n" if threads else "")
                + (f"🎭 Stage: **{stage_channels}**\n" if stage_channels else "")
                + (f"📋 Forums: **{forums}**" if forums else "")
            ),
            inline=True
        )

        boost_bar = "🟣" * boost_count + "⚫" * max(0, 14 - boost_count)
        embed.add_field(
            name=f"Boosts — Level {boost_level}",
            value=f"{boost_bar}\n**{boost_count}** boosts from **{boosters}** booster(s)",
            inline=False
        )

        embed.add_field(
            name=f"Emoji ({total_emoji})",
            value=f"🖼️ Static: **{static_emoji}**\n✨ Animated: **{animated_emoji}**",
            inline=True
        )
        embed.add_field(
            name=f"Stickers ({total_stickers})",
            value=f"**{total_stickers}** / {guild.sticker_limit}",
            inline=True
        )

        embed.add_field(
            name="Security",
            value=(
                f"🔒 Verification: **{verification}**\n"
                f"🛡️ Content Filter: **{content_filter}**\n"
                f"🔞 NSFW Level: **{nsfw_level}**\n"
                f"🔑 2FA Requirement: **{mfa}**"
            ),
            inline=False
        )

        embed.add_field(
            name=f"Roles ({total_roles})",
            value=roles_display[:1024] if roles_display else "None",
            inline=False
        )

        if guild.features:
            embed.add_field(
                name="Server Features",
                value=", ".join(features)[:1024],
                inline=False
            )

        if guild.system_channel:
            embed.add_field(name="System Channel", value=guild.system_channel.mention, inline=True)
        if guild.rules_channel:
            embed.add_field(name="Rules Channel", value=guild.rules_channel.mention, inline=True)
        if guild.public_updates_channel:
            embed.add_field(name="Updates Channel", value=guild.public_updates_channel.mention, inline=True)
        embed.add_field(name="Preferred Locale", value=str(guild.preferred_locale), inline=True)

        embed.set_footer(
            text=f"Requested by {interaction.user} • {guild.name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))