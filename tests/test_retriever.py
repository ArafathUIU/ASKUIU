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


def test_retrieve_tuition_fees(retriever):
    results = retriever.retrieve_data("What is the tuition fee for BSc in CSE?", k=3)
    assert len(results) > 0
    all_text = " ".join(doc["text"] for doc in results)
    assert "6,500" in all_text or "141" in all_text or "10,14,500" in all_text


def test_retrieve_department_heads(retriever):
    results_eee = retriever.retrieve_data("Who is the head of EEE department?", k=3)
    eee_text = " ".join(doc["text"] for doc in results_eee)
    assert "Kaled Masukur Rahman" in eee_text or "EEE" in eee_text

    results_cse = retriever.retrieve_data("Who is the head of CSE department?", k=3)
    cse_text = " ".join(doc["text"] for doc in results_cse)
    assert "Mohammad Nurul Huda" in cse_text or "CSE" in cse_text


def test_query_typo_normalization():
    expanded = Retriever.normalize_and_expand_query("wherre is UIU?")
    assert "where" in expanded
    assert "permanent campus" in expanded

    tuition_exp = Retriever.normalize_and_expand_query("tution fee for couse")
    assert "tuition" in tuition_exp
    assert "course" in tuition_exp
