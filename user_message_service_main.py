import logging
from fastapi import FastAPI

from user_event_types import IncomingUserEvent
from user_message_service_init import user_message_service


AUDIT_RECENT_EVENTS_COUNT = 5


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()


@app.post("/api/v1/event")
async def ingest_event(event: IncomingUserEvent):
    logging.info(f"Received new event {event.type} for user {event.user_id} on {event.timestamp}")
    user_message_service.ingest_event(event)
    return {}


@app.get("/api/v1/{user_id}/audit")
async def get_audit_log(user_id: str):
    recent_events, messages = user_message_service.get_audit(user_id, AUDIT_RECENT_EVENTS_COUNT)
    return {
        "recent_events": recent_events,
        "message_requests": messages
    }
