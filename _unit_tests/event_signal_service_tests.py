import pytest
from datetime import datetime

from user_events.user_event_types import IncomingUserEvent, UserTraits, PaymentFailedProperties
from event_signals.event_signal_service import EventSignalService
from event_signals.user_event_to_signal_config import UserEventToSignalConfig


@pytest.fixture
def config_fixture():
    return UserEventToSignalConfig(
        user_event_types={
            "signup_completed": {
                "default_signal": "signup",
                "cases": [
                    {
                        "signal": "signup_with_marketing",
                        "condition": "user_traits.marketing_opt_in == True"
                    }
                ]
            },
            "payment_failed": {
                "default_signal": "payment_failed",
                "cases": [
                    {
                        "signal": "payment_failed_with_insufficient_funds",
                        "condition": "properties.failure_reason == 'INSUFFICIENT_FUNDS'"
                    }
                ]
            }
        }
    )


@pytest.fixture
def event_fixture_signup():
    return IncomingUserEvent(
        user_id="user_1",
        type="signup_completed",
        timestamp=datetime.now(),
        properties={},
        user_traits=UserTraits(
            email="test@example.com",
            country="US",
            marketing_opt_in=True
        )
    )


@pytest.fixture
def event_fixture_payment_failed_with_funds():
    return IncomingUserEvent(
        user_id="user_2",
        type="payment_failed",
        timestamp=datetime.now(),
        properties=PaymentFailedProperties(
            amount=10,
            attempt_number=1,
            failure_reason="INSUFFICIENT_FUNDS"
        ),
        user_traits=UserTraits(
            email="user2@example.com",
            country="UK",
            marketing_opt_in=False
        )
    )


@pytest.fixture
def event_fixture_payment_failed_other_reason():
    return IncomingUserEvent(
        user_id="user_3",
        type="payment_failed",
        timestamp=datetime.now(),
        properties=PaymentFailedProperties(
            amount=10,
            attempt_number=1,
            failure_reason="CARD_EXPIRED"
        ),
        user_traits=UserTraits(
            email="user3@example.com",
            country="CA",
            marketing_opt_in=True
        )
    )


def test_get_event_signal_with_signup_marketing(config_fixture, event_fixture_signup):
    service = EventSignalService(config=config_fixture)

    signal = service.get_event_with_signal(event_fixture_signup)

    assert signal.signal == "signup_with_marketing"


def test_payment_failed_insufficient_funds(config_fixture, event_fixture_payment_failed_with_funds):
    service = EventSignalService(config=config_fixture)

    signal = service.get_event_with_signal(event_fixture_payment_failed_with_funds)

    assert signal.signal == "payment_failed_with_insufficient_funds"


def test_payment_failed_other_reason(config_fixture, event_fixture_payment_failed_other_reason):
    service = EventSignalService(config=config_fixture)

    signal = service.get_event_with_signal(event_fixture_payment_failed_other_reason)

    assert signal.signal == "payment_failed"


def test_unknown_event_type(config_fixture):
    service = EventSignalService(config=config_fixture)
    event = IncomingUserEvent(
        user_id="user_unknown",
        type="unknown_event",
        timestamp=datetime.now(),
        properties={},
        user_traits=UserTraits(
            email="unknown@example.com",
            country="US",
            marketing_opt_in=True
        )
    )

    with pytest.raises(ValueError):
        service.get_event_with_signal(event)


def test_eval_error_handling(config_fixture, event_fixture_signup):
    service = EventSignalService(config=config_fixture)

    config_fixture.user_event_types["signup_completed"].cases[0].condition = "invalid_condition_value"

    with pytest.raises(RuntimeError):
        service.get_event_with_signal(event_fixture_signup)