"""
MIT License

Copyright (c) 2019-2025 PythonistaGuild, EvieePy; 2025-present ReWaveLink Development Team.

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

import asyncio
from collections.abc import Callable
import sys
from typing import TYPE_CHECKING, Any, Coroutine, ParamSpec, TypeVar, overload

if TYPE_CHECKING:
    from relink.gateway.client import Client

if sys.version_info < (3, 14):
    from asyncio import iscoroutinefunction as iscoro
else:
    from inspect import iscoroutinefunction as iscoro

P = ParamSpec("P")
T = TypeVar("T")
EventCallback = Callable[P, Coroutine[Any, Any, T]]


class EventRouter:
    """Represents an event router that handles receiving and dispatching events
    on a :class:`relink.gateway.Player`.
    """

    _client: Client[Any]
    _event_map: dict[str, list[EventCallback[..., Any]]]
    _task_set: set[asyncio.Task[Any]]

    def __init__(self, client: Client[Any]) -> None:
        self._client = client
        self._event_map = {}
        self._task_set = set()

    @overload
    def listen(self, func: EventCallback[P, T], /) -> EventCallback[P, T]: ...

    @overload
    def listen(
        self, *, event: str
    ) -> Callable[[EventCallback[P, T]], EventCallback[P, T]]: ...

    @overload
    def listen(
        self, *, event: None = None
    ) -> Callable[[EventCallback[P, T]], EventCallback[P, T]]: ...

    def listen(
        self, func: EventCallback[P, T] | None = None, event: str | None = None
    ) -> Any:
        """Registers a new event listener.

        This is a decorator that can be used in three different ways:

            .. code-block:: python3

                @router.listen
                async def on_event():
                    ...

                @router.listen()
                async def on_event():
                    ...

                @router.listen("event")
                async def function():
                    ...

        Parameters
        ----------
        event: :class:`str` | :data:`None`
            The event to listen to. If this is ``None`` or not set, it extracts the event
            name from the decorated function.
        """

        # case 1 -> func is not None: invoked without parenthesis
        if func is not None:
            event_name = func.__name__.removeprefix("on_")

            if not iscoro(func):
                raise TypeError("event callbacks must be coroutines")

            try:
                self._event_map[event_name].append(func)
            except KeyError:
                self._event_map[event_name] = [func]

            return func

        # case 2 & 3 -> name is maybe None: invoked with parenthesis
        def inner(func: EventCallback[P, T]) -> EventCallback[P, T]:
            event_name = event
            if event_name is None:
                event_name = func.__name__.removeprefix("on_")

            if not iscoro(func):
                raise TypeError("event callbacks must be coroutines")

            try:
                self._event_map[event_name].append(func)
            except KeyError:
                self._event_map[event_name] = [func]
            return func

        return inner

    def _inner_dispatch(self, event: str, coro: Coroutine[Any, Any, Any]) -> None:
        task = asyncio.create_task(
            coro, name=f"relink-event-dispatcher:{event}-{id(coro):#x}"
        )
        self._task_set.add(task)
        task.add_done_callback(self._task_set.discard)

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Dispatches all event listeners for ``event``.

        Parameters
        ----------
        event: :class:`str`
            The event to be dispatched. This must not be prefixed with ``on_``.
        *args: Any
            The positional arguments to pass to the event's callbacks.
        **kwargs: Any
            The keyword arguments to pass to the event's callbacks.
        """

        for func in self._event_map.get(event, []):
            self._inner_dispatch(event, func(*args, **kwargs))
