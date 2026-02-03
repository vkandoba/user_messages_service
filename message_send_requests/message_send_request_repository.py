from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict

from message_send_requests.message_send_request_types import MessageSendRequest


class MessageSendRequestRepositoryBase(ABC):
    @abstractmethod
    def save(self, request: MessageSendRequest) -> None:
        pass

    @abstractmethod
    def get_messages(self,
                   user_id: str,
                   period_from: datetime,
                   period_to: datetime
    ) -> List[MessageSendRequest]:
        pass


class MessageSendRequestInMemoryRepository(MessageSendRequestRepositoryBase):
    def __init__(self):
        self._data: Dict[str, List[MessageSendRequest]] = {}

    def save(self, request: MessageSendRequest) -> None:
        if request.message.user_id not in self._data:
            self._data[request.message.user_id] = []
        self._data[request.message.user_id].append(request)

    def get_messages(self,
                   user_id: str,
                   period_from: datetime,
                   period_to: datetime
    ) -> List[MessageSendRequest]:
        user_requests = self._data.get(user_id, [])
        reversed_messages = []

        for request in reversed(user_requests):
            if period_from < request.timestamp < period_to:
                reversed_messages.append(request)

        return reversed_messages[::-1]
