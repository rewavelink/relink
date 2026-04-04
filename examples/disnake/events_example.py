# This example covers the procedure of creating a simple music bot using relink,
# with event handlers for track lifecycle and node events.
# It requires an active Lavalink server, for more information on setting up one
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

    async def on_connect(self) -> None:
        # disnake fires 'on_ready' once the bot is connected and ready.
        # We start the relink client here since setup_hook is not available.
        await self.rl_client.start()
        print("ReLink nodes connected successfully!")


bot = Bot()

# Register the node we want to connect to. You can register multiple nodes
# and relink will automatically load-balance between them via 'get_best_node'.
bot.rl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
)


# Fired when a node has successfully connected and is ready to accept players.
# 'event.resumed' tells us whether this was a fresh connection or a resume.
@bot.listen()
async def on_relink_node_ready(event: relink.gateway.ReadyEvent) -> None:
    print(f"Node {event.node.id!r} is ready! (resumed={event.resumed})")


# Fired when a node connection is lost or manually closed.
@bot.listen()
async def on_relink_node_close(node: relink.Node) -> None:
    print(f"Node {node.id!r} closed.")


# Fired each time Lavalink sends a position/state update for a player.
# This happens frequently (roughly every 5 seconds by default).
@bot.listen()
async def on_relink_player_update(
    player: relink.Player, event: relink.gateway.PlayerUpdateEvent
) -> None:
    # This event fires very often; avoid heavy work here.
    pass


# Fired when a track begins playing.
@bot.listen()
async def on_relink_track_start(
    player: relink.Player, event: relink.gateway.TrackStartEvent
) -> None:
    print(f"[{player.guild}] Started: {event.track.title!r} by {event.track.author!r}")


# Fired when a track finishes, is skipped, or is replaced.
# 'event.reason' is a TrackEndReason enum describing why it ended.
# NOTE: relink automatically calls 'player.skip()' internally when the reason
# allows starting the next track, so you do not need to advance the queue here.
@bot.listen()
async def on_relink_track_end(
    player: relink.Player, event: relink.gateway.TrackEndEvent
) -> None:
    print(f"[{player.guild}] Ended: {event.track.title!r} (reason={event.reason})")


# Fired when Lavalink encounters an error while playing a track.
# 'event.exception.message' contains the error description from Lavalink.
@bot.listen()
async def on_relink_track_exception(
    player: relink.Player, event: relink.gateway.TrackExceptionEvent
) -> None:
    print(
        f"[{player.guild}] Exception on {event.track.title!r}: "
        f"{event.exception.message}"
    )


# Fired when a track gets stuck and stops progressing.
# 'event.threshold' is the number of milliseconds Lavalink waited before giving up.
@bot.listen()
async def on_relink_track_stuck(
    player: relink.Player, event: relink.gateway.TrackStuckEvent
) -> None:
    print(
        f"[{player.guild}] Track {event.track.title!r} got stuck "
        f"after {event.threshold}ms."
    )


# Now, we can run our bot.
if __name__ == "__main__":
    bot.run("TOKEN")
