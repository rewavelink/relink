.. currentmodule:: relink

Working With Players
====================


Connecting a player
-------------------

Use :class:`relink.Player` as the ``cls`` argument when connecting to a Discord voice channel:

.. code-block:: python

   player = await voice_channel.connect(cls=relink.Player)

When the player is created this way, it finds the attached :class:`relink.Client`,
selects the best connected node, and completes the Discord voice handshake.

Players can also be created using :meth:`relink.Node.create_player`, this allows you
to add extra configuration parameters for your player before connecting it to Discord, and can
still be passed to the ``cls`` argument on :meth:`discord.abc.Connectable.connect`.

.. code-block:: python

   player = node.create_player(
      volume=100,
      filters=relink.rest.schemas.PlayerFilter(
         karaoke=relink.rest.schemas.KaraokeFilter(
            level=0.5,
         )
      )
   )

   await voice_channel.connect(cls=player)

Reusing an existing player
--------------------------

In command handlers, ``ctx.voice_client`` is usually the active player:

.. code-block:: python

   player = ctx.voice_client
   if not isinstance(player, relink.Player):
       player = await ctx.author.voice.channel.connect(cls=relink.Player)

Playback controls
-----------------

The main player methods are:

* :meth:`relink.Player.play`
* :meth:`relink.Player.stop`
* :meth:`relink.Player.pause`
* :meth:`relink.Player.resume`
* :meth:`relink.Player.skip`
* :meth:`relink.Player.previous`
* :meth:`relink.Player.seek`
* :meth:`relink.Player.set_volume`
* :meth:`relink.Player.set_filters`

Moving between nodes
--------------------

If you run multiple Lavalink nodes, you can migrate a player with:

.. code-block:: python

   await player.move_to(other_node)

This is useful for draining a node or reacting to operational issues.

Disconnecting cleanly
---------------------

Use :meth:`relink.Player.disconnect` instead of only disconnecting the Discord voice client.
That ensures the Lavalink-side player is destroyed and internal state is cleaned up. This is
as simple as doing:

.. code-block:: python

   vc = ctx.voice_client
   await vc.disconnect()
