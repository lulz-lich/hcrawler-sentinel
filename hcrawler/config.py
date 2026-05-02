"""Config loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def load_config_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("YAML config requires PyYAML. Install with: pip install pyyaml")
        return yaml.safe_load(text) or {}

    if suffix == ".json":
        return json.loads(text)

    raise ValueError("Unsupported config format. Use .json, .yaml, or .yml")
