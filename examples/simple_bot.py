# NOTE: This examples requires the 'message_content' and 'members' priviliged intents

# This example covers the procedure of creating a simple music bot using relink
# and requires an active Lavalink server, for more information on setting up one
# you can check the guide at: https://relink.readthedocs.io/en/latest/guides/lavalink-setup.html

from typing import Any

import discord
from discord.ext import commands

import relink


# Start by building your clients, in this example we will subclass commands.Bot
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

# Now we will add the nodes we want our client to connect to, we can
# access our relink.Client instance with 'bot.rl_client'.

bot.rl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
)

# We will define some simple play, pause, resume, stop and skip commands.

@bot.command()
async def play(ctx: commands.Context[Bot], *, query: str) -> None:
    """Plays a song."""

    # Here we must check whether we have an active player on the guild
    # if we don't, we will connect to the author voice channel, if available.

    assert isinstance(ctx.author, discord.Member)
    vc = ctx.voice_client

    if vc is None:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("You must be in a voice channel!")
            return

        vc = await ctx.author.voice.channel.connect(cls=relink.Player)

    assert isinstance(vc, relink.Player)

    # Now, we will search 'query' with Lavalink and play the obtained track, if available
    result = await bot.rl_client.search_track(query)

    if result.is_error() or result.is_empty() or result.result is None:
        await ctx.reply("Could not find any tracks!")
        return

    data = result.result

    if isinstance(data, list):
        track = data[0]
    elif isinstance(data, relink.models.Playlist):
        track = data.tracks[0]
    else:
        track = data

    # Add our track to the queue, and play it if there is no current song
    vc.queue.put(track)

    if not vc.current:
        to_play = vc.queue.get()
        await vc.play(to_play)
        await ctx.reply(f"Now playing `{to_play.title}` by `{to_play.artist.name}`!")
    else:
        await ctx.reply(f"Added `{track.title}` by `{track.artist.name}` to the queue!")


@bot.command()
async def pause(ctx: commands.Context[Bot]) -> None:
    """Pauses the current playing song."""

    vc = ctx.voice_client

    if not isinstance(vc, relink.Player):
        await ctx.reply("Not connected to a voice channel!")
        return

    await vc.pause()
    await ctx.reply("Paused!")


@bot.command()
async def resume(ctx: commands.Context[Bot]) -> None:
    """Resumes the current playing song."""

    vc = ctx.voice_client

    if not isinstance(vc, relink.Player):
        await ctx.reply("Not connected to a voice channel!")
        return

    await vc.resume()
    await ctx.reply("Resumed!")


@bot.command()
async def stop(ctx: commands.Context[Bot]) -> None:
    """Stops and disconnects."""

    vc = ctx.voice_client

    if not isinstance(vc, relink.Player):
        await ctx.reply("Already disconnected!")
        return

    await vc.disconnect()
    await ctx.reply("Disconnected!")


@bot.command()
async def skip(ctx: commands.Context[Bot]) -> None:
    """Skips the current song."""

    vc = ctx.voice_client

    if not isinstance(vc, relink.Player):
        await ctx.reply("Not connected to a voice channel!")
        return

    # 'skip' will raise 'QueueEmpty' if there is no track to skip to
    # so we must handle that
    try:
        track = await vc.skip()
    except relink.QueueEmpty:
        await ctx.reply("There is no track to skip to!")
    else:
        if not track:
            await ctx.reply("Skipped!")
            return

        await ctx.reply(f"Skipped to `{track.title}` by `{track.artist.name}`!")


# Now, we can run our bot
if __name__ == "__main__":
    bot.run("TOKEN")
