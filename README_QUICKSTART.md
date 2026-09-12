# agent-memory-layer

本地 AI Agent 记忆工具。零依赖、零配置、开箱即用。

**5 分钟上手:**

```bash
pip install agent-memory
agent-memory add "用户偏好中文" --meta topic:style
agent-memory recall "语言偏好"
```

## 快速开始

### CLI(最简单)
```bash
# 写入记忆
agent-memory add "我喜欢简洁回复" --meta topic:style
agent-memory add "项目用 Python" --meta topic:stack

# 检索
agent-memory recall "回复风格"

# 查看
agent-memory list
```

### Python(嵌入你的 Agent)
```python
from agent_memory import MemoryLayer

mem = MemoryLayer()  # 零配置
mem.remember("用户偏好中文")
hits = mem.recall("语言偏好")
```

## 核心概念

| 概念 | 说明 |
|---|---|
| **记忆** | 一条文本 + 可选元数据 |
| **检索** | 语义搜索，自动排序 |
| **压缩** | 旧记忆自动合并成摘要 |

## 为什么用它?

- ✅ **零配置** — 无需 API Key，无需模型下载
- ✅ **完全离线** — 数据留在本机
- ✅ **自动管理** — `consolidate()` 防止记忆无限膨胀
- ✅ **可扩展** — 需要时换更好模型

## 进阶(可选)

```python
# 换成语义向量(需 pip install -e ".[hf]")
from agent_memory import LocalHFEmbedder, MemoryLayer
mem = MemoryLayer(embedder=LocalHFEmbedder())

# 换成持久化向量库(需 pip install -e ".[chroma]")
from agent_memory import ChromaStore
mem = MemoryLayer(store=ChromaStore("./db"))
```

## 完整文档

详见 [README.md](./README.md)
