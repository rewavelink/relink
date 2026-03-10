from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    Client = Any  # TODO


class BaseModel[D]:
    """
    The base class for all relink models.

    This class provides the connection to the :class:`relink.Client`
    and holds the raw msgspec data structure.
    """

    def __init__(self, *, client: Client, data: D) -> None:
        self._client: Any = client
        self._data: D = data

    @property
    def client(self) -> Client:
        """The :class:`relink.Client` instance associated with this object."""
        return self._client

    @property
    def data(self) -> D:
        """The raw msgspec schema object holding the data for this model."""
        return self._data
