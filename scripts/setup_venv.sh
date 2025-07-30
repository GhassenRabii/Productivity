#!/bin/bash
set -euo pipefail

APP_DIR=/home/ec2-user/djangoapp

cd "$APP_DIR"
sudo chown -R ec2-user:ec2-user "$APP_DIR"

# Clean and recreate virtualenv
if [ -d "venv" ]; then
  rm -rf venv
fi
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "[+] Python virtualenv setup completed."
