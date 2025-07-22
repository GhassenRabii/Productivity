#!/bin/bash
set -e

# Uncomment for debug:
# set -x

source /home/ec2-user/.bash_profile

APP_DIR=/home/ec2-user/djangoapp
GUNICORN_SVC=/etc/systemd/system/gunicorn.service
NGINX_DJANGO_CONF=/etc/nginx/conf.d/django.conf

echo "Running as user: $(whoami)"
echo "Present working dir: $(pwd)"

# Ensure correct permissions for the app directory
sudo chown -R ec2-user:ec2-user "$APP_DIR"
cd "$APP_DIR"

# Clean old virtualenv if present
if [ -d "venv" ]; then
  rm -rf venv
fi

# Setup Python venv and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# --- Fetch DB credentials from AWS Secrets Manager ---
if [ -z "$DJANGO_DB_SECRET_ARN" ]; then
  echo "DJANGO_DB_SECRET_ARN is not set!"
  exit 1
fi

DB_SECRET=$(aws secretsmanager get-secret-value --secret-id "$DJANGO_DB_SECRET_ARN" --region eu-central-1 --query SecretString --output text)
DB_USER=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin)['username'])")
DB_PASS=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin)['password'])")
DB_HOST=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin).get('host', 'localhost'))")
DB_NAME=$(echo "$DB_SECRET" | python3 -c "import sys, json; print(json.load(sys.stdin).get('dbname', 'productivitydb'))")

echo "DB_USER: $DB_USER"
echo "DB_HOST: $DB_HOST"
echo "DB_NAME: $DB_NAME"

# --- Gunicorn systemd service with env vars for Django ---
sudo tee $GUNICORN_SVC > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for Django
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="DB_USER=$DB_USER"
Environment="DB_PASSWORD=$DB_PASS"
Environment="DB_HOST=$DB_HOST"
Environment="DB_NAME=$DB_NAME"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 mysite.wsgi

[Install]
WantedBy=multi-user.target
EOF


sudo systemctl daemon-reload
sudo systemctl enable gunicorn

# Run migrations and collectstatic
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# --- Nginx setup ---
sudo yum install -y nginx

# Remove old/conflicting Nginx configs
if [ -f /etc/nginx/conf.d/default.conf ]; then
  sudo rm /etc/nginx/conf.d/default.conf
fi

# Ensure server_names_hash_bucket_size is set
if ! grep -q "server_names_hash_bucket_size" /etc/nginx/nginx.conf; then
  sudo sed -i '/http {/a \    server_names_hash_bucket_size 128;' /etc/nginx/nginx.conf
fi

# Nginx config for Django
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

sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

sudo systemctl restart gunicorn

deactivate

echo "Deployment script completed successfully."
