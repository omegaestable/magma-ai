"""Per-row pivot probe: can egg prove the pivot laws that would close the goal?

For every open frontier row this tries each candidate pivot law and reports the
three separable outcomes:

  applies       - the law closes the goal by the free syntactic gate
  applies_rev   - the law closes the goal only if the chain search runs
                  rhs -> lhs (i.e. `lemma_applies_to_goal` is direction-blind)
  survives      - no small eq1-model refutes the law
  egg           - equality saturation derived it, with wall-clock seconds

Usage:
    python stage2/experiments/pivot_probe.py --open --budget 60
    python stage2/experiments/pivot_probe.py --ids hard3_0314 --budget 120
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

from egg_bytes_probe import OPEN_ROWS, capture_steps, load_rows  # noqa: E402

PIVOTS = (
    ("collapse", "a = b"),
    ("left_projection", "a ◇ b = a"),
    ("right_projection", "a ◇ b = b"),
    ("product_constant", "a ◇ b = c ◇ d"),
    ("left_row_constant", "a ◇ b = a ◇ c"),
    ("right_col_constant", "a ◇ b = c ◇ b"),
    ("square_left", "a ◇ a = a"),
    ("left_sq_projection", "(a ◇ b) ◇ c = a"),
    ("triple_left", "((a ◇ b) ◇ c) ◇ d = a"),
    ("triple_right", "a ◇ (b ◇ (c ◇ d)) = d"),
    ("pair_right", "a ◇ (b ◇ c) = c"),
)


def reversed_goal(eq2: dict) -> dict:
    return {"lhs": eq2["rhs"], "rhs": eq2["lhs"],
            "variables": list(eq2["variables"]),
            "text": eq2.get("text", "")}


def applies(lemma: dict, eq2: dict) -> str | None:
    """Current production gate."""
    return S.lemma_applies_to_goal(lemma, eq2)


def applies_reverse(lemma: dict, eq2: dict) -> str | None:
    """Same gate, but reducing the goal's rhs down to its lhs."""
    rev = reversed_goal(eq2)
    got = S.simple_true_proof_expr(lemma, rev, hypothesis_name="hlem")
    if got is not None:
        return f"({got[1]}).symm"
    chain = S.find_rewrite_chain(
        lemma, rev, max_depth=S.LEMMA_APPLY_CHAIN_MAX_DEPTH,
        hypothesis_name="hlem")
    if chain is not None:
        return f"({chain[1]}).symm"
    return None


def probe_row(row: dict, budget: float, pivots) -> dict:
    eq1 = S.parse_equation(str(row["equation1"]))
    eq2 = S.parse_equation(str(row["equation2"]))
    out: dict = {"id": row.get("id"), "pivots": []}
    for name, text in pivots:
        lemma = S.lemma_goal(text)
        fwd = applies(lemma, eq2)
        rev = applies_reverse(lemma, eq2) if fwd is None else None
        if fwd is None and rev is None:
            continue
        survives = S.lemma_survives_models(eq1, lemma)
        entry = {"pivot": name, "applies": fwd is not None,
                 "applies_rev": rev is not None, "survives": survives}
        if survives:
            started = time.monotonic()
            rendered, cap = capture_steps(eq1, lemma, budget)
            entry["seconds"] = round(time.monotonic() - started, 2)
            entry["egg"] = rendered is not None
            entry["merged"] = "raw_steps" in cap or "explain_error" in cap
            if "explain_error" in cap:
                entry["explain_error"] = cap["explain_error"]
            if "raw_steps" in cap:
                entry["raw_steps"] = cap["raw_steps"]
            if rendered is not None:
                entry["proof_bytes"] = len(rendered.encode("utf-8"))
        out["pivots"].append(entry)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--budget", type=float, default=60.0)
    ap.add_argument("--effort", default="fast")
    ap.add_argument("--pivots", default="")
    args = ap.parse_args()

    S.set_effort(args.effort)
    rows = load_rows()
    ids = list(OPEN_ROWS) if args.open else [
        i for i in args.ids.split(",") if i.strip()]
    wanted = {p for p in args.pivots.split(",") if p.strip()}
    pivots = tuple(p for p in PIVOTS if not wanted or p[0] in wanted)
    for row_id in ids:
        row = rows.get(row_id)
        if row is None:
            print(json.dumps({"id": row_id, "error": "not found"}))
            continue
        try:
            print(json.dumps(probe_row(row, args.budget, pivots),
                             ensure_ascii=False))
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"id": row_id,
                              "error": f"{type(exc).__name__}: {exc}"}))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
