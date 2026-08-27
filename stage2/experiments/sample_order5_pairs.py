#!/usr/bin/env python3
"""Generate random order-5 equation-implication pairs, no ground truth.

Unlike the order-4 ETP catalog, there is no precomputed order-5xorder-5
implication matrix (that space is ~62,576^2 pairs and was never computed by
anyone) - `sample_etp_matrix.py`'s approach of reading a label out of a
matrix does not apply here. This script instead draws random distinct pairs
from the order-5 equation catalog itself
(`vendor/stage2-official/examples/problems/eq_size5.txt`, 62,576 laws in `*`
notation, the same catalog `evaluation_order5` is drawn from) and emits them
with NO `answer` field.

`audit_corpus.audit_row` already tolerates a missing `answer` - it just skips
the ground-truth cross-check and keeps doing full offline-oracle verification
(proof-kernel-check every TRUE certificate, model-check it against finite
models of eq1, independently re-verify every FALSE witness table). So
"oracle failures: 0" on this sample means "0 unsound answers", not "0 wrong
answers vs known truth" - there is no known truth to check against. State
that distinction whenever reporting results from this sampler.

Usage:
    python stage2/experiments/sample_order5_pairs.py --count 10000 \
        --max-variables 3 --seed 20260820 \
        --out stage2/results/order5-sample-10000-2026-08-20.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))

import solver as S  # noqa: E402

EQ_SIZE5_PATH = (REPO_ROOT / "vendor" / "stage2-official" / "examples"
                  / "problems" / "eq_size5.txt")


def load_catalog(max_variables: int,
                  catalog_path: Path | None = None) -> list[tuple[int, str]]:
    lines = (catalog_path or EQ_SIZE5_PATH).read_text(
        encoding="utf-8").splitlines()
    catalog: list[tuple[int, str]] = []
    for i, line in enumerate(lines, 1):
        text = line.strip()
        if not text:
            continue
        eq = S.parse_equation(text)
        if len(eq["variables"]) <= max_variables:
            catalog.append((i, text))
    return catalog


def sample_pairs(count: int, seed: int, max_variables: int,
                  exclude: set[tuple[int, int]] | None = None,
                  catalog_path: Path | None = None,
                  id_prefix: str = "order5",
                  goal_catalog_path: Path | None = None,
                  goal_max_variables: int | None = None) -> list[dict]:
    catalog = load_catalog(max_variables, catalog_path)
    # A separate goal catalog makes "big hypothesis, small goal" draws possible.
    # Drawing both sides from the same high-order catalog produces an almost
    # pure-FALSE population -- an order-6 pilot came back 200/200 FALSE, because
    # two unrelated strong laws essentially never imply one another. Pointing
    # the goal at a smaller catalog is where TRUE implications actually live.
    goal_catalog = (catalog if goal_catalog_path is None else
                    load_catalog(goal_max_variables if goal_max_variables
                                 is not None else max_variables,
                                 goal_catalog_path))
    same_catalog = goal_catalog_path is None
    rng = random.Random(seed)
    exclude = exclude or set()
    drawn: set[tuple[int, int]] = set()
    rows: list[dict] = []
    n = len(catalog)
    m = len(goal_catalog)
    while len(rows) < count:
        a = rng.randrange(n)
        b = rng.randrange(m)
        if same_catalog and a == b:
            continue
        i, eq1_text = catalog[a]
        j, eq2_text = goal_catalog[b]
        if eq1_text == eq2_text:
            continue
        key = (i, j)
        if key in drawn or key in exclude:
            continue
        drawn.add(key)
        rows.append({
            "id": f"{id_prefix}_{i}_{j}",
            "eq1_id": i,
            "eq2_id": j,
            "equation1": eq1_text,
            "equation2": eq2_text,
        })
    return rows


def load_exclusions(paths: list[Path]) -> set[tuple[int, int]]:
    exclude: set[tuple[int, int]] = set()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        rows = ([json.loads(line) for line in text.splitlines() if line.strip()]
                if path.suffix == ".jsonl" else json.loads(text))
        for row in rows:
            exclude.add((row["eq1_id"], row["eq2_id"]))
    return exclude


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10000)
    ap.add_argument("--max-variables", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260820)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--exclude", type=Path, nargs="*", default=[],
                    help="prior batches' jsonl files whose (eq1_id, eq2_id) "
                         "pairs must not be redrawn")
    ap.add_argument("--catalog", type=Path, default=None,
                    help="equation catalog to draw from, one law per line in "
                         "`*` notation (default: the vendored eq_size5.txt). "
                         "Use generate_eq_catalog.py to build an order-6 one; "
                         "eq ids are line numbers within THIS file, so a batch "
                         "is only comparable to others from the same catalog.")
    ap.add_argument("--id-prefix", default="order5",
                    help="row-id prefix, e.g. `order6` for an order-6 catalog")
    ap.add_argument("--goal-catalog", type=Path, default=None,
                    help="draw eq2 from a DIFFERENT catalog than eq1. Use a "
                         "smaller-order goal catalog to get a population with "
                         "a non-trivial TRUE fraction; same-catalog draws at "
                         "high order are almost pure FALSE.")
    ap.add_argument("--goal-max-variables", type=int, default=None,
                    help="variable cap for the goal catalog (default: same as "
                         "--max-variables)")
    args = ap.parse_args()

    exclude = load_exclusions(args.exclude)
    rows = sample_pairs(args.count, args.seed, args.max_variables, exclude,
                        catalog_path=args.catalog, id_prefix=args.id_prefix,
                        goal_catalog_path=args.goal_catalog,
                        goal_max_variables=args.goal_max_variables)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} {args.id_prefix} pairs (<= {args.max_variables} "
          f"variables each, no ground truth) to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
