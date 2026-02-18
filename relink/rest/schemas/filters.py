"""
MIT License

Copyright (c) 2019-2025 PythonistaGuild, EvieePy; 2026-present ReWaveLink Development Team.

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

from typing import Annotated, Any

import msgspec


class PlayerFilters(msgspec.Struct, kw_only=True):
    """
    Represents the full filter payload for a Lavalink player.

    This object is sent under ``filters`` when updating a player. Attributes set
    to ``None`` are intentionally left unset, which is useful for partial updates.

    :attr volume: Linear volume multiplier from ``0.0`` to ``5.0``. ``1.0`` is
        100% volume. Values above ``1.0`` may clip.
    :attr equalizer: List of :class:`EqualizerFilter` entries for bands ``0..14``.
    :attr karaoke: Karaoke configuration (:class:`KaraokeFilter`).
    :attr timescale: Time-domain transform configuration (:class:`TimescaleFilter`).
    :attr tremolo: Volume oscillation configuration (:class:`TremoloFilter`).
    :attr vibrato: Pitch oscillation configuration (:class:`VibratoFilter`).
    :attr rotation: Stereo rotation configuration (:class:`RotationFilter`).
    :attr distortion: Wave-shaping configuration (:class:`DistortionFilter`).
    :attr channel_mix: Cross-channel matrix configuration (:class:`ChannelMixFilter`).
    :attr low_pass: Low-pass configuration (:class:`LowPassFilter`).
    :attr plugin_filters: Plugin-defined filter payloads keyed by plugin name.
        Values are plugin-specific and passed through as-is.
    """

    volume: float | None = None
    equalizer: list[EqualizerFilter] | None = None
    karaoke: KaraokeFilter | None = None
    timescale: TimescaleFilter | None = None
    tremolo: TremoloFilter | None = None
    vibrato: VibratoFilter | None = None
    rotation: RotationFilter | None = None

    distortion: DistortionFilter | None = None
    channel_mix: ChannelMixFilter | None = msgspec.field(
        name="channelMix",
        default=None,
    )
    low_pass: LowPassFilter | None = msgspec.field(name="lowPass", default=None)

    plugin_filters: dict[str, Any] = msgspec.field(
        name="pluginFilters",
        default_factory=dict[str, Any],
    )


class EqualizerFilter(msgspec.Struct, kw_only=True):
    """
    Represents a single Lavalink equalizer band.

    Lavalink exposes 15 bands indexed ``0..14``. The frequencies are approximately:
    ``25, 40, 63, 100, 160, 250, 400, 630, 1000, 1600, 2500, 4000, 6300, 10000, 16000`` Hz.

    :attr band: Target band index from ``0`` to ``14``.
    :attr gain: Band gain multiplier from ``-0.25`` to ``1.0``.
        ``-0.25`` mutes the band and ``0.25`` roughly doubles it.
    """

    band: Annotated[int, "0..14"]
    gain: Annotated[float, "-0.25..1.0"]


class KaraokeFilter(msgspec.Struct, kw_only=True):
    """
    Represents karaoke filter configuration.

    This filter reduces content in a target frequency region, commonly used for
    vocal reduction.

    :attr level: Overall effect intensity from ``0.0`` to ``1.0``.
    :attr mono_level: Mono signal amount from ``0.0`` to ``1.0``.
    :attr filter_band: Center frequency in Hz for the target region.
    :attr filter_width: Bandwidth around ``filter_band`` in Hz.
    """

    level: Annotated[float | None, "0.0..1.0, 0.0 is no effect"] = None
    mono_level: Annotated[float | None, "0.0..1.0, 0.0 is no effect"] = msgspec.field(
        name="monoLevel", default=None
    )
    filter_band: Annotated[float | None, "frequency in Hz"] = msgspec.field(
        name="filterBand", default=None
    )
    filter_width: Annotated[float | None, "bandwidth in Hz"] = msgspec.field(
        name="filterWidth", default=None
    )


class TimescaleFilter(msgspec.Struct, kw_only=True):
    """
    Represents timescale filter configuration.

    This filter changes perceived playback speed, pitch, and rate. In Lavalink,
    omitted values are treated as ``1.0``.

    :attr speed: Playback speed multiplier (``0.0 <= x``). ``1.0`` is normal.
    :attr pitch: Pitch multiplier (``0.0 <= x``). ``1.0`` is unchanged.
    :attr rate: Internal rate multiplier (``0.0 <= x``).
    """

    speed: Annotated[float | None, "0.0 <= x"] = None
    pitch: Annotated[float | None, "0.0 <= x"] = None
    rate: Annotated[float | None, "0.0 <= x"] = None


class TremoloFilter(msgspec.Struct, kw_only=True):
    """
    Represents tremolo filter configuration.

    Tremolo rapidly oscillates output volume.

    :attr frequency: Oscillation frequency in Hz (``0.0 < x``).
    :attr depth: Effect depth (``0.0 < x <= 1.0``).
    """

    frequency: Annotated[float | None, "0.0 < x"] = None
    depth: Annotated[float | None, "0.0 < x <= 1.0"] = None


class VibratoFilter(msgspec.Struct, kw_only=True):
    """
    Represents vibrato filter configuration.

    Vibrato rapidly oscillates output pitch.

    :attr frequency: Oscillation frequency in Hz (``0.0 < x <= 14.0``).
    :attr depth: Effect depth (``0.0 < x <= 1.0``).
    """

    frequency: Annotated[float | None, "0.0 < x <= 14.0"] = None
    depth: Annotated[float | None, "0.0 < x <= 1.0"] = None


class RotationFilter(msgspec.Struct, kw_only=True):
    """
    Represents stereo rotation filter configuration.

    This effect rotates audio around left and right channels (panning).

    :attr rotation_hz: Rotation frequency in Hz. ``0.2`` is a common slow rotation.
    """

    rotation_hz: float | None = msgspec.field(name="rotationHz", default=None)


class DistortionFilter(msgspec.Struct, kw_only=True):
    """
    Represents distortion filter configuration.

    Distortion combines sinusoidal and linear transforms. Small changes can
    produce large audible differences, so tune incrementally.

    :attr sin_offset: Sine input offset component.
    :attr sin_scale: Sine scaling component.
    :attr cos_offset: Cosine input offset component.
    :attr cos_scale: Cosine scaling component.
    :attr tan_offset: Tangent input offset component.
    :attr tan_scale: Tangent scaling component.
    :attr offset: Linear output offset applied after shaping.
    :attr scale: Linear output scaling applied after shaping.
    """

    sin_offset: float | None = msgspec.field(name="sinOffset", default=None)
    sin_scale: float | None = msgspec.field(name="sinScale", default=None)

    cos_offset: float | None = msgspec.field(name="cosOffset", default=None)
    cos_scale: float | None = msgspec.field(name="cosScale", default=None)

    tan_offset: float | None = msgspec.field(name="tanOffset", default=None)
    tan_scale: float | None = msgspec.field(name="tanScale", default=None)

    offset: float | None = None
    scale: float | None = None


class ChannelMixFilter(msgspec.Struct, kw_only=True):
    """
    Represents channel mix filter configuration.

    All coefficients satisfy ``0.0 <= x <= 1.0``.
    The default matrix keeps channels independent. Setting all coefficients to
    ``0.5`` yields dual-mono output.

    :attr left_to_left: Contribution of left input to left output.
    :attr left_to_right: Contribution of left input to right output.
    :attr right_to_left: Contribution of right input to left output.
    :attr right_to_right: Contribution of right input to right output.
    """

    left_to_left: float | None = msgspec.field(name="leftToLeft", default=None)
    left_to_right: float | None = msgspec.field(name="leftToRight", default=None)
    right_to_left: float | None = msgspec.field(name="rightToLeft", default=None)
    right_to_right: float | None = msgspec.field(name="rightToRight", default=None)


class LowPassFilter(msgspec.Struct, kw_only=True):
    """
    Represents low-pass filter configuration.

    Low-pass filtering suppresses higher frequencies while preserving lower ones.

    :attr smoothing: Smoothing factor (``x > 1.0``). Values ``<= 1.0`` disable
        this filter.
    """

    smoothing: Annotated[float | None, "> 1.0"] = None
