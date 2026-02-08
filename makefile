APP_FILE = user_message_service_main
PORT = 8000
HOST = 0.0.0.0

.PHONY: run
run:
	uvicorn $(APP_FILE):app --host $(HOST) --port $(PORT)

.PHONY: run-dev
run-dev:
	uvicorn $(APP_FILE):app --host $(HOST) --port $(PORT) --reload