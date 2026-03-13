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

from typing import TYPE_CHECKING, Any

from .base import BaseModel

if TYPE_CHECKING:
    from ..gateway.client import Client
    from ..rest.schemas import filters


class Equalizer(BaseModel[filters.EqualizerFilter]):
    """
    Represents a single Lavalink equalizer band.

    Attributes
    ----------
    band: int
        The target band index (0 to 14).
    gain: float
        The band gain multiplier (-0.25 to 1.0).
    """

    __slots__ = ()

    @property
    def band(self) -> int:
        """The target band index (0 to 14)."""
        return self._data.band

    @property
    def gain(self) -> float:
        """The band gain multiplier (-0.25 to 1.0)."""
        return self._data.gain


class Karaoke(BaseModel[filters.KaraokeFilter]):
    """
    Filter that reduces vocal levels in a track, useful for karaoke.

    Attributes
    ----------
    level: float | None
        Overall effect intensity (0.0 to 1.0).
    mono_level: float | None
        Mono signal amount (0.0 to 1.0).
    filter_band: float | None
        Center frequency in Hz for the target region.
    filter_width: float | None
        Bandwidth around the filter band in Hz.
    """

    __slots__ = ()

    @property
    def level(self) -> float | None:
        """Overall effect intensity (0.0 to 1.0)."""
        return self._data.level

    @property
    def mono_level(self) -> float | None:
        """Mono signal amount (0.0 to 1.0)."""
        return self._data.mono_level

    @property
    def filter_band(self) -> float | None:
        """Center frequency in Hz for the target region."""
        return self._data.filter_band

    @property
    def filter_width(self) -> float | None:
        """Bandwidth around the filter band in Hz."""
        return self._data.filter_width


class Timescale(BaseModel[filters.TimescaleFilter]):
    """
    Adjusts the speed, pitch, and rate of audio playback.

    Attributes
    ----------
    speed: float | None
        Playback speed multiplier (>= 0.0). 1.0 is normal.
    pitch: float | None
        Pitch multiplier (>= 0.0). 1.0 is normal.
    rate: float | None
        Internal rate multiplier (>= 0.0). 1.0 is normal.
    """

    __slots__ = ()

    @property
    def speed(self) -> float | None:
        """Playback speed multiplier (>= 0.0)."""
        return self._data.speed

    @property
    def pitch(self) -> float | None:
        """Pitch multiplier (>= 0.0)."""
        return self._data.pitch

    @property
    def rate(self) -> float | None:
        """Internal rate multiplier (>= 0.0)."""
        return self._data.rate


class Tremolo(BaseModel[filters.TremoloFilter]):
    """
    Rapidly oscillates the volume of the audio.

    Attributes
    ----------
    frequency: float | None
        Oscillation frequency in Hz (> 0.0).
    depth: float | None
        Effect depth (0.0 < x <= 1.0).
    """

    __slots__ = ()

    @property
    def frequency(self) -> float | None:
        """Oscillation frequency in Hz (> 0.0)."""
        return self._data.frequency

    @property
    def depth(self) -> float | None:
        """Effect depth (0.0 < x <= 1.0)."""
        return self._data.depth


class Vibrato(BaseModel[filters.VibratoFilter]):
    """
    Rapidly oscillates the pitch of the audio.

    Attributes
    ----------
    frequency: float | None
        Oscillation frequency in Hz (0.0 < x <= 14.0).
    depth: float | None
        Effect depth (0.0 < x <= 1.0).
    """

    __slots__ = ()

    @property
    def frequency(self) -> float | None:
        """Oscillation frequency in Hz (0.0 < x <= 14.0)."""
        return self._data.frequency

    @property
    def depth(self) -> float | None:
        """Effect depth (0.0 < x <= 1.0)."""
        return self._data.depth


class Rotation(BaseModel[filters.RotationFilter]):
    """
    Rotates the audio across the stereo channels (panning effect).

    Attributes
    ----------
    rotation_hz: float | None
        Rotation frequency in Hz.
    """

    __slots__ = ()

    @property
    def rotation_hz(self) -> float | None:
        """Rotation frequency in Hz."""
        return self._data.rotation_hz


class Distortion(BaseModel[filters.DistortionFilter]):
    """
    Applies distortion effects using sine, cosine, and tangent transforms.

    Attributes
    ----------
    sin_offset: float | None
        The sine input offset component.
    sin_scale: float | None
        The sine scaling component.
    cos_offset: float | None
        The cosine input offset component.
    cos_scale: float | None
        The cosine scaling component.
    tan_offset: float | None
        The tangent input offset component.
    tan_scale: float | None
        The tangent scaling component.
    """

    __slots__ = ()

    @property
    def sin_offset(self) -> float | None:
        """The sine input offset component."""
        return self._data.sin_offset

    @property
    def sin_scale(self) -> float | None:
        """The sine scaling component."""
        return self._data.sin_scale

    @property
    def cos_offset(self) -> float | None:
        """The cosine input offset component."""
        return self._data.cos_offset

    @property
    def cos_scale(self) -> float | None:
        """The cosine scaling component."""
        return self._data.cos_scale

    @property
    def tan_offset(self) -> float | None:
        """The tangent input offset component."""
        return self._data.tan_offset

    @property
    def tan_scale(self) -> float | None:
        """The tangent scaling component."""
        return self._data.tan_scale


class ChannelMix(BaseModel[filters.ChannelMixFilter]):
    """
    Mixes left and right audio channels to manipulate stereo separation.

    Attributes
    ----------
    left_to_left: float | None
        Left input contribution to left output.
    left_to_right: float | None
        Left input contribution to right output.
    right_to_left: float | None
        Right input contribution to left output.
    right_to_right: float | None
        Right input contribution to right output.
    """

    __slots__ = ()

    @property
    def left_to_left(self) -> float | None:
        """The contribution of the left input channel to the left output channel."""
        return self._data.left_to_left

    @property
    def left_to_right(self) -> float | None:
        """The contribution of the left input channel to the right output channel."""
        return self._data.left_to_right

    @property
    def right_to_left(self) -> float | None:
        """The contribution of the right input channel to the left output channel."""
        return self._data.right_to_left

    @property
    def right_to_right(self) -> float | None:
        """The contribution of the right input channel to the right output channel."""
        return self._data.right_to_right


class LowPass(BaseModel[filters.LowPassFilter]):
    """
    Suppresses higher frequencies in the audio signal.

    Attributes
    ----------
    smoothing: float | None
        Smoothing factor (x > 1.0).
    """

    __slots__ = ()

    @property
    def smoothing(self) -> float | None:
        """Smoothing factor (x > 1.0)."""
        return self._data.smoothing


class Filters(BaseModel[filters.PlayerFilters]):
    """
    The main container for all active player filters.

    This class provides a Pythonic interface to the underlying Lavalink filter state.

    Attributes
    ----------
    volume: float
        The linear volume multiplier (0.0 to 5.0).
    equalizer: list[Equalizer]
        A list of active equalizer bands.
    karaoke: Karaoke | None
        The active karaoke filter, if set.
    timescale: Timescale | None
        The active timescale filter, if set.
    tremolo: Tremolo | None
        The active tremolo filter, if set.
    vibrato: Vibrato | None
        The active vibrato filter, if set.
    rotation: Rotation | None
        The active rotation filter, if set.
    distortion: Distortion | None
        The active distortion filter, if set.
    channel_mix: ChannelMix | None
        The active channel mix filter, if set.
    low_pass: LowPass | None
        The active low pass filter, if set.
    plugin_filters: dict[str, Any]
        A dictionary of raw plugin-defined filter payloads.
    """

    __slots__ = (
        "_equalizer",
        "_karaoke",
        "_timescale",
        "_tremolo",
        "_vibrato",
        "_rotation",
        "_distortion",
        "_channel_mix",
        "_low_pass",
    )

    def __init__(self, *, client: Client, data: filters.PlayerFilters) -> None:
        super().__init__(client=client, data=data)

        self._equalizer = [
            Equalizer(client=client, data=e) for e in (self._data.equalizer or [])
        ]
        self._karaoke = self._wrap(Karaoke, self._data.karaoke)
        self._timescale = self._wrap(Timescale, self._data.timescale)
        self._tremolo = self._wrap(Tremolo, self._data.tremolo)
        self._vibrato = self._wrap(Vibrato, self._data.vibrato)
        self._rotation = self._wrap(Rotation, self._data.rotation)
        self._distortion = self._wrap(Distortion, self._data.distortion)
        self._channel_mix = self._wrap(ChannelMix, self._data.channel_mix)
        self._low_pass = self._wrap(LowPass, self._data.low_pass)

    def _wrap(self, cls: Any, data: Any) -> Any | None:
        return cls(client=self._client, data=data) if data else None

    @property
    def volume(self) -> float:
        """The linear volume multiplier (0.0 to 5.0). Defaults to 1.0."""
        return self._data.volume if self._data.volume is not None else 1.0

    @property
    def equalizer(self) -> list[Equalizer]:
        """A list of active equalizer bands."""
        return self._equalizer

    @property
    def karaoke(self) -> Karaoke | None:
        """The active karaoke filter, if set."""
        return self._karaoke

    @property
    def timescale(self) -> Timescale | None:
        """The active timescale filter, if set."""
        return self._timescale

    @property
    def tremolo(self) -> Tremolo | None:
        """The active tremolo filter, if set."""
        return self._tremolo

    @property
    def vibrato(self) -> Vibrato | None:
        """The active vibrato filter, if set."""
        return self._vibrato

    @property
    def rotation(self) -> Rotation | None:
        """The active rotation filter, if set."""
        return self._rotation

    @property
    def distortion(self) -> Distortion | None:
        """The active distortion filter, if set."""
        return self._distortion

    @property
    def channel_mix(self) -> ChannelMix | None:
        """The active channel mix filter, if set."""
        return self._channel_mix

    @property
    def low_pass(self) -> LowPass | None:
        """The active low pass filter, if set."""
        return self._low_pass

    @property
    def plugin_filters(self) -> dict[str, Any]:
        """A dictionary of raw plugin-defined filter payloads."""
        return self._data.plugin_filters

    @property
    def payload(self) -> filters.PlayerFilters:
        """Returns the underlying msgspec schema for API requests."""
        return self._data
