<div align="center">

![ReLink](https://raw.githubusercontent.com/rewavelink/relink/main/docs/_static/images/banner.png)

**ReLink** is a high-performance Lavalink v4 wrapper for Python, inspired by [WaveLink](https://github.com/PythonistaGuild/Wavelink).

[Documentation](https://relink.readthedocs.io/en/latest) · [Discord](https://discord.gg/tPHVWBPedt) · [Migration from WaveLink](https://relink.readthedocs.io/en/latest/guides/migrating-from-wavelink.html)



[![PyPI](https://img.shields.io/pypi/v/rewavelink)](https://pypi.org/project/rewavelink)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/github/license/rewavelink/relink)](LICENSE)
[![Lavalink](https://img.shields.io/badge/lavalink-4.x-orange)](https://lavalink.dev)
[![Discord](https://img.shields.io/discord/1471146455002775624?label=discord)](https://discord.gg/tPHVWBPedt)

</div>

---

## Features

- Full Lavalink v4+ REST API support
- Built on [msgspec](https://github.com/jcrist/msgspec) for rapid serialization and strict type validation
- Optional [curl_cffi](https://github.com/lexiforest/curl_cffi) and [orjson](https://github.com/ijl/orjson) for faster networking and serialization
- Drop-in familiarity for Wavelink users — [migration guide included](https://relink.readthedocs.io/en/latest/guides/migrating-from-wavelink.html)
- Actively maintained, unlike the library you're probably migrating from
- Async-first and Pyright strict-compliant
- Built-in support for [discord.py](https://github.com/Rapptz/discord.py), [pycord](https://github.com/Pycord-Development/pycord), and [disnake](https://github.com/DisnakeDev/disnake)

## Installation

> [!NOTE]
> A [virtual environment](https://docs.python.org/3/library/venv.html) is recommended, especially on Linux where the system Python may restrict package installations.
> 
### Requirements:
- Python 3.12 or higher
- A running Lavalink 4.x server ([guide on setup](https://relink.readthedocs.io/en/latest/guides/lavalink-setup.html))
- Any of the supported libraries:
  - [discord.py](https://pypi.org/project/discord.py)[voice] 2.7+
  - [py-cord](https://pypi.org/project/py-cord)[voice] 2.8+
  - [disnake](https://pypi.org/project/disnake)[voice] 2.12+

To install the stable version from PyPI:
```sh
# Linux/macOS
python3 -m pip install -U rewavelink

# Windows
py -3 -m pip install -U rewavelink
```

To install with optional speed improvements:
```sh
# Linux/macOS
python3 -m pip install -U "rewavelink[speed]"

# Windows
py -3 -m pip install -U "rewavelink[speed]"
```

<br>

<p align="center">
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/footers/gray0_ctp_on_line.svg?sanitize=true" />
</p>

<p align="center">
        <i><code>&copy 2026 <a href="https://github.com/rewavelink">ReLink Development Team</a></code></i>
</p>
