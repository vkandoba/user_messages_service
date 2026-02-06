from pydantic import BaseModel
from typing import List, Optional, Union

from configs.config_utils import Period


class RequiresBefore(BaseModel):
    type: str = "requires_before"
    event_type: str
    within_period: Optional[Period]

class HasLimit(BaseModel):
    type: str = "has_limit"
    max: int
    within_period: Optional[Period]

Prerequisite = Union[RequiresBefore, HasLimit]

class MessageRule(BaseModel):
    message: str
    on_signal: str
    template: str
    channel: str
    reason: str
    prerequisites: Optional[List[Prerequisite]] = None

class MessageRulesConfig(BaseModel):
    message_rules: List[MessageRule]