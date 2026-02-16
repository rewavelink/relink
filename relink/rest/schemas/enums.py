from __future__ import annotations

from enum import StrEnum


__all__ = ("TrackLoadResult",)


class TrackLoadResult(StrEnum):
    """Represents the type of a TrackLoadingResult's :attr:`TrackLoadingResult.load_type`."""

    """A track has been loaded."""
    TRACK = "track"

    """A playlist has been loaded."""
    PLAYLIST = "playlist"

    """A search query has been loaded."""
    SEARCH = "search"

    """There has beeen no matches for your identifier."""
    EMPTY = "empty"

    """Loading has failed with an error."""
    ERROR = "error"
