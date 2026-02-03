import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict


from user_events.user_event_types import UserEvent


# TODO: should be async-based
class UserEventRepositoryBase(ABC):
    @abstractmethod
    def save(self, event: UserEvent) -> None:
        pass

    @abstractmethod
    def get_recent(self, user_id: str, n: int) -> List[UserEvent]:
        pass

    @abstractmethod
    def get_user_events(self, user_id: str, period_from: datetime, period_to: datetime) -> List[UserEvent]:
        pass

class UserEventInMemoryRepository(UserEventRepositoryBase):
    def __init__(self):
        self._data: Dict[str, List[UserEvent]] = {}
        self._lock = asyncio.Lock()

    def save(self, event: UserEvent) -> None:
        async with self._lock:
            if event.user_id not in self._data:
                self._data[event.user_id] = []
            self._data[event.user_id].append(event)

    def get_recent(self, user_id: str, n: int) -> List[UserEvent]:
        return self._data.get(user_id, [])[-n:]

    def get_user_events(self,
                     user_id: str,
                     period_from: datetime,
                     period_to: datetime
    ) -> List[UserEvent]:
        user_events = self._data.get(user_id, [])
        reversed_events = []

        for request in reversed(user_events):
            if period_from < request.timestamp < period_to:
                reversed_events.append(request)

        return reversed_events[::-1]
