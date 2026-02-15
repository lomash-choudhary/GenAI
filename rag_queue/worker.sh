#!/bin/bash
cd /workspaces/GenAI
source venv/bin/activate
export $(grep -v '^#' rag_queue/.env | xargs)
rq worker --with-scheduler --url redis://valkey:6379