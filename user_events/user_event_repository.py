import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict

from user_event_types import IncomingUserEvent


# TODO: should be async-based and thread-safe
class IncomingUserEventRepositoryBase(ABC):
    @abstractmethod
    def save(self, event: IncomingUserEvent) -> None:
        pass

    @abstractmethod
    def get_recent(self, user_id: str, n: int) -> list[IncomingUserEvent]:
        pass

    @abstractmethod
    def get_user_events(self, user_id: str, period_from: datetime, period_to: datetime) -> list[IncomingUserEvent]:
        pass


class IncomingUserEventInMemoryRepository(IncomingUserEventRepositoryBase):
    def __init__(self):
        self._data: Dict[str, list[IncomingUserEvent]] = {}
        self._lock = asyncio.Lock()

    def save(self, event: IncomingUserEvent) -> None:
        if event.user_id not in self._data:
            self._data[event.user_id] = []
        self._data[event.user_id].append(event)

    def get_recent(self, user_id: str, n: int) -> list[IncomingUserEvent]:
        return self._data.get(user_id, [])[-n:]

    def get_user_events(self,
                     user_id: str,
                     period_from: datetime,
                     period_to: datetime
    ) -> List[IncomingUserEvent]:
        user_events = self._data.get(user_id, [])
        reversed_events = []

        for request in reversed(user_events):
            if period_from < request.timestamp < period_to:
                reversed_events.append(request)

        return reversed_events[::-1]
