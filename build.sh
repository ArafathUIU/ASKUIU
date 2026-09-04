#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=== Upgrading pip ==="
pip install --upgrade pip

echo "=== Installing dependencies from requirements.txt ==="
pip install -r requirements.txt

echo "=== Pre-caching FastEmbed ONNX model ==="
python -c "from fastembed import TextEmbedding; list(TextEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2').embed(['UIU']))"

echo "=== Build complete ==="
