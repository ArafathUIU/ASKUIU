"""Generate sentence embeddings from the UIU knowledge base CSV.

Usage:
    python scripts/generate_embeddings.py

This script reads app/rag/data/AskUIU.csv (single-column Text file),
generates embeddings using sentence-transformers/all-MiniLM-L6-v2, and
saves them to app/rag/data/article_embeddings.pkl.
"""

import os
import pickle

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(PROJECT_ROOT, "app", "rag", "data", "AskUIU.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "app", "rag", "data", "article_embeddings.pkl")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_texts(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")
    df = pd.read_csv(csv_path)
    if "Text" not in df.columns:
        raise ValueError(f"CSV must contain a 'Text' column. Columns: {df.columns.tolist()}")
    texts = df["Text"].dropna().astype(str).tolist()
    print(f"Loaded {len(texts)} documents from {csv_path}")
    return texts


def generate_embeddings(texts, model_name=MODEL_NAME):
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    print("Encoding documents...")
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    print(f"Generated embeddings shape: {embeddings.shape}")
    return embeddings


def save_embeddings(embeddings, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        pickle.dump(embeddings, f)
    print(f"Saved embeddings to {output_path}")


def main():
    texts = load_texts(CSV_PATH)
    embeddings = generate_embeddings(texts)
    save_embeddings(embeddings, OUTPUT_PATH)


if __name__ == "__main__":
    main()
