import logging
import threading
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from app.rag.generator import Generator
    from app.rag.retriever import Retriever

logger = logging.getLogger(__name__)

_retriever_instance: Optional[Any] = None
_generator_instance: Optional[Any] = None
_init_lock = threading.Lock()


def get_retriever():
    global _retriever_instance
    if _retriever_instance is None:
        with _init_lock:
            if _retriever_instance is None:
                logger.info("Initializing global Retriever instance...")
                from app.rag.retriever import Retriever
                _retriever_instance = Retriever()
    return _retriever_instance


def get_generator():
    global _generator_instance
    if _generator_instance is None:
        with _init_lock:
            if _generator_instance is None:
                logger.info("Initializing global Generator instance...")
                from app.rag.generator import Generator
                _generator_instance = Generator()
    return _generator_instance


def is_retriever_ready() -> bool:
    return _retriever_instance is not None


def warmup_async():
    """Warm up retriever and generator in a background thread after server starts."""
    def _warmup():
        try:
            logger.info("Background warmup: initializing retriever and generator...")
            get_retriever()
            get_generator()
            logger.info("Background warmup: complete! System ready.")
        except Exception as e:
            logger.warning("Background warmup encountered error: %s", e)

    t = threading.Thread(target=_warmup, daemon=True, name="rag-warmup")
    t.start()


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
    def retriever(self):
        return get_retriever()

    @property
    def generator(self):
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


# Module singletons with lazy resolution to keep application startup instantaneous
class _LazyRetriever:
    def __getattr__(self, name):
        return getattr(get_retriever(), name)


class _LazyGenerator:
    def __getattr__(self, name):
        return getattr(get_generator(), name)


rag_service = RAGService()
retriever = _LazyRetriever()
generator = _LazyGenerator()
