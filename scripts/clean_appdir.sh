#!/bin/bash
set -euo pipefail

echo "[INFO] Cleaning /home/ec2-user/djangoapp directory..."

# Ensure ec2-user owns the directory (optional but safer)
sudo chown -R ec2-user:ec2-user /home/ec2-user/djangoapp

# Delete contents safely with elevated permissions
sudo rm -rf /home/ec2-user/djangoapp/*

echo "[INFO] Clean-up complete."
