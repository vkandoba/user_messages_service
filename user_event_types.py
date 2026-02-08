from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, model_validator, ValidationError


class UserTraits(BaseModel):
    email: Optional[EmailStr] = None
    country: Optional[str] = None
    marketing_opt_in: Optional[bool] = None
    risk_segment: Optional[str] = None

class PaymentFailedProperties(BaseModel):
    amount: float
    attempt_number: int
    failure_reason: str

class UserEventBase(BaseModel):
    user_id: str
    type: str = Field(alias="event_type")
    timestamp: datetime = Field(alias="event_timestamp")

class IncomingUserEvent(UserEventBase):
    user_traits: Optional[UserTraits]
    properties: Optional[PaymentFailedProperties] | Dict[str, Any]

    @model_validator(mode="after")
    def validate_event(self):
        if self.type == "payment_failed":
            if not isinstance(self.properties, PaymentFailedProperties):
                try:
                    self.properties = PaymentFailedProperties(**self.properties)
                except (TypeError, ValidationError) as e:
                    raise ValueError(f"Invalid properties for 'payment_failed': {e}")
        return self