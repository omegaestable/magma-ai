#!/usr/bin/env python3
"""Randomized cross-source accuracy spot-check for the Stage 2 solver.

Runs many small, balanced, random batches across many sources so latent solver
mistakes surface over time. The target is *accuracy* — the solver must never
submit a verdict that contradicts ground truth — not coverage; skipping a row is
safe, submitting a wrong answer is not.

Each row is solved and verified by the *same* path the corpus audit uses
(`audit_corpus.audit_row`): `solve_problem`, then the offline oracles (proof
kernel for `exact_expr`/`singleton`/`lemma` certificates, finite-model check on
every TRUE verdict, witness re-verification on every FALSE), plus a ground-truth
label cross-check. Nothing here reimplements verification.

Sources
-------
- the 8 *distinct* benchmark sets (official normal/hard1/hard2/hard3 and the HF
  evaluation_* sets); the HF normal/hard* mirrors are excluded because they are
  the same problems in `*` instead of `◇` notation.
- `etp`: the Equational Theories Project outcome matrix in `data/exports/`
  (4694x4694 ~= 22M labelled implication pairs), a validated second ground-truth
  source the solver has never been sampled against.

A caught mistake is appended to the git-tracked
`stage2/fixtures/spotcheck_failures.jsonl` and replayed forever by
`stage2/tests/test_spotcheck_regressions.py`, which runs inside the pre-package
gate — so a mistake found once can never silently return.

Usage
-----
    python stage2/experiments/spotcheck.py                 # 5 TRUE + 5 FALSE / source
    python stage2/experiments/spotcheck.py --true 10 --false 10
    python stage2/experiments/spotcheck.py --sources etp,hard3 --seed 123
    python stage2/experiments/spotcheck.py --pure-random    # ignore the coverage ledger
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "experiments"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "tests"))

from audit_corpus import HF_SETS, SETS, audit_row, load_problems  # noqa: E402

# Distinct benchmark sources: the official core plus the HF *evaluation* sets.
# The HF normal/hard/hard1/hard2/hard3 files are notational mirrors of the
# official sets (same eq ids, `*` vs `◇`) and add no content, so they are
# deliberately excluded.
BENCHMARK_SOURCES: dict[str, Path] = {
    "normal": SETS["normal"],
    "hard1": SETS["hard1"],
    "hard2": SETS["hard2"],
    "hard3": SETS["hard3"],
    "eval_normal": HF_SETS["hf_evaluation_normal"],
    "eval_hard": HF_SETS["hf_evaluation_hard"],
    "eval_extra_hard": HF_SETS["hf_evaluation_extra_hard"],
    "eval_order5": HF_SETS["hf_evaluation_order5"],
}

ETP_SOURCE = "etp"
ALL_SOURCES = [*BENCHMARK_SOURCES, ETP_SOURCE]

EXPORTS = REPO_ROOT / "data" / "exports"
ETP_EQUATIONS = EXPORTS / "equations.txt"
ETP_OUTCOMES = EXPORTS / "general_outcomes.json.gz"

COVERAGE_LEDGER = REPO_ROOT / "stage2" / "results" / "spotcheck-coverage.json"
FAILURES_FIXTURE = REPO_ROOT / "stage2" / "fixtures" / "spotcheck_failures.jsonl"


# ---------------------------------------------------------------------------
# ETP outcome matrix: a synthetic, essentially unlimited labelled source.
# ---------------------------------------------------------------------------

class ETPMatrix:
    """Lazy view over the 4694x4694 ETP outcome matrix and equation texts.

    Equation ids are 1-based line numbers in `equations.txt`; matrix cell
    [i-1][j-1] is the outcome of `Equation i implies Equation j`. Every cell is
    `{implicit,explicit}_proof_{true,false}`, so a cell ending in `_true` is a
    TRUE implication.
    """

    def __init__(self) -> None:
        self.equations = [
            line.strip()
            for line in ETP_EQUATIONS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        with gzip.open(ETP_OUTCOMES, "rt", encoding="utf-8") as handle:
            self.outcomes = json.load(handle)["outcomes"]
        self.n = len(self.equations)
        if len(self.outcomes) != self.n:
            raise ValueError(
                f"ETP matrix ({len(self.outcomes)}) and equations.txt "
                f"({self.n}) disagree")

    def label(self, eq1_id: int, eq2_id: int) -> bool | None:
        """True/False label, or None if either id is outside the matrix."""
        if not (1 <= eq1_id <= self.n and 1 <= eq2_id <= self.n):
            return None
        return self.outcomes[eq1_id - 1][eq2_id - 1].endswith("_true")

    def problem(self, eq1_id: int, eq2_id: int) -> dict:
        return {
            "id": f"etp_{eq1_id}_{eq2_id}",
            "eq1_id": eq1_id,
            "eq2_id": eq2_id,
            "equation1": self.equations[eq1_id - 1],
            "equation2": self.equations[eq2_id - 1],
            "answer": bool(self.label(eq1_id, eq2_id)),
        }

    def sample(self, want_true: bool, seen: set[str], rng: random.Random,
               *, pure_random: bool, max_attempts: int = 4000) -> dict | None:
        """One random labelled row with the requested truth value.

        Rejection-samples off-diagonal pairs (i != j, so never a trivial
        reflexive row) and, unless `pure_random`, prefers pairs not already in
        the coverage ledger.
        """
        fallback: dict | None = None
        for _ in range(max_attempts):
            i = rng.randint(1, self.n)
            j = rng.randint(1, self.n)
            if i == j:
                continue
            if self.outcomes[i - 1][j - 1].endswith("_true") != want_true:
                continue
            row = self.problem(i, j)
            if pure_random:
                return row
            if coverage_key(ETP_SOURCE, row) not in seen:
                return row
            fallback = fallback or row  # exhausted-unseen fallback
        return fallback


# ---------------------------------------------------------------------------
# Coverage ledger
# ---------------------------------------------------------------------------

def coverage_key(source: str, problem: dict) -> str:
    return f"{source}|{problem.get('eq1_id')}|{problem.get('eq2_id')}"


def load_coverage() -> set[str]:
    if not COVERAGE_LEDGER.exists():
        return set()
    try:
        return set(json.loads(COVERAGE_LEDGER.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, ValueError):
        return set()


def save_coverage(seen: set[str]) -> None:
    COVERAGE_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE_LEDGER.write_text(
        json.dumps(sorted(seen)), encoding="utf-8")


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def _benchmark_pools(path: Path) -> dict[bool, list[dict]]:
    pools: dict[bool, list[dict]] = {True: [], False: []}
    for row in load_problems(path):
        if isinstance(row.get("answer"), bool):
            pools[row["answer"]].append(row)
    return pools


def _pick_benchmark(pool: list[dict], count: int, source: str,
                    seen: set[str], rng: random.Random,
                    *, pure_random: bool) -> list[dict]:
    shuffled = pool[:]
    rng.shuffle(shuffled)
    if pure_random:
        return shuffled[:count]
    unseen = [r for r in shuffled if coverage_key(source, r) not in seen]
    if len(unseen) >= count:
        return unseen[:count]
    # Prefer unseen, then top up with already-seen rows to keep class balance.
    remainder = [r for r in shuffled if coverage_key(source, r) not in
                 {coverage_key(source, u) for u in unseen}]
    return (unseen + remainder)[:count]


def sample_batch(sources: list[str], n_true: int, n_false: int,
                 seen: set[str], rng: random.Random, *, pure_random: bool,
                 etp: ETPMatrix | None) -> list[tuple[str, dict]]:
    batch: list[tuple[str, dict]] = []
    for source in sources:
        if source == ETP_SOURCE:
            assert etp is not None
            for want_true, count in ((True, n_true), (False, n_false)):
                for _ in range(count):
                    row = etp.sample(want_true, seen, rng, pure_random=pure_random)
                    if row is not None:
                        batch.append((source, row))
        else:
            pools = _benchmark_pools(BENCHMARK_SOURCES[source])
            for label, count in ((True, n_true), (False, n_false)):
                for row in _pick_benchmark(pools[label], count, source, seen,
                                           rng, pure_random=pure_random):
                    batch.append((source, row))
    return batch


# ---------------------------------------------------------------------------
# Per-row classification
# ---------------------------------------------------------------------------

# audit_row oracle values that mean the solver produced a wrong or unsound
# answer (as opposed to skipping, which is safe). Anything not in {None, "ok"}
# after a solve is a mistake; these are the named ones we surface.
MISTAKE_ORACLES = {
    "VERDICT_CONTRADICTS_LABEL",
    "FAILED",
    "problem_parse_failed",
}


def classify(result: dict) -> str:
    status = result.get("status")
    if status == "crash":
        return "mistake"
    if status == "skip":
        return "skip"
    # solved
    oracle = result.get("oracle")
    if oracle in (None, "ok"):
        return "correct"
    return "mistake"


def _audit_one(item: tuple[str, dict], *, false_budget: float,
               effort: str) -> tuple[str, dict, dict]:
    source, problem = item
    result = audit_row(problem, subsumption=False,
                       false_budget=false_budget, effort=effort)
    return source, problem, result


# ---------------------------------------------------------------------------
# Failure fixture
# ---------------------------------------------------------------------------

def load_pinned_keys() -> set[tuple]:
    keys: set[tuple] = set()
    if not FAILURES_FIXTURE.exists():
        return keys
    for line in FAILURES_FIXTURE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            keys.add((row.get("eq1_id"), row.get("eq2_id")))
    return keys


def pin_failure(source: str, problem: dict, result: dict) -> bool:
    """Append a caught mistake to the git-tracked regression fixture.

    Deduped by (eq1_id, eq2_id). Returns True if it was newly pinned.
    """
    key = (problem.get("eq1_id"), problem.get("eq2_id"))
    if key in load_pinned_keys():
        return False
    record = {
        "source": source,
        "id": problem.get("id"),
        "eq1_id": problem.get("eq1_id"),
        "eq2_id": problem.get("eq2_id"),
        "equation1": problem.get("equation1"),
        "equation2": problem.get("equation2"),
        "answer": problem.get("answer"),
        "observed": {
            "status": result.get("status"),
            "verdict": result.get("verdict"),
            "route": result.get("route"),
            "oracle": result.get("oracle"),
            "oracle_error": result.get("oracle_error"),
            "error": result.get("error"),
        },
        "pinned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    FAILURES_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    with FAILURES_FIXTURE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return True


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--true", dest="n_true", type=int, default=5,
                    help="TRUE-labelled rows per source (default 5)")
    ap.add_argument("--false", dest="n_false", type=int, default=5,
                    help="FALSE-labelled rows per source (default 5)")
    ap.add_argument("--sources", default=",".join(ALL_SOURCES),
                    help="comma-separated subset of: " + ", ".join(ALL_SOURCES))
    ap.add_argument("--seed", type=int, default=None,
                    help="RNG seed (default: time-based, printed for replay)")
    ap.add_argument("--pure-random", action="store_true",
                    help="ignore the coverage ledger; independent uniform draw")
    ap.add_argument("--effort", choices=("fast", "standard", "deep"),
                    default="fast")
    ap.add_argument("--false-budget", type=float, default=2.0)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    seed = args.seed if args.seed is not None else int(time.time())
    rng = random.Random(seed)

    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    unknown = [s for s in sources if s not in ALL_SOURCES]
    if unknown:
        print(f"unknown sources: {unknown}\nvalid: {ALL_SOURCES}")
        return 2

    etp = ETPMatrix() if ETP_SOURCE in sources else None
    seen = set() if args.pure_random else load_coverage()

    print(f"spotcheck seed={seed} sources={sources} "
          f"true={args.n_true} false={args.n_false} effort={args.effort} "
          f"pure_random={args.pure_random}", flush=True)

    batch = sample_batch(sources, args.n_true, args.n_false, seen, rng,
                         pure_random=args.pure_random, etp=etp)
    print(f"sampled {len(batch)} rows across {len(sources)} sources", flush=True)

    worker = partial(_audit_one, false_budget=args.false_budget,
                     effort=args.effort)
    started = time.monotonic()
    if args.workers <= 1:
        results = [worker(item) for item in batch]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(worker, batch, chunksize=1))
    elapsed = time.monotonic() - started

    # Per-source tallies and mistake handling.
    per_source: dict[str, dict[str, int]] = {
        s: {"attempted": 0, "correct": 0, "skip": 0, "mistake": 0}
        for s in sources}
    mistakes: list[tuple[str, dict, dict]] = []
    label_integrity_warnings: list[str] = []
    newly_pinned = 0

    for source, problem, result in results:
        outcome = classify(result)
        tally = per_source[source]
        tally["attempted"] += 1
        tally[outcome if outcome in tally else "mistake"] += 1
        seen.add(coverage_key(source, problem))

        if outcome == "mistake":
            mistakes.append((source, problem, result))
            if pin_failure(source, problem, result):
                newly_pinned += 1

        # Independent second-label integrity check: for benchmark rows in ETP
        # range, the fixture label must agree with the ETP matrix. A mismatch
        # is a data-integrity issue, surfaced but not pinned as a solver bug.
        if etp is not None and source != ETP_SOURCE:
            etp_label = etp.label(problem.get("eq1_id", -1),
                                  problem.get("eq2_id", -1))
            if etp_label is not None and etp_label != problem.get("answer"):
                label_integrity_warnings.append(
                    f"{source} {problem.get('id')}: fixture="
                    f"{problem.get('answer')} etp={etp_label}")

    if not args.pure_random:
        save_coverage(seen)

    # Report.
    print(f"\n=== spotcheck results ({elapsed:.0f}s) ===")
    header = f"{'source':18s} {'att':>4s} {'ok':>4s} {'skip':>5s} {'MISS':>5s} {'acc':>6s} {'cov':>6s}"
    print(header)
    tot = {"attempted": 0, "correct": 0, "skip": 0, "mistake": 0}
    for source in sources:
        t = per_source[source]
        for k in tot:
            tot[k] += t[k]
        solved = t["attempted"] - t["skip"]
        acc = f"{100 * t['correct'] / solved:.0f}%" if solved else "-"
        cov = f"{100 * (t['attempted'] - t['skip']) / t['attempted']:.0f}%" if t["attempted"] else "-"
        print(f"{source:18s} {t['attempted']:4d} {t['correct']:4d} "
              f"{t['skip']:5d} {t['mistake']:5d} {acc:>6s} {cov:>6s}")
    solved_tot = tot["attempted"] - tot["skip"]
    acc = f"{100 * tot['correct'] / solved_tot:.1f}%" if solved_tot else "-"
    cov = f"{100 * solved_tot / tot['attempted']:.1f}%" if tot["attempted"] else "-"
    print(f"{'TOTAL':18s} {tot['attempted']:4d} {tot['correct']:4d} "
          f"{tot['skip']:5d} {tot['mistake']:5d} {acc:>6s} {cov:>6s}")
    print(f"\naccuracy (correct / attempted-and-solved) = {acc}")
    print(f"coverage (solved / attempted)             = {cov}")

    if label_integrity_warnings:
        print(f"\n!! {len(label_integrity_warnings)} fixture/ETP label mismatches:")
        for warning in label_integrity_warnings[:20]:
            print(f"   {warning}")

    if mistakes:
        print(f"\n!! {len(mistakes)} MISTAKES ({newly_pinned} newly pinned to "
              f"{FAILURES_FIXTURE.name}):")
        for source, problem, result in mistakes[:20]:
            print(f"   {source} {problem.get('id')} "
                  f"label={problem.get('answer')} "
                  f"verdict={result.get('verdict')} "
                  f"oracle={result.get('oracle')} "
                  f"route={result.get('route')}")
        print("\nRun `pytest stage2/tests` to confirm the regression, then fix "
              "the solver until it passes.")
        return 1

    print("\nNo mistakes. Solver submitted no wrong verdict on this batch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
