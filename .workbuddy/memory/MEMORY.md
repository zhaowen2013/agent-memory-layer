# Project Memory: agent-memory-layer

## 项目概述
可插拔本地 Agent 记忆层。默认零依赖(哈希向量+SQLite+抽取式摘要),离线可跑;三层均可替换(embedder/vector store/summarizer)。提供 CLI 和 Python SDK。

## 技术栈
- Python 3.8+ 兼容
- 零依赖默认,可选:chromadb/sentence-transformers/openai
- MIT License

## 关键设计
- `MemoryLayer.remember(text, metadata)` → id
- `MemoryLayer.recall(query, top_k, metadata_filter)` → list of (entry, score)
- `MemoryLayer.consolidate()` → 把低频旧记忆压成 summary 条目,控制工作集大小
- 默认 EmbeddingProvider: `HashingEmbedder`(词哈希 TF,无模型)
- 默认 VectorStore: `SQLiteVectorStore`(余弦,JSON 存库)
- 默认 Summarizer: `ExtractiveSummarizer`(无 LLM)

## 冒烟测试状态
- 零依赖路径:✅ 通过
- CLI add/recall/list:✅ 通过

## 待扩展
- time-decay 召回权重
- HTTP server 模式(多 agent 共享)
- faiss/lance 适配器
- async/batch embedding
