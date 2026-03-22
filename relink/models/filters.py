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

from typing import TYPE_CHECKING, Any, Self, Union

import msgspec

from ..rest.schemas import filters
from .base import BaseModel

if TYPE_CHECKING:
    from ..gateway.client import Client

    FilterModelTypes = Union[
        "Equalizer",
        "Karaoke",
        "Timescale",
        "Tremolo",
        "Vibrato",
        "Rotation",
        "Distortion",
        "ChannelMix",
        "LowPass",
    ]


__all__ = (
    "Equalizer",
    "Karaoke",
    "Timescale",
    "Tremolo",
    "Vibrato",
    "Rotation",
    "Distortion",
    "ChannelMix",
    "LowPass",
    "Filters",
)

def _maybe_unset[T](val: T | None) -> T | msgspec.UnsetType:
    return val if val is not None else msgspec.UNSET


def _unwrap_unset[T](val: T | msgspec.UnsetType) -> T | None:
    return val if val is not msgspec.UNSET else None


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

    def __init__(
        self,
        *,
        band: int,
        gain: float,
    ) -> None:
        super().__init__(
            client=None,
            data=filters.EqualizerFilter(
                band=band,
                gain=gain,
            ),
        )

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.EqualizerFilter) -> Self:
        self = cls(band=data.band, gain=data.gain)
        self._client = client
        return self

    @property
    def band(self) -> int:
        """The target band index (0 to 14)."""
        return self._data.band

    @band.setter
    def band(self, value: int) -> None:
        self._data.band = value

    @property
    def gain(self) -> float:
        """The band gain multiplier (-0.25 to 1.0)."""
        return self._data.gain

    @gain.setter
    def gain(self, value: float) -> None:
        self._data.gain = value


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

    def __init__(
        self,
        *,
        level: float | None = None,
        mono_level: float | None = None,
        filter_band: float | None = None,
        filter_width: float | None = None,
    ) -> None:
        super().__init__(
            client=None,
            data=filters.KaraokeFilter(
                level=_maybe_unset(level),
                mono_level=_maybe_unset(mono_level),
                filter_band=_maybe_unset(filter_band),
                filter_width=_maybe_unset(filter_width),
            ),
        )

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.KaraokeFilter) -> Self:
        self = cls(
            level=_unwrap_unset(data.level),
            mono_level=_unwrap_unset(data.mono_level),
            filter_band=_unwrap_unset(data.filter_band),
            filter_width=_unwrap_unset(data.filter_width),
        )
        self._client = client
        return self

    @property
    def level(self) -> float | None:
        """Overall effect intensity (0.0 to 1.0)."""
        return _unwrap_unset(self._data.level)

    @level.setter
    def level(self, value: float | None) -> None:
        self._data.level = _maybe_unset(value)

    @property
    def mono_level(self) -> float | None:
        """Mono signal amount (0.0 to 1.0)."""
        return _unwrap_unset(self._data.mono_level)

    @mono_level.setter
    def mono_level(self, value: float | None) -> None:
        self._data.mono_level = _maybe_unset(value)

    @property
    def filter_band(self) -> float | None:
        """Center frequency in Hz for the target region."""
        return _unwrap_unset(self._data.filter_band)

    @filter_band.setter
    def filter_band(self, value: float | None) -> None:
        self._data.filter_band = _maybe_unset(value)

    @property
    def filter_width(self) -> float | None:
        """Bandwidth around the filter band in Hz."""
        return _unwrap_unset(self._data.filter_width)

    @filter_width.setter
    def filter_width(self, value: float | None) -> None:
        self._data.filter_width = _maybe_unset(value)


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

    def __init__(
        self,
        *,
        speed: float | None = None,
        pitch: float | None = None,
        rate: float | None = None,
    ) -> None:
        super().__init__(
            client=None,
            data=filters.TimescaleFilter(
                speed=_maybe_unset(speed),
                pitch=_maybe_unset(pitch),
                rate=_maybe_unset(rate),
            ),
        )

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.TimescaleFilter) -> Self:
        self = cls(
            speed=_unwrap_unset(data.speed),
            pitch=_unwrap_unset(data.pitch),
            rate=_unwrap_unset(data.rate),
        )
        self._client = client
        return self

    @property
    def speed(self) -> float | None:
        """Playback speed multiplier (>= 0.0)."""
        return _unwrap_unset(self._data.speed)

    @speed.setter
    def speed(self, value: float | None) -> None:
        self._data.speed = _maybe_unset(value)

    @property
    def pitch(self) -> float | None:
        """Pitch multiplier (>= 0.0)."""
        return _unwrap_unset(self._data.pitch)

    @pitch.setter
    def pitch(self, value: float | None) -> None:
        self._data.pitch = _maybe_unset(value)

    @property
    def rate(self) -> float | None:
        """Internal rate multiplier (>= 0.0)."""
        return _unwrap_unset(self._data.rate)

    @rate.setter
    def rate(self, value: float | None) -> None:
        self._data.rate = _maybe_unset(value)


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

    def __init__(
        self,
        *,
        frequency: float | None = None,
        depth: float | None = None,
    ) -> None:
        super().__init__(
            client=None,
            data=filters.TremoloFilter(
                frequency=_maybe_unset(frequency),
                depth=_maybe_unset(depth),
            ),
        )

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.TremoloFilter) -> Self:
        self = cls(
            frequency=_unwrap_unset(data.frequency),
            depth=_unwrap_unset(data.depth),
        )
        self._client = client
        return self

    @property
    def frequency(self) -> float | None:
        """Oscillation frequency in Hz (> 0.0)."""
        return _unwrap_unset(self._data.frequency)

    @frequency.setter
    def frequency(self, value: float | None) -> None:
        self._data.frequency = _maybe_unset(value)

    @property
    def depth(self) -> float | None:
        """Effect depth (0.0 < x <= 1.0)."""
        return _unwrap_unset(self._data.depth)

    @depth.setter
    def depth(self, value: float | None) -> None:
        self._data.depth = _maybe_unset(value)


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

    def __init__(
        self,
        *,
        frequency: float | None = None,
        depth: float | None = None,
    ) -> None:
        super().__init__(
            client=None,
            data=filters.VibratoFilter(
                frequency=_maybe_unset(frequency),
                depth=_maybe_unset(depth),
            ),
        )

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.VibratoFilter) -> Self:
        self = cls(
            frequency=_unwrap_unset(data.frequency),
            depth=_unwrap_unset(data.depth),
        )
        self._client = client
        return self

    @property
    def frequency(self) -> float | None:
        """Oscillation frequency in Hz (0.0 < x <= 14.0)."""
        return _unwrap_unset(self._data.frequency)

    @frequency.setter
    def frequency(self, value: float | None) -> None:
        self._data.frequency = _maybe_unset(value)

    @property
    def depth(self) -> float | None:
        """Effect depth (0.0 < x <= 1.0)."""
        return _unwrap_unset(self._data.depth)

    @depth.setter
    def depth(self, value: float | None) -> None:
        self._data.depth = _maybe_unset(value)


class Rotation(BaseModel[filters.RotationFilter]):
    """
    Rotates the audio across the stereo channels (panning effect).

    Attributes
    ----------
    rotation_hz: float | None
        Rotation frequency in Hz.
    """

    __slots__ = ()

    def __init__(
        self,
        *,
        rotation_hz: float | None = None,
    ) -> None:
        super().__init__(
            client=None,
            data=filters.RotationFilter(
                rotation_hz=_maybe_unset(rotation_hz),
            ),
        )

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.RotationFilter) -> Self:
        self = cls(
            rotation_hz=_unwrap_unset(data.rotation_hz),
        )
        self._client = client
        return self

    @property
    def rotation_hz(self) -> float | None:
        """Rotation frequency in Hz."""
        return _unwrap_unset(self._data.rotation_hz)

    @rotation_hz.setter
    def rotation_hz(self, value: float | None) -> None:
        self._data.rotation_hz = _maybe_unset(value)


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

    def __init__(
        self,
        *,
        sin_offset: float | None = None,
        sin_scale: float | None = None,
        cos_offset: float | None = None,
        cos_scale: float | None = None,
        tan_offset: float | None = None,
        tan_scale: float | None = None,
    ) -> None:
        super().__init__(
            client=None,
            data=filters.DistortionFilter(
                sin_offset=_maybe_unset(sin_offset),
                sin_scale=_maybe_unset(sin_scale),
                cos_offset=_maybe_unset(cos_offset),
                cos_scale=_maybe_unset(cos_scale),
                tan_offset=_maybe_unset(tan_offset),
                tan_scale=_maybe_unset(tan_scale),
            ),
        )

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.DistortionFilter) -> Self:
        self = cls(
            sin_offset=_unwrap_unset(data.sin_offset),
            sin_scale=_unwrap_unset(data.sin_scale),
            cos_offset=_unwrap_unset(data.cos_offset),
            cos_scale=_unwrap_unset(data.cos_scale),
            tan_offset=_unwrap_unset(data.tan_offset),
            tan_scale=_unwrap_unset(data.tan_scale),
        )
        self._client = client
        return self

    @property
    def sin_offset(self) -> float | None:
        """The sine input offset component."""
        return _unwrap_unset(self._data.sin_offset)

    @sin_offset.setter
    def sin_offset(self, value: float | None) -> None:
        self._data.sin_offset = _maybe_unset(value)

    @property
    def sin_scale(self) -> float | None:
        """The sine scaling component."""
        return _unwrap_unset(self._data.sin_scale)

    @sin_scale.setter
    def sin_scale(self, value: float | None) -> None:
        self._data.sin_scale = _maybe_unset(value)

    @property
    def cos_offset(self) -> float | None:
        """The cosine input offset component."""
        return _unwrap_unset(self._data.cos_offset)

    @cos_offset.setter
    def cos_offset(self, value: float | None) -> None:
        self._data.cos_offset = _maybe_unset(value)

    @property
    def cos_scale(self) -> float | None:
        """The cosine scaling component."""
        return _unwrap_unset(self._data.cos_scale)

    @cos_scale.setter
    def cos_scale(self, value: float | None) -> None:
        self._data.cos_scale = _maybe_unset(value)

    @property
    def tan_offset(self) -> float | None:
        """The tangent input offset component."""
        return _unwrap_unset(self._data.tan_offset)

    @tan_offset.setter
    def tan_offset(self, value: float | None) -> None:
        self._data.tan_offset = _maybe_unset(value)

    @property
    def tan_scale(self) -> float | None:
        """The tangent scaling component."""
        return _unwrap_unset(self._data.tan_scale)

    @tan_scale.setter
    def tan_scale(self, value: float | None) -> None:
        self._data.tan_scale = _maybe_unset(value)


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

    def __init__(
        self,
        *,
        left_to_left: float | None = None,
        left_to_right: float | None = None,
        right_to_left: float | None = None,
        right_to_right: float | None = None,
    ) -> None:
        super().__init__(
            client=None,
            data=filters.ChannelMixFilter(
                left_to_left=_maybe_unset(left_to_left),
                left_to_right=_maybe_unset(left_to_right),
                right_to_left=_maybe_unset(right_to_left),
                right_to_right=_maybe_unset(right_to_right),
            ),
        )

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.ChannelMixFilter) -> Self:
        self = cls(
            left_to_left=_unwrap_unset(data.left_to_left),
            left_to_right=_unwrap_unset(data.left_to_right),
            right_to_left=_unwrap_unset(data.right_to_left),
            right_to_right=_unwrap_unset(data.right_to_right),
        )
        self._client = client
        return self

    @property
    def left_to_left(self) -> float | None:
        """The contribution of the left input channel to the left output channel."""
        return _unwrap_unset(self._data.left_to_left)

    @left_to_left.setter
    def left_to_left(self, value: float | None) -> None:
        self._data.left_to_left = _maybe_unset(value)

    @property
    def left_to_right(self) -> float | None:
        """The contribution of the left input channel to the right output channel."""
        return _unwrap_unset(self._data.left_to_right)

    @left_to_right.setter
    def left_to_right(self, value: float | None) -> None:
        self._data.left_to_right = _maybe_unset(value)

    @property
    def right_to_left(self) -> float | None:
        """The contribution of the right input channel to the left output channel."""
        return _unwrap_unset(self._data.right_to_left)

    @right_to_left.setter
    def right_to_left(self, value: float | None) -> None:
        self._data.right_to_left = _maybe_unset(value)

    @property
    def right_to_right(self) -> float | None:
        """The contribution of the right input channel to the right output channel."""
        return _unwrap_unset(self._data.right_to_right)

    @right_to_right.setter
    def right_to_right(self, value: float | None) -> None:
        self._data.right_to_right = _maybe_unset(value)


class LowPass(BaseModel[filters.LowPassFilter]):
    """
    Suppresses higher frequencies in the audio signal.

    Attributes
    ----------
    smoothing: float | None
        Smoothing factor (x > 1.0).
    """

    __slots__ = ()

    def __init__(self, *, smoothing: float | None = None) -> None:
        super().__init__(
            client=None,
            data=filters.LowPassFilter(smoothing=_maybe_unset(smoothing)),
        )

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.LowPassFilter) -> Self:
        self = cls(
            smoothing=_unwrap_unset(data.smoothing),
        )
        self._client = client
        return self

    @property
    def smoothing(self) -> float | None:
        """Smoothing factor (x > 1.0)."""
        return _unwrap_unset(self._data.smoothing)

    @smoothing.setter
    def smoothing(self, value: float | None) -> None:
        self._data.smoothing = _maybe_unset(value)


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
        "_volume",
    )

    def __init__(
        self,
        *,
        equalizer: list[Equalizer] | None = None,
        karaoke: Karaoke | None = None,
        timescale: Timescale | None = None,
        tremolo: Tremolo | None = None,
        vibrato: Vibrato | None = None,
        rotation: Rotation | None = None,
        distortion: Distortion | None = None,
        channel_mix: ChannelMix | None = None,
        low_pass: LowPass | None = None,
        volume: float = 1.0,
    ) -> None:
        self._equalizer = equalizer
        self._karaoke = karaoke
        self._timescale = timescale
        self._tremolo = tremolo
        self._vibrato = vibrato
        self._rotation = rotation
        self._distortion = distortion
        self._channel_mix = channel_mix
        self._low_pass = low_pass
        self._volume = volume

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.PlayerFilters) -> Self:
        equalizer = [
            Equalizer._from_data(client, e) for e in (_unwrap_unset(data.equalizer) or [])
        ]
        karaoke = cls._wrap(Karaoke, client, data.karaoke)
        timescale = cls._wrap(Timescale, client, data.timescale)
        tremolo = cls._wrap(Tremolo, client, data.tremolo)
        vibrato = cls._wrap(Vibrato, client, data.vibrato)
        rotation = cls._wrap(Rotation, client, data.rotation)
        distortion = cls._wrap(Distortion, client, data.distortion)
        channel_mix = cls._wrap(ChannelMix, client, data.channel_mix)
        low_pass = cls._wrap(LowPass, client, data.low_pass)
        volume = _unwrap_unset(data.volume)

        self = cls(
            equalizer=equalizer,
            karaoke=karaoke,
            timescale=timescale,
            tremolo=tremolo,
            vibrato=vibrato,
            rotation=rotation,
            distortion=distortion,
            channel_mix=channel_mix,
            low_pass=low_pass,
            volume=volume if volume is not None else 1.0,
        )
        self._client = client
        return self

    @classmethod
    def _wrap[C: FilterModelTypes](cls, model: type[C], client: Client[Any], data: Any) -> C | None:
        return model._from_data(client=client, data=data) if data is not msgspec.UNSET else None

    @property
    def volume(self) -> float:
        """The linear volume multiplier (0.0 to 5.0). Defaults to 1.0."""
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = value

    @property
    def equalizer(self) -> list[Equalizer]:
        """A list of active equalizer bands."""
        return self._equalizer or []

    @equalizer.setter
    def equalizer(self, value: list[Equalizer] | None) -> None:
        self._equalizer = value

    @property
    def karaoke(self) -> Karaoke | None:
        """The active karaoke filter, if set."""
        return self._karaoke

    @karaoke.setter
    def karaoke(self, value: Karaoke | None) -> None:
        self._karaoke = value

    @property
    def timescale(self) -> Timescale | None:
        """The active timescale filter, if set."""
        return self._timescale

    @timescale.setter
    def timescale(self, value: Timescale | None) -> None:
        self._timescale = value

    @property
    def tremolo(self) -> Tremolo | None:
        """The active tremolo filter, if set."""
        return self._tremolo

    @tremolo.setter
    def tremolo(self, value: Tremolo | None) -> None:
        self._tremolo = value

    @property
    def vibrato(self) -> Vibrato | None:
        """The active vibrato filter, if set."""
        return self._vibrato

    @vibrato.setter
    def vibrato(self, value: Vibrato | None) -> None:
        self._vibrato = value

    @property
    def rotation(self) -> Rotation | None:
        """The active rotation filter, if set."""
        return self._rotation

    @rotation.setter
    def rotation(self, value: Rotation | None) -> None:
        self._rotation = value

    @property
    def distortion(self) -> Distortion | None:
        """The active distortion filter, if set."""
        return self._distortion

    @distortion.setter
    def distortion(self, value: Distortion | None) -> None:
        self._distortion = value

    @property
    def channel_mix(self) -> ChannelMix | None:
        """The active channel mix filter, if set."""
        return self._channel_mix

    @channel_mix.setter
    def channel_mix(self, value: ChannelMix | None) -> None:
        self._channel_mix = value

    @property
    def low_pass(self) -> LowPass | None:
        """The active low pass filter, if set."""
        return self._low_pass

    @low_pass.setter
    def low_pass(self, value: LowPass | None) -> None:
        self._low_pass = value

    @property
    def plugin_filters(self) -> dict[str, Any]:
        """A dictionary of raw plugin-defined filter payloads."""
        return self._data.plugin_filters

    @property
    def payload(self) -> filters.PlayerFilters:
        """Returns the underlying msgspec schema for API requests."""
        return self._generate_schema()

    def _generate_schema(self) -> filters.PlayerFilters:
        equalizer = [e._data for e in self.equalizer] or msgspec.UNSET
        karaoke = self.karaoke._data if self.karaoke else msgspec.UNSET
        timescale = self.timescale._data if self.timescale else msgspec.UNSET
        tremolo = self.tremolo._data if self.tremolo else msgspec.UNSET
        vibrato = self.vibrato._data if self.vibrato else msgspec.UNSET
        rotation = self.rotation._data if self.rotation else msgspec.UNSET
        distortion = self.distortion._data if self.distortion else msgspec.UNSET
        channel_mix = self.channel_mix._data if self.channel_mix else msgspec.UNSET
        low_pass = self.low_pass._data if self.low_pass else msgspec.UNSET
        return filters.PlayerFilters(
            volume=self.volume,
            equalizer=equalizer,
            karaoke=karaoke,
            timescale=timescale,
            tremolo=tremolo,
            vibrato=vibrato,
            rotation=rotation,
            distortion=distortion,
            channel_mix=channel_mix,
            low_pass=low_pass,
        )
