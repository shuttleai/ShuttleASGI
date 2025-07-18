"""
This module offer built-in functions for Server Sent Events.
"""

from typing import AsyncIterable, Callable, List, Optional, Tuple

from shuttleasgi.contents import ServerSentEvent, StreamedContent, TextServerSentEvent, DONEServerSentEvent
from shuttleasgi.messages import Response
from shuttleasgi.scribe import write_sse

__all__ = [
    "ServerSentEvent",
    "DONEServerSentEvent",
    "TextServerSentEvent",
    "ServerSentEventsContent",
    "ServerSentEventsResponse",
    "EventsProvider",
]


EventsProvider = Callable[[], AsyncIterable[ServerSentEvent]]


class ServerSentEventsContent(StreamedContent):
    """
    A specialized kind of StreamedContent that can be used to stream
    Server-Sent Events to a client.
    """

    def __init__(self, events_provider: EventsProvider):
        super().__init__(b"text/event-stream", self.write_events(events_provider))

    @staticmethod
    def write_events(
        events_provider: EventsProvider,
    ) -> Callable[[], AsyncIterable[bytes]]:
        async def write_events():
            async for event in events_provider():
                yield write_sse(event)

        return write_events

_DEFAULT_HEADERS = [
    (b"Cache-Control", b"no-cache"),
    (b"Connection", b"Keep-Alive"),
    (b"X-Accel-Buffering", b"no")
]

class ServerSentEventsResponse(Response):
    """
    An Response type that can be used to stream Server-Sent Events to a client.
    """

    def __init__(
        self,
        events_provider: EventsProvider,
        status: int = 200,
        headers: Optional[List[Tuple[bytes, bytes]]] = None,
    ) -> None:
        if headers is None:
            headers = _DEFAULT_HEADERS
        super().__init__(status, headers, ServerSentEventsContent(events_provider))
