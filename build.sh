#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=== Upgrading pip ==="
pip install --upgrade pip

echo "=== Installing dependencies from requirements.txt ==="
pip install -r requirements.txt

echo "=== Pre-caching FastEmbed ONNX model into persistent project cache ==="
export FASTEMBED_CACHE_PATH="${PWD}/.cache/fastembed"
mkdir -p "${FASTEMBED_CACHE_PATH}"
python -c "
import os, sys
from fastembed import TextEmbedding
cache_dir = os.environ.get('FASTEMBED_CACHE_PATH')
print(f'Caching FastEmbed model to {cache_dir}...')
try:
    model = TextEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2', cache_dir=cache_dir, threads=1)
    list(model.embed(['UIU']))
    print('FastEmbed ONNX model successfully cached!')
except Exception as e:
    print(f'Warning: FastEmbed pre-caching encountered an issue: {e}', file=sys.stderr)
"

echo "=== Build complete ==="
