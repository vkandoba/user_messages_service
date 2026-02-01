from pydantic import BaseModel
from typing import Optional


from event_signals.user_event_to_signal_config import UserEventToSignalConfig
from user_events.user_event_types import UserEvent


class EventSignal(BaseModel):
    name: str
    event_type: str


class EventSignalService:
    def __init__(self, config: UserEventToSignalConfig):
        self.config = config

    def GetEventSignal(self, event: UserEvent) -> Optional[EventSignal]:
        event_type_config = self.config.user_event_types.get(event.event_type)
        if not event_type_config:
            # TODO: log exception
            return None

        if event_type_config.cases:
            for case in event_type_config.cases:
                try:
                    if eval(case.condition, {"user_traits": event.user_traits, "properties": event.properties}):
                        return EventSignal(name=case.signal, event_type=event.event_type)
                except Exception:
                    # TODO: log exception
                    continue

        return EventSignal(name=event_type_config.default_signal, event_type=event.event_type)
