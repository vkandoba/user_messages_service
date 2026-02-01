from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr


class UserTraits(BaseModel):
    email: EmailStr
    country: str
    marketing_opt_in: bool
    risk_segment: Optional[str] = None


class UserEvent(BaseModel):
    user_id: str
    type: str
    timestamp: datetime
    properties: Dict[str, Any]
    user_traits: UserTraits

# TODO: add properties to UserEvent for payment_failed