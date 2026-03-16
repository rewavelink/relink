ReLink Documentation
====================

**ReLink** is a modern, typed, and async-first Lavalink wrapper designed specifically for ``discord.py``.

Core Building Blocks
--------------------
To keep things simple, ReLink is built around three primary components:

* :class:`relink.Client` manages Lavalink nodes for your Discord client.
* :class:`relink.Node` handles a single Lavalink connection and all REST operations.
* :class:`relink.Player` integrates with Discord voice and controls playback.

Features at a Glance
--------------------

* Lavalink v4+, giving you access to the latest stability fixes and features.
* Native ``discord.py`` Voice Protocol support. 
* Customizable history, autoplay, and queue for better experience.
* Full control over audio, from volume to complex audio filters.
* Optional ``curl_cffi`` and ``orjson`` support for extra-speed.

Getting Started
---------------

.. toctree::
   :maxdepth: 1

   installation
   quickstart
   concepts
   api/index
   guides/migrating-from-wavelink
   
License
-------
ReLink is made available under the `MIT License <https://github.com/rewavelink/relink/blob/main/LICENSE>`_.

Resources
---------

* `GitHub repository <https://github.com/rewavelink/relink>`_
* `PyPI package <https://pypi.org/project/rewavelink/>`_
* `Discord Community <https://discord.gg/tPHVWBPedt>`_
