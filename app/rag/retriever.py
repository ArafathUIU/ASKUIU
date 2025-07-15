import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import io
from typing import List, Dict, Any
import os

class Retriever:
    def __init__(self, csv_path: str = "app/rag/data/Dummy_Data.csv"):
        """Initialize retriever with CSV data and FAISS index."""
        self.df = self.load_csv_data(csv_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight embedding model
        self.index = self.build_faiss_index()
    
    def load_csv_data(self, csv_path: str) -> pd.DataFrame:
        """Load CSV content into a pandas DataFrame."""
        try:
            if os.path.exists(csv_path):
                return pd.read_csv(csv_path)
            else:
                raise FileNotFoundError(f"CSV file not found at {csv_path}")
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return pd.DataFrame()  # Return empty DataFrame on failure

    def build_faiss_index(self) -> faiss.IndexFlatL2:
        """Build FAISS index for vector-based search."""
        # Combine 'Value' and 'Additional Info' for embedding
        texts = (self.df['Value'].astype(str) + " " + self.df['Additional Info'].astype(str).fillna("")).tolist()
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype(np.float32))
        return index

    def retrieve_data(self, query: str, category: str = None, field: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve top-k relevant rows from CSV based on query, category, or field.
        
        Args:
            query (str): Search keyword or phrase.
            csv_content (str): CSV data as a string.
            category (str, optional): Filter by category (e.g., 'Faculty', 'Rules').
            field (str, optional): Filter by field (e.g., 'Name', 'Rule Description').
            top_k (int): Number of results to return.
        
        Returns:
            List[Dict[str, Any]]: List of matching rows as dictionaries.
        """
        # Filter by category and/or field if provided
        df_filtered = self.df
        if category:
            df_filtered = df_filtered[df_filtered['Category'].str.lower() == category.lower()]
        if field:
            df_filtered = df_filtered[df_filtered['Field'].str.lower() == field.lower()]
        
        # If no query, return top_k rows from filtered DataFrame
        if not query:
            return [row.to_dict() for _, row in df_filtered.head(top_k).iterrows()]
        
        # Encode query and search FAISS index
        query_embedding = self.model.encode([query], show_progress_bar=False)
        distances, indices = self.index.search(query_embedding.astype(np.float32), top_k)
        
        # Retrieve matching rows, ensuring they match category/field filters
        results = []
        for idx in indices[0]:
            if idx < len(df_filtered):
                row = df_filtered.iloc[idx].to_dict()
                results.append({
                    'Category': row['Category'],
                    'Field': row['Field'],
                    'Value': row['Value'],
                    'Additional Info': row['Additional Info']
                })
        
        return results

if __name__ == "__main__":
    # Example usage
    retriever = Retriever()
    query = "CSE faculty"
    results = retriever.retrieve_data(query, category="Faculty", top_k=3)
    for result in results:
        print(result)