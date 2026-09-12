# agent-memory-layer

本地 AI Agent 记忆工具。零依赖、零配置、开箱即用。

## 5 分钟上手

```bash
pip install agent-memory
agent-memory add "用户偏好中文" --meta topic:style
agent-memory recall "语言偏好"
```

## 核心功能

- **写入记忆**: `agent-memory add "文本" --meta topic:xxx`
- **检索记忆**: `agent-memory recall "关键词"`
- **压缩记忆**: `agent-memory consolidate`

## Python SDK

```python
from agent_memory import MemoryLayer
mem = MemoryLayer()
mem.remember("用户偏好中文")
hits = mem.recall("语言")
```

## 特性

| 特性 | 说明 |
|---|---|
| 零配置 | 无需 API Key，无需模型 |
| 离线运行 | 数据留在本机 |
| 自动压缩 | 旧记忆自动合并 |

## 安装

```bash
pip install -e .                    # 零依赖
pip install -e ".[hf]"              # + 语义向量
pip install -e ".[openai]"          # + OpenAI
pip install -e ".[chroma]"          # + ANN存储
```

## 完整文档

[README.md](./README.md) · [CHANGELOG.md](./CHANGELOG.md) · [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

MIT
