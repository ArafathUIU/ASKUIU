#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=== Upgrading pip ==="
pip install --upgrade pip

echo "=== Installing lightweight CPU-only PyTorch ==="
pip install torch --extra-index-url https://download.pytorch.org/whl/cpu

echo "=== Installing dependencies from requirements.txt ==="
pip install -r requirements.txt

echo "=== Build complete ==="
