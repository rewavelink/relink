.. currentmodule:: relink

ReLink Documentation
====================

ReLink is a maintained Lavalink client library for ``discord.py``. It gives you a
high-level voice player API while still exposing the lower-level node, model, REST,
and gateway pieces when you need them.

It is designed for bot authors who want a practical player interface first, while still
having access to the runtime types and protocol details when they need to debug,
customize, or build more advanced workflows.

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

* New users should start with :doc:`installation` and :doc:`guides/index`.
* Bot authors should then read :doc:`concepts` alongside the guide pages.
* Advanced users can jump straight to :doc:`api/index`.

Typical flow
------------

1. Create a :class:`relink.Client` after you have a ``discord.Client`` or ``commands.Bot``.
2. Register one or more nodes with :meth:`relink.Client.create_node`.
3. Start the ReLink client once your Discord client is ready.
4. Join a voice channel with :class:`relink.Player`.
5. Search for tracks, add them to the queue, and start playback.

Core pieces
-----------

The public API is easiest to understand from the outside in:

* :class:`relink.Client` is attached to your ``discord.py`` client and owns your nodes.
* :class:`relink.Node` represents a single Lavalink server connection.
* :class:`relink.Player` is the Discord voice protocol implementation used inside a guild.
* :doc:`relink.models <api/models>` contains user-facing objects such as tracks, playlists, search
  results, and settings.

License
-------

ReLink is made available under the `MIT License <https://github.com/rewavelink/relink/blob/main/LICENSE>`_.

Resources
---------

* `GitHub repository <https://github.com/rewavelink/relink>`_
* `PyPI package <https://pypi.org/project/rewavelink/>`_
* `Discord Community <https://discord.gg/tPHVWBPedt>`_

Credits
-------
* `PythonistaGuild & EvieePy <https://github.com/PythonistaGuild>`_ for the original `Wavelink library <https://github.com/PythonistaGuild/Wavelink>`_.
* `Paillat-dev <https://github.com/Paillat-dev>`_ for the 
  `content width selector. <https://github.com/Pycord-Development/pycord/pull/3040>`_.
* `Rapptz <https://github.com/Rapptz>`_ for the original
  `attributetable Sphinx extension <https://github.com/Rapptz/discord.py/blob/5d74ed3e0ce5178cf454825bd5a71f0248738f54/docs/extensions/attributetable.py>`_.
