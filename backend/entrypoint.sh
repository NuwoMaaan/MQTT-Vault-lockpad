#!/bin/sh
set -e

cd /app/backend

uv run -m auth.init

exec "$@"