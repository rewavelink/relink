from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    Client = Any  # TODO


class BaseModel[D]:
    def __init__(self, *, client: Client, data: D) -> None:
        self._client: Any = client
        self._data: D = data
