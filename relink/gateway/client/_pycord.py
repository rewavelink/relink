from __future__ import annotations

from typing import Any, Protocol

import discord

from ._base import DiscordClient


class PycordClientProto(Protocol):
    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None: ...
    @property
    def user(self) -> discord.ClientUser | None: ...


class PycordClient(DiscordClient[discord.Client]):
    __slots__ = ()

    cls = discord.Client

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        self._client.dispatch(event_name, *args, **kwargs)

    @property
    def user(self) -> discord.ClientUser | None:
        return self._client.user
