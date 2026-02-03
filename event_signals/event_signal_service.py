from typing import Optional

from event_signals.user_event_to_signal_config import UserEventToSignalConfig
from user_events.user_event_types import UserEventBase, IncomingUserEvent


class UserEventWithSignal(UserEventBase):
    signal: str

class EventSignalService:
    def __init__(self, config: UserEventToSignalConfig):
        self.config = config

    def get_event_with_signal(self, event: IncomingUserEvent) -> Optional[UserEventWithSignal]:
        event_type_config = self.config.user_event_types.get(event.type)
        if not event_type_config:
            raise ValueError("TODO")

        if event_type_config.cases:
            for case in event_type_config.cases:
                try:
                    if eval(case.condition, {"user_traits": event.user_traits, "properties": event.properties}):
                        return UserEventWithSignal(signal=case.signal, **event.model_dump())
                except Exception:
                    raise RuntimeError("TODO")

        return UserEventWithSignal(signal=event_type_config.default_signal, **event.model_dump())
