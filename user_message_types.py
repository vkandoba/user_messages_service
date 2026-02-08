from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

from user_event_types import IncomingUserEvent


class Channel(str, Enum):
    sms = "sms"
    email = "email"
    internal_alert = "internal_alert"

class Message(BaseModel):
    user_id: str
    name: str
    channel: Channel
    template: str
    reason: str

class MessageSendRequestStatus(Enum):
    SENT = "sent"
    SUPPRESSED = "suppressed"

class MessageSendRequest(BaseModel):
    timestamp: datetime
    message: Message
    status: MessageSendRequestStatus
    suppress_reason: Optional[str]

class UserAudit(BaseModel):
    recent_events: List[IncomingUserEvent]
    messages: List[MessageSendRequest]