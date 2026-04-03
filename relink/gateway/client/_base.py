from __future__ import annotations

from typing import Any, Protocol


class ClientUser(Protocol):
    id: int


class DiscordClient[ClientT: Any]:
    cls: type[ClientT] = NotImplemented

    __slots__ = ("_client", "user")

    def __init__(self, client: ClientT, /) -> None:
        self._client: ClientT = client

    def dispatch(self, event_name: str, *args: object) -> None:
        raise NotImplementedError

    @property
    def user(self) -> ClientUser | None:
        raise NotImplementedError
