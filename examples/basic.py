"""Basic usage demo for agent-memory (zero dependencies, runs offline)."""
from agent_memory import MemoryLayer


def main() -> None:
    mem = MemoryLayer(db_path=":memory:")  # default: hashed embed + sqlite + extractive summary

    mem.remember("User prefers concise replies in Chinese", metadata={"topic": "style"})
    mem.remember("Project uses FastAPI + SQLite", metadata={"topic": "stack"})
    mem.remember("User is based in Shanghai", metadata={"topic": "profile"})
    mem.remember("Likes Rust for CLI tools", metadata={"topic": "stack"})

    print("== recall: reply style ==")
    for h in mem.recall("what reply style does the user like?", top_k=2):
        print(f"  {h.text}  {h.metadata}")

    print("== recall filtered by topic=stack ==")
    for h in mem.recall("tooling preferences", top_k=5, metadata_filter={"topic": "stack"}):
        print(f"  {h.text}")

    print("== consolidate (force by lowering threshold) ==")
    # seed many low-access memories to trigger consolidation
    for i in range(60):
        mem.remember(f"ephemeral note number {i}", metadata={"topic": "tmp"})
    sid = mem.consolidate(max_entries=50, keep_recent=10)
    print(f"  summary id: {sid}")
    summary = mem.get(sid) if sid else None
    print(f"  summary text: {summary.text if summary else '(none)'}")


if __name__ == "__main__":
    main()
