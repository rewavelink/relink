.. currentmodule:: sonolink

Lavalink Setup
==============

This guide covers how to download, configure, and run a Lavalink server on your own
infrastructure. Lavalink is the audio backend that SonoLink (and Wavelink) connect to. You
manage it as a separate process from your bot.

What Lavalink is
----------------

Lavalink is a standalone Java audio-streaming server that your bot connects to over a local or
remote WebSocket. It handles decoding, buffering, and source routing so your bot process does not
need to. It exposes a REST and WebSocket API that client libraries such as SonoLink speak to
directly.

* `Lavalink GitHub repository <https://github.com/lavalink-devs/Lavalink>`_
* `Lavalink documentation <https://lavalink.dev/>`_
* `Lavalink releases <https://github.com/lavalink-devs/Lavalink/releases>`_

Prerequisites
-------------

Lavalink requires Java 17 or newer. You can check your installed Java version with:

.. code-block:: bash

   java -version

If you need to install or update Java, the recommended distributions are:

* `Eclipse Temurin (Adoptium) <https://adoptium.net/temurin/releases/>`_ — the most widely used
  open build; packages available for Linux, macOS, and Windows.
* `Amazon Corretto <https://aws.amazon.com/corretto/>`_ — AWS-maintained OpenJDK builds with
  long-term support.
* `Microsoft Build of OpenJDK <https://www.microsoft.com/openjdk>`_ — a good choice for
  Windows Server or Azure-hosted machines.

Downloading Lavalink
--------------------

Grab the latest ``Lavalink.jar`` from the GitHub releases page:

https://github.com/lavalink-devs/Lavalink/releases/latest

Download the file named ``Lavalink.jar`` from the assets section. You do not need the source
archives.

You can also obtain this file using the command line on your preferred OS:

.. code-block:: bash

   # Linux / macOS
   curl -L -o Lavalink.jar \
       https://github.com/lavalink-devs/Lavalink/releases/latest/download/Lavalink.jar

.. code-block:: powershell

   # Windows (PowerShell)
   Invoke-WebRequest `
       -Uri https://github.com/lavalink-devs/Lavalink/releases/latest/download/Lavalink.jar `
       -OutFile Lavalink.jar

Configuration
-------------

Lavalink reads a file called ``application.yml`` from the same directory you run it in.
Create this file next to ``Lavalink.jar``.

A minimal working configuration:

.. code-block:: yaml

   server:
     port: 2333
     address: 0.0.0.0

   lavalink:
     server:
       password: "youshallnotpass"
       sources:
         youtube: false  # *native* youtube source is deprecated
         bandcamp: true
         soundcloud: true
         twitch: true
         vimeo: true
         http: true
         local: false

   logging:
     level:
       root: INFO
       lavalink: INFO

The ``password`` value must match what you pass to ``sonolink.Client.create_node``. Change it
to something strong before exposing Lavalink to any non-localhost interface.

For a full reference of every configuration option, see the official documentation:

https://lavalink.dev/configuration/

Using YouTube
-------------

Most users prefer to use the ``youtube`` source, but the native Lavalink support for it has been deprecated.
This does not mean you can not use it, there is a plugin that exactly allows for this YouTube support to work
which may be found at https://github.com/lavalink-devs/youtube-source.

To add this plugin, you should add the ``plugins`` key to your ``lavalink`` as it follows:

.. code-block:: yaml

    lavalink:
      # other options...
      plugins:
        - dependency: "dev.lavalink.youtube:youtube-plugin:X.Y.Z"  # you must replace "X.Y.Z" with a version available on their GitHub
          snapshot: false  # may be set to true when you want to use a snapshot version

This plugin can be configured the same way as the native youtube source, but must be under the ``plugins.youtube`` key. The following shows an example
of this.

.. code-block:: yaml

    # other configurations, such as "lavalink", "server", etc.
    plugins:
      youtube:
        enabled: true # whether youtube source is enabled
        allowSearch: true # allows for clients to search with youtube, in SonoLink, this means whether using the TrackSourceType.YOUTUBE(_MUSIC) is allowed

For further detail on this plugin, you can check their `configuration page <https://github.com/lavalink-devs/youtube-source?tab=readme-ov-file#plugin>`_.

Running Lavalink
----------------

Once ``Lavalink.jar`` and ``application.yml`` are in the same directory, start the server:

.. code-block:: bash

   java -jar Lavalink.jar

You should see log output ending with a line similar to::

   Lavalink is ready to accept connections.

Lavalink is now listening on ``localhost:2333`` by default.

Platform-specific setup
-----------------------

Linux (systemd service)
~~~~~~~~~~~~~~~~~~~~~~~

Running Lavalink under systemd keeps it alive across reboots and restarts it on crashes.

Create a dedicated system user so Lavalink does not run as root:

.. code-block:: bash

   sudo useradd -r -s /bin/false lavalink
   sudo mkdir -p /opt/lavalink
   sudo cp Lavalink.jar /opt/lavalink/
   sudo cp application.yml /opt/lavalink/
   sudo chown -R lavalink:lavalink /opt/lavalink

Create the service file at ``/etc/systemd/system/lavalink.service``:

.. code-block:: ini

   [Unit]
   Description=Lavalink audio server
   After=network.target

   [Service]
   Type=simple
   User=lavalink
   WorkingDirectory=/opt/lavalink
   ExecStart=/usr/bin/java -Xmx512m -jar /opt/lavalink/Lavalink.jar
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target

Enable and start the service:

.. code-block:: bash

   sudo systemctl daemon-reload
   sudo systemctl enable lavalink
   sudo systemctl start lavalink
   sudo systemctl status lavalink

View logs at any time with:

.. code-block:: bash

   sudo journalctl -u lavalink -f

macOS (launchd)
~~~~~~~~~~~~~~~

For development on macOS, running Lavalink directly in a terminal session is the simplest
approach. For a persistent background service, create a launchd plist.

Place your files in ``~/lavalink/`` and create
``~/Library/LaunchAgents/dev.lavalink.plist``:

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
       "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>dev.lavalink</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/bin/java</string>
           <string>-jar</string>
           <string>/Users/YOUR_USER/lavalink/Lavalink.jar</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/Users/YOUR_USER/lavalink</string>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
       <key>StandardOutPath</key>
       <string>/Users/YOUR_USER/lavalink/lavalink.log</string>
       <key>StandardErrorPath</key>
       <string>/Users/YOUR_USER/lavalink/lavalink.err</string>
   </dict>
   </plist>

Load the agent:

.. code-block:: bash

   launchctl load ~/Library/LaunchAgents/dev.lavalink.plist

Windows (as a background process)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For local development, open a PowerShell window in the directory containing both files and run:

.. code-block:: powershell

   java -jar Lavalink.jar

To run Lavalink as a Windows Service, use `NSSM (Non-Sucking Service Manager)
<https://nssm.cc/>`_:

.. code-block:: powershell

   # After installing nssm and placing files in C:\lavalink\
   nssm install Lavalink "java" '-jar "C:\lavalink\Lavalink.jar"'
   nssm set Lavalink AppDirectory "C:\lavalink"
   nssm start Lavalink

Docker
~~~~~~

An official Docker image is published to GitHub Container Registry:

.. code-block:: bash

   docker pull ghcr.io/lavalink-devs/lavalink:4

Run a container, mounting your local ``application.yml`` into it:

.. code-block:: bash

   docker run -d \
       --name lavalink \
       -p 2333:2333 \
       -v $(pwd)/application.yml:/opt/Lavalink/application.yml \
       --restart unless-stopped \
       ghcr.io/lavalink-devs/lavalink:4

Or with Docker Compose alongside your bot. An example ``compose.yml``:

.. code-block:: yaml

   services:
     lavalink:
       image: ghcr.io/lavalink-devs/lavalink:4
       container_name: lavalink
       restart: unless-stopped
       ports:
         - "2333:2333"
       volumes:
         - ./application.yml:/opt/Lavalink/application.yml
         - ./plugins/:/opt/Lavalink/plugins/

     bot:
       build: .
       restart: unless-stopped
       depends_on:
         - lavalink
       environment:
         LAVALINK_URI: "http://lavalink:2333"
         LAVALINK_PASSWORD: "youshallnotpass"

When running both containers in the same Compose project, use ``lavalink`` (the service name)
as the hostname in your bot's node URI rather than ``localhost``.

Connecting SonoLink to your server
----------------------------------

With Lavalink running locally on port 2333, connect SonoLink as follows:

.. code-block:: python

   import sonolink

   sl_client = sonolink.Client(bot)

   sl_client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       id="main",
   )

   @bot.event
   async def on_ready() -> None:
       await sl_client.start()

If Lavalink is on a remote machine, replace ``localhost`` with the server's IP address or
hostname. Make sure the port is open in your firewall if the bot and server are on different
hosts.

.. warning::

   Never expose port 2333 to the public internet without placing it behind a reverse proxy
   with TLS. The Lavalink password provides minimal protection on its own. For remote
   deployments, consider using an nginx or Caddy reverse proxy with HTTPS and restricting
   the Lavalink port to localhost only.

Memory and JVM tuning
---------------------

Lavalink's memory consumption scales with the number of active players. A few practical
starting points:

.. list-table::
   :header-rows: 1

   * - Active players (estimate)
     - Suggested heap (``-Xmx``)
   * - 1–10
     - 128 MB
   * - 10–50
     - 256 MB
   * - 50–200
     - 512 MB
   * - 200+
     - 1 GB or more

Set the heap limit by passing the flag before ``-jar``:

.. code-block:: bash

   java -Xmx512m -jar Lavalink.jar

Plugins
-------

Lavalink 4 supports a plugin system for adding audio sources not bundled by default. Plugins
are declared in ``application.yml`` under the ``lavalink.plugins`` key:

.. code-block:: yaml

   lavalink:
     plugins:
       - dependency: "dev.lavalink.youtube:youtube-plugin:1.18.0"
         snapshot: false

Commonly used community plugins include:

* `youtube-plugin <https://github.com/lavalink-devs/youtube-source>`_ — an alternative
  YouTube source that tends to be more resilient to rate-limiting.
* `LavaSrc <https://github.com/topi314/LavaSrc>`_ — adds Spotify, Apple Music, Deezer,
  and Flowery TTS support.
* `SponsorBlock plugin <https://github.com/topi314/Sponsorblock-Plugin>`_ — integrates
  SponsorBlock segment skipping into playback.

After adding a plugin entry, restart Lavalink. It will download the plugin JAR on the next
startup.

Useful references
-----------------

* `Lavalink GitHub <https://github.com/lavalink-devs/Lavalink>`_
* `Lavalink documentation <https://lavalink.dev/>`_
* `Lavalink releases <https://github.com/lavalink-devs/Lavalink/releases>`_
* `Eclipse Temurin (Java downloads) <https://adoptium.net/temurin/releases/>`_
* `Docker image (GHCR) <https://github.com/lavalink-devs/Lavalink/pkgs/container/lavalink>`_
* `LavaSrc plugin <https://github.com/topi314/LavaSrc>`_
* `youtube-plugin <https://github.com/lavalink-devs/youtube-source>`_
