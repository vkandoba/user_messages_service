import hashlib
import yaml
from http.client import HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()


processed_events_db = set()
user_event_logs_db = {}


user_events_config = {}


class UserTraits(BaseModel):
    email: EmailStr
    country: str
    marketing_opt_in: bool
    risk_segment: Optional[str] = None


class UserEvent(BaseModel):
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


class AuditLogEntry(BaseModel):
    timestamp: datetime
    event_type: str
    action: str
    reason: str


class AuditResponse(BaseModel):
    user_id: str
    history: List[AuditLogEntry]


def load_config():
    global user_events_config
    with open("user_events_config.yaml", "r") as config_file:
        user_events_config = yaml.safe_load(config_file)


def get_event_name(event: UserEvent) -> str:
    event_config = user_events_config.get("user_events", {}).get(event.event_type, None)

    if not event_config:
        return event.event_type

    for case in event_config.get("cases", []):
        condition = case.get("condition")
        try:
            if eval(condition, {"user_traits": event.user_traits, "properties": event.properties}):
                return case.get("name", event_config.get("default_name"))
        except Exception:
            # TODO: log error
            continue

    return event_config.get("default_name", event.event_type)



def get_idempotency_key(event: UserEvent) -> str:
    raw_data = f"{event.user_id}-{event.event_type}-{event.event_timestamp.isoformat()}"
    return hashlib.md5(raw_data.encode()).hexdigest()


def handle_event(event: UserEvent) -> ProcessResult:
    idem_key = get_idempotency_key(event)

    if idem_key in processed_events_db:
        return ProcessResult(
            user_id=event.user_id,
            event_type=event.event_type,
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
            event_type=event.event_type,
            status="skipped",
            reason="user_opted_out"
        )

    log_entry = {
        "action": "sent",
        "reason": "criteria_met",
        "timestamp": datetime.now()
    }
    user_event_logs_db[event.user_id].append(log_entry)

    return ProcessResult(
        user_id=event.user_id,
        event_type=event.event_type,
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
    load_config()
    print("Config loaded:", user_events_config)