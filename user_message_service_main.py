from fastapi import FastAPI

from user_event_types import IncomingUserEvent
from user_message_service_init import user_message_service


app = FastAPI()


@app.post("/api/v1/event")
async def ingest_event(event: IncomingUserEvent):
    try:
        user_message_service.ingest_event(event)
        return True
    except Exception as e:
        return False