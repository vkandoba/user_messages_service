# message_suppress/message_suppress_service.py
from typing import Optional
from pydantic import BaseModel

from config_utils import get_period_from
from user_events.event_signal_service import UserEventWithSignal
from message_types import Message
from message_send_requests.message_send_request_repository import MessageSendRequestRepositoryBase
from messages.message_suppress_rules_config import MessageSuppressRulesConfig, SuppressRule


class SuppressDecision(BaseModel):
    is_need_supress: bool
    suppress_reason: Optional[str]


class MessageSuppressService:
    def __init__(
            self,
            config: MessageSuppressRulesConfig,
            repo: MessageSendRequestRepositoryBase
    ):
        self.config = config
        self.repo = repo

    def _get_rules_for_message(self, message_name: str) -> list[SuppressRule]:
        rules = []
        for rule in self.config.message_suppress_rules:
            if rule.message == message_name:
                rules.append(rule)

        return rules

    def should_suppress(self, event: UserEventWithSignal, message: Message) -> SuppressDecision:
        rules = self._get_rules_for_message(message.template)
        if not rules:
            return SuppressDecision(is_need_supress=False, suppress_reason=None)

        for rule in rules:
            if rule.within_period:
                period_from = get_period_from(rule.within_period, event.timestamp)
                messages = self.repo.get_messages_by_period(event.user_id, period_from, event.timestamp)
            else:
                messages = self.repo.get_messages_by_name(event.user_id, message.name)

            messages_count = len([m for m in messages if m.message.name == message.name])

            if messages_count >= rule.max_sends:
                return SuppressDecision(is_need_supress=True, reason="FORMAT REASON TODO")

        return SuppressDecision(is_need_supress=False, suppress_reason=None)