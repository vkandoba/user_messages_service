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
    event_type: str
    event_timestamp: datetime
    properties: Dict[str, Any]
    user_traits: UserTraits
