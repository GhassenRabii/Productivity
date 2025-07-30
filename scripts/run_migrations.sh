#!/bin/bash
set -euo pipefail

# Optionally source environment variables, e.g., from .bash_profile or .env
source /home/ec2-user/.bash_profile

APP_DIR=/home/ec2-user/djangoapp

echo "[+] Activating virtualenv…"
source $APP_DIR/venv/bin/activate

cd $APP_DIR

echo "[+] Fetching DB credentials from AWS Secrets Manager…"
DB_SECRET=$(aws secretsmanager get-secret-value --secret-id "$DJANGO_DB_SECRET_ARN" --region eu-central-1 --query SecretString --output text)
DB_USER=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin)['username'])")
DB_PASS=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin)['password'])")
DB_HOST=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin)['host'])")
DB_NAME=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin)['dbname'])")

export DB_USER DB_PASSWORD="$DB_PASS" DB_HOST DB_NAME

echo "[+] Running Django database migrations…"
python manage.py migrate --noinput

# Optional: collectstatic if you want
# python manage.py collectstatic --noinput

deactivate

echo "[+] Migrations completed successfully!"
