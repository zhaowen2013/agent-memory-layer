"""Pluggable text embedding providers.

The default :class:`HashingEmbedder` is pure-Python and has no model
dependency, so the library runs offline out of the box. Swap in a semantic
embedder (:class:`LocalHFEmbedder` or :class:`OpenAIEmbedder`) for better
retrieval quality.
"""
from __future__ import annotations

import abc
import hashlib
import math
import re
from typing import Optional


class EmbeddingProvider(abc.ABC):
    """Interface for turning text into a fixed-length vector."""

    dim: int = 0

    @abc.abstractmethod
    def embed(self, text: str) -> list[float]:
        ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class HashingEmbedder(EmbeddingProvider):
    """Zero-dependency lexical embedder (hashed bag-of-words + TF + L2 norm).

    Captures keyword/overlap similarity. Not semantic, but needs no model and
    is a sane default for demos, tests, and keyword-rich agent memories.
    """

    def __init__(self, dim: int = 512):
        self.dim = dim
        self._token_re = re.compile(r"\w+", re.UNICODE)

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        tokens = self._token_re.findall(text.lower())
        if not tokens:
            return vec
        counts: dict[int, int] = {}
        for tok in tokens:
            h = int.from_bytes(hashlib.md5(tok.encode("utf-8")).digest()[:4], "big") % self.dim
            counts[h] = counts.get(h, 0) + 1
        for h, c in counts.items():
            vec[h] = 1.0 + math.log(c)  # sublinear TF
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec


class OpenAIEmbedder(EmbeddingProvider):
    """OpenAI / OpenAI-compatible embeddings API."""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        from openai import OpenAI  # lazy import; optional dependency

        self.model = model
        self.dim = 1536 if "3-small" in model else 3072
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def embed(self, text: str) -> list[float]:
        resp = self._client.embeddings.create(model=self.model, input=text)
        return resp.data[0].embedding


class LocalHFEmbedder(EmbeddingProvider):
    """Local sentence-transformers model (runs on CPU/GPU, no network at call time)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer  # lazy import

        self._model = SentenceTransformer(model_name)
        self.dim = self._model.get_sentence_embedding_dimension()

    def embed(self, text: str) -> list[float]:
        return self._model.encode(text, normalize_embeddings=True).tolist()
