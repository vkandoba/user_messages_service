from datetime import datetime

from messages_suppress.message_types import MessageSendRequest, MessageSendRequestStatus
from user_event_types import IncomingUserEvent
from user_message_types import UserAudit


class UserMessageService:
    def __init__(
            self,
             event_signal_service: "EventSignalService",
             message_rules_resolver: "MessageRulesResolver",
             message_suppress_service: "MessageSuppressService",
             user_event_repo: "IncomingUserEventRepositoryBase",
             message_request_repo: "MessageSendRequestRepositoryBase",
             message_sender: "MessageSender",
        ):
        self._event_signal_service = event_signal_service
        self._message_rules_resolver = message_rules_resolver
        self._message_suppress_service = message_suppress_service
        self._message_request_repo = message_request_repo
        self._user_event_repo = user_event_repo
        self._message_sender = message_sender

    def ingest_event(self, user_event: IncomingUserEvent) -> None:
        self._user_event_repo.save(user_event)
        event_with_signal = self._event_signal_service.get_event_with_signal(user_event)

        resolved_messages = self._message_rules_resolver.apply_rules(event_with_signal)

        for message in resolved_messages:
            request_status = MessageSendRequestStatus.SENT
            should_suppress, suppress_reason = self._message_suppress_service.should_suppress(user_event, message)
            if should_suppress:
                request_status = MessageSendRequestStatus.SUPPRESSED

            message_request = MessageSendRequest(
                timestamp=datetime.now(), # TODO: add utc tz
                message=message,
                status=request_status,
                suppress_reason=suppress_reason
            )
            self._message_request_repo.save(message_request)
            if message_request.status == MessageSendRequestStatus.SENT:
                self._message_sender.send(message_request)

    def get_audit(self, user_id: str, events_count: int) -> tuple[list[IncomingUserEvent], list[MessageSendRequest]]:
        recent_events = self._user_event_repo.get_recent(user_id, events_count)
        messages = self._message_request_repo.get_messages_by_user(user_id)
        return recent_events, messages