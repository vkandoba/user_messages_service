from fastapi.testclient import TestClient

from user_message_service_main import app, user_message_service

client = TestClient(app)


def test_ingest_payment_failed_event():
    payment_failed_event = {
        "user_id": "u_12345",
        "event_type": "payment_failed",
        "event_timestamp": "2025-10-31T19:22:11Z",
        "properties": {
            "amount": 1425.00,
            "attempt_number": 4,
            "failure_reason": "INSUFFICIENT_FUNDS"
        },
        "user_traits": {
            "email": "maria@example.com",
            "country": "PT",
            "marketing_opt_in": True,
            "risk_segment": "MEDIUM"
        }
    }

    response = client.post("/api/v1/event", json=payment_failed_event)
    assert response.status_code == 200
    messages = response.json()
    [m.pop("timestamp") for m in messages]
    print(messages)
    assert messages == [
    {
        "message": {
            "channel": "email",
            "name": "insufficient_funds",
            "reason": "Payment failed due to lack of funds",
            "template": "INSUFFICIENT_FUNDS_EMAIL",
            "user_id": "u_12345"
        },
        'suppress_reason': None,
        "status": "sent",
    },
    {
        'message': {
            'channel': 'internal_alert',
            'name': 'payment_retry_exhausted_alert',
            'reason': 'At least third failed payment attempt detected',
            'template': 'HIGH_RISK_ALERT',
            'user_id': 'u_12345'
        },
        'status': 'sent',
        'suppress_reason': None
    }
]


def test_signup_completed():
    payment_failed_event = {
        "user_id": "u_12345",
        "event_type": "signup_completed",
        "event_timestamp": "2025-10-31T19:22:11Z",
        "properties": {
        },
        "user_traits": {
            "marketing_opt_in": True,
        }
    }

    response = client.post("/api/v1/event", json=payment_failed_event)
    assert response.status_code == 200
    messages = response.json()
    [m.pop("timestamp") for m in messages]
    print(messages)
    assert messages == [
        {
            'message': {
                'channel': 'email',
                'name': 'welcome',
                'reason': 'New user signed up and opted in for marketing',
                'template': 'WELCOME_EMAIL',
                'user_id': 'u_12345'},
            'status': 'sent',
            'suppress_reason': None
        }
    ]