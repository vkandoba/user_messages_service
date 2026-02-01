from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict

from message_send_requests.message_send_request_types import MessageSendRequest


class MessageSendRequestRepositoryBase(ABC):
    @abstractmethod
    def save(self, request: MessageSendRequest) -> None:
        pass

    @abstractmethod
    def get_recent(self, user_id: str, max_timestamp: datetime, n: int) -> List[MessageSendRequest]:
        pass


class MessageSendRequestInMemoryRepository(MessageSendRequestRepositoryBase):
    def __init__(self):
        self._data: Dict[str, List[MessageSendRequest]] = {}

    def save(self, request: MessageSendRequest) -> None:
        if request.message.user_id not in self._data:
            self._data[request.message.user_id] = []
        self._data[request.message.user_id].append(request)

    def get_recent(self,
                   user_id: str,
                   max_timestamp: datetime,
                   n: int) -> List[MessageSendRequest]:
        user_requests = self._data.get(user_id, [])
        recent_requests = []

        for request in reversed(user_requests):
            if request.timestamp < max_timestamp:
                recent_requests.append(request)
                if len(recent_requests) == n:
                    break

        return recent_requests[::-1]
