from datetime import datetime

import pytest
from unittest.mock import MagicMock
from messages_suppress.message_suppress_service import MessageSuppressService
from messages_suppress.message_suppress_rules_config import SuppressRule, MessageSuppressRulesConfig
from user_message_types import Message, Channel


@pytest.fixture
def message_suppress_service():
    config = MessageSuppressRulesConfig(
        message_suppress_rules=[
            SuppressRule(message="test_message", max_sends=3, within_period="24h"),
            SuppressRule(message="another_message", max_sends=2),
        ]
    )

    repo = MagicMock()
    return MessageSuppressService(config=config, repo=repo)


@pytest.fixture
def event():
    event = MagicMock()
    event.timestamp = datetime(2023, 10, 10, 12, 0, 0)
    return event


@pytest.fixture
def test_message():
    return Message(user_id="user123", name="test_message", template="test_message", channel=Channel.sms, reason="")


@pytest.fixture
def another_message():
    return Message(
        user_id="user123", name="another_message", template="another_message", channel=Channel.sms, reason=""
    )


def test_should_not_suppress_no_rules(message_suppress_service, event, test_message):
    result = message_suppress_service.should_suppress(event, test_message)
    assert result == (False, None)


def test_should_suppress_within_period(message_suppress_service, event, test_message):
    messages_in_period = [MagicMock(message=test_message)] * 3
    message_suppress_service.repo.get_messages_by_period.return_value = messages_in_period

    should_suppress, reason = message_suppress_service.should_suppress(event, test_message)
    assert should_suppress
    assert reason.startswith("Message test_message already sent more than 3 times within period from")


def test_should_not_suppress_within_period(message_suppress_service, event, test_message):
    messages_in_period = [MagicMock(message=test_message)] * 2
    message_suppress_service.repo.get_messages_by_period.return_value = messages_in_period

    result = message_suppress_service.should_suppress(event, test_message)
    assert result == (False, None)


def test_should_suppress_by_name(message_suppress_service, event, another_message):
    messages_by_name = [MagicMock(message=another_message)] * 2
    message_suppress_service.repo.get_messages_by_name.return_value = messages_by_name

    should_suppress, reason = message_suppress_service.should_suppress(event, another_message)
    assert should_suppress
    assert reason == "Message another_message already sent more than 2 times"


def test_should_not_suppress_by_name(message_suppress_service, event, another_message):
    messages_by_name = [MagicMock(message=another_message)]
    message_suppress_service.repo.get_messages_by_name.return_value = messages_by_name

    result = message_suppress_service.should_suppress(event, another_message)
    assert result == (False, None)