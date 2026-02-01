import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

processed_events_db = set()
event_logs_db = []


class UserTraits(BaseModel):
    email: EmailStr
    country: str
    marketing_opt_in: bool
    risk_segment: Optional[str] = None


class InboundEvent(BaseModel):
    user_id: str
    event_type: str
    event_timestamp: datetime
    properties: Dict[str, Any]
    user_traits: UserTraits


class ProcessResult(BaseModel):
    user_id: str
    event_type: str
    status: str
    reason: str


def get_deduplication_key(event: InboundEvent) -> str:
    raw_data = f"{event.user_id}-{event.event_type}-{event.event_timestamp.isoformat()}"
    return hashlib.md5(raw_data.encode()).hexdigest()


def process_single_event(event: InboundEvent) -> ProcessResult:
    dedup_key = get_deduplication_key(event)

    if dedup_key in processed_events_db:
        return ProcessResult(
            user_id=event.user_id,
            event_type=event.event_type,
            status="skipped",
            reason="duplicate_detected"
        )

    processed_events_db.add(dedup_key)

    if not event.user_traits.marketing_opt_in:
        log_entry = {
            "user_id": event.user_id,
            "action": "skipped",
            "reason": "user_opted_out",
            "timestamp": datetime.now()
        }
        event_logs_db.append(log_entry)

        return ProcessResult(
            user_id=event.user_id,
            event_type=event.event_type,
            status="skipped",
            reason="user_opted_out"
        )

    log_entry = {
        "user_id": event.user_id,
        "action": "sent",
        "reason": "criteria_met",
        "timestamp": datetime.now()
    }
    event_logs_db.append(log_entry)

    return ProcessResult(
        user_id=event.user_id,
        event_type=event.event_type,
        status="success",
        reason="message_triggered"
    )


@app.post("/api/v1/event", response_model=ProcessResult)
def ingest_single_event(event: InboundEvent):
    return process_single_event(event)


@app.post("/api/v1/events", response_model=List[ProcessResult])
def ingest_batch_events(events: List[InboundEvent]):
    results = []
    for event in events:
        result = process_single_event(event)
        results.append(result)
    return results