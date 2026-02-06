import yaml
from fastapi import FastAPI
from pydantic import BaseModel

from user_events.user_event_to_signal_config import UserEventToSignalConfig
from messages.message_suppress_rules_config import MessageSuppressRulesConfig
from message_rules.message_rules_config import MessageRulesConfig
from messages.message_suppress_service import MessageSuppressService
from user_events.user_event_service import UserEventService
from message_rules.message_rules_resolver import MessageRulesResolver
from message_send_requests.message_sender import MessageSenderStub
from user_events.user_event_repository import IncomingUserEventInMemoryRepository
from message_send_requests.message_send_request_repository import MessageSendRequestInMemoryRepository
from user_message_service_impl import UserMessageService
from user_event_types import IncomingUserEvent


def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


message_rules_config_yaml = load_yaml_config("configs/message_rules_config.yaml")
message_suppress_rules_config_yaml = load_yaml_config("configs/message_suppress_rules_config.yaml")
user_event_signals_map_config_yaml = load_yaml_config("configs/user_event_signals_map_config.yaml")

message_rules_config = MessageRulesConfig(**message_rules_config_yaml)
message_suppress_rules_config = MessageSuppressRulesConfig(**message_suppress_rules_config_yaml)
user_event_signals_map_config = UserEventToSignalConfig(**user_event_signals_map_config_yaml)

user_event_repo = IncomingUserEventInMemoryRepository()
message_request_repo = MessageSendRequestInMemoryRepository()

event_signal_service = UserEventService(config=user_event_signals_map_config)
message_suppress_service = MessageSuppressService(config=message_suppress_rules_config, repo=message_request_repo)
message_rules_resolver = MessageRulesResolver(
    config=message_rules_config,
    user_event_repository=user_event_repo,
    sent_messages_repository=message_request_repo
)
message_sender = MessageSenderStub()

user_message_service = UserMessageService(
    event_signal_service=event_signal_service,
    message_rules_resolver=message_rules_resolver,
    message_suppress_service=message_suppress_service,
    user_event_repo=user_event_repo,
    message_request_repo=message_request_repo,
    message_sender=message_sender
)

app = FastAPI()


class ProcessResult(BaseModel):
    success: bool
    message: str


@app.post("/api/v1/event", response_model=ProcessResult)
async def ingest_event(event: IncomingUserEvent):
    try:
        user_message_service.ingest_event(event)
        return True
    except Exception as e:
        return False