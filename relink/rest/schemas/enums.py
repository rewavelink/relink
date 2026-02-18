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


class RoutePlannerType(StrEnum):
    """Represents the type of IP route planner to use."""

    """IP address is switched on ban. Recommended for IPv4 blocks or IPv6 blocks smaller than a /64."""
    ROTATING_IP = "rotating_ip"

    """IP address is switched on clock update. Use with at least 1 /64 IPv6 block."""
    NANO_IP = "nano_ip"

    """IP address is switched on clock update, rotates to a different /64 block on ban. Use with at least 2x /64 IPv6 blocks."""
    ROTATING_NANO_IP = "rotating_nano_ip"

    """Balances load across multiple IP addresses."""
    BALANCING_IP = "balancing_ip"


class IPBlockType(StrEnum):
    """Represents the type of IP block."""

    """The ipv4 block type."""
    INET4_ADDRESS = "inet4"

    """The ipv6 block type."""
    INET6_ADDRESS = "inet6"
