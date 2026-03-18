.. currentmodule:: relink

ReLink Documentation
====================

ReLink is a maintained Lavalink client library for ``discord.py``, providing a high-level
voice player API while still exposing the underlying node, model, REST, and gateway
primitives when you need them.

It is designed for bot authors who want a practical, queue-first player interface out of
the box, without losing access to the runtime types and protocol details needed for
debugging, customisation, or more advanced workflows.

.. note::

   ReLink targets **Lavalink 4.x**. See :doc:`/guides/lavalink-setup` for instructions on
   setting up and self-hosting a Lavalink server.

Getting Started
---------------

.. toctree::
   :maxdepth: 1

   installation
   guides/index
   concepts
   api/index

Who should read what
--------------------

* **New users** — start with :doc:`installation`, then work through :doc:`guides/index`.
* **Bot authors** — read :doc:`concepts` alongside the guide pages for a fuller picture.
* **Advanced users** — jump straight to :doc:`api/index` and refer to the guides as needed.

Typical flow
------------

1. Create a :class:`relink.Client` attached to your ``discord.Client`` or ``commands.Bot``.
2. Register one or more Lavalink nodes with :meth:`relink.Client.create_node`.
3. Start the ReLink client once your Discord client is ready.
4. Connect to a voice channel using :class:`relink.Player`.
5. Search for tracks, populate the queue, and begin playback.

Core pieces
-----------

The public API is easiest to understand from the outside in:

* :class:`relink.Client` — attached to your ``discord.py`` client; owns all nodes and
  acts as the main entry point.
* :class:`relink.Node` — represents a single Lavalink server connection.
* :class:`relink.Player` — the Discord voice protocol implementation used per guild.
* :doc:`relink.models <api/models>` — user-facing objects including tracks, playlists,
  search results, and settings.

License
-------

ReLink is released under the `MIT License <https://github.com/rewavelink/relink/blob/main/LICENSE>`_.

Resources
---------

* `GitHub repository <https://github.com/rewavelink/relink>`_
* `PyPI package <https://pypi.org/project/rewavelink/>`_
* `Discord community <https://discord.gg/tPHVWBPedt>`_

Credits
-------

* `PythonistaGuild & EvieePy <https://github.com/PythonistaGuild>`_ for the original
  `Wavelink <https://github.com/PythonistaGuild/Wavelink>`_ library that ReLink builds upon.
* `Paillat-dev <https://github.com/Paillat-dev>`_ for the
  `content width selector <https://github.com/Pycord-Development/pycord/pull/3040>`_.
* `Rapptz <https://github.com/Rapptz>`_ for the original
  `attributetable Sphinx extension <https://github.com/Rapptz/discord.py/blob/5d74ed3e0ce5178cf454825bd5a71f0248738f54/docs/extensions/attributetable.py>`_.
