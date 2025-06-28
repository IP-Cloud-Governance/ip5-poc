#!/bin/sh

if [ "$ENV" = "dev" ]; then
  echo "Running in development mode with reload"
  exec uvicorn ip5_poc.main:app --host 0.0.0.0 --port 8000 --reload
else
  echo "Running in production mode"
  exec uvicorn ip5_poc.main:app --host 0.0.0.0 --port 8000
fi
