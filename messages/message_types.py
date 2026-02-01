from enum import Enum
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
