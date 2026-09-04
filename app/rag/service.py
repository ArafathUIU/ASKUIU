import logging
from typing import Optional

from app.rag.generator import Generator
from app.rag.retriever import Retriever

logger = logging.getLogger(__name__)

_retriever_instance: Optional[Retriever] = None
_generator_instance: Optional[Generator] = None


def get_retriever() -> Retriever:
    global _retriever_instance
    if _retriever_instance is None:
        logger.info("Initializing global Retriever instance...")
        _retriever_instance = Retriever()
    return _retriever_instance


def get_generator() -> Generator:
    global _generator_instance
    if _generator_instance is None:
        logger.info("Initializing global Generator instance...")
        _generator_instance = Generator()
    return _generator_instance


class RAGService:
    """Unified service wrapper for UIU RAG operations."""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["rag"] = self

    @property
    def retriever(self) -> Retriever:
        return get_retriever()

    @property
    def generator(self) -> Generator:
        return get_generator()

    def query(self, question: str, category: Optional[str] = None, k: int = 3) -> dict:
        retrieved = self.retriever.retrieve_data(question, category=category, k=k)
        answer = self.generator.generate_answer(retrieved, question)
        return {
            "response": answer,
            "sources": retrieved,
            "provider": self.generator.active_provider,
            "query": question,
        }


# Module singletons for easy import and backwards compatibility
rag_service = RAGService()
retriever = get_retriever()
generator = get_generator()
