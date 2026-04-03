from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Protocol


class ClientUser(Protocol):
    id: int


class DiscordClient[ClientT: Any](ABC):
    cls: ClassVar[type[Any]]
    __slots__ = ("_client",)

    def __init__(self, client: ClientT, /) -> None:
        self._client: ClientT = client

    @abstractmethod
    def dispatch(self, event_name: str, /, *args: Any, **kwargs: Any) -> None: ...

    @property
    @abstractmethod
    def user(self) -> ClientUser | None: ...
