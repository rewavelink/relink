.. currentmodule:: relink

Installation
============

Requirements
------------

* Python 3.12+
* discord.py 2.6+
* A running Lavalink 4.x server — see :doc:`/guides/lavalink-setup`

Installing ReLink
-----------------

Base install:

.. code-block:: bash

   pip install rewavelink

With optional speed extras:

.. code-block:: bash

   pip install "rewavelink[speed]"

The ``speed`` extra pulls in ``curl_cffi`` and ``orjson``. ReLink will prefer both
automatically when they are available.
