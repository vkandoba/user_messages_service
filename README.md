# User Message Service

Service for handling user events and managing messages sending.

## How to Run

### Install deps

**Using Pip:**
```bash
pip install -r requirements.txt
```

**Using Make:**

```bash
make install
```

### Local Run

**Using Uvicorn:**
```bash
uvicorn user_message_service_main:app --host 0.0.0.0 --port 8000
```

**Using Make:**

```bash
make run
```

## API Reference

`local_base_url: http://localhost:8000`

### Add Event

Register a new user event

`POST {base_url}api/v1/event`

**Request example:**

```bash
curl -X POST http://localhost:8000/api/v1/event \
-H "Content-Type: application/json" \
-d '{
    "user_id": "u_12345",
    "event_type": "payment_failed",
    "event_timestamp": "2025-10-31T19:22:11Z",
    "user_traits": {
        "email": "maria@example.com",
        "country": "PT",
        "marketing_opt_in": true,
        "risk_segment": "MEDIUM"
    },
    "properties": {
        "amount": 1425.00,
        "attempt_number": 2,
        "failure_reason": "INSUFFICIENT_FUNDS"
    }
}'
```

**Response example**
```bash
null
```

### Get User Audit Log

Retrieve the history of message requests and recent events for a specific user

`GET {base_url}api/v1/{user_id}/audit`

**Request example:**

```bash
curl -X GET http://localhost:8000/api/v1/u_12345/audit \
-H "Content-Type: application/json" \
```

**Response example**
```bash
{
	"recent_events": [
		{
			"user_id": "u_12345",
			"event_type": "payment_failed",
			"event_timestamp": "2025-10-31T19:22:11Z",
			"user_traits": {
				"email": "maria@example.com",
				"country": "PT",
				"marketing_opt_in": true,
				"risk_segment": "MEDIUM"
			},
			"properties": {
				"amount": 1425.0,
				"attempt_number": 2,
				"failure_reason": "INSUFFICIENT_FUNDS"
			}
		}
	],
	"message_requests": [
		{
			"timestamp": "2026-02-08T23:39:43.979550Z",
			"message": {
				"user_id": "u_12345",
				"name": "insufficient_funds",
				"channel": "email",
				"template": "INSUFFICIENT_FUNDS_EMAIL",
				"reason": "Payment failed due to lack of funds"
			},
			"status": "sent",
			"suppress_reason": null
		}
	]
}
```
