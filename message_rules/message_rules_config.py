from enum import Enum

from pydantic import BaseModel
from typing import List, Optional, Union


class Period(str, Enum):
    CALENDAR_DAY = "calendar_day"
    DAY = "24h"

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