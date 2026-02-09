from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from configs.config_utils import Period, get_period_from
from message_rules.message_rules_config import Prerequisite, RequiresBefore, HasLimit
from message_send_requests.message_send_request_repository import MessageSendRequestRepositoryBase
from user_events.user_event_repository import IncomingUserEventRepositoryBase
from user_events.user_event_service import UserEventWithSignal


class MessageRulePrerequisite(ABC):
    @abstractmethod
    def check(self, message: str, user_event: UserEventWithSignal) -> bool:
        pass


class RequiresBeforePrerequisite(MessageRulePrerequisite):
    def __init__(
            self,
            within_period: Optional[Period],
            user_event_repository: IncomingUserEventRepositoryBase
    ):
        self.within_period = within_period
        self.user_event_repository = user_event_repository

    def check(self, message: str, user_event: UserEventWithSignal) -> bool:
        period_from = get_period_from(self.within_period, user_event.timestamp)
        period_events = self.user_event_repository.get_user_events(user_event.user_id, period_from, user_event.timestamp)
        return any(event.type == user_event.type for event in period_events)


class HasLimitPrerequisite(MessageRulePrerequisite):
    def __init__(self, max: int, within_period: Optional[Period], sent_messages_repository: MessageSendRequestRepositoryBase):
        self.max = max
        self.within_period = within_period
        self.sent_messages_repository = sent_messages_repository

    def check(self, message: str, user_event: UserEventWithSignal) -> bool:
        period_from = get_period_from(self.within_period, user_event.timestamp)
        period_messages = self.sent_messages_repository.get_messages_by_period(user_event.user_id, period_from, user_event.timestamp)
        messages_with_type = [msg for msg in period_messages if msg.message == message]
        return len(messages_with_type) < self.max


class MessageRulePrerequisiteFactory:
    def __init__(
        self,
        user_event_repository: IncomingUserEventRepositoryBase,
        sent_messages_repository: MessageSendRequestRepositoryBase
    ):
        self.user_event_repository = user_event_repository
        self.sent_messages_repository = sent_messages_repository

    def create(self, prerequisite_config: Prerequisite) -> MessageRulePrerequisite:
        if isinstance(prerequisite_config, RequiresBefore):
            return RequiresBeforePrerequisite(
                within_period=prerequisite_config.within_period,
                user_event_repository=self.user_event_repository
            )
        elif isinstance(prerequisite_config, HasLimit):
            return HasLimitPrerequisite(
                max=prerequisite_config.max,
                within_period=prerequisite_config.within_period,
                sent_messages_repository=self.sent_messages_repository
            )
        else:
            raise ValueError(f"Unsupported prerequisite type: {type(prerequisite_config)}")
