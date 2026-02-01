from typing import List
from datetime import datetime, timedelta

from event_signals.event_signal_service import EventSignal
from message_rules.message_rules_config import MessageRulesConfig, RequiresBefore
from user_events.user_event_repository import UserEventRepositoryBase
from user_events.user_event_types import UserEvent


class MessageRulesResolver:
    def __init__(self, config: MessageRulesConfig, user_event_repository: UserEventRepositoryBase):
        self.config = config
        self.user_event_repository = user_event_repository

    def apply_rules(self, user_id: str, event_signal: EventSignal) -> List[dict]:
        resolved_messages = []

        for rule in self.config.message_rules:
            # TODO: create map signal -> rules
            if rule.on_signal == event_signal.name:
                if rule.requires_event_history:
                    # TODO: add timestamp
                    event_history = self.user_event_repository.get_recent(user_id=user_id, n=100)
                    if not self._check_event_history(rule.requires_before, event_history):
                        continue

                resolved_messages.append({
                    "message": rule.message,
                    "reason": rule.reason
                })

        return resolved_messages

    def _check_event_history(self,
                             requires_before: List[RequiresBefore],
                             event_history: List[UserEvent]) -> bool:
        for expected in requires_before:
            expected_event_type = expected.event_type
            required_period = timedelta(hours=expected.within_period) if expected.within_period else None
            event_found = False

            for event in event_history:
                if event["event_type"] == expected_event_type:
                    if required_period:
                        # TODO: change to current_event
                        if datetime.now() - event.timestamp <= required_period:
                            event_found = True
                            break
                    else:
                        event_found = True
                        break

            if not event_found:
                return False

        return True