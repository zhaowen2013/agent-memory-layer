"""Command-line interface for agent-memory."""
from __future__ import annotations

import argparse
import json
import sys

from . import MemoryLayer
from .stores import SQLiteVectorStore


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="agent-memory", description="Local pluggable memory for AI agents.")
    p.add_argument("--db", default="memory.db", help="SQLite DB path (default: memory.db)")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="store a memory")
    a.add_argument("text", help="memory text")
    a.add_argument("--meta", nargs="*", default=[], help="key:value metadata pairs")

    r = sub.add_parser("recall", help="retrieve similar memories")
    r.add_argument("query", help="query text")
    r.add_argument("--top-k", type=int, default=5)
    r.add_argument("--meta", nargs="*", default=[], help="filter by key:value")

    sub.add_parser("list", help="list all memories")
    sub.add_parser("consolidate", help="compress old memories into a summary")

    f = sub.add_parser("forget", help="delete a memory by id")
    f.add_argument("id")

    return p


def _parse_meta(pairs) -> dict:
    meta = {}
    for kv in pairs:
        if ":" not in kv:
            print(f"ignore malformed meta (need key:value): {kv}", file=sys.stderr)
            continue
        k, v = kv.split(":", 1)
        meta[k] = v
    return meta


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    mem = MemoryLayer(store=SQLiteVectorStore(args.db))

    if args.cmd == "add":
        mid = mem.remember(args.text, metadata=_parse_meta(args.meta))
        print(mid)
    elif args.cmd == "recall":
        for e in mem.recall(args.query, top_k=args.top_k, metadata_filter=_parse_meta(args.meta) or None):
            print(f"[{e.id}] {e.text}  {json.dumps(e.metadata, ensure_ascii=False)}")
    elif args.cmd == "list":
        for e in mem.all():
            print(f"[{e.id}] x{e.access_count} {e.text}  {json.dumps(e.metadata, ensure_ascii=False)}")
    elif args.cmd == "consolidate":
        sid = mem.consolidate()
        print("consolidated ->", sid if sid else "nothing to consolidate (below threshold)")
    elif args.cmd == "forget":
        print("deleted" if mem.forget(args.id) else "not found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
