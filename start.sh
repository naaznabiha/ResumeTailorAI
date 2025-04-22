#!/bin/sh
. /opt/venv/bin/activate
exec uvicorn app:app --host 0.0.0.0 --port $PORT
