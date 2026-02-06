from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict

from messages.message_types import MessageSendRequest


class MessageSendRequestRepositoryBase(ABC):
    @abstractmethod
    def save(self, request: MessageSendRequest) -> None:
        pass

    @abstractmethod
    def get_messages_by_period(self,
                   user_id: str,
                   period_from: datetime,
                   period_to: datetime
    ) -> List[MessageSendRequest]:
        pass

    @abstractmethod
    def get_messages_by_name(self, user_id: str, message_name: str) -> List[MessageSendRequest]:
        pass


class MessageSendRequestInMemoryRepository(MessageSendRequestRepositoryBase):
    def __init__(self):
        self._data: Dict[str, List[MessageSendRequest]] = {}

    def save(self, request: MessageSendRequest) -> None:
        if request.message.user_id not in self._data:
            self._data[request.message.user_id] = []
        self._data[request.message.user_id].append(request)

    def get_messages_by_period(self,
                   user_id: str,
                   period_from: datetime,
                   period_to: datetime
    ) -> List[MessageSendRequest]:
        user_messages = self._data.get(user_id, [])
        reversed_messages = []

        for request in reversed(user_messages):
            if period_from < request.timestamp < period_to:
                reversed_messages.append(request)

        return reversed_messages[::-1]

    def get_messages_by_name(self, user_id: str, message_name: str) -> List[MessageSendRequest]:
        user_messages = self._data.get(user_id, [])
        reversed_messages = []

        for m in reversed(user_messages):
            if m.message == message_name:
                reversed_messages.append(m)

        return reversed_messages[::-1]
