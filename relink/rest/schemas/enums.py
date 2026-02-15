from __future__ import annotations

from enum import StrEnum


__all__ = ("TrackLoadResult",)


class TrackLoadResult(StrEnum):
    """Represents the type of a TrackLoadingResult's :attr:`TrackLoadingResult.load_type`."""

    TRACK = "track"
    """A track has been loaded."""
    PLAYLIST = "playlist"
    """A playlist has been loaded."""
    SEARCH = "search"
    """A search query has been loaded."""
    EMPTY = "empty"
    """There has beeen no matches for your identifier."""
    ERROR = "error"
    """Loading has failed with an error."""
