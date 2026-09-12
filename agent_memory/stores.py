"""Pluggable vector stores.

:class:`SQLiteVectorStore` is the zero-dependency default: it stores vectors as
JSON in SQLite and ranks by exact cosine similarity. For production-scale ANN
you can inject :class:`ChromaStore` (or any class implementing
:class:`VectorStore`).
"""
from __future__ import annotations

import abc
import json
import math
import sqlite3
import time
from typing import Optional

from .core import MemoryEntry


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity, pure Python (no numpy required)."""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class VectorStore(abc.ABC):
    """Interface for persisting and querying :class:`MemoryEntry` vectors."""

    @abc.abstractmethod
    def add(self, entry: MemoryEntry) -> None:
        ...

    @abc.abstractmethod
    def get(self, id: str) -> Optional[MemoryEntry]:
        ...

    @abc.abstractmethod
    def delete(self, id: str) -> bool:
        ...

    @abc.abstractmethod
    def all(self) -> list[MemoryEntry]:
        ...

    @abc.abstractmethod
    def query(
        self, vector: list[float], top_k: int = 5, filters: Optional[dict] = None
    ) -> list[tuple[MemoryEntry, float]]:
        ...


class SQLiteVectorStore(VectorStore):
    """Default store: SQLite + JSON vectors + exact cosine ranking."""

    def __init__(self, path: str = ":memory:"):
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS memories(
                id TEXT PRIMARY KEY,
                text TEXT,
                vector TEXT,
                metadata TEXT,
                created_at REAL,
                last_accessed REAL,
                access_count INTEGER,
                summary_of TEXT
            )"""
        )
        self._conn.commit()

    def _row_to_entry(self, row) -> MemoryEntry:
        (id, text, vector, metadata, created_at, last_accessed, access_count, summary_of) = row
        return MemoryEntry(
            id=id,
            text=text,
            vector=json.loads(vector),
            metadata=json.loads(metadata),
            created_at=created_at,
            last_accessed=last_accessed,
            access_count=access_count,
            summary_of=json.loads(summary_of),
        )

    def add(self, entry: MemoryEntry) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO memories VALUES (?,?,?,?,?,?,?,?)",
            (
                entry.id,
                entry.text,
                json.dumps(entry.vector),
                json.dumps(entry.metadata),
                entry.created_at,
                entry.last_accessed,
                entry.access_count,
                json.dumps(entry.summary_of),
            ),
        )
        self._conn.commit()

    def get(self, id: str) -> Optional[MemoryEntry]:
        cur = self._conn.execute("SELECT * FROM memories WHERE id=?", (id,))
        row = cur.fetchone()
        return self._row_to_entry(row) if row else None

    def delete(self, id: str) -> bool:
        cur = self._conn.execute("DELETE FROM memories WHERE id=?", (id,))
        self._conn.commit()
        return cur.rowcount > 0

    def all(self) -> list[MemoryEntry]:
        return [self._row_to_entry(r) for r in self._conn.execute("SELECT * FROM memories").fetchall()]

    def query(self, vector: list[float], top_k: int = 5, filters: Optional[dict] = None):
        results = []
        for e in self.all():
            if filters and not all(e.metadata.get(k) == v for k, v in filters.items()):
                continue
            results.append((e, cosine(vector, e.vector or [])))
        results.sort(key=lambda x: x[1], reverse=True)
        for e, _ in results[:top_k]:  # bump access stats on returned memories
            e.access_count += 1
            e.last_accessed = time.time()
            self.add(e)
        return results[:top_k]


class ChromaStore(VectorStore):
    """Drop-in adapter for ``chromadb`` (ANN indexing, persistent)."""

    def __init__(self, path: str = "./chroma_db", collection: str = "agent_memory"):
        import chromadb  # lazy import; optional dependency

        self._client = chromadb.PersistentClient(path=path)
        self._col = self._client.get_or_create_collection(collection)
        self._path = path

    def add(self, entry: MemoryEntry) -> None:
        self._col.upsert(
            ids=[entry.id],
            documents=[entry.text],
            embeddings=[entry.vector] if entry.vector else None,
            metadatas=[entry.metadata],
        )

    def get(self, id: str) -> Optional[MemoryEntry]:
        r = self._col.get(ids=[id], include=["documents", "embeddings", "metadatas"])
        if not r["ids"]:
            return None
        return MemoryEntry(
            id=r["ids"][0],
            text=r["documents"][0],
            vector=(r["embeddings"][0] if r.get("embeddings") else None),
            metadata=r["metadatas"][0] or {},
        )

    def delete(self, id: str) -> bool:
        before = self._col.count()
        self._col.delete(ids=[id])
        return self._col.count() < before

    def all(self) -> list[MemoryEntry]:
        r = self._col.get(include=["documents", "embeddings", "metadatas"])
        out = []
        for i, doc, emb, meta in zip(
            r["ids"], r["documents"], r.get("embeddings") or [None] * len(r["ids"]), r["metadatas"]
        ):
            out.append(MemoryEntry(id=i, text=doc, vector=emb, metadata=meta or {}))
        return out

    def query(self, vector: list[float], top_k: int = 5, filters: Optional[dict] = None):
        r = self._col.query(
            query_embeddings=[vector],
            n_results=top_k,
            where=filters,
            include=["documents", "embeddings", "metadatas", "distances"],
        )
        out = []
        for id, doc, emb, meta, dist in zip(
            r["ids"][0],
            r["documents"][0],
            r["embeddings"][0],
            r["metadatas"][0],
            r["distances"][0],
        ):
            out.append(
                (
                    MemoryEntry(id=id, text=doc, vector=emb, metadata=meta or {}),
                    1.0 - float(dist),  # chroma returns distance; convert to similarity
                )
            )
        return out
