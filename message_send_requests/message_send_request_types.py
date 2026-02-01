from datetime import datetime
from pydantic import BaseModel

from messages.message_types import Message


class MessageSendRequest(BaseModel):
    timestamp: datetime
    message: Message