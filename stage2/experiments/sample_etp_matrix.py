#!/usr/bin/env python3
"""Draw a random balanced sample of rows from the full ETP outcome matrix.

The "full order 4 graph" is the 4,694x4,694 matrix of labelled implications
between ETP's order-4 magma laws (`data/exports/`) - about 22M off-diagonal
pairs, of which the official/HF benchmark sets cover only ~2,469 distinct
rows. This script draws a fresh random slice of that graph so the solver can
be measured on rows it was never tuned against, at a scale beyond the 200-row
samples used in earlier sessions (see
`stage2/results/2026-08-01-real-judge-broad-runs-and-marathon-memory-guard-bug.md`).

Reuses `ETPMatrix` from spotcheck.py rather than reimplementing matrix
loading or sampling - same rejection-sampling logic (off-diagonal pairs only),
same coverage-ledger preference for pairs not already spot-checked.

Output is a jsonl of `{id, eq1_id, eq2_id, equation1, equation2, answer}` rows,
directly consumable by `audit_corpus.py --file` and `load_problems`.

Usage:
    python stage2/experiments/sample_etp_matrix.py --count 5000 --seed 20260820 \
        --out stage2/results/etp-sample-5000-2026-08-20.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "experiments"))

from spotcheck import ETPMatrix, load_coverage, coverage_key, ETP_SOURCE  # noqa: E402


def load_exclusions(paths: list[Path]) -> set[str]:
    exclude: set[str] = set()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        rows = ([json.loads(line) for line in text.splitlines() if line.strip()]
                if path.suffix == ".jsonl" else json.loads(text))
        for row in rows:
            exclude.add(coverage_key(ETP_SOURCE, row))
    return exclude


def sample_rows(count: int, seed: int, exclude: set[str] | None = None) -> list[dict]:
    etp = ETPMatrix()
    rng = random.Random(seed)
    seen = load_coverage()  # avoid pairs the standing spotcheck loop already used
    seen = seen | (exclude or set())
    drawn: set[str] = set()
    # `pool` is `seen | drawn` maintained incrementally. Building that union
    # inside the draw loop is O(len(seen) + len(drawn)) per row, so a 100,000-row
    # draw spent essentially all of its time copying sets (10,000 rows finished
    # in ~1 min; 100,000 was still running after 10). Same contents, same RNG
    # sequence, same output — only the cost changes.
    pool: set[str] = set(seen)
    rows: list[dict] = []
    n_true = count // 2
    n_false = count - n_true
    for want_true, target in ((True, n_true), (False, n_false)):
        got = 0
        while got < target:
            row = etp.sample(want_true, pool, rng, pure_random=False)
            if row is None:
                # exhausted-unseen fallback returned nothing; fall back to
                # ignoring the ledger rather than looping forever.
                row = etp.sample(want_true, drawn, rng, pure_random=True)
            key = coverage_key(ETP_SOURCE, row)
            if key in drawn:
                continue
            drawn.add(key)
            pool.add(key)
            rows.append(row)
            got += 1
    rng.shuffle(rows)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=20260820)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--exclude", type=Path, nargs="*", default=[],
                    help="jsonl/json files whose (eq1_id, eq2_id) pairs "
                         "must not be redrawn (e.g. a prior batch's sample)")
    args = ap.parse_args()

    exclude = load_exclusions(args.exclude)
    rows = sample_rows(args.count, args.seed, exclude)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    n_true = sum(1 for r in rows if r["answer"])
    print(f"Wrote {len(rows)} rows ({n_true} true / {len(rows) - n_true} false) "
          f"to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
