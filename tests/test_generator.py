import pytest

from app.rag.generator import Generator


def test_build_context():
    generator = Generator(api_key="dummy")
    docs = [
        {"text": "UIU is a private university in Bangladesh."},
        {"text": "It was established in 2003."},
    ]
    context = generator._build_context(docs)
    assert "UIU is a private university" in context
    assert "established in 2003" in context


def test_generate_answer_without_api_key_raises(monkeypatch):
    monkeypatch.delenv("OPENCODEGO_API_KEY", raising=False)
    generator = Generator(api_key="")
    with pytest.raises(ValueError, match="OPENCODEGO_API_KEY"):
        generator.generate_answer([], "test query")
