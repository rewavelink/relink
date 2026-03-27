# NOTE: This example requires the 'message_content' and 'members' privileged intents

# This example covers an advanced music bot using relink, featuring a full
# queue system, volume control, track history, seeking, and playlist support.
# It requires an active Lavalink server — for setup instructions see:
# https://relink.readthedocs.io/en/latest/guides/lavalink-setup.html

from typing import Any

import discord
from discord.ext import commands

import relink
import relink.models
from relink.gateway.enums import QueueMode
from relink.rest.enums import TrackSourceType


# We subclass commands.Bot to hold our relink.Client instance cleanly.
# This avoids relying on globals and makes the client easy to access anywhere.
class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            intents=intents,
            command_prefix="!",
        )

        self.rl_client: relink.Client[Any] = relink.Client(self)

    async def setup_hook(self) -> None:
        # discord.py will automatically call 'setup_hook', and is the
        # safest place to start our client.
        await self.rl_client.start()
        print("ReLink nodes connected successfully!")


bot = Bot()

# Register the node we want to connect to. You can register multiple nodes
# and relink will automatically load-balance between them via 'get_best_node'.
bot.rl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
)


# Helper function for DRY (Don't Repeat Yourself)
def _player_check(ctx: commands.Context[Bot]) -> relink.Player | None:
    """Returns the active Player for this guild, or None if not connected."""
    vc = ctx.voice_client
    return vc if isinstance(vc, relink.Player) else None


# -----------------
# Playback commands
# -----------------


@bot.command()
async def play(ctx: commands.Context[Bot], *, query: str) -> None:
    """
    Plays a track or playlist, or adds it to the queue if something is already playing.

    Supports plain search queries as well as direct URLs (YouTube, SoundCloud, etc.).
    When a playlist URL is provided, all tracks are enqueued.
    """

    assert isinstance(ctx.author, discord.Member)
    vc = ctx.voice_client

    # Connect to the author's voice channel if we are not already in one.
    if vc is None:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("You must be in a voice channel!")
            return

        vc = await ctx.author.voice.channel.connect(cls=relink.Player)

    assert isinstance(vc, relink.Player)

    # Search for the query. By default this searches YouTube; pass a
    # 'source' kwarg (e.g. TrackSourceType.SOUNDCLOUD) to change that.
    result = await bot.rl_client.search_track(query, source=TrackSourceType.YOUTUBE)

    if result.is_error() or result.is_empty() or result.result is None:
        await ctx.reply("Could not find any tracks!")
        return

    data = result.result

    # Depending on the result type we either get a single track, a list of
    # search results, or a full playlist. We handle all three cases here.
    if isinstance(data, relink.models.Playlist):
        # Playlist: play the first track immediately and queue the rest.
        first, *rest = data.tracks
        vc.queue.put(first)

        if rest:
            vc.queue.put(rest)

        if not vc.current:
            await vc.play(vc.queue.get())
            await ctx.reply(
                f"Now playing `{first.title}` and queued {len(rest)} more tracks "
                f"from playlist `{data.name}`!"
            )
        else:
            await ctx.reply(
                f"Added `{data.name}` ({len(data.tracks)} tracks) to the queue!"
            )
        return

    # Single track or top search result.
    track = data[0] if isinstance(data, list) else data
    vc.queue.put(track)

    if not vc.current:
        to_play = vc.queue.get()
        await vc.play(to_play)
        await ctx.reply(f"Now playing `{to_play.title}` by `{to_play.author}`!")
    else:
        await ctx.reply(f"Added `{track.title}` by `{track.author}` to the queue!")


@bot.command()
async def pause(ctx: commands.Context[Bot]) -> None:
    """Pauses the current track."""

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Not connected to a voice channel!")
        return

    if vc.paused:
        await ctx.reply("Already paused! Use `!resume` to continue.")
        return

    await vc.pause()
    await ctx.reply("Paused!")


@bot.command()
async def resume(ctx: commands.Context[Bot]) -> None:
    """Resumes the player if it is paused."""

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Not connected to a voice channel!")
        return

    if not vc.paused:
        await ctx.reply("Not paused!")
        return

    await vc.resume()
    await ctx.reply("Resumed!")


@bot.command()
async def skip(ctx: commands.Context[Bot]) -> None:
    """Skips the current track and plays the next one in the queue."""

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Not connected to a voice channel!")
        return

    # 'skip' raises QueueEmpty when there are no further tracks to advance to.
    try:
        track = await vc.skip()
    except relink.QueueEmpty:
        await ctx.reply("The queue is empty — nothing to skip to!")
        return

    if track:
        await ctx.reply(f"Skipped to `{track.title}` by `{track.author}`!")
    else:
        await ctx.reply("Skipped! Nothing left in the queue.")


@bot.command()
async def previous(ctx: commands.Context[Bot]) -> None:
    """Goes back to the previous track in the history."""

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Not connected to a voice channel!")
        return

    # 'previous' raises HistoryEmpty when there is no track to go back to.
    try:
        track = await vc.previous()
    except relink.HistoryEmpty:
        await ctx.reply("No previous track in history!")
        return

    await ctx.reply(f"Going back to `{track.title}` by `{track.author}`!")


@bot.command()
async def seek(ctx: commands.Context[Bot], seconds: int) -> None:
    """
    Seeks to a position in the current track (in seconds).

    Example: !seek 90  →  jumps to the 1:30 mark.
    """

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Not connected to a voice channel!")
        return

    if not vc.current:
        await ctx.reply("Nothing is playing!")
        return

    await vc.seek(seconds * 1000)
    await ctx.reply(f"Seeked to {seconds}s!")


@bot.command()
async def stop(ctx: commands.Context[Bot]) -> None:
    """Stops playback, clears the queue, and disconnects the bot."""

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Already disconnected!")
        return

    await vc.disconnect()
    await ctx.reply("Disconnected and cleared the queue!")


# --------------
# Queue commands
# --------------


@bot.command()
async def queue(ctx: commands.Context[Bot]) -> None:
    """Displays the current queue (up to 10 upcoming tracks)."""

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Not connected to a voice channel!")
        return

    tracks = vc.queue.tracks

    if not tracks and not vc.current:
        await ctx.reply("The queue is empty!")
        return

    lines: list[str] = []

    if vc.current:
        lines.append(
            f"**Now playing:** `{vc.current.title}` by `{vc.current.author}`\n"
        )

    if tracks:
        lines.append("**Up next:**")
        for i, track in enumerate(tracks[:10], start=1):
            lines.append(f"`{i}.` `{track.title}` by `{track.author}`")

        if len(tracks) > 10:
            lines.append(f"\n*...and {len(tracks) - 10} more tracks.*")

    await ctx.reply("\n".join(lines))


@bot.command()
async def shuffle(ctx: commands.Context[Bot]) -> None:
    """Shuffles the current queue in place."""

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Not connected to a voice channel!")
        return

    if not vc.queue.tracks:
        await ctx.reply("The queue is empty!")
        return

    vc.queue.shuffle()
    await ctx.reply("Queue shuffled!")


@bot.command()
async def loop(ctx: commands.Context[Bot], mode: str = "track") -> None:
    """
    Sets the loop mode. Options: 'track', 'all', 'off'.

    - track: repeats the current track indefinitely.
    - all:   loops the entire queue once it finishes.
    - off:   disables looping.
    """

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Not connected to a voice channel!")
        return

    mode = mode.lower()
    mapping = {
        "track": QueueMode.LOOP,
        "all": QueueMode.LOOP_ALL,
        "off": QueueMode.NORMAL,
    }

    if mode not in mapping:
        await ctx.reply("Invalid mode! Choose from: `track`, `all`, `off`.")
        return

    vc.queue.mode = mapping[mode]
    await ctx.reply(f"Loop mode set to `{mode}`!")


# ---------------
# Player settings
# ---------------


@bot.command()
async def volume(ctx: commands.Context[Bot], value: int) -> None:
    """Sets the player volume (0–1000). Default is 100."""

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Not connected to a voice channel!")
        return

    if not 0 <= value <= 1000:
        await ctx.reply("Volume must be between 0 and 1000!")
        return

    await vc.set_volume(value)
    await ctx.reply(f"Volume set to `{value}`!")


@bot.command()
async def nowplaying(ctx: commands.Context[Bot]) -> None:
    """Shows information about the currently playing track."""

    vc = _player_check(ctx)
    if not vc:
        await ctx.reply("Not connected to a voice channel!")
        return

    track = vc.current
    if not track:
        await ctx.reply("Nothing is playing right now!")
        return

    # Convert milliseconds to a readable mm:ss position / duration.
    def fmt(ms: int) -> str:
        s = ms // 1000
        return f"{s // 60}:{s % 60:02d}"

    await ctx.reply(
        f"**Now playing:** `{track.title}` by `{track.author}`\n"
        f"**Position:** `{fmt(vc.position)}` / `{fmt(track.length)}`\n"
        f"**Volume:** `{vc.volume}` | **Loop:** `{vc.queue.mode.name.lower()}`"
    )


# Now, we can run our bot
if __name__ == "__main__":
    bot.run("TOKEN")
