from pydantic import BaseModel
from typing import List, Optional

from config_utils import Period


class RequiresBefore(BaseModel):
    event_type: str
    within_period: Optional[Period]

class HasLimit(BaseModel):
    max: int
    within_period: Optional[Period]

class MessageRule(BaseModel):
    message: str
    on_signal: str
    template: str
    channel: str
    reason: str
    requires_before: Optional[List[RequiresBefore]] = None
    has_limit: Optional[HasLimit] = None

class MessageRulesConfig(BaseModel):
    message_rules: List[MessageRule]