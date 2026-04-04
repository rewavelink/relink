# This example covers how to configure relink's settings objects and wire them
# into your bot. Settings are split into two groups:
#
# - Node-level: CacheSettings, InactivitySettings (shared across all players)
# - Player-level: AutoPlaySettings, HistorySettings (unique per player)

from typing import Any

import disnake
from disnake.ext import commands

import relink
import relink.models
from relink.gateway.enums import AutoPlayMode, InactivityMode, QueueMode, SearchProvider
from relink.models.settings import (
    AutoPlaySettings,
    CacheSettings,
    HistorySettings,
    InactivitySettings,
)


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


bot = Bot()

# CacheSettings and InactivitySettings apply to every player on the node.
bot.rl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
    cache_settings=CacheSettings(
        enabled=True,
        max_items=500,
    ),
    inactivity_settings=InactivitySettings(
        timeout=300,
        mode=InactivityMode.ALL_BOTS,
        # mode=InactivityMode.ONLY_SELF,
        # mode=InactivityMode.IGNORED_USERS,
        # user_ids=[disnake.Object(id=YOUR_USER_ID)],  # required for IGNORED_USERS
    ),
)


@bot.slash_command(name="play", description="Plays a song.")
async def play(
    inter: disnake.ApplicationCommandInteraction[Bot],
    query: str = commands.Param(description="The song name or URL to search for."),  # pyright: ignore[reportUnknownMemberType]
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

        # AutoPlaySettings and HistorySettings are per-player, so they are
        # passed when creating the player via Node.create_player().
        node = bot.rl_client.get_best_node()
        player = node.create_player(
            queue_mode=QueueMode.NORMAL,
            autoplay_settings=AutoPlaySettings(
                mode=AutoPlayMode.ENABLED,
                # mode=AutoPlayMode.PARTIAL,
                # mode=AutoPlayMode.DISABLED,
                provider=SearchProvider.YOUTUBE,
                # provider=SearchProvider.SPOTIFY,
                # provider=SearchProvider.DEEZER,
                max_seeds=100,
                discovery_count=10,
            ),
            history_settings=HistorySettings(
                enabled=True,
                max_items=50,
            ),
        )

        vc = await inter.author.voice.channel.connect(cls=player)

    assert isinstance(vc, relink.Player)

    result = await bot.rl_client.search_track(query)

    if result.is_error() or result.is_empty() or result.result is None:
        await inter.followup.send("Could not find any tracks!")
        return

    data = result.result
    track = (
        data[0]
        if isinstance(data, list)
        else (data.tracks[0] if isinstance(data, relink.models.Playlist) else data)
    )

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


# AutoPlay mode can also be changed on an existing player at any time.
# Note: this raises RuntimeError if history is disabled on the player.
@bot.slash_command(name="autoplay", description="Toggles AutoPlay on or off.")
async def autoplay(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    vc = inter.guild.voice_client if inter.guild else None

    if not isinstance(vc, relink.Player):
        await inter.response.send_message("Not connected to a voice channel!")
        return

    if vc.autoplay is AutoPlayMode.DISABLED:
        vc.autoplay = AutoPlayMode.ENABLED
        await inter.response.send_message("AutoPlay enabled!")
    else:
        vc.autoplay = AutoPlayMode.DISABLED
        await inter.response.send_message("AutoPlay disabled!")


# Now, we can run our bot
if __name__ == "__main__":
    bot.run("TOKEN")
