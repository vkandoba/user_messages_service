from datetime import datetime

from configs.config_utils import get_period_from
from message_rules.message_rules_config import MessageRulesConfig, RequiresBefore, HasLimit
from message_send_requests.message_send_request_repository import MessageSendRequestRepositoryBase
from messages.message_types import Message
from user_events.user_event_repository import IncomingUserEventRepositoryBase
from user_events.user_event_service import UserEventWithSignal


class MessageRulesResolver:
    def __init__(self,
                 config: MessageRulesConfig,
                 user_event_repository: IncomingUserEventRepositoryBase,
                 sent_messages_repository: MessageSendRequestRepositoryBase
        ):
        self.config = config
        self.user_event_repository = user_event_repository
        self.sent_messages_repository = sent_messages_repository

    def apply_rules(self, event_signal: UserEventWithSignal) -> list[Message]:
        resolved_messages: list[Message] = []

        for rule in self.config.message_rules:
            # TODO: create map signal -> rules
            if rule.on_signal == event_signal.name:
                if rule.requires_before:
                    for required_event in rule.requires_before:
                        if not self._check_event_history(
                                event_signal.user_id, event_signal.timestamp, required_event
                        ):
                            #TODO: check fail
                            continue

                if rule.has_limit:
                    if self._check_messages_limit(
                            event_signal.user_id, rule.message, event_signal.timestamp, rule.has_limit
                    ):
                        # TODO: check fail
                        continue

                message_to_send = Message(
                    user_id=event_signal.user_id,
                    name=rule.message,
                    channel=rule.channel,
                    template=rule.template,
                    reason=rule.reason
                )
                resolved_messages.append(message_to_send)

        return resolved_messages

    def _check_event_history(self, user_id: str, period_to: datetime, required_event: RequiresBefore) -> bool:
        period_from = get_period_from(required_event.within_period, period_to)
        period_events = self.user_event_repository.get_user_events(user_id, period_from, period_to)
        if any([e for e in period_events if e.type == required_event.event_type]):
            return True

        return False

    # TODO: maybe use factory and condition type
    def _check_messages_limit(
            self, user_id: str, message_name: str, period_to: datetime, limit_condition: HasLimit
    ) -> bool:
        period_from = get_period_from(limit_condition.within_period, period_to)
        period_messages = self.sent_messages_repository.get_messages_by_period(user_id, period_from, period_to)
        messages_with_type = [m for m in period_messages if m.message == message_name]

        if len(messages_with_type) >= limit_condition.max:
            return False

        return True
