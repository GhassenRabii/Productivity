#!/bin/bash
set -e

# Uncomment for verbose debugging
# set -x

# Explicitly load env vars set by EC2 UserData
source /home/ec2-user/.bash_profile

APP_DIR=/home/ec2-user/djangoapp
GUNICORN_SVC=/etc/systemd/system/gunicorn.service
NGINX_DJANGO_CONF=/etc/nginx/conf.d/django.conf

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

# --- Install and configure Nginx ---
sudo yum install -y nginx

# Nginx config for Django (serves static, proxies to Gunicorn)
sudo tee $NGINX_DJANGO_CONF > /dev/null <<EOF
server {
    listen 80;
    server_name django-alb-1073829644.eu-central-1.elb.amazonaws.com;

    location /static/ {
        alias $APP_DIR/static/;
        autoindex off;
    }

    location /media/ {
        alias $APP_DIR/media/;
        autoindex off;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable and start Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx

# --- Gunicorn systemd service ---
sudo tee $GUNICORN_SVC > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for Django
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 mysite.wsgi

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable gunicorn

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

echo "DB_USER: $DB_USER"
echo "DB_HOST: $DB_HOST"
echo "DB_NAME: $DB_NAME"

# Django manage.py commands
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Restart Gunicorn and Nginx for latest code/config
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Deactivate Python virtual environment
deactivate

# Optionally, unset secrets for good practice
unset DB_PASS DB_USER DB_NAME DB_HOST

echo "Deployment script completed successfully."
