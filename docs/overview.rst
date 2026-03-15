Overview
========

ReLink is a maintained Lavalink client library for ``discord.py``. It gives you a
high-level voice player API while still exposing the lower-level node, model, REST,
and gateway pieces when you need them.

Architecture
------------

The public API is easiest to understand from the outside in:

* :class:`relink.Client` is attached to your ``discord.py`` client and owns your nodes.
* :class:`relink.Node` represents a single Lavalink server connection.
* :class:`relink.Player` is the Discord voice protocol implementation used inside a guild.
* :doc:`relink.models <api/models>` contains user-facing objects such as tracks, playlists, search
  results, and settings.

Typical flow
------------

1. Create a :class:`relink.Client` after you have a ``discord.Client`` or ``commands.Bot``.
2. Register one or more nodes with :meth:`relink.Client.create_node`.
3. Start the ReLink client once your Discord client is ready.
4. Join a voice channel with :class:`relink.Player`.
5. Search for tracks, add them to the queue, and start playback.

Who should read what
--------------------

* New users should read :doc:`installation` and :doc:`quickstart` first.
* Users building a bot should then read :doc:`concepts` and the guide pages.
* Advanced users can jump straight to :doc:`api/index`.
