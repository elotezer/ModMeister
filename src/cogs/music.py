from __future__ import annotations
import asyncio
import os
import re

import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

YTDLP_OPTIONS = {
    "format": "bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "default_search": "scsearch",
    "source_address": "0.0.0.0",
    "prefer_ffmpeg": True,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -protocol_whitelist file,http,https,tcp,tls,crypto,hls,m3u8",
    "options": "-vn",
}

SOUNDCLOUD_RE = re.compile(r"https?://(www\.)?soundcloud\.com/\S+")
SPOTIFY_TRACK_RE = re.compile(r"https?://open\.spotify\.com/track/([A-Za-z0-9]+)")
SPOTIFY_PLAYLIST_RE = re.compile(r"https?://open\.spotify\.com/playlist/([A-Za-z0-9]+)")


def success_embed(description: str) -> discord.Embed:
    return discord.Embed(description=f"✅  {description}", color=0x2ecc71)


def error_embed(description: str) -> discord.Embed:
    return discord.Embed(description=f"🚫  {description}", color=0xe74c3c)


def info_embed(title: str, description: str = "") -> discord.Embed:
    return discord.Embed(title=title, description=description, color=0x3498db)


def get_spotify_client() -> spotipy.Spotify | None:
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))


async def resolve_query(link: str) -> list[str]:
    """
    Takes a SoundCloud URL or Spotify URL/link.
    Returns a list of search queries (SoundCloud search strings) to play.
    """
    spotify = get_spotify_client()

    track_match = SPOTIFY_TRACK_RE.match(link)
    playlist_match = SPOTIFY_PLAYLIST_RE.match(link)

    if track_match and spotify:
        track = spotify.track(track_match.group(1))
        artist = track["artists"][0]["name"]
        title = track["name"]
        return [f"{artist} - {title}"]

    if playlist_match and spotify:
        results = spotify.playlist_tracks(playlist_match.group(1))
        queries = []
        for item in results["items"]:
            track = item.get("track")
            if track:
                artist = track["artists"][0]["name"]
                title = track["name"]
                queries.append(f"{artist} - {title}")
        return queries[:25]

    return [link]


async def fetch_source(query: str) -> dict | None:
    """Runs yt-dlp in a thread and returns track info."""
    opts = {**YTDLP_OPTIONS, "noplaylist": True}

    def extract():
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                if not SOUNDCLOUD_RE.match(query):
                    info = ydl.extract_info(f"scsearch:{query}", download=False)
                    entries = info.get("entries")
                    return entries[0] if entries else None
                return ydl.extract_info(query, download=False)
            except Exception:
                return None

    return await asyncio.get_event_loop().run_in_executor(None, extract)


class Track:
    def __init__(self, info: dict, requested_by: discord.Member):
        self.title: str = info.get("title", "Unknown")
        self.url: str = info["url"]
        self.webpage_url: str = info.get("webpage_url", "")
        self.thumbnail: str | None = info.get("thumbnail")
        self.duration: int = info.get("duration", 0)
        self.uploader: str = info.get("uploader", "Unknown")
        self.requested_by: discord.Member = requested_by

    @property
    def duration_fmt(self) -> str:
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"

    def now_playing_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Now Playing",
            description=f"**[{self.title}]({self.webpage_url})**",
            color=0xff7700
        )
        embed.add_field(name="Uploader", value=self.uploader, inline=True)
        embed.add_field(name="Duration", value=self.duration_fmt, inline=True)
        embed.add_field(name="Requested by", value=self.requested_by.mention, inline=True)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        embed.set_footer(
            text=f"Requested by {self.requested_by}",
            icon_url=self.requested_by.display_avatar.url
        )
        return embed


class GuildMusicState:
    def __init__(self):
        self.queue: list[Track] = []
        self.current: Track | None = None
        self.voice_client: discord.VoiceClient | None = None
        self.loop: bool = False

    def is_playing(self) -> bool:
        return self.voice_client is not None and self.voice_client.is_playing()

    def clear(self):
        self.queue.clear()
        self.current = None
        self.loop = False


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.states: dict[int, GuildMusicState] = {}

    def get_state(self, guild_id: int) -> GuildMusicState:
        if guild_id not in self.states:
            self.states[guild_id] = GuildMusicState()
        return self.states[guild_id]

    async def check_voice(self, interaction: discord.Interaction) -> bool:
        """Returns True if the user is in the same voice channel as the bot. Sends an error if not."""
        state = self.get_state(interaction.guild_id)
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                embed=error_embed("You need to be in a voice channel to use this command."),
                ephemeral=True
            )
            return False
        if state.voice_client and interaction.user.voice.channel != state.voice_client.channel:
            await interaction.response.send_message(
                embed=error_embed(f"You need to be in {state.voice_client.channel.mention} to control playback."),
                ephemeral=True
            )
            return False
        return True

    def play_next(self, guild_id: int, channel: discord.TextChannel):
        state = self.get_state(guild_id)

        if state.loop and state.current:
            next_track = state.current
        elif state.queue:
            next_track = state.queue.pop(0)
        else:
            state.current = None
            asyncio.run_coroutine_threadsafe(
                channel.send(embed=info_embed("Queue finished", "No more tracks in the queue.")),
                self.bot.loop
            )
            return

        state.current = next_track
        source = discord.FFmpegPCMAudio(next_track.url, **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(source, volume=0.5)

        def after(error):
            if error:
                print(f"Player error: {error}")
            self.play_next(guild_id, channel)

        state.voice_client.play(source, after=after)
        asyncio.run_coroutine_threadsafe(
            channel.send(embed=next_track.now_playing_embed()),
            self.bot.loop
        )

    @app_commands.command(name="play", description="Play a SoundCloud or Spotify track/playlist link")
    async def play(self, interaction: discord.Interaction, link: str):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                embed=error_embed("You need to be in a voice channel first."),
                ephemeral=True
            )
            return

        await interaction.response.defer()

        voice_channel = interaction.user.voice.channel
        state = self.get_state(interaction.guild_id)

        try:
            if state.voice_client is None or not state.voice_client.is_connected():
                state.voice_client = await asyncio.wait_for(
                    voice_channel.connect(), timeout=10.0
                )
            elif state.voice_client.channel != voice_channel:
                await state.voice_client.move_to(voice_channel)
        except asyncio.TimeoutError:
            state.voice_client = None
            await interaction.followup.send(embed=error_embed("Timed out trying to connect to voice. Try again."))
            return
        except Exception as e:
            state.voice_client = None
            await interaction.followup.send(embed=error_embed(f"Failed to connect to voice: {e}"))
            return

        if not state.voice_client.is_connected():
            state.voice_client = None
            await interaction.followup.send(embed=error_embed("Could not connect to voice channel. Try again."))
            return

        queries = await resolve_query(link)

        if len(queries) > 1:
            await interaction.followup.send(
                embed=info_embed(f"Spotify Playlist", f"Queuing **{len(queries)}** tracks...")
            )

        queued_count = 0
        first_track = None

        for query in queries:
            info = await fetch_source(query)
            if not info:
                continue
            track = Track(info, interaction.user)
            state.queue.append(track)
            queued_count += 1
            if first_track is None:
                first_track = track

        if queued_count == 0:
            await interaction.followup.send(embed=error_embed("Could not find or stream the requested track."))
            return

        if not state.is_playing():
            self.play_next(interaction.guild_id, interaction.channel)
        else:
            if len(queries) == 1 and first_track:
                embed = success_embed(f"Added **[{first_track.title}]({first_track.webpage_url})** to the queue.")
                embed.add_field(name="Position", value=str(len(state.queue)), inline=True)
                embed.add_field(name="Duration", value=first_track.duration_fmt, inline=True)
                if first_track.thumbnail:
                    embed.set_thumbnail(url=first_track.thumbnail)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    embed=success_embed(f"Added **{queued_count}** tracks to the queue.")
                )

    @app_commands.command(name="skip", description="Skip the current track")
    async def skip(self, interaction: discord.Interaction):
        if not await self.check_voice(interaction):
            return
        state = self.get_state(interaction.guild_id)
        if not state.is_playing():
            await interaction.response.send_message(
                embed=error_embed("Nothing is playing right now."), ephemeral=True
            )
            return

        state.voice_client.stop()
        await interaction.response.send_message(embed=success_embed("Skipped ⏭️"))

    @app_commands.command(name="stop", description="Stop playback and clear the queue")
    async def stop(self, interaction: discord.Interaction):
        if not await self.check_voice(interaction):
            return
        state = self.get_state(interaction.guild_id)
        if state.voice_client is None:
            await interaction.response.send_message(
                embed=error_embed("I'm not in a voice channel."), ephemeral=True
            )
            return

        state.clear()
        await state.voice_client.disconnect()
        state.voice_client = None
        await interaction.response.send_message(embed=success_embed("Stopped and disconnected."))

    @app_commands.command(name="pause", description="Pause the current track")
    async def pause(self, interaction: discord.Interaction):
        if not await self.check_voice(interaction):
            return
        state = self.get_state(interaction.guild_id)
        if not state.is_playing():
            await interaction.response.send_message(
                embed=error_embed("Nothing is playing right now."), ephemeral=True
            )
            return

        state.voice_client.pause()
        await interaction.response.send_message(embed=success_embed("Paused ⏸️"))

    @app_commands.command(name="resume", description="Resume the paused track")
    async def resume(self, interaction: discord.Interaction):
        if not await self.check_voice(interaction):
            return
        state = self.get_state(interaction.guild_id)
        if state.voice_client is None or not state.voice_client.is_paused():
            await interaction.response.send_message(
                embed=error_embed("Nothing is paused right now."), ephemeral=True
            )
            return

        state.voice_client.resume()
        await interaction.response.send_message(embed=success_embed("Resumed ▶️"))

    @app_commands.command(name="queue", description="Show the current queue")
    async def queue(self, interaction: discord.Interaction):
        state = self.get_state(interaction.guild_id)

        if not state.current and not state.queue:
            await interaction.response.send_message(
                embed=info_embed("Queue", "The queue is empty."), ephemeral=True
            )
            return

        embed = discord.Embed(title="Queue", color=0xff7700)

        if state.current:
            embed.add_field(
                name="▶️  Now Playing",
                value=f"**[{state.current.title}]({state.current.webpage_url})** `{state.current.duration_fmt}` — {state.current.requested_by.mention}",
                inline=False
            )

        if state.queue:
            lines = []
            for i, track in enumerate(state.queue[:10], 1):
                lines.append(f"`{i}.` **[{track.title}]({track.webpage_url})** `{track.duration_fmt}` — {track.requested_by.mention}")
            if len(state.queue) > 10:
                lines.append(f"*...and {len(state.queue) - 10} more*")
            embed.add_field(name="Up Next", value="\n".join(lines), inline=False)

        loop_status = "🔁 Loop: **On**" if state.loop else "🔁 Loop: **Off**"
        embed.set_footer(text=loop_status)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="loop", description="Toggle looping the current track")
    async def loop(self, interaction: discord.Interaction):
        if not await self.check_voice(interaction):
            return
        state = self.get_state(interaction.guild_id)
        state.loop = not state.loop
        status = "enabled 🔁" if state.loop else "disabled"
        await interaction.response.send_message(embed=success_embed(f"Loop {status}."))

    @app_commands.command(name="volume", description="Set playback volume (0–100)")
    async def volume(self, interaction: discord.Interaction, level: int):
        if not await self.check_voice(interaction):
            return
        if not 0 <= level <= 100:
            await interaction.response.send_message(
                embed=error_embed("Volume must be between 0 and 100."), ephemeral=True
            )
            return

        state = self.get_state(interaction.guild_id)
        if not state.is_playing():
            await interaction.response.send_message(
                embed=error_embed("Nothing is playing right now."), ephemeral=True
            )
            return

        state.voice_client.source.volume = level / 100
        await interaction.response.send_message(embed=success_embed(f"Volume set to **{level}%** 🔊"))

    @app_commands.command(name="nowplaying", description="Show the currently playing track")
    async def nowplaying(self, interaction: discord.Interaction):
        state = self.get_state(interaction.guild_id)
        if not state.current:
            await interaction.response.send_message(
                embed=info_embed("Nothing playing", "No track is currently playing."), ephemeral=True
            )
            return

        await interaction.response.send_message(embed=state.current.now_playing_embed())


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))