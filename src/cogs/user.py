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

    @app_commands.command(name="avatar", description="Display a user's avatar")
    @app_commands.describe(user="The user to get the avatar of (defaults to you)")
    async def avatar(self, interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            user = interaction.user
        
        embed = discord.Embed(
            title=f"{user.name}'s Avatar",
            color=0x3498db
        )
        embed.set_image(url=user.display_avatar.url)
        embed.add_field(name="Avatar URL", value=f"[Click here]({user.display_avatar.url})", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roles", description="Display a user's roles")
    @app_commands.describe(user="The user to get roles of (defaults to you)")
    async def roles(self, interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            member = interaction.user
        else:
            member = interaction.guild.get_member(user.id)
            if member is None:
                await interaction.response.send_message(f"User {user.mention} is not a member of this server.")
                return
        
        roles = []
        for role in member.roles:
            if role.name != "@everyone":
                roles.append(role.mention)
        
        if not roles:
            roles_display = "No roles"
        else:
            roles_display = ", ".join(roles)
        
        embed = discord.Embed(
            title=f"{member.display_name}'s Roles",
            description=roles_display,
            color=0x3498db
        )
        embed.add_field(name="Total Roles", value=str(len(roles)), inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
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
        
        truncated_prompt = prompt[:100]
        if len(prompt) > 100:
            truncated_prompt += "..."
            
        embed.set_footer(text=f"Q: {truncated_prompt}", icon_url=interaction.user.display_avatar.url)
        
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
        
        truncated_prompt = prompt[:100]
        if len(prompt) > 100:
            truncated_prompt += "..."
            
        embed.set_footer(text=f"Q: {truncated_prompt}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)


    @app_commands.command(name="serverinfo", description="Display detailed information about this server")
    async def serverinfo(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild = interaction.guild

        total_members = guild.member_count
        humans = 0
        bots = 0
        online = 0
        
        for member in guild.members:
            if member.bot:
                bots += 1
            else:
                humans += 1
                
            if member.status != discord.Status.offline:
                online += 1

        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        stage_channels = len(guild.stage_channels)
        threads = len(guild.threads)
        
        forums = 0
        for channel in guild.channels:
            if isinstance(channel, discord.ForumChannel):
                forums += 1

        total_roles = len(guild.roles) - 1
        role_list = []
        for role in reversed(guild.roles):
            if role.name != "@everyone":
                role_list.append(role.mention)
                
        roles_display = ""
        for role_mention in role_list[:20]:
            if roles_display != "":
                roles_display += ", "
            roles_display += role_mention
            
        if total_roles > 20:
            roles_display += f" *+{total_roles - 20} more*"

        total_emoji = len(guild.emojis)
        animated_emoji = 0
        for emoji in guild.emojis:
            if emoji.animated:
                animated_emoji += 1
                
        static_emoji = total_emoji - animated_emoji
        total_stickers = len(guild.stickers)

        boost_level = guild.premium_tier
        
        if guild.premium_subscription_count is not None:
            boost_count = guild.premium_subscription_count
        else:
            boost_count = 0
            
        boosters = len(guild.premium_subscribers)

        created_at = discord.utils.format_dt(guild.created_at, style="F")
        created_ago = discord.utils.format_dt(guild.created_at, style="R")

        features = []
        if guild.features:
            for feature in guild.features:
                formatted_feature = feature.replace("_", " ").title()
                features.append(formatted_feature)
        else:
            features.append("None")

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

        embed_color = 0x3498db
        if guild.me.color != discord.Color.default():
            embed_color = guild.me.color

        embed = discord.Embed(color=embed_color)
        
        if guild.icon:
            embed.set_author(name=guild.name, icon_url=guild.icon.url)
            embed.set_thumbnail(url=guild.icon.url)
        else:
            embed.set_author(name=guild.name)
            
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        owner_mention = "Unknown"
        if guild.owner:
            owner_mention = guild.owner.mention

        embed.add_field(name="Owner", value=owner_mention, inline=True)
        embed.add_field(name="Server ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="Created", value=f"{created_at}\n{created_ago}", inline=False)

        embed.add_field(
            name=f"Members ({total_members})",
            value=f"👤 Humans: **{humans}**\n🤖 Bots: **{bots}**\n🟢 Online: **{online}**",
            inline=True
        )

        channels_text = f"💬 Text: **{text_channels}**\n"
        channels_text += f"🔊 Voice: **{voice_channels}**\n"
        channels_text += f"📁 Categories: **{categories}**"
        
        if threads > 0:
            channels_text += f"\n🧵 Threads: **{threads}**"
        if stage_channels > 0:
            channels_text += f"\n🎭 Stage: **{stage_channels}**"
        if forums > 0:
            channels_text += f"\n📋 Forums: **{forums}**"

        total_channels = text_channels + voice_channels + stage_channels + forums
        embed.add_field(
            name=f"Channels ({total_channels})",
            value=channels_text,
            inline=True
        )

        boost_bar = ""
        for i in range(14):
            if i < boost_count:
                boost_bar += "🟣"
            else:
                boost_bar += "⚫"
                
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

        final_roles_display = "None"
        if roles_display:
            final_roles_display = roles_display[:1024]
            
        embed.add_field(
            name=f"Roles ({total_roles})",
            value=final_roles_display,
            inline=False
        )

        if guild.features:
            joined_features = ", ".join(features)[:1024]
            embed.add_field(
                name="Server Features",
                value=joined_features,
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

    @app_commands.command(name="invite", description="Create a server invite link")
    @app_commands.describe(duration="How long the invite should last (default: 1 day)")
    @app_commands.choices(duration=[
        app_commands.Choice(name="30 minutes", value=1800),
        app_commands.Choice(name="1 hour", value=3600),
        app_commands.Choice(name="6 hours", value=21600),
        app_commands.Choice(name="12 hours", value=43200),
        app_commands.Choice(name="1 day", value=86400),
        app_commands.Choice(name="7 days", value=604800),
        app_commands.Choice(name="Never", value=0)
    ])
    async def create_invite(self, interaction: discord.Interaction, duration: int = 86400):
        await interaction.response.defer()
        channel = interaction.channel
        
        is_valid_channel = False
        if isinstance(channel, discord.TextChannel):
            is_valid_channel = True
        elif isinstance(channel, discord.VoiceChannel):
            is_valid_channel = True
        elif isinstance(channel, discord.ForumChannel):
            is_valid_channel = True
        elif isinstance(channel, discord.StageChannel):
            is_valid_channel = True

        if not is_valid_channel:
            await interaction.followup.send("I cannot create an invite for this type of channel.")
            return

        invite = await channel.create_invite(max_age=duration, unique=True)
        
        if duration == 0:
            duration_text = "Never expires"
        else:
            expiration_timestamp = int(invite.created_at.timestamp() + duration)
            duration_text = f"Expires in <t:{expiration_timestamp}:R>"
        
        embed = discord.Embed(
            title="Invite Created",
            description=f"**Link:** {invite.url}\n\n**Channel:** {channel.mention}\n**Duration:** {duration_text}",
            color=0x3498db
        )
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(User(bot))