from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from relink.rest.schemas.player import UpdatePlayerRequest, UpdatePlayerTrackRequest

from ._base import HandlerBase, _log

if TYPE_CHECKING:
    from ..node import Node

__all__ = ()


class LifecycleHandler(HandlerBase):
    async def disconnect(self, *, force: bool = False) -> None:
        try:
            if self._player._node is None:
                return

            self._player._node._remove_player(self._player.guild_id)

            if self._player._node._resume_session is None:
                return

            await self._player._node._manager.destroy_player(
                session_id=self._player._node._resume_session,
                guild_id=str(self._player.guild_id),
            )

            _log.info(
                "Player %s: Disconnected and removed from Node %r.",
                self._player.guild_id,
                self._player._node.id,
            )

        except Exception as exc:
            _log.warning(
                "Player %s: Error during disconnect cleanup: %s",
                self._player.guild_id,
                exc,
                exc_info=True,
            )

        finally:
            self._player._queue.reset()
            await discord.VoiceProtocol.disconnect(self._player, force=force)

    async def move_to(self, node: Node, /) -> None:
        if self._player._node is node:
            return

        old_node = self._player._node
        self._player._node = node

        if old_node:
            old_node._remove_player(self._player.guild_id)
        node._add_player(self._player)

        await self._player._dispatch_voice_update()
        assert node._resume_session is not None

        track_payload = (
            UpdatePlayerTrackRequest(encoded=self._player.current.encoded)
            if self._player.current
            else None
        )
        data = UpdatePlayerRequest(
            track=track_payload,
            position=self._player.position,
            volume=self._player._volume,
            paused=self._player._paused,
            filters=self._player._filters,
        )

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild_id),
            data=data,
        )

        if old_node and old_node._resume_session:
            try:
                await old_node._manager.destroy_player(
                    session_id=old_node._resume_session,
                    guild_id=str(self._player.guild_id),
                )
            except Exception as exc:
                _log.warning(
                    "Player %s: Failed to destroy player on old node during migration. Error: %s",
                    self._player.guild_id,
                    exc,
                    exc_info=True,
                )

        _log.info(
            "Player %s: Successfully migrated to Node %r.",
            self._player.guild_id,
            node.id,
        )
