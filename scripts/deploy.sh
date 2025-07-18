#!/bin/bash
set -e

# Only debug non-sensitive steps
set -x
source /home/ec2-user/.bash_profile
APP_DIR=/home/ec2-user/djangoapp
echo "Running as user: $(whoami)"
echo "Present working dir: $(pwd)"
echo "DJANGO_DB_HOST = $DJANGO_DB_HOST"
sudo chown -R ec2-user:ec2-user $APP_DIR
cd $APP_DIR

if [ -d "venv" ]; then
  rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

set +x  # Stop debug before secrets

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

env | grep DJANGO

python manage.py migrate --noinput
python manage.py collectstatic --noinput

sudo systemctl restart gunicorn || echo "Gunicorn restart skipped (not configured yet)"

deactivate

# Unset secrets for extra security
unset DJANGO_DB_USER DJANGO_DB_PASS DB_USER DB_PASS DB_SECRET
