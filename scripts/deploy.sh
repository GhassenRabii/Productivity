#!/bin/bash
set -e

# Uncomment the line below for debugging (prints all commands as they run)
# set -x

# Explicitly load env vars set by EC2 UserData
source /home/ec2-user/.bash_profile

APP_DIR=/home/ec2-user/djangoapp

# Show who and where (safe for debugging)
echo "Running as user: $(whoami)"
echo "Present working dir: $(pwd)"
echo "DJANGO_DB_SECRET_ARN = $DJANGO_DB_SECRET_ARN"
echo "DJANGO_DB_HOST = $DJANGO_DB_HOST"

# Ensure correct permissions for the application directory
sudo chown -R ec2-user:ec2-user "$APP_DIR"

cd "$APP_DIR"

# Clean up any old venv to avoid permission issues
if [ -d "venv" ]; then
  rm -rf venv
fi

# Create a new Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create/Update Gunicorn systemd service for Django
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for Django
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/djangoapp
Environment="PATH=/home/ec2-user/djangoapp/venv/bin"
ExecStart=/home/ec2-user/djangoapp/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 mysite.wsgi

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to pick up new service
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn || echo "Gunicorn restart skipped (not configured yet)"


# Fetch DB credentials from AWS Secrets Manager (needs DJANGO_DB_SECRET_ARN set!)
if [ -z "$DJANGO_DB_SECRET_ARN" ]; then
  echo "DJANGO_DB_SECRET_ARN is not set!"
  exit 1
fi

DB_SECRET=$(aws secretsmanager get-secret-value --secret-id "$DJANGO_DB_SECRET_ARN" --region eu-central-1 --query SecretString --output text)
DB_USER=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin)['username'])")
DB_PASS=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin)['password'])")
DB_HOST=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin).get('host', 'localhost'))")
DB_NAME=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin).get('dbname', 'productivitydb'))")

export DB_USER
export DB_PASSWORD="$DB_PASS"
export DB_HOST
export DB_NAME


# Show only non-sensitive envs for debug
echo "DB_USER: $DB_USER"
echo "DB_HOST: $DB_HOST"
echo "DB_NAME: $DB_NAME"

# Django manage.py commands
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Restart Gunicorn (if enabled)
sudo systemctl restart gunicorn || echo "Gunicorn restart skipped (not configured yet)"

# Deactivate Python virtual environment
deactivate

# Optionally, unset secrets for good practice
unset DB_PASS DB_USER DB_NAME DB_HOST

echo "Deployment script completed successfully."
