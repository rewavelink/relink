from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseModel

if TYPE_CHECKING:
    from ..rest.schemas.track import Track


class Album:
    """
    Represents album metadata usually provided by external plugins like LavaSrc.

    Attributes
    ----------
    name: str | None
        The name of the album, or None if not available.
    url: str | None
        The URL to the album on the source provider.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def __repr__(self) -> str:
        return f"<relink.Album name={self.name!r}>"

    @property
    def name(self) -> str | None:
        """The name of the album."""
        return self._data.get("albumName")

    @property
    def url(self) -> str | None:
        """The URL to the album."""
        return self._data.get("albumUrl")


class Artist:
    """
    Represents artist metadata usually provided by external plugins like LavaSrc.

    Attributes
    ----------
    name: str | None
        The name of the artist, or None if not available.
    url: str | None
        The URL to the artist's profile on the source provider.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def __repr__(self) -> str:
        return f"<relink.Artist name={self.name!r}>"

    @property
    def name(self) -> str | None:
        """The name of the artist."""
        return self._data.get("artistName")

    @property
    def url(self) -> str | None:
        """The URL to the artist profile."""
        return self._data.get("artistUrl")


class Playable(BaseModel[Track]):
    """
    Represents a playable track within relink.

    This class wraps the raw :class:`relink.rest.schemas.Track` schema and provides
    a high-level interface for accessing track metadata and state.
    """

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return f"<relink.Playable title={self.title!r} author={self.author!r} source={self.source_name!r}>"

    @property
    def identifier(self) -> str:
        """The unique identifier for this track based on its source (e.g., YouTube Video ID)."""
        return self._data.info.identifier

    @property
    def encoded(self) -> str:
        """The base64 encoded string used by Lavalink to identify this track."""
        return self._data.encoded

    @property
    def source_name(self) -> str:
        """The name of the source manager that provided this track (e.g., 'youtube', 'spotify')."""
        return self._data.info.source_name

    @property
    def uri(self) -> str | None:
        """The direct URL to the track, if available."""
        return self._data.info.uri

    @property
    def isrc(self) -> str | None:
        """The International Standard Recording Code for the track, if available."""
        return self._data.info.isrc

    @property
    def title(self) -> str:
        """The title of the track."""
        return self._data.info.title

    @property
    def author(self) -> str:
        """The author or artist of the track."""
        return self._data.info.author

    @property
    def artwork(self) -> str | None:
        """A URL to the track's artwork/thumbnail, if available."""
        return self._data.info.artwork_url

    @property
    def album(self) -> Album:
        """The :class:`Album` metadata for this track. Only populated by certain plugins."""
        return Album(self._data.plugin_info or {})

    @property
    def artist(self) -> Artist:
        """The :class:`Artist` metadata for this track. Only populated by certain plugins."""
        return Artist(self._data.plugin_info or {})

    @property
    def length(self) -> int:
        """The total duration of the track in milliseconds."""
        return self._data.info.length

    @property
    def position(self) -> int:
        """The starting position of the track in milliseconds."""
        return self._data.info.position

    @property
    def is_stream(self) -> bool:
        """Whether the track is a live stream."""
        return self._data.info.is_stream

    @property
    def is_seekable(self) -> bool:
        """Whether the track supports seeking."""
        return self._data.info.is_seekable
