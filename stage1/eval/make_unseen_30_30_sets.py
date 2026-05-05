#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

import sim_lab

ROOT = Path(__file__).resolve().parent
DEFAULT_OUT_DIR = ROOT / "data" / "benchmark"
DEFAULT_STATE_PATH = DEFAULT_OUT_DIR / "rotating_official_state.json"
DEFAULT_LATEST_PATH = DEFAULT_OUT_DIR / "rotating_official_latest.json"
LEGACY_UNSEEN_GLOB = "*_unseen_*.jsonl"
DEFAULT_SPECS = (
    {"subset": "normal", "n_true": 30, "n_false": 30},
    {"subset": "hard", "n_true": 20, "n_false": 20},
    {"subset": "hard2", "n_true": 10, "n_false": 10},
    {"subset": "hard3", "n_true": 10, "n_false": 10},
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def stable_seed(label: str) -> int:
    digest = hashlib.sha256(label.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def default_state() -> dict:
    return {"version": 1, "generation_count": 0, "subsets": {}}


def load_state(path: Path) -> dict:
    if not path.exists():
        return default_state()
    state = load_json(path)
    state.setdefault("version", 1)
    state.setdefault("generation_count", 0)
    state.setdefault("subsets", {})
    return state


def resolve_specs(args: argparse.Namespace) -> list[dict]:
    return [
        {"subset": "normal", "n_true": args.normal_true, "n_false": args.normal_false},
        {"subset": "hard", "n_true": args.hard_true, "n_false": args.hard_false},
        {"subset": "hard2", "n_true": args.hard2_true, "n_false": args.hard2_false},
        {"subset": "hard3", "n_true": args.hard3_true, "n_false": args.hard3_false},
    ]


def ensure_official_subset(subset: str, refresh_cache: bool) -> Path:
    cache_path = sim_lab.HF_CACHE_DIR / f"{subset}.jsonl"
    if refresh_cache and cache_path.exists():
        cache_path.unlink()
    return sim_lab.download_hf_subset(subset)


def subset_rows(subset: str, refresh_cache: bool) -> list[dict]:
    path = ensure_official_subset(subset, refresh_cache=refresh_cache)
    rows = load_jsonl(path)
    for row in rows:
        row.setdefault("difficulty", subset)
    return rows


def ordered_bucket(rows: list[dict], subset: str, answer_value: bool, cycle: int) -> list[dict]:
    bucket = [dict(row) for row in rows if bool(row["answer"]) is answer_value]
    bucket.sort(key=lambda row: row["id"])
    rng = random.Random(stable_seed(f"{subset}:{int(answer_value)}:cycle:{cycle}"))
    rng.shuffle(bucket)
    return bucket


def bucket_state(state: dict, subset: str, answer_value: bool) -> dict:
    subset_state = state["subsets"].setdefault(subset, {})
    key = "true" if answer_value else "false"
    return subset_state.setdefault(key, {"cycle": 0, "offset": 0})


def draw_from_bucket(rows: list[dict], subset: str, answer_value: bool, count: int, state: dict) -> tuple[list[dict], dict]:
    bucket = [row for row in rows if bool(row["answer"]) is answer_value]
    if len(bucket) < count:
        label = "TRUE" if answer_value else "FALSE"
        raise ValueError(f"Subset {subset} has only {len(bucket)} {label} rows; need {count}")

    current = bucket_state(state, subset, answer_value)
    wrapped = False
    while True:
        cycle = int(current["cycle"])
        offset = int(current["offset"])
        ordered = ordered_bucket(rows, subset, answer_value, cycle)
        if offset + count <= len(ordered):
            selected = ordered[offset:offset + count]
            current["offset"] = offset + count
            return selected, {
                "cycle": cycle,
                "offset_start": offset,
                "offset_end": current["offset"],
                "pool_size": len(ordered),
                "wrapped": wrapped,
            }
        current["cycle"] = cycle + 1
        current["offset"] = 0
        wrapped = True


def build_bundle_rows(rows: list[dict], subset: str, n_true: int, n_false: int, state: dict, rotation_index: int) -> tuple[list[dict], dict]:
    chosen_true, true_meta = draw_from_bucket(rows, subset, True, n_true, state)
    chosen_false, false_meta = draw_from_bucket(rows, subset, False, n_false, state)
    selected = chosen_true + chosen_false
    rng = random.Random(stable_seed(f"bundle:{subset}:rotation:{rotation_index}"))
    rng.shuffle(selected)
    materialized = []
    for row in selected:
        materialized.append({
            **row,
            "source_subset": subset,
            "rotation_index": rotation_index,
        })
    metadata = {
        "subset": subset,
        "requested": {"true": n_true, "false": n_false},
        "selected": {"true": n_true, "false": n_false, "total": len(materialized)},
        "true_bucket": true_meta,
        "false_bucket": false_meta,
        "ids": [row["id"] for row in materialized],
    }
    return materialized, metadata


def output_path(out_dir: Path, subset: str, n_true: int, n_false: int, rotation_index: int, stamp: str) -> Path:
    total = n_true + n_false
    return out_dir / (
        f"{subset}_balanced{total}_true{n_true}_false{n_false}_rotation{rotation_index:04d}_{stamp}.jsonl"
    )


def purge_legacy_unseen(out_dir: Path) -> list[str]:
    removed: list[str] = []
    for path in sorted(out_dir.glob(LEGACY_UNSEEN_GLOB)):
        path.unlink()
        removed.append(rel(path))
    return removed


def build_rotation_bundle(
    specs: list[dict],
    out_dir: Path,
    state_path: Path,
    latest_path: Path,
    stamp: str,
    refresh_cache: bool,
    purge_legacy: bool,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    state = load_state(state_path)
    rotation_index = int(state["generation_count"]) + 1
    removed_legacy = purge_legacy_unseen(out_dir) if purge_legacy else []

    payload = {
        "generated_at": iso_now(),
        "stamp": stamp,
        "rotation_index": rotation_index,
        "source": {
            "dataset": sim_lab.HF_DATASET,
            "subsets": [spec["subset"] for spec in specs],
            "refresh_cache": refresh_cache,
        },
        "legacy_unseen_removed": removed_legacy,
        "files": [],
    }

    for spec in specs:
        rows = subset_rows(spec["subset"], refresh_cache=refresh_cache)
        bundle_rows, metadata = build_bundle_rows(
            rows=rows,
            subset=spec["subset"],
            n_true=spec["n_true"],
            n_false=spec["n_false"],
            state=state,
            rotation_index=rotation_index,
        )
        path = output_path(out_dir, spec["subset"], spec["n_true"], spec["n_false"], rotation_index, stamp)
        write_jsonl(path, bundle_rows)
        payload["files"].append({
            **metadata,
            "path": rel(path),
        })

    state["generation_count"] = rotation_index
    state["last_generated_at"] = payload["generated_at"]
    state["latest_manifest"] = rel(latest_path)
    write_json(state_path, state)
    write_json(latest_path, payload)
    return payload


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate rotating official-like benchmark bundles from the SAIR Hugging Face subsets. "
            "Defaults: normal 30/30, hard 20/20, hard2 10/10, hard3 10/10."
        )
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--state-path", default=str(DEFAULT_STATE_PATH))
    parser.add_argument("--latest-path", default=str(DEFAULT_LATEST_PATH))
    parser.add_argument("--stamp", default=default_stamp())
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--purge-legacy-unseen", action="store_true")
    parser.add_argument("--normal-true", type=int, default=DEFAULT_SPECS[0]["n_true"])
    parser.add_argument("--normal-false", type=int, default=DEFAULT_SPECS[0]["n_false"])
    parser.add_argument("--hard-true", type=int, default=DEFAULT_SPECS[1]["n_true"])
    parser.add_argument("--hard-false", type=int, default=DEFAULT_SPECS[1]["n_false"])
    parser.add_argument("--hard2-true", type=int, default=DEFAULT_SPECS[2]["n_true"])
    parser.add_argument("--hard2-false", type=int, default=DEFAULT_SPECS[2]["n_false"])
    parser.add_argument("--hard3-true", type=int, default=DEFAULT_SPECS[3]["n_true"])
    parser.add_argument("--hard3-false", type=int, default=DEFAULT_SPECS[3]["n_false"])
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    payload = build_rotation_bundle(
        specs=resolve_specs(args),
        out_dir=Path(args.out_dir),
        state_path=Path(args.state_path),
        latest_path=Path(args.latest_path),
        stamp=args.stamp,
        refresh_cache=args.refresh_cache,
        purge_legacy=args.purge_legacy_unseen,
    )
    for item in payload["files"]:
        print(
            f"WROTE {item['path']} total={item['selected']['total']} "
            f"cycle_true={item['true_bucket']['cycle']} cycle_false={item['false_bucket']['cycle']}"
        )
    if payload["legacy_unseen_removed"]:
        print(f"REMOVED legacy unseen files={len(payload['legacy_unseen_removed'])}")
    print(f"LATEST {rel(Path(args.latest_path))}")


if __name__ == "__main__":
    main()
