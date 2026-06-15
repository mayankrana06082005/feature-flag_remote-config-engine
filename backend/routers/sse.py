import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

active_connections = []

@router.get("/stream")
async def stream(request: Request):
    queue = asyncio.Queue()
    active_connections.append(queue)

    async def event_generator():
        # 1. Immediate greeting so the browser knows the connection is alive!
        yield {
            "event": "connected",
            "data": "Stream established"
        }
        
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                # 2. Wait for a database update, but wake up every 15 seconds!
                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {
                        "event": "update",
                        "data": event_data
                    }
                except asyncio.TimeoutError:
                    # 3. Send a heartbeat ping to keep Edge from killing the socket
                    yield {
                        "event": "ping",
                        "data": "keep-alive"
                    }
        except asyncio.CancelledError:
            pass
        finally:
            if queue in active_connections:
                active_connections.remove(queue)

    return EventSourceResponse(event_generator())

async def broadcast_update():
    for connection_queue in active_connections:
        await connection_queue.put("state_mutated")