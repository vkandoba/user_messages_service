import pytest
from datetime import datetime

from user_event_types import IncomingUserEvent, UserTraits, PaymentFailedProperties
from user_events.user_event_service import UserEventService
from user_events.user_event_to_signal_config import UserEventToSignalConfig


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
        event_type="signup_completed",
        event_timestamp=datetime.now(),
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
        event_type="payment_failed",
        event_timestamp=datetime.now(),
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
        event_type="payment_failed",
        event_timestamp=datetime.now(),
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


def test_get_event_signals_with_signup_marketing(config_fixture, event_fixture_signup):
    service = UserEventService(config=config_fixture)

    signals = service.get_event_with_signals(event_fixture_signup)

    assert len(signals) == 1
    assert signals[0].signal == "signup_with_marketing"


def test_payment_failed_insufficient_funds(config_fixture, event_fixture_payment_failed_with_funds):
    service = UserEventService(config=config_fixture)

    signals = service.get_event_with_signals(event_fixture_payment_failed_with_funds)

    assert len(signals) == 1
    assert signals[0].signal == "payment_failed_with_insufficient_funds"


def test_payment_failed_other_reason(config_fixture, event_fixture_payment_failed_other_reason):
    service = UserEventService(config=config_fixture)

    signals = service.get_event_with_signals(event_fixture_payment_failed_other_reason)

    assert len(signals) == 1
    assert signals[0].signal == "payment_failed"


def test_unknown_event_type(config_fixture):
    service = UserEventService(config=config_fixture)
    event = IncomingUserEvent(
        user_id="user_unknown",
        event_type="unknown_event",
        event_timestamp=datetime.now(),
        properties={},
        user_traits=UserTraits(
            email="unknown@example.com",
            country="US",
            marketing_opt_in=True
        )
    )

    with pytest.raises(ValueError):
        service.get_event_with_signals(event)
