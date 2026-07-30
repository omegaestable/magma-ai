"""ETP-guided pivot discovery: which intermediate law makes a hard TRUE row easy.

The governing fact of this project (2026-07-22): **proof-search cost scales with
goal size, so a small law that implies the goal can be reachable when the goal is
not.** `projection_bootstrap`, `lemma_bootstrap` and `lemma_chain` all exploit it
and are worth ~+47 official TRUE rows between them.

Their weakness is candidate generation. `enumerated_lemma_library()` guesses ~600
small laws, and the 2026-07-23 oracle-pivot experiment showed widening that list is
measured-dead. But the Equational Theories Project already computed the answer: its
outcome matrix records, for all 4694 x 4694 pairs, whether one law implies another.
So for a row `e1 => e2` we can ask it directly for every `M` with
`e1 => M` and `M => e2`, ranked by how small `M` is — a ground-truth pivot list
instead of a guess.

Dev-time tool only. The submitted solver may not read `data/`, so anything learned
here has to graduate into a generalised family or a baked-in library entry
(Operational Note 2 / Banned Approach 3).

    python stage2/experiments/etp_pivots.py --ids hard2_0073,hard2_0099
    python stage2/experiments/etp_pivots.py --set hard2 --unsolved-only --max-pivots 6
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))

import solver as S  # noqa: E402

CACHE = REPO_ROOT / "data" / "teorth_cache"
GRAPH = CACHE / "graph.json"
MATRIX_CACHE = CACHE / "outcome_matrix.bin"
EQUATIONS = REPO_ROOT / "data" / "exports" / "equations.txt"

N = 4694

# Teorth outcome codes, as used by theory/tools/fetch_teorth_data.py.
# Positive => implication holds; negative => refuted; 0 => unknown.
CODE_SEMANTICS = {
    1: -4,  # explicit_conjecture_false
    2: -4,  # explicit_proof_false
    3: 4,   # explicit_proof_true
    4: -1,  # implicit_conjecture_false
    5: 1,   # implicit_conjecture_true
    6: -3,  # implicit_proof_false
    7: 3,   # implicit_proof_true
    8: 0,   # unknown
}


def load_matrix() -> bytearray:
    """Decode the RLE outcome matrix to a flat bytearray of raw codes (~22 MB).

    Cached on disk because the RLE expansion takes several seconds and every
    caller wants the same bytes.
    """
    if MATRIX_CACHE.exists():
        data = bytearray(MATRIX_CACHE.read_bytes())
        if len(data) == N * N:
            return data
    raw = json.loads(GRAPH.read_text(encoding="utf-8"))
    rle = raw["rle_encoded_array"]
    flat = bytearray()
    for i in range(0, len(rle), 2):
        flat.extend(bytes([int(rle[i])]) * int(rle[i + 1]))
    if len(flat) != N * N:
        raise ValueError(f"decoded {len(flat)} cells, expected {N * N}")
    MATRIX_CACHE.write_bytes(bytes(flat))
    return flat


def load_equations() -> dict[int, str]:
    """Equation id -> text. One law per line; the id is the 1-based line number,
    matching the ETP's own numbering (line 1 is `x = x` = Equation1)."""
    out: dict[int, str] = {}
    for lineno, line in enumerate(
            EQUATIONS.read_text(encoding="utf-8").splitlines(), 1):
        text = line.strip()
        if text:
            out[lineno] = text
    return out


class Outcomes:
    def __init__(self) -> None:
        self.flat = load_matrix()
        self.equations = load_equations()

    def code(self, a: int, b: int) -> int:
        if not (1 <= a <= N and 1 <= b <= N):
            return 8
        return self.flat[(a - 1) * N + (b - 1)]

    def holds(self, a: int, b: int) -> bool | None:
        """True / False / None(unknown) for `a implies b`."""
        sem = CODE_SEMANTICS.get(self.code(a, b), 0)
        if sem > 0:
            return True
        if sem < 0:
            return False
        return None

    def pivots(self, a: int, b: int, *, limit: int = 12) -> list[tuple[int, str, int]]:
        """Every M with a => M => b, ranked by equation text length.

        Shorter is better: a small law is a smaller proof-search target, which is
        the entire reason this list is useful.
        """
        found: list[tuple[int, str, int]] = []
        for m in range(1, N + 1):
            if m in (a, b):
                continue
            if self.holds(a, m) is not True:
                continue
            if self.holds(m, b) is not True:
                continue
            text = self.equations.get(m, "")
            if not text:
                continue
            found.append((m, text, len(text)))
        found.sort(key=lambda t: t[2])
        return found[:limit]


SETS = {
    "normal": REPO_ROOT / "data/stage2_official_problems/normal.jsonl",
    "hard1": REPO_ROOT / "data/stage2_official_problems/hard1.jsonl",
    "hard2": REPO_ROOT / "data/stage2_official_problems/hard2.jsonl",
    "hard3": REPO_ROOT / "data/stage2_official_problems/hard3.jsonl",
    "evaluation_normal": REPO_ROOT / "data/hf_cache/evaluation_normal.jsonl",
    "evaluation_hard": REPO_ROOT / "data/hf_cache/evaluation_hard.jsonl",
    "evaluation_extra_hard": REPO_ROOT / "data/hf_cache/evaluation_extra_hard.jsonl",
    "evaluation_order5": REPO_ROOT / "data/hf_cache/evaluation_order5.jsonl",
}


def load_rows(name: str) -> list[dict]:
    path = SETS[name]
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_all() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for name in SETS:
        if SETS[name].exists():
            for row in load_rows(name):
                out.setdefault(str(row["id"]), row)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--set", dest="set_name", default="")
    ap.add_argument("--unsolved-only", action="store_true")
    ap.add_argument("--true-only", action="store_true")
    ap.add_argument("--max-pivots", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--verify-labels", action="store_true",
                    help="cross-check ETP outcomes against benchmark labels")
    args = ap.parse_args()

    started = time.monotonic()
    oc = Outcomes()
    print(f"loaded outcome matrix ({len(oc.flat)} cells, "
          f"{len(oc.equations)} equation texts) in "
          f"{time.monotonic() - started:.1f}s", flush=True)

    catalog = load_all()
    if args.verify_labels:
        agree = disagree = unknown = 0
        for row in catalog.values():
            if not isinstance(row.get("answer"), bool):
                continue
            got = oc.holds(int(row["eq1_id"]), int(row["eq2_id"]))
            if got is None:
                unknown += 1
            elif got == row["answer"]:
                agree += 1
            else:
                disagree += 1
                if disagree <= 5:
                    print(f"  DISAGREE {row['id']}: label={row['answer']} etp={got}")
        print(f"label cross-check: agree={agree} disagree={disagree} unknown={unknown}")
        if disagree:
            print("  ^ disagreement means the id mapping or codes are wrong; "
                  "do not trust pivots until this is 0")
        return 0 if disagree == 0 else 1

    if args.ids:
        rows = [catalog[i] for i in args.ids.split(",") if i.strip() in catalog]
    elif args.set_name:
        rows = load_rows(args.set_name)
    else:
        print("pass --ids or --set")
        return 2

    if args.true_only:
        rows = [r for r in rows if r.get("answer") is True]
    if args.unsolved_only:
        keep = []
        for r in rows:
            S.set_effort("fast")
            S.clear_term_caches()
            if S.solve_problem(r, false_time_budget=2.0) is None:
                keep.append(r)
        rows = keep
    if args.limit:
        rows = rows[: args.limit]

    print(f"\n{len(rows)} row(s)\n", flush=True)
    results = []
    for r in rows:
        e1, e2 = int(r["eq1_id"]), int(r["eq2_id"])
        direct = oc.holds(e1, e2)
        piv = oc.pivots(e1, e2, limit=args.max_pivots)
        print(f"{r['id']}  Eq{e1} => Eq{e2}   label={r.get('answer')} etp={direct}")
        print(f"   eq1: {r['equation1']}")
        print(f"   eq2: {r['equation2']}")
        if not piv:
            print("   no ETP pivot found")
        for m, text, ln in piv:
            print(f"   pivot Eq{m:<5} ({ln:>3} chars)  {text}")
        print(flush=True)
        results.append({"id": r["id"], "eq1_id": e1, "eq2_id": e2,
                        "label": r.get("answer"), "etp": direct,
                        "pivots": [{"id": m, "text": t} for m, t, _ in piv]})

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
