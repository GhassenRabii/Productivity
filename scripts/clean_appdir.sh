#!/bin/bash
set -euo pipefail

APP_DIR="/home/ec2-user/djangoapp"

echo "[INFO] Cleaning $APP_DIR directory..."

if [ -d "$APP_DIR" ]; then
  # Ensure ec2-user owns the directory (optional but safer)
  sudo chown -R ec2-user:ec2-user "$APP_DIR"
  
  # Delete contents safely with elevated permissions
  sudo rm -rf "${APP_DIR:?}/"*
  echo "[INFO] Clean-up complete."
else
  echo "[INFO] $APP_DIR does not exist, nothing to clean."
fi
