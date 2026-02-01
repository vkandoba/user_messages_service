from pydantic import BaseModel, Field
from typing import Optional, List

class SuppressRule(BaseModel):
    message: str
    max_sends: int
    period: Optional[str] = Field(None, description="Optional period for suppression, e.g., 'calendar_day'.")

class MessageSuppressRulesConfig(BaseModel):
    message_suppress_rules: List[SuppressRule]