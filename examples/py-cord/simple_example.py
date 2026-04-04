# This example covers the procedure of creating a simple music bot using relink
# and requires an active Lavalink server, for more information on setting up one
# you can check the guide at: https://relink.readthedocs.io/en/latest/guides/lavalink-setup.html
# 
# This examples requires installing "py-cord[voice]", please make sure you've installed it!

from typing import Annotated, Any

import discord
import relink


# We subclass discord.Bot to hold our relink.Client instance cleanly.
# This avoids relying on globals and makes the client easy to access anywhere.
class Bot(discord.Bot):
    def __init__(self) -> None:
        super().__init__()

        self.rl_client: relink.Client[Any] = relink.Client(self, framework="pycord")
        self.ready_ran: bool = False

    async def on_ready(self) -> None:
        if self.ready_ran:
            return

        self.ready_ran = True
        await self.rl_client.start()
        print("ReLink nodes connected successfully!")


bot = Bot()

# Register the node we want to connect to. You can register multiple nodes
# and relink will automatically load-balance between them via 'get_best_node'.
bot.rl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
)


# Here we will define some simple play, pause, resume, stop and skip commands.

@bot.slash_command(name="play", description="Plays a song.")
async def play(
    ctx: discord.ApplicationContext,
    query: Annotated[str, discord.Option(str, description="The song name or URL to search for.")],
) -> None:
    # we should defer because this command's logic may take longer than 3 seconds
    await ctx.defer()

    # Here we must check whether we have an active player on the guild
    # if we don't, we will connect to the author voice channel, if available

    assert isinstance(ctx.user, discord.Member)
    vc = ctx.voice_client

    if vc is None:
        if not ctx.user.voice or not ctx.user.voice.channel:
            await ctx.respond("You must be in a voice channel!")
            return

        vc = await ctx.user.voice.channel.connect(cls=relink.Player)

    assert isinstance(vc, relink.Player)

    # Now, we will search 'query' with Lavalink and play the obtained track, if available
    result = await bot.rl_client.search_track(query)

    if result.is_error() or result.is_empty() or result.result is None:
        await ctx.respond("Could not find any tracks!")
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
        await ctx.respond(
            f"Now playing `{to_play.title}` by `{to_play.author}`"
        )
    else:
        await ctx.respond(
            f"Added `{track.title}` by `{track.author}` to the queue!"
        )


@bot.slash_command(name="pause", description="Pauses the current playing song.")
async def pause(ctx: discord.ApplicationContext) -> None:
    vc: relink.Player | None = ctx.voice_client  # pyright: ignore[reportAssignmentType]

    if not isinstance(vc, relink.Player):
        await ctx.respond("Not connected to a voice channel!")
        return

    await vc.pause()
    await ctx.respond("Paused!")


@bot.slash_command(name="resume", description="Resumes the current playing song.")
async def resume(ctx: discord.ApplicationContext) -> None:
    vc: relink.Player | None = ctx.voice_client  # pyright: ignore[reportAssignmentType]

    if not isinstance(vc, relink.Player):
        await ctx.respond("Not connected to a voice channel!")
        return

    await vc.resume()
    await ctx.respond("Resumed!")


@bot.slash_command(name="stop", description="Stops playback and disconnects the bot.")
async def stop(ctx: discord.ApplicationContext) -> None:
    vc: relink.Player | None = ctx.voice_client  # pyright: ignore[reportAssignmentType]

    if not isinstance(vc, relink.Player):
        await ctx.respond("Already disconnected!")
        return

    await vc.disconnect()
    await ctx.respond("Disconnected!")


@bot.slash_command(name="skip", description="Skips the current song.")
async def skip(ctx: discord.ApplicationContext) -> None:
    vc: relink.Player | None = ctx.voice_client  # pyright: ignore[reportAssignmentType]

    if not isinstance(vc, relink.Player):
        await ctx.respond("Not connected to a voice channel!")
        return

    # 'skip' will raise 'QueueEmpty' if there are no tracks in queue
    try:
        track = await vc.skip()
    except relink.QueueEmpty:
        await ctx.respond("There is no track to skip to!")
    else:
        if not track:
            await ctx.respond("Skipped!")
            return

        await ctx.respond(
            f"Skipped to `{track.title}` by `{track.author}`"
        )


# Now, we can run our bot
if __name__ == "__main__":
    bot.run("TOKEN")
