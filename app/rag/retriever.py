import logging
import math
import os
import pickle
import re
from collections import Counter

import faiss
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DEFAULT_CSV_PATH = os.path.join(PROJECT_ROOT, "app", "rag", "data", "AskUIU.csv")
DEFAULT_EMBEDDINGS_PATH = os.path.join(
    PROJECT_ROOT, "app", "rag", "data", "article_embeddings.pkl"
)


class BM25Ranker:
    """Lightweight, self-contained BM25 implementation for lexical keyword search."""

    def __init__(self, corpus, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        self.doc_lens = [len(tokens) for tokens in self.tokenized_corpus]
        self.avg_doc_len = sum(self.doc_lens) / max(self.corpus_size, 1)
        self.doc_freqs = []
        self.idf = {}
        self._initialize()

    @staticmethod
    def _tokenize(text):
        return re.findall(r"\b[a-zA-Z0-9_\-\.]+\b", str(text).lower())

    def _initialize(self):
        df_counter = Counter()
        for tokens in self.tokenized_corpus:
            unique_tokens = set(tokens)
            df_counter.update(unique_tokens)
            self.doc_freqs.append(Counter(tokens))

        for term, freq in df_counter.items():
            self.idf[term] = math.log(
                1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5)
            )

    def get_scores(self, query):
        query_tokens = self._tokenize(query)
        scores = np.zeros(self.corpus_size, dtype=np.float32)

        for token in query_tokens:
            idf_val = self.idf.get(token, 0.0)
            if idf_val <= 0:
                continue

            for idx in range(self.corpus_size):
                tf = self.doc_freqs[idx].get(token, 0)
                if tf > 0:
                    doc_len = self.doc_lens[idx]
                    denom = tf + self.k1 * (
                        1.0 - self.b + self.b * (doc_len / self.avg_doc_len)
                    )
                    scores[idx] += idf_val * (tf * (self.k1 + 1.0)) / denom

        return scores


class Retriever:
    """Intelligent hybrid retriever combining dense semantic embeddings and BM25 lexical search."""

    def __init__(
        self,
        csv_path=None,
        embeddings_path=None,
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        auto_build=True,
    ):
        self.csv_path = csv_path or DEFAULT_CSV_PATH
        self.embeddings_path = embeddings_path or DEFAULT_EMBEDDINGS_PATH
        self.model_name = model_name

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Initializing SentenceTransformer on device: %s", self.device)
        self.embedding_model = SentenceTransformer(self.model_name).to(self.device)

        self.df = self._load_csv(self.csv_path)

        # Load or auto-build embeddings
        self.article_embeddings = self._load_or_build_embeddings(auto_build=auto_build)

        # Build normalized FAISS index for Cosine Similarity
        self.dimension = self.article_embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)
        normalized_embs = self.article_embeddings.copy().astype(np.float32)
        faiss.normalize_L2(normalized_embs)
        self.index.add(normalized_embs)

        # Build BM25 index over documents
        corpus_texts = [
            f"{row.get('Title', '')} {row.get('Text', '')}"
            for _, row in self.df.iterrows()
        ]
        self.bm25 = BM25Ranker(corpus_texts)
        logger.info("Retriever initialized with %d indexed documents", len(self.df))

    def _load_csv(self, csv_path):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            if "Text" not in df.columns:
                raise ValueError(f"CSV at {csv_path} must contain a 'Text' column")
            return df
        except Exception as e:
            raise ValueError(f"Failed to load CSV at {csv_path}: {e}")

    def _load_or_build_embeddings(self, auto_build=True):
        if os.path.exists(self.embeddings_path):
            try:
                with open(self.embeddings_path, "rb") as f:
                    embeddings = pickle.load(f)
                    if isinstance(embeddings, list):
                        embeddings = np.array(embeddings)
                    return embeddings.astype(np.float32)
            except Exception as e:
                logger.warning("Failed to load existing embeddings (%s), rebuilding...", e)

        if not auto_build:
            raise FileNotFoundError(
                f"Embeddings file not found at {self.embeddings_path}."
            )

        logger.info("Auto-building embeddings for %d documents...", len(self.df))
        texts = self.df["Text"].fillna("").astype(str).tolist()
        embeddings = self.embedding_model.encode(
            texts, convert_to_numpy=True, show_progress_bar=False
        ).astype(np.float32)

        os.makedirs(os.path.dirname(self.embeddings_path), exist_ok=True)
        with open(self.embeddings_path, "wb") as f:
            pickle.dump(embeddings, f)
        logger.info("Saved fresh embeddings to %s", self.embeddings_path)
        return embeddings

    @staticmethod
    def normalize_and_expand_query(query: str) -> str:
        """Fix common misspellings and expand university domain queries."""
        if not query:
            return ""
        q = query.strip()

        typo_map = {
            r"\bwherre\b": "where",
            r"\bwhr\b": "where",
            r"\blocatoin\b": "location",
            r"\bloction\b": "location",
            r"\badmissoin\b": "admission",
            r"\badmision\b": "admission",
            r"\bdept\b": "department",
            r"\bdep\b": "department",
            r"\bschlarship\b": "scholarship",
            r"\bscholarshp\b": "scholarship",
            r"\btution\b": "tuition",
            r"\bcredts\b": "credits",
            r"\bcouse\b": "course",
            r"\bprogarm\b": "program",
        }
        for pat, repl in typo_map.items():
            q = re.sub(pat, repl, q, flags=re.IGNORECASE)

        # Contextual keyword expansion for short domain queries
        q_lower = q.lower()
        if any(w in q_lower for w in ["where is", "location of", "address of", "permanent campus"]):
            if "campus" not in q_lower:
                q = f"{q} permanent campus location address United City Madani Avenue Badda"
        has_head = any(w in q_lower for w in ["head", "chair", "lead", "director", "dean"])
        if ("eee" in q_lower or "electrical" in q_lower) and has_head:
            q = f"{q} Department Heads Department of EEE chairperson head Dr. Kaled Masukur Rahman"
        elif ("cse" in q_lower or "computer science" in q_lower) and has_head:
            q = f"{q} Department Heads Department of CSE chairperson head Dr. Mohammad Nurul Huda"
        elif ("civil" in q_lower or "ce" in q_lower) and has_head:
            q = f"{q} Department Heads Department of Civil Engineering head Dr. Rumana Afrin"
        elif ("pharmacy" in q_lower or "pharm" in q_lower) and has_head:
            q = f"{q} Department Heads Department of Pharmacy head Dr. Tahmina Foyez"
        elif ("english" in q_lower) and has_head:
            q = f"{q} Department Heads Department of English head Dr. Md. Kamrul Hasan"
        elif ("data science" in q_lower or "datascience" in q_lower) and (has_head or "director" in q_lower):
            q = f"{q} Department Heads BSc in Data Science Program Director Dr. Jannatun Noor Mukta"
        elif "proctor" in q_lower:
            q = f"{q} Proctorial Committee Proctor Dr. Rumana Afrin"
        elif any(w in q_lower for w in ["vice chancellor", "vc", "vice-chancellor"]):
            q = f"{q} Vice Chancellor Prof. Dr. Md. Abul Kashem Mia"
        elif any(w in q_lower for w in ["tuition", "fee", "cost", "how much", "credit fee", "per credit"]):
            q = f"{q} tuition fees credit breakdown waiver total cost Tk 6500"
        elif any(w in q_lower for w in ["shuttle", "bus", "transport"]):
            q = f"{q} transportation service shuttle bus routes Notun Bazar"
        elif any(w in q_lower for w in ["mars rover", "rover team", "urc", "maven"]):
            q = f"{q} UIU Mars Rover Team MAVEN URC Asia No. 1 World No. 3"
        elif any(w in q_lower for w in ["grading", "gpa", "cgpa", "probation"]):
            q = f"{q} grading scale grade points CGPA 2.00 academic probation"

        return q

    def generate_embeddings(self, text):
        return self.embedding_model.encode(text, convert_to_numpy=True)

    def retrieve_data(self, query, category=None, field=None, k=4, hybrid=True, deduplicate_sources=True):
        """Retrieve top-k documents using Hybrid RRF (Dense + BM25) with query normalization and diverse source deduplication."""
        if not query or not query.strip():
            return []

        search_query = self.normalize_and_expand_query(query)

        # Dense retrieval
        query_emb = self.generate_embeddings(search_query).reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query_emb)
        candidate_k = min(len(self.df), max(k * 5, 20))
        dense_scores, dense_indices = self.index.search(query_emb, candidate_k)

        dense_ranks = {}
        for rank, idx in enumerate(dense_indices[0]):
            if idx >= 0 and idx < len(self.df):
                dense_ranks[int(idx)] = rank + 1

        if hybrid:
            # BM25 lexical retrieval
            bm25_scores = self.bm25.get_scores(search_query)
            top_bm25_indices = np.argsort(bm25_scores)[::-1][:candidate_k]
            bm25_ranks = {}
            for rank, idx in enumerate(top_bm25_indices):
                if bm25_scores[idx] > 0:
                    bm25_ranks[int(idx)] = rank + 1

            # Reciprocal Rank Fusion (RRF)
            all_candidate_indices = set(dense_ranks.keys()).union(bm25_ranks.keys())
            rrf_scores = {}
            for idx in all_candidate_indices:
                score = 0.0
                if idx in dense_ranks:
                    score += 1.0 / (60.0 + dense_ranks[idx])
                if idx in bm25_ranks:
                    score += 1.0 / (60.0 + bm25_ranks[idx])
                rrf_scores[idx] = score

            sorted_indices = sorted(
                rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True
            )
        else:
            sorted_indices = [int(i) for i in dense_indices[0] if i >= 0]

        # Filter and build rich metadata results with source deduplication
        results = []
        seen_sources = set()

        for idx in sorted_indices:
            row = self.df.iloc[idx]
            row_category = str(row.get("Category", "")).strip().lower()

            if category and row_category != str(category).strip().lower():
                continue
            if field and str(row.get("Field", "")).strip().lower() != str(field).strip().lower():
                continue

            source_url = str(row.get("Source", "https://www.uiu.ac.bd/")).strip().rstrip("/").lower()
            if deduplicate_sources and source_url in seen_sources:
                continue

            seen_sources.add(source_url)
            item = {
                "index": int(idx),
                "text": str(row.get("Text", "")).strip(),
                "title": str(row.get("Title", "UIU Knowledge Base")).strip(),
                "source": str(row.get("Source", "https://www.uiu.ac.bd/")).strip(),
                "category": row_category or "general",
                "chunk_index": int(row.get("ChunkIndex", 0)) if pd.notna(row.get("ChunkIndex")) else 0,
            }

            if idx in dense_ranks:
                dense_pos = np.where(dense_indices[0] == idx)[0]
                if len(dense_pos) > 0:
                    item["confidence"] = round(float(dense_scores[0][dense_pos[0]]), 3)
            else:
                item["confidence"] = 0.5

            results.append(item)
            if len(results) >= k:
                break

        # Fallback to fill up to k if deduplication was overly strict
        if len(results) < k:
            for idx in sorted_indices:
                if any(r["index"] == idx for r in results):
                    continue
                row = self.df.iloc[idx]
                row_category = str(row.get("Category", "")).strip().lower()
                if category and row_category != str(category).strip().lower():
                    continue

                item = {
                    "index": int(idx),
                    "text": str(row.get("Text", "")).strip(),
                    "title": str(row.get("Title", "UIU Knowledge Base")).strip(),
                    "source": str(row.get("Source", "https://www.uiu.ac.bd/")).strip(),
                    "category": row_category or "general",
                    "chunk_index": int(row.get("ChunkIndex", 0)) if pd.notna(row.get("ChunkIndex")) else 0,
                    "confidence": 0.5,
                }
                results.append(item)
                if len(results) >= k:
                    break

        return results


    @staticmethod
    def process_context(docs, max_tokens=1536):
        """Format retrieved docs into a clean context string for LLM generation with citation tags."""
        processed_docs = []
        remaining_tokens = max_tokens
        for i, doc in enumerate(docs, 1):
            if remaining_tokens <= 0:
                break
            if isinstance(doc, dict):
                text = doc.get("text", "")
                title = doc.get("title", f"Source {i}")
                source = doc.get("source", "")
                header = f"[{i}] {title} ({source}):\n"
            else:
                header = ""
                text = str(doc)

            header_tokens = len(header.split())
            available_for_text = max(remaining_tokens - header_tokens, 0)
            if available_for_text <= 0 and processed_docs:
                break

            words = text.split()
            if len(words) > available_for_text:
                truncated_text = " ".join(words[:available_for_text])
                formatted = f"{header}{truncated_text}..."
                remaining_tokens = 0
            else:
                formatted = f"{header}{text}"
                remaining_tokens -= (header_tokens + len(words))

            processed_docs.append(formatted)

        return "\n\n".join(processed_docs)


    def get_stats(self):
        """Return index statistics."""
        return {
            "total_documents": len(self.df),
            "categories": self.df["Category"].value_counts().to_dict() if "Category" in self.df else {},
            "embedding_dimension": self.dimension,
            "device": self.device,
            "model_name": self.model_name,
        }
