#!/usr/bin/env python3
"""
distill.py — Agentic distillation engine for cheatsheet mutation feedback.

Processes evaluation failures from run manifests into a structured error
taxonomy and ranked pattern library.  Produces three artifacts per cycle:

    {out_dir}/{cycle:04d}_error_taxonomy.json    — per-failure annotations + aggregates
    {out_dir}/{cycle:04d}_pattern_library.json   — ranked pattern clusters
    {out_dir}/{cycle:04d}_distillation_brief.md  — compact markdown brief for prompt injection

Usage (standalone):
    python distill.py --manifest results/vnext_search_v2/champions/current.json
                      --out-dir results/vnext_search_v2/distilled_signals
                      --cycle 6

Usage (programmatic — called from vnext_search_v2.py):
    import distill
    artifacts = distill.run_distillation(manifest=manifest, cycle_number=6,
                                         out_dir=Path("results/vnext_search_v2/distilled_signals"))
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Equation parsing utilities
# ---------------------------------------------------------------------------

def _var_tokens(expr: str) -> list[str]:
    """Return ordered list of single-letter variable tokens from an expression."""
    return re.findall(r'\b([a-z])\b', expr)


def leftmost_leaf(expr: str) -> Optional[str]:
    tokens = _var_tokens(expr)
    return tokens[0] if tokens else None


def rightmost_leaf(expr: str) -> Optional[str]:
    tokens = _var_tokens(expr)
    return tokens[-1] if tokens else None


def split_equation(eq: str) -> tuple[str, str]:
    """Split 'LHS = RHS' on first ' = ', return (lhs, rhs)."""
    parts = eq.split(' = ', 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return eq.strip(), ""


def equation_vars(eq: str) -> set[str]:
    return set(_var_tokens(eq))


def _find_matching(expr: str, start: int) -> int:
    depth = 0
    for index in range(start, len(expr)):
        char = expr[index]
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0:
                return index
    return -1


def _parse_expr(expr: str):
    expr = expr.strip()
    if expr.startswith('(') and _find_matching(expr, 0) == len(expr) - 1:
        expr = expr[1:-1].strip()
    depth = 0
    last_star = -1
    for index, char in enumerate(expr):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif char == '*' and depth == 0:
            last_star = index
    if last_star >= 0:
        left = expr[:last_star].strip()
        right = expr[last_star + 1:].strip()
        return ('*', _parse_expr(left), _parse_expr(right))
    return ('var', expr)


def parse_equation_tree(eq: str):
    normalized = eq.replace('\u25c7', '*').strip()
    lhs, rhs = split_equation(normalized)
    return _parse_expr(lhs), _parse_expr(rhs)


def _collect_tree_vars(tree, variables: set[str]) -> None:
    if tree[0] == 'var':
        variables.add(tree[1])
        return
    _collect_tree_vars(tree[1], variables)
    _collect_tree_vars(tree[2], variables)


def eval_tree(tree, assignment: dict[str, int], table: list[list[int]]) -> int:
    if tree[0] == 'var':
        return assignment[tree[1]]
    left = eval_tree(tree[1], assignment, table)
    right = eval_tree(tree[2], assignment, table)
    return table[left][right]


def check_equation(eq: str, table: list[list[int]]) -> bool:
    lhs, rhs = parse_equation_tree(eq)
    variables: set[str] = set()
    _collect_tree_vars(lhs, variables)
    _collect_tree_vars(rhs, variables)
    ordered = sorted(variables)
    for values in itertools.product(range(len(table)), repeat=len(ordered)):
        assignment = dict(zip(ordered, values))
        if eval_tree(lhs, assignment, table) != eval_tree(rhs, assignment, table):
            return False
    return True


def first_failing_assignment(eq: str, table: list[list[int]]) -> Optional[dict]:
    lhs, rhs = parse_equation_tree(eq)
    variables: set[str] = set()
    _collect_tree_vars(lhs, variables)
    _collect_tree_vars(rhs, variables)
    ordered = sorted(variables)
    for values in itertools.product(range(len(table)), repeat=len(ordered)):
        assignment = dict(zip(ordered, values))
        lhs_value = eval_tree(lhs, assignment, table)
        rhs_value = eval_tree(rhs, assignment, table)
        if lhs_value != rhs_value:
            return {
                "assignment": assignment,
                "lhs_value": lhs_value,
                "rhs_value": rhs_value,
            }
    return None


WITNESS_LIBRARY: list[dict] = [
    {"name": "LP", "rule": "x*y = x", "table": [[0, 0], [1, 1]]},
    {"name": "RP", "rule": "x*y = y", "table": [[0, 1], [0, 1]]},
    {"name": "C0", "rule": "x*y = 0", "table": [[0, 0], [0, 0]]},
    {"name": "XOR", "rule": "x*y = (x+y) mod 2", "table": [[0, 1], [1, 0]]},
    {"name": "Z3A", "rule": "x*y = (x+y) mod 3", "table": [[0, 1, 2], [1, 2, 0], [2, 0, 1]]},
    {"name": "AND", "rule": "x*y = x AND y", "table": [[0, 0], [0, 1]]},
    {"name": "OR", "rule": "x*y = x OR y", "table": [[0, 1], [1, 1]]},
    {"name": "XNOR", "rule": "x*y = 1 iff x=y else 0", "table": [[1, 0], [0, 1]]},
]


def find_verified_witnesses(eq1: str, eq2: str) -> list[dict]:
    verified: list[dict] = []
    for witness in WITNESS_LIBRARY:
        table = witness["table"]
        if not check_equation(eq1, table):
            continue
        failure = first_failing_assignment(eq2, table)
        if failure is None:
            continue
        verified.append(
            {
                "name": witness["name"],
                "rule": witness["rule"],
                "assignment": failure["assignment"],
                "lhs_value": failure["lhs_value"],
                "rhs_value": failure["rhs_value"],
            }
        )
    return verified


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

def extract_pair_features(eq1: str, eq2: str) -> dict:
    """Extract structural invariants for one (E1, E2) implication pair."""
    lhs1, rhs1 = split_equation(eq1)
    lhs2, rhs2 = split_equation(eq2)

    ll_lhs1 = leftmost_leaf(lhs1)
    ll_rhs1 = leftmost_leaf(rhs1)
    ll_lhs2 = leftmost_leaf(lhs2)
    ll_rhs2 = leftmost_leaf(rhs2)

    rl_lhs1 = rightmost_leaf(lhs1)
    rl_rhs1 = rightmost_leaf(rhs1)
    rl_lhs2 = rightmost_leaf(lhs2)
    rl_rhs2 = rightmost_leaf(rhs2)

    vars1 = equation_vars(eq1)
    vars2 = equation_vars(eq2)
    new_vars_in_e2 = vars2 - vars1

    # LP obstruction: LP satisfies E1 AND LP does not satisfy E2
    lp_satisfies_e1 = (ll_lhs1 is not None) and (ll_lhs1 == ll_rhs1)
    lp_satisfies_e2 = (ll_lhs2 is not None) and (ll_lhs2 == ll_rhs2)
    lp_obstruction = lp_satisfies_e1 and not lp_satisfies_e2

    # RP obstruction: RP satisfies E1 AND RP does not satisfy E2
    rp_satisfies_e1 = (rl_lhs1 is not None) and (rl_lhs1 == rl_rhs1)
    rp_satisfies_e2 = (rl_lhs2 is not None) and (rl_lhs2 == rl_rhs2)
    rp_obstruction = rp_satisfies_e1 and not rp_satisfies_e2

    # Multiplicity-based signals
    e1_vars = _var_tokens(eq1)
    e2_vars = _var_tokens(eq2)
    e1_var_mult = {v: e1_vars.count(v) for v in set(e1_vars)}
    e2_var_mult = {v: e2_vars.count(v) for v in set(e2_vars)}

    return {
        "ll_lhs1": ll_lhs1, "ll_rhs1": ll_rhs1,
        "ll_lhs2": ll_lhs2, "ll_rhs2": ll_rhs2,
        "rl_lhs1": rl_lhs1, "rl_rhs1": rl_rhs1,
        "rl_lhs2": rl_lhs2, "rl_rhs2": rl_rhs2,
        "vars_e1": sorted(vars1),
        "vars_e2": sorted(vars2),
        "new_vars_in_e2": sorted(new_vars_in_e2),
        "lp_satisfies_e1": lp_satisfies_e1,
        "lp_satisfies_e2": lp_satisfies_e2,
        "lp_obstruction": lp_obstruction,
        "rp_satisfies_e1": rp_satisfies_e1,
        "rp_satisfies_e2": rp_satisfies_e2,
        "rp_obstruction": rp_obstruction,
        "e1_var_multiplicity": e1_var_mult,
        "e2_var_multiplicity": e2_var_mult,
    }


# ---------------------------------------------------------------------------
# Error classification
# ---------------------------------------------------------------------------

PATTERN_LABELS: dict[str, str] = {
    "fp_lp_obstruction_missed":   "FP: LP obstruction was applicable but missed",
    "fp_rp_obstruction_missed":   "FP: RP obstruction was applicable but missed",
    "fp_both_projections_missed": "FP: Both LP and RP obstructions applicable, both missed",
    "fp_new_variable_trap":       "FP: E2 introduces variables absent from E1 (strong FALSE signal)",
    "fn_no_projection_handle":    "FN: No LP/RP obstruction available; TRUE proof missed",
    "fn_projection_both_hold":    "FN: Both LP+RP satisfy E1 and E2 — model could not use them to prove",
    "generic_fp":                 "FP: No detected structural pattern",
    "generic_fn":                 "FN: No detected structural pattern",
}


def classify_failure(failure: dict) -> tuple[str, list[str]]:
    """
    Classify a single wrong-answer entry.

    Returns:
        (error_class, [pattern_label, ...])
    """
    ground_truth = failure.get("ground_truth")
    predicted = failure.get("predicted")
    eq1 = failure.get("equation1") or failure.get("eq1") or ""
    eq2 = failure.get("equation2") or failure.get("eq2") or ""

    if predicted is None:
        return "parse_fail", []

    if ground_truth is False and predicted is True:
        error_class = "false_positive"
    elif ground_truth is True and predicted is False:
        error_class = "false_negative"
    else:
        return "unknown", []

    patterns: list[str] = []
    if not eq1 or not eq2:
        return error_class, patterns

    feat = extract_pair_features(eq1, eq2)

    if error_class == "false_positive":
        if feat["lp_obstruction"] and feat["rp_obstruction"]:
            patterns.append("fp_both_projections_missed")
        elif feat["lp_obstruction"]:
            patterns.append("fp_lp_obstruction_missed")
        elif feat["rp_obstruction"]:
            patterns.append("fp_rp_obstruction_missed")
        if feat["new_vars_in_e2"]:
            patterns.append("fp_new_variable_trap")
        if not patterns:
            patterns.append("generic_fp")

    elif error_class == "false_negative":
        if (feat["lp_satisfies_e1"] and feat["lp_satisfies_e2"]
                and feat["rp_satisfies_e1"] and feat["rp_satisfies_e2"]):
            patterns.append("fn_projection_both_hold")
        elif not feat["lp_obstruction"] and not feat["rp_obstruction"]:
            patterns.append("fn_no_projection_handle")
        if not patterns:
            patterns.append("generic_fn")

    return error_class, patterns


def annotate_failure(failure: dict) -> dict:
    """Add error_class, patterns, and features to a failure dict."""
    eq1 = failure.get("equation1") or failure.get("eq1") or ""
    eq2 = failure.get("equation2") or failure.get("eq2") or ""
    features = extract_pair_features(eq1, eq2) if (eq1 and eq2) else {}
    error_class, patterns = classify_failure(failure)
    verified_witnesses = []
    if eq1 and eq2 and error_class == "false_positive":
        verified_witnesses = find_verified_witnesses(eq1, eq2)
    return {
        **failure,
        "error_class": error_class,
        "patterns": patterns,
        "features": features,
        "verified_witnesses": verified_witnesses,
    }


# ---------------------------------------------------------------------------
# Taxonomy and pattern library aggregation
# ---------------------------------------------------------------------------

def build_error_taxonomy(annotated_failures: list[dict]) -> dict:
    """
    Aggregate annotated failures into a structured taxonomy.

    Returns:
        {
          "total_failures": int,
          "by_class": {"false_positive": {"count": int, "examples": [...]}, ...},
          "by_pattern": {pattern_label: {"count": int, "description": str, "examples": [...]}},
        }
    """
    by_class: dict[str, list] = defaultdict(list)
    by_pattern: dict[str, list] = defaultdict(list)

    for f in annotated_failures:
        by_class[f.get("error_class", "unknown")].append(f)
        for pat in f.get("patterns", []):
            by_pattern[pat].append(f)

    def compact(f: dict) -> dict:
        return {
            "id": f.get("id"),
            "ground_truth": f.get("ground_truth"),
            "predicted": f.get("predicted"),
            "equation1": f.get("equation1"),
            "equation2": f.get("equation2"),
            "features": f.get("features", {}),
            "verified_witnesses": f.get("verified_witnesses", [])[:3],
        }

    return {
        "total_failures": len(annotated_failures),
        "by_class": {
            cls: {"count": len(items), "examples": [compact(f) for f in items[:5]]}
            for cls, items in by_class.items()
        },
        "by_pattern": {
            pat: {
                "count": len(items),
                "description": PATTERN_LABELS.get(pat, pat),
                "examples": [compact(f) for f in items[:3]],
            }
            for pat, items in sorted(by_pattern.items(), key=lambda kv: -len(kv[1]))
        },
    }


def build_pattern_library(taxonomy: dict) -> dict:
    """
    Flatten taxonomy into a ranked pattern library for mutation guidance.

    Returns:
        {"ranked_patterns": [{"rank": int, "pattern": str, "count": int,
                               "description": str, "examples": [...]}, ...]}
    """
    ranked = [
        {
            "rank": rank,
            "pattern": pat,
            "count": info["count"],
            "description": info["description"],
            "examples": info.get("examples", [])[:2],
        }
        for rank, (pat, info) in enumerate(taxonomy["by_pattern"].items(), start=1)
    ]
    return {"ranked_patterns": ranked}


def build_witness_library(annotated_failures: list[dict]) -> dict:
    ranked_witnesses: dict[str, list[dict]] = defaultdict(list)

    for failure in annotated_failures:
        if failure.get("error_class") != "false_positive":
            continue
        for witness in failure.get("verified_witnesses", []):
            ranked_witnesses[witness["name"]].append(
                {
                    "id": failure.get("id"),
                    "equation1": failure.get("equation1"),
                    "equation2": failure.get("equation2"),
                    "rule": witness["rule"],
                    "assignment": witness["assignment"],
                    "lhs_value": witness["lhs_value"],
                    "rhs_value": witness["rhs_value"],
                }
            )

    ranked = []
    for rank, (name, examples) in enumerate(sorted(ranked_witnesses.items(), key=lambda kv: (-len(kv[1]), kv[0])), start=1):
        ranked.append(
            {
                "rank": rank,
                "witness": name,
                "count": len(examples),
                "rule": examples[0]["rule"],
                "examples": examples[:3],
            }
        )
    return {"ranked_witnesses": ranked}


# ---------------------------------------------------------------------------
# Distillation brief (compact markdown for prompt injection)
# ---------------------------------------------------------------------------

def render_distillation_brief(taxonomy: dict, pattern_library: dict, cycle_number: int) -> str:
    """
    Produce a compact markdown brief for injection into invoke_copilot_candidate prompt.
    Kept intentionally short so it fits in the prompt budget context.
    """
    top = pattern_library["ranked_patterns"][:5]
    by_class = taxonomy.get("by_class", {})
    fp_count = by_class.get("false_positive", {}).get("count", 0)
    fn_count = by_class.get("false_negative", {}).get("count", 0)

    lines = [
        f"=== DISTILLATION BRIEF (cycle {cycle_number}) ===",
        f"Total failures: {taxonomy['total_failures']}  |  FP={fp_count}  FN={fn_count}",
        "",
        "Top failure patterns (most frequent first):",
    ]
    for p in top:
        lines.append(f"  [{p['rank']}] {p['pattern']} (n={p['count']})")
        lines.append(f"      {p['description']}")
        for ex in p.get("examples", [])[:1]:
            lines.append(f"      E1: {ex.get('equation1','?')}")
            lines.append(f"      E2: {ex.get('equation2','?')}")
    lines += [
        "",
        "Edit priority: address the top-ranked pattern first.",
        "=== END DISTILLATION BRIEF ===",
    ]
    return "\n".join(lines)


def render_witness_brief(witness_library: dict, cycle_number: int) -> str:
    ranked = witness_library.get("ranked_witnesses", [])[:5]
    lines = [
        f"=== VERIFIED WITNESS BRIEF (cycle {cycle_number}) ===",
        "Use these as external generation cues, not as unconditional rules.",
        "Prefer witnesses that were actually verified on recent false positives.",
        "",
    ]
    if not ranked:
        lines.append("No verified witness separations were found in the current failure set.")
    for item in ranked:
        lines.append(f"[{item['rank']}] {item['witness']} (n={item['count']}) :: {item['rule']}")
        for example in item.get("examples", [])[:1]:
            assignment = ", ".join(f"{key}={value}" for key, value in sorted(example["assignment"].items()))
            lines.append(f"    E1: {example['equation1']}")
            lines.append(f"    E2: {example['equation2']}")
            lines.append(
                f"    verified fail on {example['id']}: assignment {assignment} gives LHS={example['lhs_value']} RHS={example['rhs_value']}"
            )
    lines += ["", "=== END VERIFIED WITNESS BRIEF ==="]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# High-level runner
# ---------------------------------------------------------------------------

def collect_all_failures(manifest: dict) -> list[dict]:
    """Extract all failure entries from a champion or candidate manifest."""
    all_failures = []
    for gate in manifest.get("gate_runs", []):
        for failure in gate.get("failures", []):
            all_failures.append({**failure, "benchmark": gate.get("benchmark")})
    return all_failures


def collect_failures_from_result_file(result_payload: dict) -> list[dict]:
    failures: list[dict] = []
    for result in result_payload.get("results", []):
        if result.get("correct"):
            continue
        failures.append(
            {
                "id": result.get("id"),
                "ground_truth": result.get("ground_truth"),
                "predicted": result.get("predicted"),
                "equation1": result.get("equation1"),
                "equation2": result.get("equation2"),
                "benchmark": result_payload.get("benchmark") or result_payload.get("subset"),
            }
        )
    return failures


def run_distillation_from_failures(failures: list[dict], cycle_number: int, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"{cycle_number:04d}"

    annotated = [annotate_failure(f) for f in failures]
    taxonomy = build_error_taxonomy(annotated)
    pattern_library = build_pattern_library(taxonomy)
    witness_library = build_witness_library(annotated)
    brief = render_distillation_brief(taxonomy, pattern_library, cycle_number)
    witness_brief = render_witness_brief(witness_library, cycle_number)

    tax_path = out_dir / f"{prefix}_error_taxonomy.json"
    lib_path = out_dir / f"{prefix}_pattern_library.json"
    brief_path = out_dir / f"{prefix}_distillation_brief.md"
    witness_lib_path = out_dir / f"{prefix}_witness_library.json"
    witness_brief_path = out_dir / f"{prefix}_witness_brief.md"

    tax_path.write_text(json.dumps(taxonomy, indent=2), encoding="utf-8")
    lib_path.write_text(json.dumps(pattern_library, indent=2), encoding="utf-8")
    brief_path.write_text(brief, encoding="utf-8")
    witness_lib_path.write_text(json.dumps(witness_library, indent=2), encoding="utf-8")
    witness_brief_path.write_text(witness_brief, encoding="utf-8")

    print(f"  distill: {tax_path.name} ({tax_path.stat().st_size} B)")
    print(f"  distill: {lib_path.name} ({lib_path.stat().st_size} B)")
    print(f"  distill: {brief_path.name} ({brief_path.stat().st_size} B)")
    print(f"  distill: {witness_lib_path.name} ({witness_lib_path.stat().st_size} B)")
    print(f"  distill: {witness_brief_path.name} ({witness_brief_path.stat().st_size} B)")

    top_pattern = (
        pattern_library["ranked_patterns"][0]["pattern"]
        if pattern_library["ranked_patterns"] else None
    )
    top_witness = (
        witness_library["ranked_witnesses"][0]["witness"]
        if witness_library["ranked_witnesses"] else None
    )
    return {
        "error_taxonomy_path": str(tax_path),
        "pattern_library_path": str(lib_path),
        "distillation_brief_path": str(brief_path),
        "witness_library_path": str(witness_lib_path),
        "witness_brief_path": str(witness_brief_path),
        "total_failures": taxonomy["total_failures"],
        "fp_count": taxonomy["by_class"].get("false_positive", {}).get("count", 0),
        "fn_count": taxonomy["by_class"].get("false_negative", {}).get("count", 0),
        "top_pattern": top_pattern,
        "top_witness": top_witness,
    }


def run_distillation(manifest: dict, cycle_number: int, out_dir: Path) -> dict:
    """
    Run the full distillation pipeline on a manifest.

    Writes:
        {out_dir}/{cycle_number:04d}_error_taxonomy.json
        {out_dir}/{cycle_number:04d}_pattern_library.json
        {out_dir}/{cycle_number:04d}_distillation_brief.md

    Returns a dict of paths and summary stats.
    """
    failures = collect_all_failures(manifest)
    return run_distillation_from_failures(failures, cycle_number, out_dir)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Distillation engine for cheatsheet mutation feedback."
    )
    parser.add_argument(
        "--manifest",
        help="Path to champion or candidate manifest JSON (for vnext_search_v2)"
    )
    parser.add_argument(
        "--result-file",
        help="Optional raw simulator result JSON to distill directly outside vnext_search_v2"
    )
    parser.add_argument(
        "--out-dir", default="results/vnext_search_v2/distilled_signals",
        help="Output directory for artifacts"
    )
    parser.add_argument(
        "--cycle", type=int, default=0,
        help="Cycle number used as artifact filename prefix"
    )
    args = parser.parse_args()

    if not args.manifest and not args.result_file:
        parser.error("one of --manifest or --result-file is required")

    if args.result_file:
        payload = json.loads(Path(args.result_file).read_text(encoding="utf-8"))
        artifacts = run_distillation_from_failures(
            failures=collect_failures_from_result_file(payload),
            cycle_number=args.cycle,
            out_dir=Path(args.out_dir),
        )
    else:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        artifacts = run_distillation(
            manifest=manifest,
            cycle_number=args.cycle,
            out_dir=Path(args.out_dir),
        )
    print(json.dumps(artifacts, indent=2))


if __name__ == "__main__":
    main()
