from fastapi import APIRouter
from db.connection_events import get_connection_events

router = APIRouter(prefix='/connection-events')

@router.get("/{from_dt}")
async def connection_events_req(from_dt: str):
    events = get_connection_events(from_dt)
    return events
