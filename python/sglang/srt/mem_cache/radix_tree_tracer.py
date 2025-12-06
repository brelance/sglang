from __future__ import annotations

import json
import os
import threading
from typing import Any, Dict

DEFAULT_TRACE_PATH = "tree_node_trace.json"


class RadixTreeTracer:
    """Simple JSONL tracer for radix tree snapshots."""

    def __init__(self, path: str = DEFAULT_TRACE_PATH):
        self.path = path
        self._lock = threading.Lock()

    def dump(self, snapshot: Dict[str, Any], path: str | None = None) -> str:
        """Append a snapshot (dict) to the trace file and return the path used."""
        file_path = path or self.path
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        with self._lock:
            with open(file_path, "a", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=True)
                f.write("\n")
        return file_path
