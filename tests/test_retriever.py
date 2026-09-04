import pytest

from app.rag.retriever import Retriever


@pytest.fixture(scope="module")
def retriever():
    return Retriever()


def test_retriever_loads_csv(retriever):
    assert retriever.df is not None
    assert "Text" in retriever.df.columns
    assert len(retriever.df) > 0


def test_retriever_embedding_shape(retriever):
    embedding = retriever.generate_embeddings("What is UIU?")
    assert embedding.shape == (384,)


def test_retrieve_data_returns_results(retriever):
    results = retriever.retrieve_data("Who is the CSE head?", k=3)
    assert isinstance(results, list)
    assert len(results) == 3
    assert all("text" in doc for doc in results)
    # Check enhanced metadata
    assert all("title" in doc for doc in results)
    assert all("source" in doc for doc in results)
    assert all("category" in doc for doc in results)
    assert all("confidence" in doc for doc in results)


def test_category_filtering(retriever):
    results = retriever.retrieve_data("admission requirements", category="admission", k=3)
    assert len(results) > 0
    assert all(doc["category"] == "admission" for doc in results)


def test_process_context_truncates(retriever):
    docs = [{"text": "word " * 1000, "title": "Test Title", "source": "https://uiu.ac.bd"}]
    context = retriever.process_context(docs, max_tokens=100)
    assert isinstance(context, str)
    assert len(context.split()) <= 100
    assert "[1]" in context
