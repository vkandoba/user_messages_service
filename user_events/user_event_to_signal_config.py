from pydantic import BaseModel
from typing import List, Optional


class EventCase(BaseModel):
    signal: str
    condition: str


class EventConfig(BaseModel):
    default_signal: str
    cases: Optional[List[EventCase]] = None


class UserEventToSignalConfig(BaseModel):
    user_event_types: dict[str, EventConfig]