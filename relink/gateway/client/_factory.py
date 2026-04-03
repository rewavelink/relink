from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import DiscordClient

if TYPE_CHECKING:
    from ...gateway.player_new import FrameworkLiteral


class ClientFactory[ClientT: Any]:
    __slots__ = ()

    @staticmethod
    def create(client: Any, framework: FrameworkLiteral) -> DiscordClient[ClientT]:
        if framework == "disnake":
            from ._disnake import DisnakeClient as Client
        elif framework == "pycord":
            from ._pycord import PycordClient as Client
        elif framework == "discord.py":
            from ._dpy import DpyClient as Client
        else:
            raise ValueError(f"Unsupported framework: {framework}")

        print(
            "checking client type...",
            "expected:",
            Client.cls,
            "got:",
            type(client),
            "framework:",
            framework,
        )
        expected_type = Client.cls  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        if not isinstance(client, expected_type):
            raise TypeError(
                f"Expected client of type {expected_type.__name__}, got {type(client).__name__}"
            )

        return Client(client)  # type: ignore
