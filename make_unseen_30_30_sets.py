#!/usr/bin/env python3
import argparse
import json
import random
from datetime import datetime
from pathlib import Path


def load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_seed_list(seed_text: str):
    return [int(s.strip()) for s in seed_text.split(",") if s.strip()]


def collect_excluded_ids(benchmark_dir: Path):
    excluded = set()
    for p in benchmark_dir.glob("*_unseen_*.jsonl"):
        for row in load_jsonl(p):
            rid = row.get("id")
            if rid:
                excluded.add(rid)
    return excluded


def balanced_sample(rows, n_true, n_false, seed, excluded_ids):
    rng = random.Random(seed)
    true_rows = [r for r in rows if bool(r["answer"]) is True and r.get("id") not in excluded_ids]
    false_rows = [r for r in rows if bool(r["answer"]) is False and r.get("id") not in excluded_ids]

    if len(true_rows) < n_true or len(false_rows) < n_false:
        raise ValueError(
            f"Not enough rows after exclusion: true={len(true_rows)} false={len(false_rows)} "
            f"need true={n_true} false={n_false}"
        )

    rng.shuffle(true_rows)
    rng.shuffle(false_rows)
    picked = true_rows[:n_true] + false_rows[:n_false]
    rng.shuffle(picked)
    return picked


def build_output_path(out_dir: Path, subset: str, n_true: int, n_false: int, seed: int, stamp: str):
    return out_dir / f"{subset}_balanced{n_true+n_false}_true{n_true}_false{n_false}_seed{seed}_unseen_{stamp}.jsonl"


def main():
    parser = argparse.ArgumentParser(description="Generate unseen balanced 30/30 normal and hard3 seed sets.")
    parser.add_argument("--normal-source", default="data/hf_cache/normal.jsonl")
    parser.add_argument("--hard3-source", default="data/hf_cache/hard3.jsonl")
    parser.add_argument("--out-dir", default="data/benchmark")
    parser.add_argument("--normal-seeds", default="20260401")
    parser.add_argument("--hard3-seeds", default="20260401")
    parser.add_argument("--n-true", type=int, default=30)
    parser.add_argument("--n-false", type=int, default=30)
    parser.add_argument("--exclude-existing-unseen", action="store_true")
    parser.add_argument("--stamp", default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    normal_rows = load_jsonl(Path(args.normal_source))
    hard3_rows = load_jsonl(Path(args.hard3_source))

    excluded = set()
    if args.exclude_existing_unseen:
        excluded = collect_excluded_ids(out_dir)

    normal_seeds = parse_seed_list(args.normal_seeds)
    hard3_seeds = parse_seed_list(args.hard3_seeds)

    print(f"excluded_ids={len(excluded)}")

    for seed in normal_seeds:
        sample = balanced_sample(normal_rows, args.n_true, args.n_false, seed, excluded)
        out_path = build_output_path(out_dir, "normal", args.n_true, args.n_false, seed, args.stamp)
        write_jsonl(out_path, sample)
        print(f"WROTE {out_path.as_posix()} rows={len(sample)}")

    for seed in hard3_seeds:
        sample = balanced_sample(hard3_rows, args.n_true, args.n_false, seed, excluded)
        out_path = build_output_path(out_dir, "hard3", args.n_true, args.n_false, seed, args.stamp)
        write_jsonl(out_path, sample)
        print(f"WROTE {out_path.as_posix()} rows={len(sample)}")


if __name__ == "__main__":
    main()
