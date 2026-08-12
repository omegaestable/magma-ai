"""Find a maximal implication CHAIN from eq1 to eq2 in the ETP outcome matrix,
then prove each hop with multi-rule equality saturation.

Why a chain and not a pivot: `etp_pivots.py` answers "which single law M has
eq1 => M => eq2", and on the rows left after `egg_ladder` shipped, every such M is
as hard to prove as the goal. But the matrix is the *transitive closure* of a
graph, so between eq1 and eq2 there is usually a whole ladder
`eq1 => M1 => M2 => ... => eq2`, and each hop is a much smaller step. That is
exactly the shape `egg_ladder` builds certificates in — it just cannot discover
the rungs, because the solver may not read `data/`.

So this is the dev-time discoverer: it finds the chain, proves each hop, and emits
the assembled `lemma_chain` certificate for `distill_certs.py` to judge and pin
(rail 5h). Nothing here ships; the *certificate* does.

    python stage2/experiments/etp_chain.py --ids hard3_0214
    python stage2/experiments/etp_chain.py --ids hard2_0073 --hop-budget 30
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "tests"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "experiments"))

import oracles  # noqa: E402
import solver as S  # noqa: E402

from egg_bytes_probe import load_rows  # noqa: E402
from etp_pivots import Outcomes  # noqa: E402


def explicit_chain(start: int, goal: int, *, max_depth: int) -> list[int] | None:
    """ETP's own proof decomposition, from the explicit implication edges.

    Preferred over the matrix because each edge is a single ETP theorem, so each
    hop is a step somebody has already shown is one step.
    """
    from trace_teorth_path import bfs_path, implication_edges
    path = bfs_path(implication_edges(), start, goal, max_depth)
    return path


def matrix_chain(out: Outcomes, start: int, goal: int, *,
                 max_links: int) -> list[int]:
    """A chain start -> ... -> goal, every link a matrix-confirmed implication.

    Greedy from `start`: among the laws `start` implies that still imply `goal`,
    take the strongest (the one implying the most of the others), which is the
    smallest move away from `current` and therefore the most provable hop.

    Equivalent intermediates are **kept**, which was the fix that made this work:
    rejecting them as "zero-length steps" is what made `hard3_0214` report no
    intermediates at all, while the explicit graph has a four-hop path for it. A
    chain through equivalent forms is a sequence of cheap rewrites — exactly the
    rungs wanted — so loops are prevented with a visited set instead.
    """
    path = [start]
    visited = {start}
    current = start
    for _ in range(max_links):
        if out.holds(current, goal) is None:
            break
        candidates = [
            mid for mid in range(1, 4695)
            if mid not in visited and mid != goal
            and out.holds(current, mid) is True
            and out.holds(mid, goal) is True
        ]
        if not candidates:
            break

        def strength(mid: int) -> int:
            return sum(1 for other in candidates
                       if other != mid and out.holds(mid, other) is True)
        current = max(candidates, key=strength)
        visited.add(current)
        path.append(current)
    path.append(goal)
    return path


def chain(out: Outcomes, start: int, goal: int, *, max_links: int,
          prefer_explicit: bool = True) -> tuple[list[int], str]:
    if prefer_explicit:
        found = explicit_chain(start, goal, max_depth=max_links + 2)
        if found and len(found) > 2:
            return found, "explicit"
    return matrix_chain(out, start, goal, max_links=max_links), "matrix"


def etp_rungs(out: Outcomes, eq1_id: int, *, limit: int) -> list[tuple[int, str]]:
    """Every law the matrix says eq1 implies, smallest first.

    This is the graph's real contribution, and it is not the eq1 -> eq2 path. A
    path in implication order is one hard step (eq1 to the strongest
    intermediate) followed by trivial ones, because each later law is a
    *consequence* of the earlier — that is not a ladder of increasing knowledge.
    What a ladder needs is side facts: laws that follow from eq1 and help prove
    the target without implying it. Idempotence is the measured example — it
    unlocked `hard3_0266` and it does not imply that goal at all.
    `lemma_survives_models` can only say "not obviously refutable"; the matrix
    says *derivable*, so every candidate here is one egg could in principle get.
    """
    out_rows: list[tuple[int, int, str]] = []
    for mid in range(1, 4695):
        if mid == eq1_id:
            continue
        if out.holds(eq1_id, mid) is not True:
            continue
        text = out.equations.get(mid)
        if not text:
            continue
        try:
            law = S.lemma_goal(text)
        except ValueError:
            continue
        size = S.term_size(law["lhs"]) + S.term_size(law["rhs"])
        out_rows.append((size, mid, text))
    out_rows.sort()
    return [(mid, text) for _size, mid, text in out_rows[:limit]]


def build_ladder(eq1: dict, eq2: dict, candidates: list[tuple[int, str]], *,
                 hop_budget: float, max_rungs: int,
                 targets: list[tuple[str, dict, str]]
                 ) -> tuple[str, list[str]] | None:
    """Add graph-verified rungs one at a time, retrying the goal after each."""
    rules = [S._egg_rule_from(eq1, "h")]
    blocks: list[tuple[str, dict, str]] = []
    log: list[str] = []
    used: set = {S.canonical_law_key(eq1)}

    def try_finish() -> tuple[str, list[str]] | None:
        for name, lemma, goal_expr in targets:
            proof = S.egg_saturate_prove_multi(rules, lemma,
                                              time_budget=hop_budget)
            if proof is None:
                continue
            log.append(f"closed via pivot {name} ({len(proof)}B)")
            return S.lemma_chain_certificate(
                blocks, lemma, proof, list(eq2["variables"]), goal_expr), log
        if blocks:
            proof = S.egg_saturate_prove_multi(rules, eq2,
                                              time_budget=hop_budget)
            if proof is not None:
                log.append(f"closed the goal directly ({len(proof)}B)")
                return S._lemma_chain_goal_certificate(
                    blocks, list(eq2["variables"]), proof), log
        return None

    for _round in range(max_rungs + 1):
        done = try_finish()
        if done is not None:
            return done
        added = False
        for mid, text in candidates:
            try:
                law = S.lemma_goal(text)
            except ValueError:
                continue
            key = S.canonical_law_key(law)
            if key in used:
                continue
            proof = S.egg_saturate_prove_multi(
                rules, law, time_budget=hop_budget,
                max_proof_bytes=S.EGG_LADDER_MAX_LAW_BYTES)
            if proof is None:
                continue
            used.add(key)
            hyp = f"hlem{len(blocks)}"
            blocks.append((hyp, law, proof))
            rules.append(S._egg_rule_from(law, hyp))
            log.append(f"rung {hyp} = Eq{mid} {text} ({len(proof)}B)")
            added = True
            break
        if not added:
            log.append("no further graph-verified rung provable")
            return None
    return None


def prove_chain(eq1: dict, eq2: dict, texts: list[str], *,
                hop_budget: float) -> tuple[str, list[str]] | None:
    """Prove each hop from the laws already established, and assemble the
    `lemma_chain` certificate. Every hop is proved by the same
    `egg_saturate_prove_multi` the shipped route uses, so the result is a
    certificate the offline kernel checks block by block."""
    rules = [S._egg_rule_from(eq1, "h")]
    blocks: list[tuple[str, dict, str]] = []
    log: list[str] = []
    for index, text in enumerate(texts):
        law = S.lemma_goal(text)
        started = time.monotonic()
        proof = S.egg_saturate_prove_multi(rules, law, time_budget=hop_budget)
        secs = round(time.monotonic() - started, 1)
        if proof is None:
            log.append(f"hop {index}: FAILED {text} ({secs}s)")
            return None
        log.append(f"hop {index}: ok {text} -> {len(proof)}B ({secs}s)")
        hyp = f"hlem{len(blocks)}"
        blocks.append((hyp, law, proof))
        rules.append(S._egg_rule_from(law, hyp))

    # Last leg: the goal itself, from every law now in scope.
    started = time.monotonic()
    goal_proof = S.egg_saturate_prove_multi(rules, eq2, time_budget=hop_budget)
    secs = round(time.monotonic() - started, 1)
    if goal_proof is None:
        log.append(f"goal: FAILED ({secs}s)")
        return None
    log.append(f"goal: ok -> {len(goal_proof)}B ({secs}s)")
    code = S._lemma_chain_goal_certificate(
        blocks, list(eq2["variables"]), goal_proof)
    return code, log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True)
    ap.add_argument("--max-links", type=int, default=6)
    ap.add_argument("--hop-budget", type=float, default=20.0)
    ap.add_argument("--matrix-only", action="store_true",
                    help="skip ETP's explicit edges and use the outcome matrix")
    ap.add_argument("--mode", choices=("ladder", "chain"), default="ladder",
                    help="ladder: graph-verified consequences of eq1 as rungs "
                         "(the useful mode); chain: walk the eq1 -> eq2 path")
    ap.add_argument("--rung-limit", type=int, default=60)
    ap.add_argument("--effort", default="fast")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    S.set_effort(args.effort)
    out = Outcomes()
    rows = load_rows()
    results = []
    for row_id in [i.strip() for i in args.ids.split(",") if i.strip()]:
        row = rows.get(row_id)
        if row is None:
            print(f"{row_id}: not found")
            continue
        eq1 = S.parse_equation(str(row["equation1"]))
        eq2 = S.parse_equation(str(row["equation2"]))
        a, b = int(row.get("eq1_id", 0)), int(row.get("eq2_id", 0))
        print(f"\n=== {row_id}: Eq{a} => Eq{b}", flush=True)
        print(f"    eq1 {eq1['text']}\n    eq2 {eq2['text']}", flush=True)
        if not (a and b):
            print("    no equation ids; cannot use the matrix")
            continue
        entry: dict = {"id": row_id}
        if args.mode == "ladder":
            candidates = etp_rungs(out, a, limit=args.rung_limit)
            print(f"    {len(candidates)} graph-verified consequences of eq1 "
                  f"(smallest first): "
                  f"{', '.join(f'Eq{m}' for m, _t in candidates[:8])}...",
                  flush=True)
            pivots: list[tuple[str, dict, str]] = []
            for name, text in S.EGG_LADDER_PIVOTS:
                lemma = S.lemma_goal(text)
                expr = S.lemma_closes_goal(lemma, eq2)
                if expr is not None:
                    pivots.append((name, lemma, expr))
            pivots.extend(S.goal_generalization_pivots(eq2))
            built = build_ladder(eq1, eq2, candidates,
                                 hop_budget=args.hop_budget,
                                 max_rungs=args.max_links, targets=pivots)
            entry["mode"] = "ladder"
        else:
            path, source = chain(out, a, b, max_links=args.max_links,
                                 prefer_explicit=not args.matrix_only)
            print(f"    chain ({source}): "
                  f"{' => '.join(f'Eq{n}' for n in path)}", flush=True)
            mids = path[1:-1]
            for mid in mids:
                print(f"      Eq{mid}: {out.equations.get(mid, '?')}", flush=True)
            if not mids:
                print("    no intermediates found", flush=True)
                continue
            texts = [out.equations[m] for m in mids]
            built = prove_chain(eq1, eq2, texts, hop_budget=args.hop_budget)
            entry["chain"] = path
        if built is None:
            print("    chain not provable at this budget", flush=True)
            entry["status"] = "unproved"
        else:
            code, log = built
            for line in log:
                print(f"      {line}", flush=True)
            shape = oracles.classify_true_certificate(code)
            try:
                oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
                oracles.check_no_banned_tactics(code)
                kernel = "ok"
            except oracles.OracleError as exc:
                kernel = f"FAIL: {exc}"
            print(f"    CERTIFICATE {len(code.encode('utf-8'))} bytes, "
                  f"shape {shape}, kernel {kernel}", flush=True)
            entry.update(status="proved", shape=shape, kernel=kernel, code=code,
                         bytes=len(code.encode("utf-8")))
        results.append(entry)
    if args.out:
        args.out.write_text(json.dumps(results, indent=1, ensure_ascii=False),
                            encoding="utf-8")
        print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
