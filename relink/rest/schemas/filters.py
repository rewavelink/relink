"""
MIT License

Copyright (c) 2019-2026 PythonistaGuild, EvieePy; 2026-present ReWaveLink Development Team.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations
from typing import Any

import msgspec


class PlayerFilters(msgspec.Struct, kw_only=True):
    """Represents a Filter structure payload."""

    volume: float | None = None
    equalizer: list[EqualizerFilter] | None = None
    karaoke: KaraokeFilter | None = None
    timescale: TimescaleFilter | None = None
    tremolo: TremoloFilter | None = None
    vibrato: VibratoFilter | None = None
    rotation: RotationFilter | None = None
    distortion: DistortionFilter | None = None
    channel_mix: ChannelMixFilter | None = msgspec.field(
        name="channelMix", default=None
    )
    low_pass: LowPassFilter | None = msgspec.field(name="lowPass", default=None)
    plugin_filters: dict[str, Any] = msgspec.field(
        name="pluginFilters", default_factory=dict[str, Any]
    )


class EqualizerFilter(msgspec.Struct, kw_only=True):
    """Represents an EqualizerFilter structure payload."""

    band: int  # 0-14
    gain: float  # -0.25 to 1.0


class KaraokeFilter(msgspec.Struct, kw_only=True):
    """Represents a KaraokeFilter structure payload."""

    level: float | None = None  # 0-1.0, 0.0 is no effect
    mono_level: float | None = None  # 0-1.0, 0.0 is no effect
    filter_band: float | None = None  # hz
    filter_width: float | None = None


class TimescaleFilter(msgspec.Struct, kw_only=True):
    """Represents a TimescaleFilter structure payload."""

    speed: float | None = None
    pitch: float | None = None
    rate: float | None = None


class TremoloFilter(msgspec.Struct, kw_only=True):
    """Represents a TremoloFilter structure payload."""

    frequency: float | None = None  # <= 14.0
    depth: float | None = None  # <= 1.0


class VibratoFilter(msgspec.Struct, kw_only=True):
    """Represents a VibratoFilter structure payload."""

    frequency: float | None = None  # <= 14.0
    depth: float | None = None  # <= 1.0


class RotationFilter(msgspec.Struct, kw_only=True):
    """Represents a RotationFilter structure payload."""

    rotation_hz: float | None = msgspec.field(name="rotationHz", default=None)


class DistortionFilter(msgspec.Struct, kw_only=True):
    """Represents a DistortionFilter structure payload."""

    sin_offset: float | None = msgspec.field(name="sinOffset", default=None)
    sin_scale: float | None = msgspec.field(name="sinScale", default=None)
    cos_offset: float | None = msgspec.field(name="cosOffset", default=None)
    cos_scale: float | None = msgspec.field(name="cosScale", default=None)
    tan_offset: float | None = msgspec.field(name="tanOffset", default=None)
    tan_scale: float | None = msgspec.field(name="tanScale", default=None)
    offset: float | None = None
    scale: float | None = None


class ChannelMixFilter(msgspec.Struct, kw_only=True):
    """Represents a ChannelMixFilter structure payload."""

    left_to_left: float | None = msgspec.field(
        name="leftToLeft", default=None
    )  # <= 1.0
    left_to_right: float | None = msgspec.field(
        name="leftToRight", default=None
    )  # <= 1.0
    right_to_left: float | None = msgspec.field(
        name="rightToLeft", default=None
    )  # <= 1.0
    right_to_right: float | None = msgspec.field(
        name="rightToRight", default=None
    )  # <= 1.0


class LowPassFilter(msgspec.Struct, kw_only=True):
    """Represents a LowPassFilter structure payload."""

    smoothing: float | None = None  # > 1.0
