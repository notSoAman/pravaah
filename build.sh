#!/usr/bin/env bash
set -o errexit

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Installing Node.js dependencies..."
npm install

echo "==> Compiling Tailwind CSS..."
npm run build

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running database migrations..."
python manage.py migrate

if [ -f "fixtures/initial_data.json" ]; then
    echo "==> Loading initial data..."
    python manage.py loaddata fixtures/initial_data.json
fi

echo "==> Build complete!"
