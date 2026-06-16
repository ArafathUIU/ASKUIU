import os
import pickle

import faiss
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_CSV_PATH = os.path.join(PROJECT_ROOT, "app", "rag", "data", "AskUIU.csv")
DEFAULT_EMBEDDINGS_PATH = os.path.join(
    PROJECT_ROOT, "app", "rag", "data", "article_embeddings.pkl"
)


class Retriever:
    def __init__(
        self,
        csv_path=None,
        embeddings_path=None,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.csv_path = csv_path or DEFAULT_CSV_PATH
        self.embeddings_path = embeddings_path or DEFAULT_EMBEDDINGS_PATH

        self.df = self._load_csv(self.csv_path)
        self.article_embeddings = self._load_embeddings(self.embeddings_path)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embedding_model = SentenceTransformer(model_name).to(self.device)

        dimension = len(self.article_embeddings[0])
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(self.article_embeddings))

    @staticmethod
    def _load_csv(csv_path):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            if "Text" not in df.columns:
                raise ValueError(f"CSV at {csv_path} must contain a 'Text' column")
            return df
        except Exception as e:
            raise ValueError(f"Failed to load CSV at {csv_path}: {e}")

    @staticmethod
    def _load_embeddings(embeddings_path):
        if not os.path.exists(embeddings_path):
            raise FileNotFoundError(
                f"Embeddings file not found at {embeddings_path}. "
                "Run 'python scripts/generate_embeddings.py' to create it."
            )
        try:
            with open(embeddings_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load embeddings at {embeddings_path}: {e}")

    def generate_embeddings(self, text):
        return self.embedding_model.encode(text, convert_to_numpy=True)

    def retrieve_data(self, query, category=None, field=None, k=3):
        query_embedding = self.generate_embeddings(query)
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype("float32"), k
        )
        results = []
        for idx in indices[0]:
            if idx < len(self.df):
                row = self.df.iloc[idx]
                item = {"text": str(row.get("Text", "")), "index": int(idx)}
                for col in ["Category", "Field"]:
                    if col in row:
                        item[col.lower()] = row[col]
                if category and item.get("category") != category:
                    continue
                if field and item.get("field") != field:
                    continue
                results.append(item)
        return results

    @staticmethod
    def process_context(docs, max_tokens=1536):
        processed_docs = []
        total_tokens = 0
        for doc in docs:
            text = doc["text"] if isinstance(doc, dict) else doc
            tokens = len(text.split())
            if total_tokens + tokens <= max_tokens:
                processed_docs.append(text)
                total_tokens += tokens
            else:
                break
        return "\n".join(f"- {doc}" for doc in processed_docs)
