#!/bin/bash

source ./.venv/bin/activate
uvicorn gpt_entity_api:app --reload --host 0.0.0.0 --port 3001 | tee server.log &   # run in background
echo "Server running at http://localhost:8000"

