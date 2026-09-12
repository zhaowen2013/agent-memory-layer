# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of agent-memory-layer
- Pluggable `EmbeddingProvider` interface with three implementations:
  - `HashingEmbedder`: pure-Python word-hash TF vectors (zero deps)
  - `LocalHFEmbedder`: local sentence-transformers models
  - `OpenAIEmbedder`: OpenAI-compatible API embeddings
- Pluggable `VectorStore` interface with two implementations:
  - `SQLiteVectorStore`: cosine similarity over SQLite (default)
  - `ChromaStore`: persistent ANN via chromadb
- Pluggable `Summarizer` interface with two implementations:
  - `ExtractiveSummarizer`: keyword-weighted sentence selection (no LLM)
  - `LLMSummarizer`: semantic summary via OpenAI-compatible chat model
- `MemoryLayer` facade with `remember()`, `recall()`, `forget()`, `consolidate()`
- CLI tool `agent-memory` with subcommands: `add`, `recall`, `list`, `consolidate`, `forget`
- `metadata_filter` support in recall for precise retrieval
- `access_count` and `last_accessed` tracking for consolidation decisions
- GitHub Actions CI testing on Python 3.9–3.12
- MIT license

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

## [0.1.0] — 2026-09-12
- Initial public release

[Unreleased]: https://github.com/zhaowen2013/agent-memory-layer/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/zhaowen2013/agent-memory-layer/releases/tag/v0.1.0
