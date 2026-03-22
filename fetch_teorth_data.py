#!/usr/bin/env python3
"""
fetch_teorth_data.py — Download and cache Teorth/equational_theories external assets.

Assets fetched from https://github.com/teorth/equational_theories :
  - equations.txt       : canonical equation list (one per line, 0-indexed IDs)
  - duals.json          : dual equation pairs {id_str: dual_id_str}
  - smallest_magma.txt  : smallest-magma representatives per equation

Cache location: data/teorth_cache/

Usage:
    python fetch_teorth_data.py              # download missing, skip cached
    python fetch_teorth_data.py --force      # re-download all
    python fetch_teorth_data.py --check      # only verify what's cached
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests

TEORTH_RAW = (
    "https://raw.githubusercontent.com/teorth/equational_theories/main"
)

# Candidate URL paths — the repo layout may vary; first match wins per asset.
# Each entry is a list of fallback paths tried in order.
ASSET_FALLBACKS: dict[str, list[str]] = {
    "equations.txt": [
        f"{TEORTH_RAW}/equational_theories/data/equations.txt",
        f"{TEORTH_RAW}/equations.txt",
    ],
    "duals.json": [
        f"{TEORTH_RAW}/equational_theories/data/duals.json",
        f"{TEORTH_RAW}/duals.json",
    ],
    "smallest_magma.txt": [
        f"{TEORTH_RAW}/equational_theories/data/smallest_magma.txt",
        f"{TEORTH_RAW}/smallest_magma.txt",
    ],
}

CACHE_DIR = Path(__file__).resolve().parent / "data" / "teorth_cache"
TIMEOUT_S = 30


def fetch_asset(name: str, force: bool = False) -> Path:
    """Download one asset, trying candidate URLs in order.  Returns cache path."""
    cache_path = CACHE_DIR / name
    if cache_path.exists() and not force:
        print(f"  cached  : {cache_path.name} ({cache_path.stat().st_size:,} bytes)")
        return cache_path

    urls = ASSET_FALLBACKS.get(name, [])
    last_exc: Exception = RuntimeError(f"No URLs configured for {name}")
    for url in urls:
        try:
            print(f"  fetching: {url}")
            resp = requests.get(url, timeout=TIMEOUT_S)
            resp.raise_for_status()
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(resp.content)
            print(f"  saved   : {cache_path.name} ({cache_path.stat().st_size:,} bytes)")
            return cache_path
        except Exception as exc:  # noqa: BLE001
            print(f"  WARN    : {url} — {exc}")
            last_exc = exc

    raise RuntimeError(f"Failed to fetch {name}: {last_exc}") from last_exc


def fetch_all(force: bool = False) -> dict[str, Path | None]:
    """Fetch all configured assets.  Returns {name: Path | None}."""
    print(f"Teorth cache dir: {CACHE_DIR}")
    results: dict[str, Path | None] = {}
    for name in ASSET_FALLBACKS:
        try:
            results[name] = fetch_asset(name, force=force)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR   : could not fetch {name}: {exc}")
            results[name] = None
    return results


# ---------------------------------------------------------------------------
# Convenience loaders (used by distill.py and other modules)
# ---------------------------------------------------------------------------

def load_equations(cache_dir: Path | None = None) -> dict[int, str]:
    """
    Load equations.txt and return {equation_id (0-based): equation_text} dict.
    Equations use the Teorth notation (◇ operator); convert as needed downstream.
    """
    path = (cache_dir or CACHE_DIR) / "equations.txt"
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    return {i: line.strip() for i, line in enumerate(lines) if line.strip()}


def load_duals(cache_dir: Path | None = None) -> dict[str, str]:
    """Load duals.json → {eq_id_str: dual_eq_id_str}."""
    path = (cache_dir or CACHE_DIR) / "duals.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_smallest_magma(cache_dir: Path | None = None) -> dict[str, str]:
    """
    Load smallest_magma.txt.  Format varies by repo version; returns raw lines
    as {line_index_str: line_text} for downstream parsing.
    """
    path = (cache_dir or CACHE_DIR) / "smallest_magma.txt"
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    return {str(i): line.strip() for i, line in enumerate(lines) if line.strip()}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and cache Teorth equational_theories external assets."
    )
    parser.add_argument("--force", action="store_true", help="Re-download even if cached")
    parser.add_argument(
        "--check", action="store_true",
        help="Only report which files are cached; do not download"
    )
    args = parser.parse_args()

    if args.check:
        print(f"Cache dir: {CACHE_DIR}")
        for name in ASSET_FALLBACKS:
            path = CACHE_DIR / name
            status = f"OK  ({path.stat().st_size:,} bytes)" if path.exists() else "MISSING"
            print(f"  [{status}] {name}")
        return

    results = fetch_all(force=args.force)

    # Sanity-check: count equations
    eqs = load_equations()
    if eqs:
        print(f"  equations loaded: {len(eqs):,} entries (IDs 0–{max(eqs):,})")

    failed = [n for n, p in results.items() if p is None]
    if failed:
        print(f"\nWARNING: {len(failed)} asset(s) could not be downloaded: {failed}")
        print("URLs in ASSET_FALLBACKS may need updating for the current repo layout.")


if __name__ == "__main__":
    main()
