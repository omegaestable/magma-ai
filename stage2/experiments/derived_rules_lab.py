#!/usr/bin/env python3
"""Deterministic critical-pair (Knuth-Bendix-lite) lab for the TRUE frontier.

Idea: the deterministic-skip TRUE rows need "smart hypothesis instantiation"
(2026-07-20 finding). Critical pairs of the hypothesis with itself produce
derived equations that PACKAGE two exact instantiations into one reusable
rewrite rule, each with a constructive Lean proof expression. Running the
bidirectional closure over {base rule} + derived rules searches derivations
the base closure cannot reach at the same depth.

Every found proof is rendered to the solver's substitution_true_certificate
shape and verified with the local Lean judge before being counted.

Dev-only measurement tool; promotion into solver.py happens separately.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from itertools import product
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
OFFICIAL = REPO / "vendor" / "stage2-official"
SOLVER_DIR = REPO / "stage2" / "solver"
sys.path.insert(0, str(OFFICIAL))
sys.path.insert(0, str(SOLVER_DIR))

import solver as S  # noqa: E402

Term = tuple

# --------------------------------------------------------------------------
# Unification (terms are ("var", name) | ("op", l, r))
# --------------------------------------------------------------------------

def walk(term: Term, subst: dict[str, Term]) -> Term:
    while term[0] == "var" and term[1] in subst:
        term = subst[term[1]]
    return term


def occurs(name: str, term: Term, subst: dict[str, Term]) -> bool:
    term = walk(term, subst)
    if term[0] == "var":
        return term[1] == name
    return occurs(name, term[1], subst) or occurs(name, term[2], subst)


def unify(a: Term, b: Term, subst: dict[str, Term]) -> dict[str, Term] | None:
    a = walk(a, subst)
    b = walk(b, subst)
    if a == b:
        return subst
    if a[0] == "var":
        if occurs(a[1], b, subst):
            return None
        out = dict(subst)
        out[a[1]] = b
        return out
    if b[0] == "var":
        if occurs(b[1], a, subst):
            return None
        out = dict(subst)
        out[b[1]] = a
        return out
    out = unify(a[1], b[1], subst)
    if out is None:
        return None
    return unify(a[2], b[2], out)


def resolve(term: Term, subst: dict[str, Term]) -> Term:
    term = walk(term, subst)
    if term[0] == "var":
        return term
    return ("op", resolve(term[1], subst), resolve(term[2], subst))


def rename_term(term: Term, suffix: str) -> Term:
    if term[0] == "var":
        return ("var", term[1] + suffix)
    return ("op", rename_term(term[1], suffix), rename_term(term[2], suffix))


def term_vars(term: Term) -> set[str]:
    if term[0] == "var":
        return {term[1]}
    return term_vars(term[1]) | term_vars(term[2])


# --------------------------------------------------------------------------
# Rules
#
# A rule proves  lhs = rhs  (patterns over rule_vars). Its `prove(concrete)`
# builds a Lean proof expression once every rule_var is bound to a concrete
# term (over the goal's variables).
#
# Base rule proof:      h a b c...            (eq1 instance)
# Derived rule proof:   (step1).trans (congrArg ctx step2)  built from two
#                       eq1 instances as recorded at critical-pair time.
# --------------------------------------------------------------------------

class Rule:
    __slots__ = ("lhs", "rhs", "vars", "proof_only_vars", "builder", "label")

    def __init__(self, lhs: Term, rhs: Term, builder, label: str,
                 extra_vars: set[str] | None = None):
        self.lhs = lhs
        self.rhs = rhs
        pattern_vars = term_vars(lhs) | term_vars(rhs)
        # Vars only in the proof templates: any value is sound (the h-instance
        # proves the pattern equation for every value), so they take a default
        # fill and never join the fill product.
        self.proof_only_vars = sorted((extra_vars or set()) - pattern_vars)
        self.vars = sorted(pattern_vars)
        self.builder = builder
        self.label = label


def base_rules(eq1: dict[str, Any]) -> list[Rule]:
    ev = list(eq1["variables"])

    def fwd(subst: dict[str, Term]) -> str:
        return S.call_expression(ev, subst)

    def bwd(subst: dict[str, Term]) -> str:
        return f"({S.call_expression(ev, subst)}).symm"

    return [
        Rule(eq1["lhs"], eq1["rhs"], fwd, "base_fwd"),
        Rule(eq1["rhs"], eq1["lhs"], bwd, "base_bwd"),
    ]


def canonicalize_rule(lhs: Term, rhs: Term) -> tuple[Term, Term, dict[str, str]]:
    mapping: dict[str, str] = {}

    def canon(term: Term) -> Term:
        if term[0] == "var":
            if term[1] not in mapping:
                mapping[term[1]] = f"v{len(mapping)}"
            return ("var", mapping[term[1]])
        return ("op", canon(term[1]), canon(term[2]))

    return canon(lhs), canon(rhs), mapping


def nonvar_paths(term: Term, prefix: tuple[int, ...] = ()) -> list[tuple[int, ...]]:
    if term[0] != "op":
        return []
    out = [prefix]
    out.extend(nonvar_paths(term[1], prefix + (0,)))
    out.extend(nonvar_paths(term[2], prefix + (1,)))
    return out


def critical_pair_rules(
    eq1: dict[str, Any],
    *,
    max_rule_size: int = 15,
    max_rules: int = 48,
) -> list[Rule]:
    """Depth-1 critical pairs of eq1 with itself, with constructive proofs."""
    ev = list(eq1["variables"])
    L1 = rename_term(eq1["lhs"], "@1")
    R1 = rename_term(eq1["rhs"], "@1")
    L2 = rename_term(eq1["lhs"], "@2")
    R2 = rename_term(eq1["rhs"], "@2")

    rules: list[Rule] = []
    seen: set[tuple[Term, Term]] = set()

    # orientation of copy k: which side we match/expand FROM
    for s1, t1, s1_is_L in ((L1, R1, True), (R1, L1, False)):
        for s2, t2, s2_is_L in ((L2, R2, True), (R2, L2, False)):
            for p in nonvar_paths(s2):
                sub = S.term_at_path(s2, p)
                sigma = unify(s1, sub, {})
                if sigma is None:
                    continue
                new_lhs = resolve(t2, sigma)
                inner_repl = resolve(t1, sigma)
                expanded = resolve(s2, sigma)
                new_rhs = S.replace_subterm(expanded, p, inner_repl)
                if new_lhs == new_rhs:
                    continue
                if max(S.term_size(new_lhs), S.term_size(new_rhs)) > max_rule_size:
                    continue
                canon_l, canon_r, mapping = canonicalize_rule(new_lhs, new_rhs)
                if (canon_l, canon_r) in seen:
                    continue
                seen.add((canon_l, canon_r))

                def remap(term: Term) -> Term:
                    # Vars that vanished from the rule patterns still occur in
                    # the instantiation templates; extend the mapping so they
                    # become rule vars and receive default fills at use time.
                    if term[0] == "var":
                        if term[1] not in mapping:
                            mapping[term[1]] = f"v{len(mapping)}"
                        return ("var", mapping[term[1]])
                    return ("op", remap(term[1]), remap(term[2]))

                # per-eq1-var instantiation patterns (over canonical rule vars)
                tau2 = {v: remap(resolve(("var", v + "@2"), sigma)) for v in ev}
                tau1 = {v: remap(resolve(("var", v + "@1"), sigma)) for v in ev}
                expanded_pat = remap(expanded)

                def make_builder(tau1=tau1, tau2=tau2, expanded_pat=expanded_pat,
                                 p=p, s1_is_L=s1_is_L, s2_is_L=s2_is_L):
                    def build(subst: dict[str, Term]) -> str:
                        # subst binds canonical rule vars -> concrete terms
                        c2 = {v: S.instantiate_term(t, subst) for v, t in tau2.items()}
                        c1 = {v: S.instantiate_term(t, subst) for v, t in tau1.items()}
                        whole = S.instantiate_term(expanded_pat, subst)
                        call2 = S.call_expression(ev, c2)
                        step1 = f"({call2}).symm" if s2_is_L else call2
                        call1 = S.call_expression(ev, c1)
                        inner = call1 if s1_is_L else f"({call1}).symm"
                        if p:
                            ctx = S.context_to_lean(whole, p, "t")
                            step2 = f"congrArg (fun t => {ctx}) ({inner})"
                        else:
                            step2 = inner
                        return f"({step1}).trans ({step2})"
                    return build

                label = f"cp:{'L' if s1_is_L else 'R'}{'L' if s2_is_L else 'R'}:{'.'.join(map(str, p)) or 'root'}"
                all_vars = set()
                for t in list(tau1.values()) + list(tau2.values()):
                    all_vars |= term_vars(t)
                rules.append(Rule(canon_l, canon_r, make_builder(), label, extra_vars=all_vars))
                # both orientations of the derived rule
                fwd_rule = rules[-1]

                def make_rev(fwd_rule=fwd_rule):
                    def build(subst: dict[str, Term]) -> str:
                        return f"({fwd_rule.builder(subst)}).symm"
                    return build

                rules.append(Rule(canon_r, canon_l, make_rev(), label + ":rev", extra_vars=all_vars))

    rules.sort(key=lambda r: (S.term_size(r.lhs) + S.term_size(r.rhs), r.label))
    return rules[:max_rules]


# --------------------------------------------------------------------------
# Rule-set closure (mirrors solver's bidirectional closure, generalized)
# --------------------------------------------------------------------------

def rule_steps(
    rules: list[Rule],
    term: Term,
    pool: list[Term],
    fill_pool: list[Term],
    *,
    max_size: int,
    max_depth: int,
    max_fills: int,
    deadline: float | None,
) -> list[tuple[Term, str]]:
    steps: list[tuple[Term, str]] = []
    seen: set[Term] = set()
    default_term = pool[0]
    for path in S.subterm_paths(term):
        if deadline is not None and time.monotonic() >= deadline:
            break
        sub = S.term_at_path(term, path)
        for rule in rules:
            subst: dict[str, Term] = {}
            if not S.match_term(rule.lhs, sub, subst):
                continue
            needed = [v for v in rule.vars if v not in subst]
            if len(needed) > 3:
                continue
            fills_src = fill_pool if len(needed) > 1 else pool
            fill_iter = product(fills_src, repeat=len(needed)) if needed else ((),)
            count = 0
            for fills in fill_iter:
                count += 1
                if count > max_fills:
                    break
                full = dict(subst)
                for v, val in zip(needed, fills):
                    full[v] = val
                for v in rule.proof_only_vars:
                    full[v] = default_term
                replacement = S.instantiate_term(rule.rhs, full)
                new_term = S.replace_subterm(term, path, replacement)
                if new_term == term or new_term in seen:
                    continue
                if S.term_size(new_term) > max_size or S.term_depth(new_term) > max_depth:
                    continue
                proof = rule.builder(full)
                if path:
                    ctx = S.context_to_lean(term, path, "t")
                    proof = f"congrArg (fun t => {ctx}) ({proof})"
                seen.add(new_term)
                steps.append((new_term, proof))
    steps.sort(key=lambda item: (S.term_size(item[0]), S.term_depth(item[0])))
    return steps


def derived_closure_proof(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    max_depth: int = 4,
    pool_limit: int = 16,
    fill_pool_cap: int = 10,
    frontier_limit: int = 2600,
    max_fills: int = 1200,
    term_slack: int = 10,
    depth_slack: int = 3,
    time_budget: float = 8.0,
    max_rules: int = 48,
) -> str | None:
    deadline = time.monotonic() + time_budget
    rules = base_rules(eq1) + critical_pair_rules(eq1, max_rules=max_rules)
    pool = S.absorption_term_pool(eq1, eq2, pool_limit=pool_limit)
    if not pool:
        return None
    fill_pool = pool[:fill_pool_cap]

    max_size = max(S.term_size(eq1["lhs"]), S.term_size(eq1["rhs"]),
                   S.term_size(eq2["lhs"]), S.term_size(eq2["rhs"])) + term_slack
    max_depth_t = max(S.term_depth(eq1["lhs"]), S.term_depth(eq1["rhs"]),
                      S.term_depth(eq2["lhs"]), S.term_depth(eq2["rhs"])) + depth_slack

    left_seen: dict[Term, str | None] = {eq2["lhs"]: None}
    right_seen: dict[Term, str | None] = {eq2["rhs"]: None}
    left_frontier = [eq2["lhs"]]
    right_frontier = [eq2["rhs"]]

    def expand(frontier, seen, other, from_left):
        nxt = []
        for term in frontier:
            if time.monotonic() >= deadline:
                return nxt, None, True
            prefix = seen[term]
            for new_term, proof in rule_steps(
                rules, term, pool, fill_pool,
                max_size=max_size, max_depth=max_depth_t,
                max_fills=max_fills, deadline=deadline,
            ):
                if new_term in seen:
                    continue
                new_proof = S.chain_trans(prefix, proof)
                if new_term in other:
                    if from_left:
                        return nxt, S.combine_meeting_proofs(new_proof, other[new_term]), False
                    return nxt, S.combine_meeting_proofs(other[new_term], new_proof), False
                seen[new_term] = new_proof
                nxt.append(new_term)
                if len(seen) >= frontier_limit:
                    break
            if len(seen) >= frontier_limit:
                break
        return nxt[:frontier_limit], None, False

    for _ in range(max_depth):
        if time.monotonic() >= deadline:
            return None
        left_frontier, result, timed_out = expand(left_frontier, left_seen, right_seen, True)
        if timed_out or result is not None:
            return result
        right_frontier, result, timed_out = expand(right_frontier, right_seen, left_seen, False)
        if timed_out or result is not None:
            return result
        if not left_frontier and not right_frontier:
            return None
    return None


# --------------------------------------------------------------------------
# Frontier measurement with local judge verification
# --------------------------------------------------------------------------

DEFAULT_PROOF_POLICY = {
    "allowed_axioms": ["propext", "Quot.sound", "Classical.choice"],
    "allowed_declarations": ["letFun"],
    "allowed_declaration_prefixes": [
        "And.", "Bool.", "Classical.", "Decidable.", "Eq.",
        "EquationLHS", "EquationRHS", "Goal", "Exists.", "False.",
        "Fin.", "Fintype.", "Function.", "HEq.", "Iff.", "Init.", "Int.", "Lean.",
        "List.", "Magma.", "Mathlib.", "MemoFinOp.", "Nat.", "Nonempty.", "Not.",
        "NthRewrites.", "OfNat.", "Option.", "Or.", "Prod.", "PUnit.",
        "RewriteCombinations.", "RewriteGoal.", "RewriteHypothesis.",
        "RewriteHypothesisAndGoal.", "SimpleRewrites.",
        "Std.", "Subgraph.", "Subtype.", "Sum.",
        "Trans.", "True.", "Unit.",
        "JudgeDecide.", "JudgeFinOp.", "JudgeMagma.",
        "inst", "of_decide_", "submission.",
        "congrArg", "congr_arg", "eq_self", "of_eq_true", "id",
        "eq_comm", "eq_mp", "eq_mpr", "rfl", "absurd",
    ],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frontier-file", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--time-budget", type=float, default=8.0)
    ap.add_argument("--max-rules", type=int, default=48)
    ap.add_argument("--verify", action="store_true", default=True)
    ap.add_argument("--no-verify", dest="verify", action="store_false")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    from judge.verify import verify_answer  # heavy import, keep local

    rows = []
    for line in Path(args.frontier_file).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    if args.limit:
        rows = rows[: args.limit]

    out_dir = Path(args.out_dir) if args.out_dir else (
        REPO / "tmp_stage2_smoke" / f"{date.today().isoformat()}-derived-rules"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger = (out_dir / "ledger.jsonl").open("w", encoding="utf-8")

    cracked = verified = 0
    t0 = time.monotonic()
    for i, problem in enumerate(rows):
        eq1 = S.parse_equation(str(problem["equation1"]))
        eq2 = S.parse_equation(str(problem["equation2"]))
        t1 = time.monotonic()
        try:
            proof_expr = derived_closure_proof(
                eq1, eq2, time_budget=args.time_budget, max_rules=args.max_rules
            )
        except Exception as e:  # noqa: BLE001
            proof_expr = None
            print(f"  ERROR {problem['id']}: {type(e).__name__}: {e}", flush=True)
        rec = {"id": problem["id"], "equation1": problem["equation1"],
               "equation2": problem["equation2"],
               "cracked": proof_expr is not None,
               "search_seconds": round(time.monotonic() - t1, 2)}
        if proof_expr is not None:
            cracked += 1
            code = S.substitution_true_certificate(eq2["variables"], proof_expr)
            rec["code_bytes"] = len(code.encode("utf-8"))
            if args.verify:
                jp = {"id": problem["id"], "eq1_id": problem["eq1_id"],
                      "eq2_id": problem["eq2_id"], "equation1": problem["equation1"],
                      "equation2": problem["equation2"],
                      "proof_policy": problem.get("proof_policy") or DEFAULT_PROOF_POLICY}
                v = verify_answer(jp, json.dumps({"verdict": "true", "code": code}))
                rec["judge"] = v.get("status")
                if v.get("status") == "accepted":
                    verified += 1
                else:
                    rec["lean_error"] = (v.get("stderr") or v.get("message") or "")[:500]
        ledger.write(json.dumps(rec, ensure_ascii=False) + "\n")
        ledger.flush()
        if (i + 1) % 5 == 0 or i + 1 == len(rows):
            print(f"  [{i+1}/{len(rows)}] cracked={cracked} verified={verified} "
                  f"{time.monotonic()-t0:.0f}s", flush=True)

    ledger.close()
    summary = {"date": date.today().isoformat(), "rows": len(rows),
               "cracked": cracked, "verified": verified,
               "time_budget": args.time_budget, "max_rules": args.max_rules,
               "wall_seconds": round(time.monotonic() - t0, 1)}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
