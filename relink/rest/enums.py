from __future__ import annotations

from enum import StrEnum


__all__ = ("TrackLoadResultType",)


class TrackLoadResultType(StrEnum):
    """Represents the type of a TrackLoadingResult's :attr:`TrackLoadingResultType.load_type`."""

    TRACK = "TRACK"
    """A track has been loaded."""
    PLAYLIST = "PLAYLIST"
    """A playlist has been loaded."""
    SEARCH = "SEARCH"
    """A search query has been loaded."""
    EMPTY = "EMPTY"
    """There has beeen no matches for your identifier."""
    ERROR = "ERROR"
    """Loading has failed with an error."""
