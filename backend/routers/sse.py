from fastapi import APIRouter, Request, Query
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

from services.broadcaster import broadcaster
from services.targeting import evaluate_flag


router = APIRouter(tags=["Stream"])

@router.get("/stream")
async def stream(
    request: Request, 
    userId: str = Query(..., description="Unique ID of the connecting user"), 
    groups: str = Query("", description="Comma-separated list of groups")
):
    """
    Maintains an open SSE connection. Evaluates targeting rules on the fly 
    and pushes personalized updates down the stream.
    """
    q = broadcaster.subscribe()
    
    user_context = {
        "userId": userId,
        "groups": [g.strip() for g in groups.split(",")] if groups else []
    }
    
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    event = await asyncio.wait_for(q.get(), timeout=15.0)
                    
                    if event["event"] == "flag_updated":
                        flag_data = event["data"]
                        is_enabled = evaluate_flag(flag_data, user_context)
                        
                        payload = {"id": flag_data["id"], "enabled": is_enabled}
                        yield {"event": "flag_updated", "data": json.dumps(payload)}
                    
                    elif event["event"] == "config_updated":
                        yield {"event": "config_updated", "data": json.dumps(event["data"])}
                        
                except asyncio.TimeoutError:
                    pass
        finally:
            broadcaster.unsubscribe(q)
            
    return EventSourceResponse(event_generator())