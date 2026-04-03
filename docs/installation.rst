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

The ``speed`` extra installs ``curl_cffi``. ReLink will use it automatically
when available.
