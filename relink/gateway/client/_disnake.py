from __future__ import annotations

from typing import Any, Protocol

import disnake

from ._base import DiscordClient


class DisnakeClientProto(Protocol):
    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None: ...
    @property
    def user(self) -> disnake.ClientUser | None: ...


class DisnakeClient(DiscordClient[disnake.Client]):
    __slots__ = ()

    cls = disnake.Client

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        self._client.dispatch(event_name, *args, **kwargs)

    @property
    def user(self) -> disnake.ClientUser | None:
        return self._client.user
