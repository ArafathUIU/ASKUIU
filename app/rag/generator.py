import logging
import os

import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Generator:
    def __init__(
        self,
        api_key=None,
        base_url=None,
        model=None,
    ):
        self.api_key = api_key or os.getenv("OPENCODEGO_API_KEY")
        self.base_url = (
            base_url or os.getenv("OPENCODEGO_BASE_URL", "https://api.opencode.ai/v1")
        ).rstrip("/")
        self.model = model or os.getenv(
            "OPENCODEGO_MODEL", "opencode-go/kimi-k2.7-code"
        )

    def generate_answer(self, retrieved_docs, query, max_tokens=300):
        if not self.api_key:
            logger.error("OPENCODEGO_API_KEY is not configured")
            raise ValueError(
                "OPENCODEGO_API_KEY not found. Set it in your environment or .env file."
            )
        context = self._build_context(retrieved_docs)
        return self._call_llm(query, context, max_tokens=max_tokens)

    @staticmethod
    def _build_context(docs, max_tokens=1536):
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

    def _call_llm(self, question, context, max_tokens=300):
        prompt = f"""Use the following context to answer the question. If the context is insufficient, say:
"Sorry, I don't have enough information to answer that yet."

Question: {question}

Context:
{context}"""

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert assistant for United International University (UIU). "
                    "Based on the following context, provide a concise and accurate answer "
                    "to the query in 2-3 sentences. Cite relevant details from the context and ensure clarity."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except httpx.HTTPStatusError as e:
            logger.error(
                "Opencode Go API HTTP error: %s - %s",
                e.response.status_code,
                e.response.text,
            )
            return "Sorry, the language model service returned an error."
        except Exception as e:
            logger.exception("Error generating response with Opencode Go")
            return "Sorry, an error occurred while generating the response."
