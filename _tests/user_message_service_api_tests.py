from fastapi.testclient import TestClient

from user_message_service_main import app, user_message_service

client = TestClient(app)


def test_ingest_event():
    payment_failed_event = {
        "user_id": "u_12345",
        "event_type": "payment_failed",
        "event_timestamp": "2025-10-31T19:22:11Z",
        "properties": {
            "amount": 1425.00,
            "attempt_number": 2,
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
    }
]