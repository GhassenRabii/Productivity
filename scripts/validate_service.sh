#!/bin/bash
set -e

echo "[*] Validating Gunicorn service..."
if ! systemctl is-active --quiet gunicorn; then
  echo "❌ Gunicorn is NOT running!"
  exit 1
else
  echo "✅ Gunicorn is running."
fi

echo "[*] Validating Nginx service..."
if ! systemctl is-active --quiet nginx; then
  echo "❌ Nginx is NOT running!"
  exit 1
else
  echo "✅ Nginx is running."
fi

# Optionally, check HTTP response (localhost or ELB, as appropriate)
echo "[*] Checking HTTP response from localhost..."
if ! curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1 | grep -q "200"; then
  echo "❌ Django app did not return HTTP 200!"
  exit 1
else
  echo "✅ Django app responded with HTTP 200."
fi

echo "[*] Validate service completed successfully!"
