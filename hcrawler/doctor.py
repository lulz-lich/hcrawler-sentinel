"""Environment diagnostics."""

from __future__ import annotations

import importlib.util
import platform
import sys


def run_doctor() -> tuple[bool, list[str]]:
    checks: list[str] = []
    ok = True

    checks.append(f"Python: {sys.version.split()[0]}")
    checks.append(f"Platform: {platform.system()} {platform.release()}")

    for module in ["requests", "bs4", "colorama", "yaml"]:
        found = importlib.util.find_spec(module) is not None
        checks.append(f"{module}: {'OK' if found else 'MISSING'}")
        if not found:
            ok = False

    aiohttp_found = importlib.util.find_spec("aiohttp") is not None
    checks.append(f"aiohttp optional async engine: {'OK' if aiohttp_found else 'not installed'}")

    return ok, checks
