import logging
from user_events.user_event_to_signal_config import UserEventToSignalConfig
from user_event_types import UserEventBase, IncomingUserEvent


class UserEventWithSignal(UserEventBase):
    signal: str

class UserEventService:
    def __init__(self, config: UserEventToSignalConfig):
        self.config = config

    def get_event_with_signals(self, event: IncomingUserEvent) -> list[UserEventWithSignal]:
        event_type_config = self.config.user_event_types.get(event.type)
        if not event_type_config:
            logging.error(f"No signal config found for event type: {event.type}")
            raise ValueError(f"No signal config found for event type: {event.type}")

        result_events: list[UserEventWithSignal] = []
        if event_type_config.cases:
            for case in event_type_config.cases:
                try:
                    if eval(case.condition, {"user_traits": event.user_traits, "properties": event.properties}):
                        result_events.append(UserEventWithSignal(
                            signal=case.signal,
                            user_id=event.user_id,
                            event_type=event.type,
                            event_timestamp=event.timestamp,
                        ))
                except Exception as e:
                    logging.error(f"Error evaluating condition '{case.condition}' for event type: {event.type} - {e}")

        if not result_events:
            return [UserEventWithSignal(
                signal=event_type_config.default_signal,
                user_id=event.user_id,
                event_type=event.type,
                event_timestamp=event.timestamp,
            )]

        return result_events
