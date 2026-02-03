from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, model_validator, ValidationError


class UserTraits(BaseModel):
    email: EmailStr
    country: str
    marketing_opt_in: bool
    risk_segment: Optional[str] = None


class PaymentFailedProperties(BaseModel):
    amount: float
    attempt_number: int
    failure_reason: str

class UserEventBase(BaseModel):
    user_id: str
    type: str
    timestamp: datetime

class IncomingUserEvent(UserEventBase):
    properties: Optional[PaymentFailedProperties] | Dict[str, Any]
    user_traits: UserTraits

    @model_validator(mode="after")
    def validate_event(self):
        if self.type == "payment_failed":
            if not isinstance(self.properties, PaymentFailedProperties):
                try:
                    self.properties = PaymentFailedProperties(**self.properties)
                except (TypeError, ValidationError) as e:
                    raise ValueError(f"Invalid properties for 'payment_failed': {e}")
        return self