from datetime import datetime, timezone

from configs.config_utils import get_period_from
from user_message_types import Message
from message_send_requests.message_send_request_repository import MessageSendRequestRepositoryBase
from messages_suppress.message_suppress_rules_config import MessageSuppressRulesConfig, SuppressRule
from user_events.user_event_service import UserEventWithSignal


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

    def should_suppress(self, event: UserEventWithSignal, message: Message) -> tuple[bool, str | None]:
        rules = self._get_rules_for_message(message.name)
        if not rules:
            return False, None

        for rule in rules:
            if rule.within_period:
                now = datetime.now(tz=timezone.utc)
                period_from = get_period_from(rule.within_period, now)
                messages = self.repo.get_messages_by_period(message.user_id, period_from, now)
                suppress_reason_suffix = f" within period from {period_from} to {now}"
            else:
                messages = self.repo.get_messages_by_name(message.user_id, message.name)
                suppress_reason_suffix = ""

            messages_count = len([m for m in messages if m.message.name == message.name])

            if messages_count >= rule.max_sends:
                reason = f"Message {message.name} already sent {rule.max_sends} times{suppress_reason_suffix}"
                return True, reason

        return False, None