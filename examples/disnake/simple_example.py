# This example covers the procedure of creating a simple music bot using relink
# and requires an active Lavalink server, for more information on setting up one
# you can check the guide at: https://relink.readthedocs.io/en/latest/guides/lavalink-setup.html

from typing import Any

import disnake
from disnake.ext import commands

import relink


# We subclass commands.InteractionBot to hold our relink.Client instance cleanly.
# This avoids relying on globals and makes the client easy to access anywhere.
class Bot(commands.InteractionBot):
    def __init__(self) -> None:
        intents = disnake.Intents(guilds=True, voice_states=True)

        super().__init__(intents=intents)

        self.rl_client: relink.Client[Any] = relink.Client(self)

    async def on_ready(self) -> None:
        # disnake fires 'on_ready' once the bot is connected and ready.
        # We start the relink client here since setup_hook is not available.
        await self.rl_client.start()
        print("ReLink nodes connected successfully!")
        print("Slash commands are registered automatically by disnake!")


bot = Bot()

# Register the node we want to connect to. You can register multiple nodes
# and relink will automatically load-balance between them via 'get_best_node'.
bot.rl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
)

# We will define some simple play, pause, resume, stop and skip commands.


@bot.slash_command(name="play", description="Plays a song.")
async def play(
    inter: disnake.ApplicationCommandInteraction[Bot],
    query: str = commands.Param(  # pyright: ignore[reportUnknownMemberType]
        description="The song name or URL to search for.",
    ),
) -> None:
    await inter.response.defer()

    # Ensure we are in a guild and the author is a Member to resolve 'voice' type
    if not inter.guild or not isinstance(inter.author, disnake.Member):
        await inter.followup.send("This command must be used in a server!")
        return

    vc = inter.guild.voice_client

    if vc is None:
        if not inter.author.voice or not inter.author.voice.channel:
            await inter.followup.send("You must be in a voice channel!")
            return

        vc = await inter.author.voice.channel.connect(cls=relink.Player)

    assert isinstance(vc, relink.Player)

    # Now, we will search 'query' with Lavalink and play the obtained track, if available
    result = await bot.rl_client.search_track(query)

    if result.is_error() or result.is_empty() or result.result is None:
        await inter.followup.send("Could not find any tracks!")
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
        await inter.followup.send(
            f"Now playing `{to_play.title}` by `{to_play.author}`!"
        )
    else:
        await inter.followup.send(
            f"Added `{track.title}` by `{track.author}` to the queue!"
        )


@bot.slash_command(name="pause", description="Pauses the current playing song.")
async def pause(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    vc = inter.guild.voice_client if inter.guild else None

    if not isinstance(vc, relink.Player):
        await inter.response.send_message("Not connected to a voice channel!")
        return

    await vc.pause()
    await inter.response.send_message("Paused!")


@bot.slash_command(name="resume", description="Resumes the current playing song.")
async def resume(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    vc = inter.guild.voice_client if inter.guild else None

    if not isinstance(vc, relink.Player):
        await inter.response.send_message("Not connected to a voice channel!")
        return

    await vc.resume()
    await inter.response.send_message("Resumed!")


@bot.slash_command(name="stop", description="Stops playback and disconnects the bot.")
async def stop(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    vc = inter.guild.voice_client if inter.guild else None

    if not isinstance(vc, relink.Player):
        await inter.response.send_message("Already disconnected!")
        return

    await vc.disconnect()
    await inter.response.send_message("Disconnected!")


@bot.slash_command(name="skip", description="Skips the current song.")
async def skip(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    vc = inter.guild.voice_client if inter.guild else None

    if not isinstance(vc, relink.Player):
        await inter.response.send_message("Not connected to a voice channel!")
        return

    # 'skip' will raise 'QueueEmpty' if there are no tracks in queue
    try:
        track = await vc.skip()
    except relink.QueueEmpty:
        await inter.response.send_message("There is no track to skip to!")
    else:
        if not track:
            await inter.response.send_message("Skipped!")
            return

        await inter.response.send_message(
            f"Skipped to `{track.title}` by `{track.author}`!"
        )


# Now, we can run our bot
if __name__ == "__main__":
    bot.run("TOKEN")
