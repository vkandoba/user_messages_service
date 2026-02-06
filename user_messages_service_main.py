import hashlib
import yaml
from http.client import HTTPException
from typing import List
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

from user_events.event_signal_service import UserEventService
from user_events.user_event_to_signal_config import UserEventToSignalConfig


app = FastAPI()


processed_events_db = set()
user_event_logs_db = {}


user_events_config = {}


class ProcessResult(BaseModel):
    user_id: str
    event_type: str
    status: str
    reason: str


class AuditLogEntry(BaseModel):
    timestamp: datetime
    event_type: str
    action: str
    reason: str


class AuditResponse(BaseModel):
    user_id: str
    history: List[AuditLogEntry]


def load_user_event_config(filepath: str) -> UserEventToSignalConfig:
    with open(filepath, "r") as file:
        raw_config = yaml.safe_load(file)
    return UserEventToSignalConfig(**raw_config)


event_signal_service = UserEventService(load_user_event_config("configs/user_event_signals_map_config.yaml"))


def get_idempotency_key(event: UserEvent) -> str:
    raw_data = f"{event.user_id}-{event.type}-{event.timestamp.isoformat()}"
    return hashlib.md5(raw_data.encode()).hexdigest()


def handle_event(event: UserEvent) -> ProcessResult:
    idem_key = get_idempotency_key(event)

    if idem_key in processed_events_db:
        return ProcessResult(
            user_id=event.user_id,
            event_type=event.type,
            status="skipped",
            reason="duplicate_detected"
        )

    processed_events_db.add(idem_key)

    if event.user_id not in user_event_logs_db:
        user_event_logs_db[event.user_id] = []

    if not event.user_traits.marketing_opt_in:
        log_entry = {
            "action": "skipped",
            "reason": "user_opted_out",
            "timestamp": datetime.now()
        }
        user_event_logs_db[event.user_id].append(log_entry)

        return ProcessResult(
            user_id=event.user_id,
            event_type=event.type,
            status="skipped",
            reason="user_opted_out"
        )

    log_entry = {
        "action": "sent",
        "reason": "criteria_met",
        "timestamp": datetime.now()
    }
    user_event_logs_db[event.user_id].append(log_entry)

    event_signal_service.get_event_with_signal(event)

    return ProcessResult(
        user_id=event.user_id,
        event_type=event.type,
        status="success",
        reason="message_triggered"
    )


@app.post("/api/v1/event", response_model=ProcessResult)
def ingest_single_event(event: UserEvent):
    return handle_event(event)


@app.post("/api/v1/events", response_model=List[ProcessResult])
def ingest_batch_events(events: List[UserEvent]):
    results = []
    for event in events:
        result = handle_event(event)
        results.append(result)
    return results


@app.get("/audit/{user_id}", response_model=AuditResponse)
def get_user_audit_log(user_id: str):
    if user_id not in user_event_logs_db:
        raise HTTPException(status_code=404, detail="User history not found")

    return AuditResponse(
        user_id=user_id,
        history=user_event_logs_db[user_id]
    )

# TODO: use on_event
@app.on_event("startup")
def startup_event():
    # TODO: maybe use it
    print("Config loaded:")