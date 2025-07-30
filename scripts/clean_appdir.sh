#!/bin/bash
set -euo pipefail

APP_DIR="/home/ec2-user/djangoapp"

echo "[INFO] Ensuring $APP_DIR exists..."
sudo mkdir -p "$APP_DIR"
sudo chown ec2-user:ec2-user "$APP_DIR"

echo "[INFO] Cleaning $APP_DIR directory..."

# Ensure ec2-user owns the directory
sudo chown -R ec2-user:ec2-user "$APP_DIR"

# Delete contents safely with elevated permissions
sudo rm -rf "${APP_DIR:?}/"*

echo "[INFO] Clean-up complete."
