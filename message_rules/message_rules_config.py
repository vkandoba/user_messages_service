from pydantic import BaseModel
from typing import List, Optional


class RequiresBefore(BaseModel):
    event_type: str
    within_period: Optional[int]  # In hours


class MessageRule(BaseModel):
    message: str
    on_signal: str
    template: str
    channel: str
    reason: str
    requires_before: Optional[List[RequiresBefore]] = None


class MessageRulesConfig(BaseModel):
    message_rules: List[MessageRule]