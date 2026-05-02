"""Scope file loading."""

from __future__ import annotations

from pathlib import Path

from .urltools import normalize_start_url


def load_scope_file(path: Path) -> list[str]:
    targets: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        targets.append(normalize_start_url(line))
    return targets
