#!/bin/bash
set -e

# Load env vars set by UserData
source /home/ec2-user/.bash_profile

APP_DIR=/home/ec2-user/djangoapp

cd $APP_DIR

# Setup Python venv if not present
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Fetch DB credentials from Secrets Manager (expects env var DJANGO_DB_SECRET_ARN)
if [ -z "$DJANGO_DB_SECRET_ARN" ]; then
  echo "DJANGO_DB_SECRET_ARN is not set!"
  exit 1
fi

DB_SECRET=$(aws secretsmanager get-secret-value --secret-id $DJANGO_DB_SECRET_ARN --region eu-central-1 --query SecretString --output text)
DB_USER=$(echo $DB_SECRET | python3 -c "import sys, json; print(json.load(sys.stdin)['username'])")
DB_PASS=$(echo $DB_SECRET | python3 -c "import sys, json; print(json.load(sys.stdin)['password'])")

export DJANGO_DB_USER=$DB_USER
export DJANGO_DB_PASS=$DB_PASS
export DJANGO_DB_HOST=${DJANGO_DB_HOST:-localhost}

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# (Optional) Restart Gunicorn (assumes systemd unit named gunicorn)
sudo systemctl restart gunicorn || echo "Gunicorn restart skipped (not configured yet)"

deactivate
