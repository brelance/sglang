from __future__ import annotations

import json
import os
import threading
import time
from typing import Any, Dict, List, Optional


class RadixMoELogger:
    """Lightweight JSONL logger for Radix path and MoE expert selections."""

    def __init__(self):
        log_dir = os.getenv("SGLANG_RADIX_MOE_LOG_DIR")
        if not log_dir:
            self.enabled = False
            self.log_dir = ""
            return

        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.radix_path_file = os.path.join(self.log_dir, "radix_paths.jsonl")
        self.moe_log_file = os.path.join(self.log_dir, "moe_selections.jsonl")
        self._radix_lock = threading.Lock()
        self._moe_lock = threading.Lock()
        self.enabled = True

    def is_enabled(self) -> bool:
        return self.enabled

    def _append(self, path: str, payload: Dict[str, Any], lock: threading.Lock):
        payload = dict(payload)
        payload.setdefault("timestamp", time.time())
        with lock:
            with open(path, "a", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
                f.write("\n")

    def log_radix_path(
        self,
        req_id: str,
        matched_path: List[int],
        match_len: int,
        match_depth: int,
        extra: Optional[Dict[str, Any]] = None,
    ):
        if not self.enabled:
            return
        payload: Dict[str, Any] = {
            "req_id": req_id,
            "matched_path": matched_path,
            "match_len": match_len,
            "match_depth": match_depth,
        }
        if extra:
            payload.update(extra)
        self._append(self.radix_path_file, payload, self._radix_lock)

    def log_moe_selection(self, record: Dict[str, Any]):
        if not self.enabled:
            return
        self._append(self.moe_log_file, record, self._moe_lock)


_LOGGER: Optional[RadixMoELogger] = None
_LOCK = threading.Lock()


def get_radix_moe_logger() -> RadixMoELogger:
    global _LOGGER
    if _LOGGER is None:
        with _LOCK:
            if _LOGGER is None:
                _LOGGER = RadixMoELogger()
    return _LOGGER
