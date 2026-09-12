# agent-memory-layer

**AI Agent 记忆的永久化工具。** 本地优先、零依赖开箱、完全可插拔——给 Agent 一个不需要云端、不会被清空的长期记忆。

```bash
pip install -e .
agent-memory add "用户偏好中文简洁回复"
agent-memory recall "怎么回应用户的风格偏好"
```

## 问题与定位

大部分 AI Agent 的"记忆"都依赖云端或会随 session 结束丢失。本工具把 **Agent 的记忆永久化到本地**,并且:

- **零云端依赖** — 数据留在本机,离线可跑
- **可插拔** — Embedder / 向量库 / 摘要器都可以替换(默认纯 Python 词哈希+SQLite,无需 GPU)
- **自动压缩** — `consolidate()` 把低频旧记忆压成摘要,控制工作集大小
- **CLI + SDK 双入口** — 既能当命令行工具用,也能嵌入自己的 Agent

## 安装

```bash
pip install -e .                      # 零依赖,离线可用
pip install -e ".[hf]"                # + 本地语义向量(sentence-transformers)
pip install -e ".[openai]"            # + OpenAI 向量化与摘要
pip install -e ".[chroma]"            # + 持久化 ANN 向量库
```

## 快速上手(CLI)

```bash
# 写入记忆
agent-memory add "用户偏好中文简洁回复" --meta topic:style
agent-memory add "项目用 FastAPI + SQLite" --meta topic:stack

# 检索(语义搜索)
agent-memory recall "怎么回应用户的风格偏好" --top-k 3

# 自动压缩旧记忆(防止工作集无限膨胀)
agent-memory consolidate

# 查看全部
agent-memory list
```

## 快速上手(Python SDK)

```python
from agent_memory import MemoryLayer

mem = MemoryLayer(db_path="memory.db")

mem.remember("用户偏好中文简洁回复", metadata={"topic": "style"})
mem.remember("项目用 FastAPI + SQLite", metadata={"topic": "stack"})

hits = mem.recall("怎么回应用户", top_k=3)
for h in hits:
    print(h.text, h.metadata)

mem.consolidate()  # 压缩低频旧记忆,保持工作集可控
```

## 架构(三层都可插拔)

```
MemoryLayer
    ├── EmbeddingProvider  (Hashing / LocalHF / OpenAI)
    ├── VectorStore        (SQLite / Chroma / faiss future)
    └── Summarizer         (Extractive / LLM)
```

每个组件都是接口,注入即可替换:

```python
from agent_memory import MemoryLayer
from agent_memory.stores import ChromaStore
from agent_memory.embeddings import LocalHFEmbedder

mem = MemoryLayer(embedder=LocalHFEmbedder(), store=ChromaStore("./db"))
```

## 核心特性

| 特性 | 说明 |
|---|---|
| 零依赖默认 | 纯 Python 哈希向量 + SQLite,无需模型/AI API |
| 长期记忆压缩 | `consolidate()` 自动把低频记忆压成摘要,防止工作集膨胀 |
| 元数据过滤 | recall 时按 metadata 字段过滤,精准召回 |
| 访问统计 | 每次 recall 自动递增 access_count,作为压缩决策依据 |
| 多粒度插件 | 三层全接口化,按需换底层实现 |

## 组件一览

| 接口 | 默认(零依赖) | 可替换 |
|---|---|---|
| `EmbeddingProvider` | `HashingEmbedder`(词哈希 TF) | `LocalHFEmbedder`, `OpenAIEmbedder` |
| `VectorStore` | `SQLiteVectorStore`(余弦) | `ChromaStore` |
| `Summarizer` | `ExtractiveSummarizer`(无 LLM) | `LLMSummarizer` |

## 路线

- [ ] 时间衰减召回权重(越旧越降权)
- [ ] 批量/异步 embedding
- [ ] faiss/lance 适配器
- [ ] HTTP server 模式(多 Agent 共享同一记忆库)
- [ ] JSONL 导出导入

## License

MIT
