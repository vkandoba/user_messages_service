# message_suppress/message_suppress_service.py
from datetime import datetime
from typing import Optional

from message_types import Message
from message_send_requests.message_send_request_repository import MessageSendRequestRepositoryBase
from messages.message_suppress_rules_config import MessageSuppressRulesConfig, SuppressRule


class SuppressDecision(str):
    SUPPRESS = "Suppress"
    SEND = "Send"


class MessageSuppressService:
    def __init__(self, config: MessageSuppressRulesConfig, repository: MessageSendRequestRepositoryBase):
        self.config = config
        self.repository = repository

    def _get_rules_for_message(self, message_name: str) -> list[SuppressRule]:
        rules = []
        for rule in self.config.message_suppress_rules:
            if rule.message == message_name:
                rules.append(rule)

        return rules

    def should_suppress(self, message: Message) -> tuple[SuppressDecision, Optional[str]]:
        rules = self._get_rules_for_message(message.template)
        if not rules:
            return SuppressDecision.SEND, None

        max_timestamp = datetime.now()
        for rule in rules:
            # TODO: get boundaries and check it
            if rule.period == "calendar_day":
                max_timestamp = datetime.combine(max_timestamp.date(), datetime.min.time())

            recent_requests = self.repository.get_recent(
                user_id=message.user_id,
                max_timestamp=max_timestamp,
                n=rule.max_sends + 1
            )

            if len(recent_requests) >= rule.max_sends:
                suppress_reason = (f"Message '{message.template}' has been sent {len(recent_requests)} times,"
                                   f"last time TODO within {rule.period}"
                                   f"exceeding limit of {rule.max_sends}.")
                return SuppressDecision.SUPPRESS, suppress_reason

        return SuppressDecision.SEND, None