from user_events.user_event_to_signal_config import UserEventToSignalConfig
from user_event_types import UserEventBase, IncomingUserEvent


class UserEventWithSignal(UserEventBase):
    signal: str

class UserEventService:
    def __init__(self, config: UserEventToSignalConfig):
        self.config = config

    def get_event_with_signal(self, event: IncomingUserEvent) -> UserEventWithSignal:
        event_type_config = self.config.user_event_types.get(event.type)
        if not event_type_config:
            raise ValueError("TODO")

        if event_type_config.cases:
            for case in event_type_config.cases:
                try:
                    if eval(case.condition, {"user_traits": event.user_traits, "properties": event.properties}):
                        return UserEventWithSignal(
                            signal=case.signal,
                            user_id=event.user_id,
                            event_type=event.type,
                            event_timestamp=event.timestamp,
                        )
                except Exception as e:
                    raise RuntimeError("TODO")

        return UserEventWithSignal(signal=event_type_config.default_signal, **event.model_dump())
