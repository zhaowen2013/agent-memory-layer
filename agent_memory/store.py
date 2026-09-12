"""High-level memory layer that wires embeddings, storage, and summarization."""
from __future__ import annotations

from typing import Optional

from .core import MemoryEntry, new_id
from .embeddings import EmbeddingProvider, HashingEmbedder
from .stores import VectorStore, SQLiteVectorStore
from .summary import Summarizer, ExtractiveSummarizer


class MemoryLayer:
    """Pluggable local memory for agents.

    Defaults are fully offline (hashed embeddings + SQLite + extractive
    summarizer). Inject any component to upgrade capability.
    """

    def __init__(
        self,
        embedder: Optional[EmbeddingProvider] = None,
        store: Optional[VectorStore] = None,
        summarizer: Optional[Summarizer] = None,
        db_path: str = ":memory:",
    ):
        self.embedder = embedder or HashingEmbedder()
        self.store = store or SQLiteVectorStore(db_path)
        self.summarizer = summarizer or ExtractiveSummarizer()

    # ----- write -----
    def remember(self, text: str, metadata: Optional[dict] = None, id: Optional[str] = None) -> str:
        """Store a memory. Returns its id."""
        mid = id or new_id()
        entry = MemoryEntry(
            id=mid,
            text=text,
            vector=self.embedder.embed(text),
            metadata=metadata or {},
        )
        self.store.add(entry)
        return mid

    # ----- read -----
    def recall(self, query: str, top_k: int = 5, metadata_filter: Optional[dict] = None) -> list[MemoryEntry]:
        """Return the top_k most similar memories to ``query``."""
        vec = self.embedder.embed(query)
        return [e for e, _ in self.store.query(vec, top_k=top_k, filters=metadata_filter)]

    def get(self, id: str) -> Optional[MemoryEntry]:
        return self.store.get(id)

    def all(self) -> list[MemoryEntry]:
        return self.store.all()

    # ----- delete -----
    def forget(self, id: str) -> bool:
        return self.store.delete(id)

    # ----- compaction -----
    def consolidate(
        self,
        max_entries: int = 50,
        keep_recent: int = 10,
        max_words: int = 80,
    ) -> Optional[str]:
        """Compress the least-accessed old memories into one summary entry.

        Returns the new summary memory id, or ``None`` if below ``max_entries``.
        """
        entries = self.store.all()
        if len(entries) < max_entries:
            return None
        entries.sort(key=lambda e: (e.access_count, e.last_accessed))
        candidates = entries[:-keep_recent]
        to_compress = candidates[: max(1, len(candidates) // 2)]
        if not to_compress:
            return None
        summary_text = self.summarizer.summarize(to_compress, max_words=max_words)
        summary_id = new_id()
        summary_entry = MemoryEntry(
            id=summary_id,
            text=summary_text,
            vector=self.embedder.embed(summary_text),
            metadata={"type": "summary"},
            summary_of=[e.id for e in to_compress],
        )
        self.store.add(summary_entry)
        for e in to_compress:
            self.store.delete(e.id)
        return summary_id
