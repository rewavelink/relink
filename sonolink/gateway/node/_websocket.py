"""
MIT License

Copyright (c) 2026-present SonoLink Development Team.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import asyncio
import logging

import msgspec

from sonolink.gateway.enums import NodeStatus
from sonolink.network.message import MessageType

from ._base import BaseNodeComponent

__all__ = ("WebsocketBridge",)

_log = logging.getLogger(__name__)

class WebsocketBridge(BaseNodeComponent):
    """Internal component responsible for managing websocket connections."""

    def build_headers(self) -> dict[str, str]:
        assert self.node._client is not None

        headers = self.node._client._build_ws_headers()
        if self.node._resume_session:
            headers["Session-Id"] = self.node._resume_session

        return headers

    async def connect_ws(self, headers: dict[str, str]) -> bool:
        self.node._ws = await self.node._manager.connect_ws("/v4/websocket", headers=headers)
        self.node._keep_alive = asyncio.create_task(self.keep_alive_coro())
        return True

    async def keep_alive_coro(self) -> None:
        assert self.node._ws is not None
        assert self.node._client

        while True:
            msg = await self.node._ws.receive()

            if MessageType.CLOSE in msg.flags:
                self.node._client._dispatch("node_close", self.node)

                if self.node.auto_reconnect and self.node._status not in (
                    NodeStatus.CONNECTING,
                    NodeStatus.DISCONNECTED,
                ):
                    _log.info("%r WS closed, attempting reconnect...", self.node)
                    asyncio.create_task(self.node.connect())
                break

            if msg.data is None:
                _log.debug("Received a None message from the websocket. Ignoring.")
                continue

            raw = msg.data
            if isinstance(raw, str):
                raw = raw.encode("utf-8")
            data = msgspec.json.decode(raw)

            event_type = data.pop("op", None)
            _log.debug("Received event OP=%s ; D=%r", event_type, data)

            try:
                match event_type:
                    case "ready":
                        await self.node._events.handle_ready(data)
                    case "playerUpdate":
                        await self.node._events.handle_player_update(data)
                    case "stats":
                        self.node._events.handle_stats(data)
                    case "event":
                        await self.node._events.handle_event(data)
                    case _:
                        _log.debug(
                            "Received unhandled event type %r from Node %r",
                            event_type,
                            self.node,
                        )
            except Exception as exc:
                _log.error(
                    "Node %r: Unhandled exception while processing OP=%s: %s",
                    self.node._id,
                    event_type,
                    exc,
                    exc_info=True,
                )
