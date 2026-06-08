import asyncio
from typing import Dict, Any

class EventBroadcaster:
    """
    Manages active SSE (Server-Sent Event) client connections.
    Distributes events (like flag updates) to all connected clients.
    """
    def __init__(self):
        # A list to hold active asyncio Queues, one for each connected client
        self._listeners: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        """
        Creates a new queue for a connecting client and adds it to the listeners list.
        """
        q = asyncio.Queue()
        self._listeners.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        """
        Removes a queue when a client disconnects. Crucial for preventing memory leaks.
        """
        if q in self._listeners:
            self._listeners.remove(q)

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """
        Pushes a generic event to all connected queues concurrently.
        """
        message = {"event": event_type, "data": data}
        for q in self._listeners:
            # We use put_nowait to avoid blocking if a specific queue is unexpectedly full
            try:
                q.put_nowait(message)
            except asyncio.QueueFull:
                pass

# This singleton instance will be imported by our FastAPI routers

broadcaster = EventBroadcaster()