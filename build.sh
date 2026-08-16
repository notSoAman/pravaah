#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "==> Installing Python dependencies..."
if [ -d ".venv" ] && [ -z "$RENDER" ]; then
    .venv/bin/pip install -r requirements.txt
else
    pip install -r requirements.txt
fi

echo "==> Installing Node dependencies & compiling Tailwind CSS..."
npm install
npm run build

echo "==> Collecting static files..."
if [ -d ".venv" ] && [ -z "$RENDER" ]; then
    .venv/bin/python manage.py collectstatic --noinput
    .venv/bin/python manage.py migrate
else
    python manage.py collectstatic --noinput
    python manage.py migrate
fi

echo "==> Build complete!"
