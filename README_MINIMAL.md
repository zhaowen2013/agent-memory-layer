# agent-memory-layer

Local-first, pluggable memory layer for AI agents. Zero dependencies by default.

**Features:**
- Plug-and-play: swap embeddings, vector stores, and summarizers
- Zero-cloud: runs entirely offline with hashed vectors + SQLite
- Auto-compression: `consolidate()` keeps memory bounded
- CLI + Python SDK

## Quick Start

```python
from agent_memory import MemoryLayer

mem = MemoryLayer(db_path="memory.db")
mem.remember("User prefers concise replies", metadata={"topic": "style"})
hits = mem.recall("reply style", top_k=3)
```

Or CLI:

```bash
agent-memory add "User prefers concise replies" --meta topic:style
agent-memory recall "reply style"
```

## Install

```bash
pip install -e .                    # zero deps
pip install -e ".[hf]"              # + semantic embeddings
pip install -e ".[openai]"          # + OpenAI API
pip install -e ".[chroma]"          # + ANN vector DB
```

## Architecture

```
MemoryLayer
    ├── EmbeddingProvider (Hashing / LocalHF / OpenAI)
    ├── VectorStore       (SQLite / Chroma)
    └── Summarizer        (Extractive / LLM)
```

Each layer is fully pluggable. See README.md for full docs.

## License

MIT
