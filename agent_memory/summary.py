"""Pluggable memory summarizers used by :meth:`MemoryLayer.consolidate`."""
from __future__ import annotations

import abc
import re
from collections import Counter
from typing import Optional

from .core import MemoryEntry


class Summarizer(abc.ABC):
    """Interface for compressing a list of memories into one text."""

    @abc.abstractmethod
    def summarize(self, entries: list[MemoryEntry], max_words: int = 80) -> str:
        ...


class ExtractiveSummarizer(Summarizer):
    """Zero-dependency extractive summary: keep the highest-frequency sentences.

    No LLM required — good default for offline consolidation.
    """

    _SPLIT_RE = re.compile(r"[。.!?！？\n]")
    _WORD_RE = re.compile(r"\w+", re.UNICODE)

    def summarize(self, entries: list[MemoryEntry], max_words: int = 80) -> str:
        text = " ".join(e.text for e in entries)
        sentences = [s.strip() for s in self._SPLIT_RE.split(text) if s.strip()]
        if not sentences:
            return ""
        freq = Counter(w for w in self._WORD_RE.findall(text.lower()))
        ranked = sorted(
            sentences,
            key=lambda s: sum(freq.get(w, 0) for w in self._WORD_RE.findall(s.lower())),
            reverse=True,
        )
        out, used = [], 0
        for s in ranked:
            cost = len(s.split())
            if used + cost > max_words and out:
                break
            out.append(s)
            used += cost
        return " ".join(out) if out else sentences[0]


class LLMSummarizer(Summarizer):
    """Semantic summary via an OpenAI / OpenAI-compatible chat model."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        language: str = "Chinese",
    ):
        from openai import OpenAI  # lazy import; optional dependency

        self.model = model
        self.language = language
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def summarize(self, entries: list[MemoryEntry], max_words: int = 80) -> str:
        joined = "\n".join(f"- {e.text}" for e in entries)
        prompt = (
            f"将以下记忆压缩为不超过 {max_words} 字的中文摘要,保留关键事实与用户偏好,去除重复:"
            f"\n{joined}"
        )
        resp = self._client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
