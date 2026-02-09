import logging
from message_rules.message_rules_config import MessageRulesConfig, RequiresBefore, HasLimit, Prerequisite
from message_rules.message_rules_prerequisite import MessageRulePrerequisiteFactory
from message_send_requests.message_send_request_repository import MessageSendRequestRepositoryBase
from messages_suppress.message_types import Message
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

    def apply_rules(self, event_with_signal: UserEventWithSignal) -> list[Message]:
        resolved_messages: list[Message] = []

        for rule in self.config.message_rules:
            # TODO: create map signal -> rules
            if rule.on_signal == event_with_signal.signal:
                if not self._check_prerequisites(rule.message, event_with_signal, rule.prerequisites):
                    logging.info(f"Skipping {rule.message} because the event doesn't meet the pre-conditions")
                    continue

                message_to_send = Message(
                    user_id=event_with_signal.user_id,
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
            if not rule_prerequisite.check(message_name, event_signal):
                return False

        return True
