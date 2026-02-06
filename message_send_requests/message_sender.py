from abc import ABC, abstractmethod

from messages.message_types import MessageSendRequest


class MessageSender(ABC):
    @abstractmethod
    def send(self, request: MessageSendRequest):
        pass


class MessageSenderStub(MessageSender):
    def send(self, request: MessageSendRequest):
        print(f"Send message ...")
