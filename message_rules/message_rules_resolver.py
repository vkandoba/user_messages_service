from message_rules.message_rules_config import MessageRulesConfig, RequiresBefore, HasLimit, Prerequisite
from message_rules.message_rules_prerequisite import MessageRulePrerequisiteFactory
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
        self.rule_prerequisite_factory = MessageRulePrerequisiteFactory(user_event_repository, sent_messages_repository)

    def apply_rules(self, event_signal: UserEventWithSignal) -> list[Message]:
        resolved_messages: list[Message] = []

        for rule in self.config.message_rules:
            # TODO: create map signal -> rules
            if rule.on_signal == event_signal.name:
                if not self._check_prerequisites(rule.message, event_signal, rule.prerequisites):
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

    def _check_prerequisites(
            self,
            message_name: str,
            event_signal: UserEventWithSignal,
            prerequisite_configs: list[Prerequisite]
    ) -> bool:
        if not prerequisite_configs:
            return True

        for prerequisite_config in prerequisite_configs:
            rule_prerequisite = self.rule_prerequisite_factory.create(prerequisite_config)
            if not rule_prerequisite.check(
                    event_signal.user_id, event_signal.timestamp, event_type=event_signal.type, message_name=message_name
            ):
                return False

        return True

    # def _check_event_history(self, user_id: str, period_to: datetime, required_event: RequiresBefore) -> bool:
    #     period_from = get_period_from(required_event.within_period, period_to)
    #     period_events = self.user_event_repository.get_user_events(user_id, period_from, period_to)
    #     if any([e for e in period_events if e.type == required_event.event_type]):
    #         return True
    #
    #     return False
    #
    # # TODO: maybe use factory and condition type
    # def _check_messages_limit(
    #         self, user_id: str, message_name: str, period_to: datetime, limit_condition: HasLimit
    # ) -> bool:
    #     period_from = get_period_from(limit_condition.within_period, period_to)
    #     period_messages = self.sent_messages_repository.get_messages_by_period(user_id, period_from, period_to)
    #     messages_with_type = [m for m in period_messages if m.message == message_name]
    #
    #     if len(messages_with_type) >= limit_condition.max:
    #         return False
    #
    #     return True
