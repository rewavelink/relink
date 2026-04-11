.. currentmodule:: sonolink

Working With Players
====================


Connecting a player
-------------------

For most bots, the simplest way to create a player is to pass :class:`sonolink.Player`
to your Discord client when connecting to a voice channel:

.. code-block:: python

   player = await voice_channel.connect(cls=sonolink.Player)

When you connect this way, the player will:

* use the :class:`sonolink.Client` attached to your Discord client,
* choose the best available connected node,
* complete the Discord voice handshake for you.

This is usually the easiest place to start because it keeps player creation
short and predictable.

If you need to configure the player before connecting, create it first, either by using an
instance or by using :meth:`sonolink.Node.create_player`, and then pass the configured instance
as ``cls`` to :meth:`discord:discord.abc.Connectable.connect` (discord.py),
:meth:`pycord:discord.VoiceChannel.connect` (py-cord), or
:meth:`disnake:disnake.VoiceChannel.connect`.

.. code-block:: python

   from sonolink.models import Karaoke, Filters

   player = sonolink.Player(
      node=node,
      volume=100,
      filters=Filters(
         karaoke=Karaoke(level=0.5),
      ),
   )

   # or

   player = node.create_player(
      volume=100,
      filters=Filters(
         karaoke=Karaoke(level=0.5),
      ),
   )

   await voice_channel.connect(cls=player)

Reusing an existing player
--------------------------

In command handlers, the active voice connection is available via ``ctx.voice_client`` —
see :attr:`discord:discord.ext.commands.Context.voice_client` (discord.py),
:attr:`pycord:discord.ext.commands.Context.voice_client` (py-cord), or
:attr:`disnake:disnake.ext.commands.Context.voice_client` (disnake).

.. code-block:: python

   player = ctx.voice_client
   if not isinstance(player, sonolink.Player):
       player = await ctx.author.voice.channel.connect(cls=sonolink.Player)

Subclassing a player
--------------------

If you need to extend or override player behaviour, subclass :class:`sonolink.Player` directly.
The framework adapter is injected automatically at class-creation time, so your subclass
works as a drop-in replacement anywhere :class:`sonolink.Player` is accepted.

.. code-block:: python

   class MyPlayer(sonolink.Player):
       async def stop(
           self,
           /,
           *,
           clear_queue: bool = False,
           clear_history: bool = False,
       ) -> None:
           print("Method stop is overridden.")
           await super().stop(clear_queue=clear_queue, clear_history=clear_history)

Pass your subclass the same way you would pass :class:`sonolink.Player`:

.. code-block:: python

   player = await voice_channel.connect(cls=MyPlayer)

.. warning::

   Your subclass must be defined **after** constructing :class:`sonolink.Client`, otherwise
   the framework adapter may not be resolved correctly. Alternatively, set the
   ``RELINK_FRAMEWORK`` environment variable before any imports to force a specific
   framework ahead of time.

Playback controls
-----------------

The main playback methods on :class:`sonolink.Player` are:

* :meth:`sonolink.Player.play`
* :meth:`sonolink.Player.stop`
* :meth:`sonolink.Player.pause`
* :meth:`sonolink.Player.resume`
* :meth:`sonolink.Player.skip`
* :meth:`sonolink.Player.previous`
* :meth:`sonolink.Player.seek`
* :meth:`sonolink.Player.set_volume`
* :meth:`sonolink.Player.set_filters`

All of these methods act on the current player attached to a guild. In practice,
that means they are the methods you will call from command handlers, button
callbacks, or playback services.

:meth:`sonolink.Player.play`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`sonolink.Player.play` to start a specific track right away.

.. code-block:: python

   track = result.result[0]
   await player.play(track)

``play`` starts the track you pass to it immediately. It does not automatically
pick the next track from the queue for you.

It is the direct "play this now" call, and it also accepts optional keyword
arguments such as ``start``, ``end``, ``volume``, and ``paused`` when you need
more control over playback.

:meth:`sonolink.Player.stop`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`sonolink.Player.stop` to end the current track and clear the active
playback state.

.. code-block:: python

   await player.stop()

This is useful when you want playback to end without immediately starting another track.
By default, this stops the current track but leaves the queue and history intact.

If you want a more complete reset, you can also clear queued and historical tracks:

.. code-block:: python

   await player.stop(clear_queue=True, clear_history=True)

This is a good fit for commands such as ``stop``, ``leave``, ``clear``, or admin-side
"reset player" actions.

:meth:`sonolink.Player.pause` and :meth:`sonolink.Player.resume`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`sonolink.Player.pause` to pause playback and
:meth:`sonolink.Player.resume` to continue it later.

.. code-block:: python

   await player.pause()
   await player.resume()

These methods simply change the state of the current track. The paused state is
also available through :attr:`sonolink.Player.paused` if you want to show playback
status in an embed or avoid repeating a pause or resume action.

If it fits your control flow better, ``await player.pause(False)`` is equivalent
to calling ``resume()``.

:meth:`sonolink.Player.skip`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`sonolink.Player.skip` to move forward to the next track.

.. code-block:: python

   next_track = await player.skip()

``skip`` is queue-aware:

* if there is another track in the queue, it starts that track,
* if autoplay is enabled, autoplay may provide the next track,
* if neither applies, playback stops.

This makes it a better choice than manually calling ``stop()`` when your intent is
"go to whatever should play next".

:meth:`sonolink.Player.previous`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`sonolink.Player.previous` to return to the most recent track in history.

.. code-block:: python

   previous_track = await player.previous()

This is meant to behave like a real "back" button, not just replay the current
song. When possible, it pulls the last track from history, pushes the current
track back to the front of the queue, and starts the previous track.

That means ``previous`` depends on queue history being available. If there is no playback
history yet, it will fail rather than guessing what "previous" should mean.

:meth:`sonolink.Player.seek`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`sonolink.Player.seek` to jump to a specific position in the current track.
The position is expressed in milliseconds.

.. code-block:: python

   await player.seek(60_000)  # 1 minute

``seek`` also matters outside dedicated seek commands, because some Lavalink
behavior, especially filter application, may only become audible after playback
position changes.

:meth:`sonolink.Player.set_volume`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`sonolink.Player.set_volume` to change the player's output volume.

.. code-block:: python

   await player.set_volume(75)

SonoLink volume values use the Lavalink range of ``0`` to ``1000``:

* ``100`` is the normal default volume,
* values below ``100`` reduce volume,
* values above ``100`` amplify audio and may sound harsh or clip at higher levels.

:meth:`sonolink.Player.set_filters`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`sonolink.Player.set_filters` to apply Lavalink filters such as karaoke,
timescale, equalizer, tremolo, or rotation.

.. code-block:: python

   from sonolink.models import Filters, Timescale

   filters = Filters(timescale=Timescale(speed=1.1))
   await player.set_filters(filters, seek=True)

Filters are grouped into a single :class:`sonolink.models.Filters` object and then
applied in one call.

The ``seek=True`` part is often important. Some filters are not immediately
audible until playback position changes, so seeking to the current position
makes the effect audible right away.

For more information on filters, see :doc:`/guides/filters`.

Playing tracks
--------------

A common playback flow is:

1. search for a track,
2. add it to the queue,
3. start playback only if nothing is currently playing.

.. code-block:: python

   result = await sl_client.search_track("never gonna give you up")
   if result.is_error() or result.is_empty() or result.result is None:
       return

   data = result.result
   rest = []

   if isinstance(data, list):
       play_track = data[0]
   elif isinstance(data, sonolink.models.Playlist):
       play_track = data.tracks[0]
       rest = data.tracks[1:]
   else:
       play_track = data

   if not player.current:
       await player.play(play_track)
   else:
       rest = [play_track, *rest]

   for track in rest:
       await player.queue.put_wait(track)

Moving between nodes
--------------------

If you run multiple Lavalink nodes, you can migrate a player with:

.. code-block:: python

   await player.move_to(other_node)

This is mainly useful for operational workflows such as:

* draining a busy or unhealthy node,
* moving guilds away from a node before maintenance,
* redistributing load across multiple Lavalink instances.

You probably will not need this in day-to-day command logic, but it becomes
very useful in larger bots and multi-node deployments.

Disconnecting cleanly
---------------------

Use :meth:`sonolink.Player.disconnect` instead of only disconnecting the Discord voice client.
This ensures the Lavalink-side player is destroyed and SonoLink can clean up its internal state
for that guild.

In practice, this is as simple as:

.. code-block:: python

   vc = ctx.voice_client
   await vc.disconnect()

If ``vc`` is a :class:`sonolink.Player`, this will call the player implementation and perform
the full cleanup. This is the recommended way to handle leave or disconnect commands.
