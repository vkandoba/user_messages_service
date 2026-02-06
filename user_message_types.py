from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


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