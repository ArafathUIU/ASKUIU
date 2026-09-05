import json
import logging
import os
import re
import time
from typing import Dict, Generator as PyGenerator, List, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Generator:
    """Multi-provider answer generator supporting Groq (Llama-3.3), Google Gemini,

    OpenAI-compatible APIs, Opencode Go, and an offline concise extractive fallback engine.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "auto")).lower()

        # Groq config (Ultra-fast LPU inference)
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        self.groq_base_url = "https://api.groq.com/openai/v1"


        # Google Gemini config
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        # Opencode Go config
        self.opencodego_key = api_key or os.getenv("OPENCODEGO_API_KEY")
        self.opencodego_base_url = (
            base_url or os.getenv("OPENCODEGO_BASE_URL", "https://opencode.ai/zen/go/v1")
        ).rstrip("/")
        self.opencodego_model = model or os.getenv("OPENCODEGO_MODEL", "kimi-k2.7-code")

        # OpenAI / generic OpenAI-compatible config (Ollama, DeepSeek)
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_base_url = (
            os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        ).rstrip("/")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self.explicit_empty_key = (api_key == "")
        self.active_provider = self._resolve_active_provider()
        logger.info("Generator active provider resolved to: %s", self.active_provider)

    def _resolve_active_provider(self) -> str:
        if self.explicit_empty_key or (self.provider == "opencodego" and not self.opencodego_key):
            return "opencodego"

        if self.provider == "groq" and self.groq_key:
            return "groq"
        if self.provider == "gemini" and self.gemini_key:
            return "gemini"
        if self.provider == "opencodego" and self.opencodego_key:
            return "opencodego"
        if self.provider == "openai" and self.openai_key:
            return "openai"

        # Auto detection priority: Groq -> Gemini -> OpenCode Go -> OpenAI
        if self.groq_key:
            return "groq"
        if self.gemini_key:
            return "gemini"
        if self.opencodego_key:
            return "opencodego"
        if self.openai_key:
            return "openai"

        return "extractive_fallback"

    def _build_context(self, docs: List[Dict], max_tokens: int = 768) -> str:
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

    def _build_system_prompt(self) -> str:
        return (
            "You are ASKUIU, the official intelligent AI assistant for United International University (UIU). "
            "Provide a direct, accurate, and concise answer (strictly 1 to 3 clear sentences, or a tight bulleted list of 2-4 points only if listing specific items). "
            "Ground your response strictly in the provided context and cite sources using inline brackets like [1], [2]. "
            "Do not repeat the user's question, and avoid fluff, preamble, or conversational filler. "
            "If the context does not contain sufficient facts to answer the question, state directly: "
            "'I do not have enough verified information from UIU records to answer that accurately.' "
            "Never guess or fabricate facts, tuition amounts, or faculty names."
        )

    def generate_answer(
        self, retrieved_docs: List[Dict], query: str, max_tokens: int = 512
    ) -> str:
        """Generate an accurate and concise answer using the active LLM provider or fallback."""
        if self.active_provider == "opencodego" and not self.opencodego_key:
            raise ValueError(
                "OPENCODEGO_API_KEY not found. Set it in your environment or .env file."
            )

        if not retrieved_docs:
            return "Sorry, I couldn't find any relevant university documents matching your question."

        context = self._build_context(retrieved_docs, max_tokens=max_tokens)

        # 1. Groq (High-speed LPU inference)
        if self.active_provider == "groq":
            try:
                return self._call_openai_compatible(
                    query, context, max_tokens=max_tokens,
                    base_url=self.groq_base_url, api_key=self.groq_key, model=self.groq_model
                )
            except Exception as e:
                logger.warning("Groq call failed (%s), falling back...", e)

        # 2. Google Gemini
        if self.active_provider == "gemini":
            try:
                return self._call_gemini(query, context, max_tokens=max_tokens)
            except Exception as e:
                logger.warning("Gemini failed (%s), falling back...", e)

        # 3. Opencode Go / OpenAI
        if self.active_provider in ("opencodego", "openai"):
            try:
                return self._call_openai_compatible(query, context, max_tokens=max_tokens)
            except Exception as e:
                logger.warning("OpenAI-compatible LLM failed (%s), falling back...", e)

        # 4. Resilient Concise Extractive Fallback
        return self._extractive_fallback(retrieved_docs, query)

    def stream_answer(
        self, retrieved_docs: List[Dict], query: str, max_tokens: int = 512
    ) -> PyGenerator[str, None, None]:
        """Stream concise answer tokens in real-time."""
        if not retrieved_docs:
            yield "Sorry, I couldn't find any relevant university documents matching your question."
            return

        context = self._build_context(retrieved_docs, max_tokens=max_tokens)

        # 1. Groq Streaming
        if self.active_provider == "groq":
            try:
                for chunk in self._stream_openai_compatible(
                    query, context, max_tokens=max_tokens,
                    base_url=self.groq_base_url, api_key=self.groq_key, model=self.groq_model
                ):
                    yield chunk
                return
            except Exception as e:
                logger.warning("Groq stream failed (%s), using fallback...", e)

        # 2. Gemini Streaming
        if self.active_provider == "gemini":
            try:
                for chunk in self._stream_gemini(query, context, max_tokens=max_tokens):
                    yield chunk
                return
            except Exception as e:
                logger.warning("Gemini stream failed (%s), using fallback...", e)

        # 3. Opencode Go / OpenAI Streaming
        if self.active_provider in ("opencodego", "openai"):
            try:
                for chunk in self._stream_openai_compatible(
                    query, context, max_tokens=max_tokens
                ):
                    yield chunk
                return
            except Exception as e:
                logger.warning("OpenAI-compatible stream failed (%s), using fallback...", e)

        # 4. Extractive Fallback Streaming
        answer = self._extractive_fallback(retrieved_docs, query)
        words = answer.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")

    def _call_gemini(self, question: str, context: str, max_tokens: int = 512) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent"
            f"?key={self.gemini_key}"
        )
        prompt = f"Context:\n{context}\n\nQuestion: {question}"
        payload = {
            "system_instruction": {"parts": [{"text": self._build_system_prompt()}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.1,
            },
        }

        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            return "Sorry, no response generated."

    def _stream_gemini(
        self, question: str, context: str, max_tokens: int = 512
    ) -> PyGenerator[str, None, None]:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:streamGenerateContent"
            f"?alt=sse&key={self.gemini_key}"
        )
        prompt = f"Context:\n{context}\n\nQuestion: {question}"
        payload = {
            "system_instruction": {"parts": [{"text": self._build_system_prompt()}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.1,
            },
        }

        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        raw = line[6:].strip()
                        if not raw or raw == "[DONE]":
                            continue
                        try:
                            data = json.loads(raw)
                            candidates = data.get("candidates", [])
                            if candidates:
                                parts = (
                                    candidates[0]
                                    .get("content", {})
                                    .get("parts", [])
                                )
                                for part in parts:
                                    text = part.get("text", "")
                                    if text:
                                        yield text
                        except json.JSONDecodeError:
                            continue

    def _call_openai_compatible(
        self,
        question: str,
        context: str,
        max_tokens: int = 512,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        target_base_url = (
            base_url
            or (self.opencodego_base_url if self.active_provider == "opencodego" else self.openai_base_url)
        )
        target_api_key = (
            api_key
            or (self.opencodego_key if self.active_provider == "opencodego" else self.openai_key)
        )
        target_model = (
            model
            or (self.opencodego_model if self.active_provider == "opencodego" else self.openai_model)
        )

        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ]

        with httpx.Client(timeout=45.0) as client:
            for attempt in range(2):
                try:
                    response = client.post(
                        f"{target_base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {target_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": target_model,
                            "messages": messages,
                            "max_tokens": max_tokens,
                            "temperature": 0.1,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    choice = data["choices"][0]["message"]
                    content = choice.get("content", "").strip()
                    if not content:
                        content = choice.get("reasoning_content", "").strip()
                    return content or "Sorry, no response generated."
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429 and attempt == 0:
                        retry_after = float(e.response.headers.get("retry-after", 2.0))
                        logger.warning("Groq rate limit hit, backing off for %.1fs...", retry_after)
                        time.sleep(min(retry_after, 3.0))
                        continue
                    raise

    def _stream_openai_compatible(
        self,
        question: str,
        context: str,
        max_tokens: int = 512,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> PyGenerator[str, None, None]:
        target_base_url = (
            base_url
            or (self.opencodego_base_url if self.active_provider == "opencodego" else self.openai_base_url)
        )
        target_api_key = (
            api_key
            or (self.opencodego_key if self.active_provider == "opencodego" else self.openai_key)
        )
        target_model = (
            model
            or (self.opencodego_model if self.active_provider == "opencodego" else self.openai_model)
        )

        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ]

        with httpx.Client(timeout=45.0) as client:
            with client.stream(
                "POST",
                f"{target_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {target_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": target_model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.1,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        raw = line[6:].strip()
                        if raw == "[DONE]":
                            break
                        try:
                            data = json.loads(raw)
                            choices = data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

    def _extractive_fallback(self, docs: List[Dict], query: str) -> str:
        """Concise and direct extractive synthesis when no external LLM key is configured.

        Selects the top 1-2 most relevant sentences answering the question directly.
        """
        if not docs:
            return "Sorry, I do not have enough verified information from UIU records to answer that accurately."

        query_tokens = set(re.findall(r"\w+", query.lower()))
        stop_words = {"what", "where", "who", "when", "how", "is", "are", "the", "at", "in", "for", "to", "of", "and", "a", "an", "does", "do", "tell", "me", "about"}
        keywords = query_tokens - stop_words

        best_sentence = ""
        best_overlap = -1
        best_doc_idx = 1

        for i, doc in enumerate(docs[:4], 1):
            text = doc.get("text", "")
            raw_sentences = re.split(r"(?<=[.!?\n])\s+", text)
            for sentence in raw_sentences:
                s = sentence.strip()
                s_clean = re.sub(r"^[#*\-\d.\s]+", "", s).strip()
                if len(s_clean) < 20 or len(s_clean) > 300:
                    continue
                s_tokens = set(re.findall(r"\w+", s_clean.lower()))
                overlap = len(keywords.intersection(s_tokens))
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_sentence = s_clean
                    best_doc_idx = i

        if best_sentence:
            clean_s = best_sentence.rstrip(".")
            return f"{clean_s} [{best_doc_idx}]."

        # Fallback to direct clean snippet of top document
        top_text = docs[0].get("text", "").strip()
        first_line = top_text.splitlines()[0] if top_text else ""
        first_line = re.sub(r"^[#*\-\d.\s]+", "", first_line).strip()[:200]
        return f"{first_line} [1]."
