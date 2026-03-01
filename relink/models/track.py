from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseModel

if TYPE_CHECKING:
    from ..rest.schemas.track import Track as TrackSchema


class Track(BaseModel[TrackSchema]): ...
