"""Smoke tests for agent-memory core (no network, no heavy deps)."""
import pytest

from agent_memory import (
    MemoryLayer,
    MemoryEntry,
    HashingEmbedder,
    SQLiteVectorStore,
    ExtractiveSummarizer,
    cosine,
)


def test_cosine_identical():
    v = [1.0, 0.0, 0.0]
    assert abs(cosine(v, v) - 1.0) < 1e-9


def test_cosine_orthogonal():
    assert cosine([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_remember_and_recall():
    mem = MemoryLayer(db_path=":memory:")
    mem.remember("User likes Python for scripting", metadata={"topic": "lang"})
    mem.remember("User likes Rust for performance", metadata={"topic": "lang"})
    hits = mem.recall("which language for scripting", top_k=1)
    assert hits and "Python" in hits[0].text


def test_metadata_filter():
    mem = MemoryLayer(db_path=":memory:")
    mem.remember("a", metadata={"k": "x"})
    mem.remember("b", metadata={"k": "y"})
    hits = mem.recall("a", top_k=5, metadata_filter={"k": "x"})
    assert len(hits) == 1 and hits[0].text == "a"


def test_forget():
    mem = MemoryLayer(db_path=":memory:")
    mid = mem.remember("temp")
    assert mem.forget(mid) is True
    assert mem.get(mid) is None


def test_consolidate_creates_summary():
    mem = MemoryLayer(db_path=":memory:")
    for i in range(60):
        mem.remember(f"note {i}", metadata={"topic": "tmp"})
    sid = mem.consolidate(max_entries=50, keep_recent=10)
    assert sid is not None
    summary = mem.get(sid)
    assert summary is not None
    assert summary.metadata.get("type") == "summary"
    # compressed entries should be gone
    assert len(mem.all()) < 60


def test_store_persists(tmp_path):
    db = str(tmp_path / "m.db")
    m1 = MemoryLayer(db_path=db)
    m1.remember("persisted memory")
    m2 = MemoryLayer(db_path=db)  # reopen
    assert any("persisted memory" in e.text for e in m2.all())


def test_extractive_summary_runs():
    s = ExtractiveSummarizer()
    out = s.summarize([MemoryEntry(id="1", text="agent needs memory. memory must persist. agent runs offline.")])
    assert out
