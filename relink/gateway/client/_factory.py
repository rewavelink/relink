from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast, overload

from ._base import DiscordClient

if TYPE_CHECKING:
    from relink.gateway.player import FrameworkLiteral

    from .adapters._disnake import DisnakeClient
    from .adapters._dpy import DpyClient
    from .adapters._pycord import PycordClient


class ClientFactory:
    __slots__ = ()

    @overload
    @staticmethod
    def create(client: Any, framework: Literal["disnake"]) -> DisnakeClient: ...

    @overload
    @staticmethod
    def create(client: Any, framework: Literal["pycord"]) -> PycordClient: ...

    @overload
    @staticmethod
    def create(client: Any, framework: Literal["discord.py"]) -> DpyClient: ...

    @staticmethod
    def create(client: Any, framework: FrameworkLiteral) -> DiscordClient[Any]:
        match framework:
            case "discord.py":
                from .adapters._dpy import DpyClient as Client
            case "pycord":
                from .adapters._pycord import PycordClient as Client
            case "disnake":
                from .adapters._disnake import DisnakeClient as Client
            case _:  # pyright: ignore[reportUnnecessaryComparison]
                raise ValueError(f"Unsupported framework: {framework}")

        expected_type = Client.cls
        if not isinstance(client, expected_type):
            raise TypeError(
                f"Expected client of type {expected_type.__name__!r}, got {type(client).__name__!r}"
            )

        return Client(cast(Any, client))
