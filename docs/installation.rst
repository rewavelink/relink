Installation
============

Requirements
------------

ReLink currently targets:

* Python 3.12+
* discord.py 2.6+
* Lavalink v4+

Install the package
-------------------

Install the base package:

.. code-block:: bash

   pip install rewavelink

Install with the optional speed extras:

.. code-block:: bash

   pip install "rewavelink[speed]"

The ``speed`` extra adds ``curl_cffi`` and ``orjson``. ReLink will prefer
``curl_cffi`` automatically when it is available.

Lavalink checklist
------------------

Before writing bot code, make sure you have:

* A running Lavalink v4+ server.
* The node URI, for example ``http://localhost:2333``.
* The node password configured in Lavalink.

What ReLink does not provide
----------------------------

ReLink is a Python client library. It does not start or manage the Lavalink server for you.
