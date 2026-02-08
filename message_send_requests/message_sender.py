from abc import ABC, abstractmethod

from messages_suppress.message_types import MessageSendRequest


class MessageSender(ABC):
    @abstractmethod
    def send(self, request: MessageSendRequest):
        pass


class FakeMessageSender(MessageSender):
    def send(self, request: MessageSendRequest):
        print(f"Send message ...")
