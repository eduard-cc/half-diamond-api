#!/bin/bash
set -e

cd /app/api/src
uvicorn main:app --host 0.0.0.0 --port 8000 &

cd /app/web
npm run preview -- --host 0.0.0.0 &

wait