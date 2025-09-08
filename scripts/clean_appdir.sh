#!/bin/bash
set -euo pipefail

APP_DIR="/home/ec2-user/djangoapp"
PERSIST_DIR="/home/ec2-user/persist"

echo "[INFO] Stopping services (if running)…"
sudo systemctl stop gunicorn 2>/dev/null || true
sudo systemctl stop nginx    2>/dev/null || true

echo "[INFO] Ensuring $APP_DIR exists and owned by ec2-user…"
sudo mkdir -p "$APP_DIR"
sudo chown -R ec2-user:ec2-user "$APP_DIR"

# Optional: preserve media uploads between releases
if [ -d "$APP_DIR/media" ]; then
  echo "[INFO] Preserving media to $PERSIST_DIR/media …"
  mkdir -p "$PERSIST_DIR/media"
  rsync -a "$APP_DIR/media/" "$PERSIST_DIR/media/" || true
fi

echo "[INFO] Cleaning $APP_DIR …"
# Extra safety: only remove inside APP_DIR
sudo rm -rf "${APP_DIR:?}/"* "${APP_DIR:?}"/.[!.]* "${APP_DIR:?}"/..?* 2>/dev/null || true

echo "[INFO] Clean-up complete."
