import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from message_rules.message_rules_config import MessageRulesConfig, MessageRule, RequiresBefore, HasLimit
from message_rules.message_rules_resolver import MessageRulesResolver
from user_events.user_event_service import UserEventWithSignal


@pytest.fixture
def message_rules_config_fixture():
    return MessageRulesConfig(
        message_rules=[
            MessageRule(
                message="welcome",
                on_signal="signup_with_marketing",
                template="WELCOME_EMAIL",
                channel="email",
                reason="New user signed up and opted in for marketing",
                prerequisites=None
            ),
            MessageRule(
                message="bank_account_ready",
                on_signal="link_bank_success",
                template="BANK_LINK_NUDGE_SMS",
                channel="sms",
                reason="User linked bank within 24h of registration",
                prerequisites=[
                    RequiresBefore(
                        event_type="signup_completed",
                        within_period="24h"
                    )
                ]
            ),
            MessageRule(
                message="insufficient_funds",
                on_signal="payment_failed_with_insufficient_funds",
                template="INSUFFICIENT_FUNDS_EMAIL",
                channel="email",
                reason="Payment failed due to lack of funds",
                prerequisites=[
                    HasLimit(
                        max=1,
                        within_period="calendar_day"
                    )
                ]
            )
        ]
    )


@pytest.fixture
def event_signal_fixture():
    return UserEventWithSignal(
        user_id="user_1",
        signal="signup_with_marketing",
        event_type="signup_completed",
        event_timestamp=datetime.utcnow()
    )


@pytest.fixture
def mock_user_event_repository():
    return MagicMock()


@pytest.fixture
def mock_sent_messages_repository():
    return MagicMock()


@pytest.fixture
def resolver_fixture(message_rules_config_fixture, mock_user_event_repository, mock_sent_messages_repository):
    return MessageRulesResolver(
        config=message_rules_config_fixture,
        user_event_repository=mock_user_event_repository,
        sent_messages_repository=mock_sent_messages_repository
    )


def test_apply_rules_no_prerequisites(resolver_fixture, event_signal_fixture):
    messages = resolver_fixture.apply_rules(event_signal_fixture)

    assert len(messages) == 1
    assert messages[0].name == "welcome"
    assert messages[0].template == "WELCOME_EMAIL"
    assert messages[0].channel == "email"


def test_apply_rules_requires_before_prerequisite(resolver_fixture, event_signal_fixture, mock_user_event_repository):
    event_signal_fixture.signal = "link_bank_success"
    event_signal_fixture.user_id = "user_2"
    mock_user_event_repository.get_user_events.return_value = [
        MagicMock(type="signup_completed", timestamp=datetime.utcnow() - timedelta(hours=1))
    ]

    messages = resolver_fixture.apply_rules(event_signal_fixture)

    assert len(messages) == 1
    assert messages[0].name == "bank_account_ready"
    assert messages[0].template == "BANK_LINK_NUDGE_SMS"


def test_apply_rules_requires_before_prerequisite_no_matching_event(resolver_fixture, event_signal_fixture, mock_user_event_repository):
    event_signal_fixture.signal = "link_bank_success"
    event_signal_fixture.user_id = "user_3"
    mock_user_event_repository.get_user_events.return_value = [
        MagicMock(type="other_event", timestamp=datetime.utcnow() - timedelta(hours=1))
    ]

    messages = resolver_fixture.apply_rules(event_signal_fixture)

    assert len(messages) == 0


def test_apply_rules_has_limit_prerequisite(resolver_fixture, event_signal_fixture, mock_sent_messages_repository):
    event_signal_fixture.signal = "payment_failed_with_insufficient_funds"
    event_signal_fixture.user_id = "user_4"
    mock_sent_messages_repository.get_messages_by_period.return_value = []

    messages = resolver_fixture.apply_rules(event_signal_fixture)

    assert len(messages) == 1
    assert messages[0].name == "insufficient_funds"
    assert messages[0].template == "INSUFFICIENT_FUNDS_EMAIL"


def test_apply_rules_has_limit_prerequisite_exceeded_limit(resolver_fixture, event_signal_fixture, mock_sent_messages_repository):
    event_signal_fixture.signal = "payment_failed_with_insufficient_funds"
    event_signal_fixture.user_id = "user_5"
    mock_sent_messages_repository.get_messages_by_period.return_value = [
        MagicMock(message="insufficient_funds")
    ]

    messages = resolver_fixture.apply_rules(event_signal_fixture)

    assert len(messages) == 0


def test_apply_rules_no_matching_signal(resolver_fixture, event_signal_fixture):
    event_signal_fixture.signal = "unknown_signal"
    messages = resolver_fixture.apply_rules(event_signal_fixture)

    assert len(messages) == 0