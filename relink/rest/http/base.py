from collections.abc import Mapping
from typing import Any, Protocol


class HTTPClient(Protocol):  # TODO: implement HTTP client for a shared class
    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> Any: ...
