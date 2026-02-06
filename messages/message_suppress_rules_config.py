from pydantic import BaseModel
from typing import Optional, List

from config_utils import Period


class SuppressRule(BaseModel):
    message: str
    max_sends: int
    within_period: Optional[Period]

class MessageSuppressRulesConfig(BaseModel):
    message_suppress_rules: List[SuppressRule]