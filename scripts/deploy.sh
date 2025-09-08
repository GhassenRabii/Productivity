#!/bin/bash
set -euo pipefail

source /home/ec2-user/.bash_profile

APP_DIR=/home/ec2-user/djangoapp
GUNICORN_SVC=/etc/systemd/system/gunicorn.service
NGINX_DJANGO_CONF=/etc/nginx/conf.d/django.conf
NGINX_CONF=/etc/nginx/nginx.conf
REGION=eu-central-1

echo "[*] Running as user: $(whoami)"
echo "[*] In: $(pwd)"

# Restore persisted media if you used the persistence step
if [ -d /home/ec2-user/persist/media ]; then
  mkdir -p "$APP_DIR/media"
  rsync -a /home/ec2-user/persist/media/ "$APP_DIR/media/"
fi

# Ensure ownership
sudo chown -R ec2-user:ec2-user "$APP_DIR"
cd "$APP_DIR"

# Clean pyc just in case
find "$APP_DIR" -name '__pycache__' -type d -exec rm -rf {} + || true
find "$APP_DIR" -name '*.pyc' -delete || true

# --- Require DB secret ---
: "${DJANGO_DB_SECRET_ARN:?ERROR: DJANGO_DB_SECRET_ARN is not set}"

# --- Virtualenv ---
if [ -d venv ]; then rm -rf venv; fi
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# --- DB creds from Secrets Manager ---
DB_SECRET=$(aws secretsmanager get-secret-value --secret-id "$DJANGO_DB_SECRET_ARN" --region "$REGION" --query SecretString --output text)
DB_USER=$(echo "$DB_SECRET" | python3 -c "import sys,json;print(json.load(sys.stdin)['username'])")
DB_PASS=$(echo "$DB_SECRET" | python3 -c "import sys,json;print(json.load(sys.stdin)['password'])")
DB_HOST=$(echo "$DB_SECRET" | python3 -c "import sys,json;print(json.load(sys.stdin)['host'])")
DB_NAME=$(echo "$DB_SECRET" | python3 -c "import sys,json;print(json.load(sys.stdin)['dbname'])")

export DB_USER DB_PASSWORD="$DB_PASS" DB_HOST DB_NAME
echo "[*] DB_USER=$DB_USER  DB_HOST=$DB_HOST  DB_NAME=$DB_NAME"

# --- Gunicorn systemd unit ---
cat > /tmp/gunicorn.service <<EOF
[Unit]
Description=gunicorn daemon for Django
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=DB_USER=$DB_USER
Environment=DB_PASSWORD=$DB_PASS
Environment=DB_HOST=$DB_HOST
Environment=DB_NAME=$DB_NAME
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 mysite.wsgi
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/gunicorn.service "$GUNICORN_SVC"
sudo systemctl daemon-reload
sudo systemctl enable gunicorn

# --- Django mgmt ---
echo "[*] Migrations present:"
ls -la tasks/migrations || true
echo "[*] Applying migrations…"
python manage.py migrate --noinput
echo "[*] Collecting static…"
python manage.py collectstatic --noinput

# --- Nginx ---
if ! rpm -q nginx >/dev/null 2>&1; then
  sudo yum install -y nginx
fi

sudo chmod o+x /home/ec2-user
sudo chmod o+x /home/ec2-user/djangoapp
sudo chmod -R 755 "$APP_DIR/static"
sudo chown -R ec2-user:nginx "$APP_DIR/static"

sudo find /etc/nginx/conf.d/ ! -name 'django.conf' -type f -delete || true

sudo cp "$NGINX_CONF" "$NGINX_CONF.bak" || true
sudo tee "$NGINX_CONF" > /dev/null <<'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /run/nginx.pid;

events { worker_connections 1024; }

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
    access_log  /var/log/nginx/access.log  main;

    sendfile on;
    keepalive_timeout 65;

    include /etc/nginx/conf.d/*.conf;
    server_names_hash_bucket_size 128;
}
EOF

sudo tee "$NGINX_DJANGO_CONF" > /dev/null <<EOF
server {
    listen 80;
    server_name _;

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
echo "[*] Deployment complete."
