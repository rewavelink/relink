.. currentmodule:: sonolink

Installation
============

Requirements
------------

* Python 3.12+
* One of: `discord.py 2.7+ <https://github.com/Rapptz/discord.py>`_,
  `py-cord 2.8+ <https://github.com/Pycord-Development/pycord>`_, or
  `disnake 2.12+ <https://github.com/DisnakeDev/disnake>`_
* A running Lavalink 4.x server — see :doc:`/guides/lavalink-setup`

Installing SonoLink
-----------------

Base install:

.. code-block:: bash

   pip install sonolink

With optional speed extras:

.. code-block:: bash

   pip install "sonolink[speed]"

The ``speed`` extra installs ``curl_cffi``. SonoLink will prefer it
automatically when available.
