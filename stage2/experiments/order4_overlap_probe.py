#!/usr/bin/env python3
"""Probe direct self-overlap helper laws on frozen order-4 misses.

This is deliberately a solver-internal research driver.  It asks whether the
small critical pairs of the hypothesis, bound as independently checkable helper
lemmas, let the existing multi-law e-graph prove a collapse/pivot or the goal.
It never trusts the campaign label as a proof.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "tests"))

import oracles  # noqa: E402
import solver as S  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def direct_overlap_equations(
    eq1: dict[str, Any], *, deadline: float, max_helpers: int
) -> tuple[S._KBCompletion, list[S._KBEquation]]:
    comp = S._KBCompletion(
        [(eq1["lhs"], eq1["rhs"])],
        deadline=deadline,
        max_size=S.COMPLETION_MAX_SIZE,
        max_active=max(32, max_helpers + 1),
    )
    comp.seed()
    helpers: list[S._KBEquation] = []
    while len(helpers) < max_helpers and not comp.out_of_time():
        equation = comp.step()
        if equation is None:
            break
        helpers.append(equation)
        # Do not superpose derived helpers here: the point of this probe is the
        # bounded direct self-overlap frontier, not another completion pass.
    return comp, helpers


def helper_blocks(
    comp: S._KBCompletion,
    eq1: dict[str, Any],
    helpers: list[S._KBEquation],
) -> list[tuple[str, dict[str, Any], str]] | None:
    renderer = S._KBRenderer(comp, eq1["variables"])
    references = []
    for equation in helpers:
        identity = {
            name: ("var", name)
            for name in renderer.chain_vars(
                equation.lhs, equation.rhs, equation.chain
            )
        }
        references.append(((), equation.eid, identity, 1))
    return renderer.helper_blocks(references)


def try_with_helpers(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    blocks: list[tuple[str, dict[str, Any], str]],
    *,
    target_budget: float,
) -> tuple[str, str] | None:
    rules = [S._egg_rule_from(eq1, "h")]
    rules.extend(S._egg_rule_from(law, name) for name, law, _proof in blocks)

    proof = S.egg_saturate_prove_multi(rules, eq2, time_budget=target_budget)
    if proof is not None:
        code = S._lemma_chain_goal_certificate(blocks, eq2["variables"], proof)
        if len(code.encode("utf-8")) <= S.MAX_LEAN_CODE_BYTES:
            return "goal", code

    for name, text in S.EGG_LADDER_PIVOTS:
        lemma = S.lemma_goal(text)
        goal_expr = S.lemma_closes_goal(lemma, eq2)
        if goal_expr is None or not S.lemma_survives_models(eq1, lemma):
            continue
        proof = S.egg_saturate_prove_multi(
            rules, lemma, time_budget=target_budget
        )
        if proof is None:
            continue
        code = S.lemma_chain_certificate(
            blocks, lemma, proof, eq2["variables"], goal_expr
        )
        if len(code.encode("utf-8")) <= S.MAX_LEAN_CODE_BYTES:
            return name, code
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--eq1-ids", default="")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument(
        "--per-family",
        type=int,
        default=0,
        help="take this many rows per selected eq1 family before --limit",
    )
    parser.add_argument("--helpers", type=int, default=12)
    parser.add_argument("--mine-budget", type=float, default=1.0)
    parser.add_argument("--target-budget", type=float, default=1.0)
    parser.add_argument(
        "--completion-budget",
        type=float,
        default=0.0,
        help="also time completion_prove in isolation (0 disables it)",
    )
    parser.add_argument(
        "--completion-max-size",
        type=int,
        default=0,
        help=(
            "research-only pair-weight cap for one unfailing completion run; "
            "0 uses the solver's promotion ladder"
        ),
    )
    parser.add_argument(
        "--projection-target",
        choices=("left", "right"),
        help="replace each row's goal with the selected projection law",
    )
    parser.add_argument(
        "--target-equation",
        help="replace each row's goal with this research target equation",
    )
    parser.add_argument(
        "--helper-route",
        action="store_true",
        help="also time the source solver's bounded helper-collapse route",
    )
    parser.add_argument(
        "--egg-budget",
        type=float,
        default=0.0,
        help="also run single-rule egg directly on the selected target",
    )
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--code-dir",
        type=Path,
        help="optional research directory for independently checked certificates",
    )
    args = parser.parse_args()

    selected_ids = {
        int(value) for value in args.eq1_ids.split(",") if value.strip()
    }
    rows = read_jsonl(args.rows)
    if selected_ids:
        rows = [row for row in rows if int(row.get("eq1_id", -1)) in selected_ids]
    if args.per_family > 0:
        family_counts: dict[int, int] = {}
        balanced: list[dict[str, Any]] = []
        for row in rows:
            family = int(row.get("eq1_id", -1))
            if family_counts.get(family, 0) >= args.per_family:
                continue
            family_counts[family] = family_counts.get(family, 0) + 1
            balanced.append(row)
        rows = balanced
    rows = rows[: args.limit]

    results: list[dict[str, Any]] = []
    for row in rows:
        S.clear_term_caches()
        eq1 = S.parse_equation(row["equation1"])
        eq2 = S.parse_equation(row["equation2"])
        if args.projection_target == "left":
            eq2 = S.parse_equation("x = x ◇ y")
        elif args.projection_target == "right":
            eq2 = S.parse_equation("x = y ◇ x")
        if args.target_equation:
            eq2 = S.parse_equation(args.target_equation)
        started = time.monotonic()
        comp, helpers = direct_overlap_equations(
            eq1,
            deadline=time.monotonic() + args.mine_budget,
            max_helpers=args.helpers,
        )
        result: dict[str, Any] = {
            "id": row["id"],
            "eq1_id": row.get("eq1_id"),
            "label": row.get("label"),
            "helpers": [
                {
                    "eid": equation.eid,
                    "weight": equation.weight,
                    "law": (
                        f"{S.term_to_lean(equation.lhs)} = "
                        f"{S.term_to_lean(equation.rhs)}"
                    ),
                }
                for equation in helpers
            ],
            "solved": False,
        }
        if args.completion_budget > 0:
            completion_started = time.monotonic()
            if args.completion_max_size > 0:
                completion = S._completion_prove_once(
                    eq1,
                    eq2,
                    deadline=time.monotonic() + args.completion_budget,
                    bridge=True,
                    max_size=args.completion_max_size,
                    max_active=10_000,
                    unfailing=True,
                    norm_push=True,
                    seed_merges=True,
                    evict_passive=True,
                )
            else:
                completion = S.completion_prove(
                    eq1,
                    eq2,
                    time_budget=args.completion_budget,
                    bridge=True,
                    escalate=True,
                )
            result["completion_seconds"] = round(
                time.monotonic() - completion_started, 3
            )
            result["completion_route"] = completion[0] if completion else None
            if completion is not None:
                oracles.check_true_lemma_chain_certificate(
                    completion[1], eq1, eq2
                )
                result["completion_code_bytes"] = len(
                    completion[1].encode("utf-8"))
                if args.code_dir:
                    args.code_dir.mkdir(parents=True, exist_ok=True)
                    (args.code_dir / f"{row['id']}-completion.lean").write_text(
                        completion[1], encoding="utf-8")
        if args.helper_route:
            helper_started = time.monotonic()
            helper_result = S.completion_helper_collapse_route(eq1, eq2)
            result["helper_route_seconds"] = round(
                time.monotonic() - helper_started, 3
            )
            result["helper_route"] = helper_result[0] if helper_result else None
            if helper_result is not None:
                oracles.check_true_lemma_chain_certificate(
                    helper_result[1], eq1, eq2
                )
        if args.egg_budget > 0:
            egg_started = time.monotonic()
            egg_proof = S.egg_saturate_prove(
                eq1, eq2, time_budget=args.egg_budget)
            result["egg_seconds"] = round(time.monotonic() - egg_started, 3)
            result["egg_proved"] = egg_proof is not None
            if egg_proof is not None:
                egg_code = S.submission_certificate(
                    eq2["variables"], f"  exact {egg_proof}\n")
                oracles.check_true_exact_certificate(egg_code, eq1, eq2)
                result["egg_code_bytes"] = len(egg_code.encode("utf-8"))
                if args.code_dir:
                    args.code_dir.mkdir(parents=True, exist_ok=True)
                    (args.code_dir / f"{row['id']}-egg.lean").write_text(
                        egg_code, encoding="utf-8")
        for count in range(1, len(helpers) + 1):
            blocks = helper_blocks(comp, eq1, helpers[:count])
            if blocks is None:
                continue
            found = try_with_helpers(
                eq1, eq2, blocks, target_budget=args.target_budget
            )
            if found is None:
                continue
            route, code = found
            oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
            result.update(
                solved=True,
                route=f"overlap:{route}:h{len(blocks)}",
                helper_prefix=count,
                code_bytes=len(code.encode("utf-8")),
            )
            break
        result["seconds"] = round(time.monotonic() - started, 3)
        results.append(result)
        print(json.dumps(result, ensure_ascii=False), flush=True)

    def row_solved(row: dict[str, object]) -> bool:
        return bool(row["solved"] or row.get("helper_route")
                    or row.get("completion_route"))

    summary = {
        "rows": len(results),
        "solved": sum(row_solved(row) for row in results),
        "helper_route_solved": sum(bool(row.get("helper_route"))
                                   for row in results),
        "by_family": {},
    }
    for eq1_id in sorted({int(row["eq1_id"]) for row in results}):
        family = [row for row in results if int(row["eq1_id"]) == eq1_id]
        summary["by_family"][str(eq1_id)] = {
            "rows": len(family),
            "solved": sum(row_solved(row) for row in family),
            "helper_route_solved": sum(bool(row.get("helper_route"))
                                       for row in family),
        }
    print(json.dumps({"summary": summary}, indent=2), flush=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps({"summary": summary, "rows": results},
                       ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
