#!/bin/bash

set -e

APP_DIR=/home/ubuntu/app

cd $APP_DIR

# Setup Python venv if not present
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip & install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Django migrations & static files
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# (Optional) Restart Gunicorn (assumes a systemd unit named gunicorn)
sudo systemctl restart gunicorn || echo "Gunicorn restart skipped (not configured yet)"

deactivate
