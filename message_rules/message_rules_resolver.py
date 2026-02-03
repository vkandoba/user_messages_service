from typing import List
from datetime import datetime, timedelta

from event_signals.event_signal_service import EventSignal
from message_rules.message_rules_config import MessageRulesConfig, RequiresBefore, Period, HasLimit
from message_send_requests.message_send_request_repository import MessageSendRequestRepositoryBase
from user_events.user_event_repository import UserEventRepositoryBase


class MessageRulesResolver:
    def __init__(self,
                 config: MessageRulesConfig,
                 user_event_repository: UserEventRepositoryBase,
                 sent_messages_repository: MessageSendRequestRepositoryBase
        ):
        self.config = config
        self.user_event_repository = user_event_repository
        self.sent_messages_repository = sent_messages_repository

    def apply_rules(self, user_id: str, event_signal: EventSignal) -> List[dict]:
        resolved_messages = []

        for rule in self.config.message_rules:
            # TODO: create map signal -> rules
            if rule.on_signal == event_signal.name:
                if rule.requires_before:
                    for required_event in rule.requires_before:
                        if not self._check_event_history(
                                user_id, event_signal.timestamp, required_event
                        ):
                            #TODO: check fail
                            continue

                if rule.has_limit:
                    if self._check_messages_limit(user_id, rule.message, event_signal.timestamp, rule.has_limit):
                        # TODO: check fail
                        continue

                resolved_messages.append({
                    "message": rule.message,
                    "reason": rule.reason
                })

        return resolved_messages

    def _check_event_history(self, user_id: str, period_to: datetime, required_event: RequiresBefore) -> bool:
        period_from = self.get_period_from(required_event.within_period, period_to)
        period_events = self.user_event_repository.get_user_events(user_id, period_from, period_to)
        if any([e for e in period_events if e.type == required_event.event_type]):
            return True

        return False

    # TODO: maybe use factory and condition type
    def _check_messages_limit(
            self, user_id: str, message_name: str, period_to: datetime, limit_condition: HasLimit
    ) -> bool:
        period_from = self.get_period_from(limit_condition.within_period, period_to)
        period_messages = self.sent_messages_repository.get_messages(user_id, period_from, period_to)
        messages_with_type = [m for m in period_messages if m.message == message_name]

        if len(messages_with_type) >= limit_condition.max:
            return False

        return True

    @staticmethod
    def get_period_from(period: Period, period_to: datetime) -> datetime:
        if period == Period.CALENDAR_DAY:
            return datetime.combine(period_to.date(), datetime.min.time())
        elif period == Period.DAY:
            return period_to - timedelta(hours=24)
        else:
            raise ValueError("Unsupported period type")
