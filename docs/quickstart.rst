Quickstart
==========

This page shows the shortest practical setup for a bot using one node and one player.

Minimal example
---------------

.. code-block:: python

   import discord
   from discord.ext import commands

   import relink


   bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
   rl_client = relink.Client(bot)

   rl_client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       id="main",
   )


   @bot.event
   async def on_ready() -> None:
       await rl_client.start()


   @bot.command()
   async def play(ctx: commands.Context[commands.Bot], *, query: str) -> None:
       if ctx.author.voice is None or ctx.author.voice.channel is None:
           await ctx.send("Join a voice channel first.")
           return

       if ctx.voice_client is None:
           player = await ctx.author.voice.channel.connect(cls=relink.Player)
       else:
           player = ctx.voice_client

       result = await rl_client.search_track(query)
       if result.is_error() or result.is_empty() or result.result is None:
           await ctx.send("No tracks found.")
           return

       data = result.result
       if isinstance(data, list):
           track = data[0]
       else:
           track = data.tracks[0] if hasattr(data, "tracks") else data

       player.queue.put(track)

       if player.current is None:
           await player.play(player.queue.get())

       await ctx.send(f"Queued: {track.title}")


   bot.run("TOKEN")

What this example covers
------------------------

* ``relink.Client`` is attached to the bot.
* A Lavalink node is registered with :meth:`relink.Client.create_node`.
* :meth:`relink.Client.start` connects the node when Discord is ready.
* ``voice_channel.connect(cls=relink.Player)`` creates a ReLink player.
* :meth:`relink.Client.search_track` returns a :class:`relink.models.SearchResult`.
* The chosen track is put into the queue and played.

Recommended next reads
----------------------

* :doc:`concepts`
* :doc:`guides/players`
* :doc:`guides/queue`
