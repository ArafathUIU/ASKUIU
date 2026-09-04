#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=== Upgrading pip ==="
pip install --upgrade pip

echo "=== Installing lightweight CPU-only PyTorch ==="
pip install torch --extra-index-url https://download.pytorch.org/whl/cpu

echo "=== Installing dependencies from requirements.txt ==="
pip install -r requirements.txt

echo "=== Pre-downloading SentenceTransformer model into cache ==="
export HF_HOME="${PWD}/.cache/huggingface"
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

echo "=== Build complete ==="
