from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from ..schemas import session

if TYPE_CHECKING:
    from .base import HTTPClient


class SessionHTTPMixin:
    """Mixin for Session related HTTP operations."""

    async def update_session(
        self: HTTPClient,
        *,
        session_id: str,
        data: session.UpdateSessionRequest,
        no_replace: bool = False,
    ) -> session.UpdateSessionResponse:
        url = f"/sessions/{session_id}"
        res = await self.request(
            "PATCH",
            url,
            data=msgspec.json.encode(data),
            params={"noReplace": str(no_replace)},
        )
        return msgspec.json.decode(res, type=session.UpdateSessionResponse)
