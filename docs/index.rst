ReLink Documentation
====================

**ReLink** is a Lavalink wrapper for ``discord.py`` with a typed, async-first API.
The library is organized around three public building blocks:

* :class:`relink.Client` manages Lavalink nodes for your Discord client.
* :class:`relink.Node` handles one Lavalink connection plus REST operations.
* :class:`relink.Player` integrates with Discord voice and controls playback.

What you can do with ReLink
---------------------------

* Connect to one or more Lavalink v4+ nodes.
* Search tracks and playlists through Lavalink.
* Join voice channels using a native ``discord.py`` voice protocol.
* Manage queues, history, volume, filters, and autoplay settings.
* Use optional ``curl_cffi`` networking for faster HTTP and websocket handling.

Start here
----------

.. toctree::
   :maxdepth: 2

   overview
   installation
   quickstart
   concepts
   guides/index
   api/index

Project links
-------------

* `GitHub repository <https://github.com/rewavelink/relink>`_
* `PyPI package <https://pypi.org/project/relink/>`_
