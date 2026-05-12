#!/usr/bin/env python3
"""Fetch official SAIR problem sets into root-level data caches.

This keeps two local mirrors:
1. Hugging Face selected-problem subsets under ``data/hf_cache/``
2. Vendored Stage 2 official public problem files under
   ``data/stage2_official_problems/``
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
HF_DATASET = "SAIRfoundation/equational-theories-selected-problems"
HF_BASE_URL = f"https://huggingface.co/datasets/{HF_DATASET}/resolve/main"
HF_SUBSETS = (
    "normal",
    "hard",
    "hard1",
    "hard2",
    "hard3",
    "evaluation_normal",
    "evaluation_hard",
    "evaluation_extra_hard",
    "evaluation_order5",
)
HF_CACHE_DIR = REPO_ROOT / "data" / "hf_cache"
HF_METADATA_DIR = HF_CACHE_DIR / "metadata"
HF_MANIFEST = HF_CACHE_DIR / "manifest.json"

OFFICIAL_STAGE2_SOURCE = REPO_ROOT / "vendor" / "stage2-official" / "examples" / "problems"
OFFICIAL_STAGE2_MIRROR = REPO_ROOT / "data" / "stage2_official_problems"
OFFICIAL_STAGE2_MANIFEST = OFFICIAL_STAGE2_MIRROR / "manifest.json"

TIMEOUT_S = 60


def download_file(url: str, target: Path, force: bool = False) -> dict:
    if target.exists() and not force:
        return {
            "path": str(target.relative_to(REPO_ROOT)).replace("\\", "/"),
            "bytes": target.stat().st_size,
            "status": "cached",
            "url": url,
        }

    response = requests.get(url, timeout=TIMEOUT_S)
    response.raise_for_status()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(response.content)
    return {
        "path": str(target.relative_to(REPO_ROOT)).replace("\\", "/"),
        "bytes": len(response.content),
        "status": "downloaded",
        "url": url,
    }


def fetch_hf_subsets(force: bool = False) -> dict:
    files: list[dict] = []
    for subset in HF_SUBSETS:
        data_url = f"{HF_BASE_URL}/data/{subset}.jsonl"
        meta_url = f"{HF_BASE_URL}/metadata/{subset}.json"
        files.append(download_file(data_url, HF_CACHE_DIR / f"{subset}.jsonl", force=force))
        files.append(download_file(meta_url, HF_METADATA_DIR / f"{subset}.json", force=force))

    readme = download_file(
        f"{HF_BASE_URL}/README.md",
        HF_CACHE_DIR / "README.upstream.md",
        force=force,
    )
    files.append(readme)

    manifest = {
        "fetched_at": datetime.now(UTC).isoformat(),
        "source_dataset": HF_DATASET,
        "subsets": list(HF_SUBSETS),
        "files": files,
    }
    HF_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def mirror_official_stage2(force: bool = False) -> dict:
    files: list[dict] = []
    if not OFFICIAL_STAGE2_SOURCE.exists():
        raise FileNotFoundError(f"Missing vendored official problem directory: {OFFICIAL_STAGE2_SOURCE}")

    for source in sorted(path for path in OFFICIAL_STAGE2_SOURCE.rglob("*") if path.is_file()):
        rel = source.relative_to(OFFICIAL_STAGE2_SOURCE)
        target = OFFICIAL_STAGE2_MIRROR / rel
        if force or not target.exists() or source.read_bytes() != target.read_bytes():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            status = "copied"
        else:
            status = "unchanged"
        files.append(
            {
                "path": str(target.relative_to(REPO_ROOT)).replace("\\", "/"),
                "bytes": target.stat().st_size,
                "status": status,
                "source": str(source.relative_to(REPO_ROOT)).replace("\\", "/"),
            }
        )

    manifest = {
        "mirrored_at": datetime.now(UTC).isoformat(),
        "source": str(OFFICIAL_STAGE2_SOURCE.relative_to(REPO_ROOT)).replace("\\", "/"),
        "files": files,
    }
    OFFICIAL_STAGE2_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    OFFICIAL_STAGE2_MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch SAIR Hugging Face subsets and mirror official Stage 2 problem files.")
    parser.add_argument("--force", action="store_true", help="Re-download and re-copy even when files already exist.")
    parser.add_argument("--skip-hf", action="store_true", help="Skip Hugging Face subset downloads.")
    parser.add_argument("--skip-stage2-mirror", action="store_true", help="Skip mirroring vendored Stage 2 official problem files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.skip_hf:
        hf_manifest = fetch_hf_subsets(force=args.force)
        print(f"Hugging Face subsets cached: {len(hf_manifest['subsets'])}")
        print(f"Manifest: {HF_MANIFEST.relative_to(REPO_ROOT)}")
    if not args.skip_stage2_mirror:
        stage2_manifest = mirror_official_stage2(force=args.force)
        print(f"Official Stage 2 files mirrored: {len(stage2_manifest['files'])}")
        print(f"Manifest: {OFFICIAL_STAGE2_MANIFEST.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
