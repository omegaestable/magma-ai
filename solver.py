"""Research-only decision engine for equational implication.

This solver is useful for offline discovery, proof mining, and counterexample
search. It is not the Stage 1 submission artifact.
"""

from __future__ import annotations
import time
import logging
from typing import Optional
from dataclasses import dataclass

from analyze_equations import (
    parse_equation, get_vars, count_ops, get_depth, term_size,
    count_var_occ, get_dual, is_specialization,
)
from proof_search import find_proof, ImplicationGraph, canonizer_refutes
from magma_search import find_counterexample

logger = logging.getLogger(__name__)


# ── Paper-informed helper functions ───────────────────────────────

def _is_singleton_equivalent(lhs, rhs, vars_l: set, vars_r: set) -> bool:
    """Paper §2: An equation is equivalent to the singleton law (x=y)
    iff its LHS and RHS have disjoint variable sets and at least one
    side contains a ◇ operation.

    The 1,496 such laws form the largest equivalence class. If eq1 is
    in this class, it implies everything; if eq2 is but eq1 isn't, FALSE.
    """
    if vars_l & vars_r:
        return False  # shared variables → not singleton-equivalent
    has_op = not isinstance(lhs, str) or not isinstance(rhs, str)
    return has_op


def _var_multiplicity_vector(term, all_vars: list) -> tuple:
    """Compute the multiplicity vector (occurrence count per variable)
    for a term, ordered by all_vars.

    Paper §5.2: Variable multiplicity is a matching invariant — preserved
    under any single-step rewrite. This means the multiset of variable
    counts on LHS must match RHS for any equation reachable by rewriting.
    """
    return tuple(count_var_occ(term, v) for v in all_vars)


def _multiplicity_refutes(eq1, eq2) -> bool:
    """Paper §5.2: Matching invariant refutation.

    If eq1 has identical variable multiplicity on both sides (balanced),
    then every equation derivable from eq1 by rewriting also has balanced
    multiplicity. If eq2 does NOT have balanced multiplicity, then
    eq1 cannot imply eq2.

    This is a necessary condition: balanced eq1 can only imply balanced eq2.
    """
    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2

    all_vars1 = sorted(get_vars(lhs1) | get_vars(rhs1))
    if not all_vars1:
        return False

    # Check if eq1 is balanced (same multiplicity on both sides)
    mv_l1 = _var_multiplicity_vector(lhs1, all_vars1)
    mv_r1 = _var_multiplicity_vector(rhs1, all_vars1)
    eq1_balanced = (mv_l1 == mv_r1)

    if not eq1_balanced:
        return False  # eq1 is unbalanced — no simple refutation

    # eq1 IS balanced. Check if eq2 is also balanced.
    all_vars2 = sorted(get_vars(lhs2) | get_vars(rhs2))
    if not all_vars2:
        return False

    mv_l2 = _var_multiplicity_vector(lhs2, all_vars2)
    mv_r2 = _var_multiplicity_vector(rhs2, all_vars2)
    eq2_balanced = (mv_l2 == mv_r2)

    # If eq1 is balanced but eq2 isn't, eq1 cannot imply eq2.
    return not eq2_balanced


@dataclass
class SolverResult:
    """Result of the solver's decision."""
    verdict: bool               # TRUE (implies) or FALSE (doesn't)
    confidence: float           # 0.0 to 1.0
    method: str                 # how we decided
    proof: Optional[str] = None # proof or counterexample details
    time_s: float = 0.0


class Solver:
    """Main decision engine.

    Combines fast heuristics with deep search to decide
    whether Eq1 → Eq2 for any given pair.
    """

    def __init__(
        self,
        impl_graph: Optional[ImplicationGraph] = None,
        timeout: float = 30.0,
        base_rate: float = 0.37,
    ):
        """
        Args:
            impl_graph: Preloaded implication graph (from known data)
            timeout: Max seconds per problem
            base_rate: Prior probability of TRUE (from data: ~37%)
        """
        self.impl_graph = impl_graph
        self.timeout = timeout
        self.base_rate = base_rate

    def solve(
        self,
        eq1_str: str,
        eq2_str: str,
        eq1_idx: int = 0,
        eq2_idx: int = 0,
    ) -> SolverResult:
        """Determine whether eq1 implies eq2.

        Strategy:
          Phase 0: Instant checks (trivial cases, specialization)
          Phase 1: Structural analysis → decide search priority
          Phase 2: Primary search (proof or counterexample)
          Phase 3: Secondary search (the other one)
          Phase 4: Fall back to heuristic probability
        """
        t0 = time.time()

        # ── Phase 0: Instant checks ──
        result = self._instant_checks(eq1_str, eq2_str, eq1_idx, eq2_idx)
        if result is not None:
            result.time_s = time.time() - t0
            return result

        # ── Phase 1: Analyze structure → route ──
        prior, features = self._compute_prior(eq1_str, eq2_str)
        likely_true = prior > 0.5

        remaining = self.timeout - (time.time() - t0)
        if remaining <= 0:
            return SolverResult(likely_true, prior, "prior_only", time_s=time.time() - t0)

        # ── Phase 2: Primary search ──
        if likely_true:
            # Try proof first
            proof_budget = remaining * 0.6
            proof_result = find_proof(
                eq1_str, eq2_str, timeout=proof_budget,
                impl_graph=self.impl_graph, eq1_idx=eq1_idx, eq2_idx=eq2_idx
            )
            if proof_result is not None:
                return SolverResult(True, 0.97, f"proof:{proof_result['method']}",
                                    proof=proof_result.get('proof', ''),
                                    time_s=time.time() - t0)

            remaining = self.timeout - (time.time() - t0)
            if remaining <= 0:
                return SolverResult(True, prior, "prior_after_failed_proof",
                                    time_s=time.time() - t0)

            # Phase 3: Try counterexample
            cex_result = find_counterexample(eq1_str, eq2_str, timeout=remaining * 0.9)
            if cex_result is not None:
                return SolverResult(False, 0.97, f"counterexample:{cex_result['method']}",
                                    proof=f"magma size {cex_result['size']}: {cex_result['table']}",
                                    time_s=time.time() - t0)
        else:
            # Try counterexample first
            cex_budget = remaining * 0.6
            cex_result = find_counterexample(eq1_str, eq2_str, timeout=cex_budget)
            if cex_result is not None:
                return SolverResult(False, 0.97, f"counterexample:{cex_result['method']}",
                                    proof=f"magma size {cex_result['size']}: {cex_result['table']}",
                                    time_s=time.time() - t0)

            remaining = self.timeout - (time.time() - t0)
            if remaining <= 0:
                return SolverResult(False, 1.0 - prior, "prior_after_failed_cex",
                                    time_s=time.time() - t0)

            # Phase 3: Try proof
            proof_result = find_proof(
                eq1_str, eq2_str, timeout=remaining * 0.9,
                impl_graph=self.impl_graph, eq1_idx=eq1_idx, eq2_idx=eq2_idx
            )
            if proof_result is not None:
                return SolverResult(True, 0.97, f"proof:{proof_result['method']}",
                                    proof=proof_result.get('proof', ''),
                                    time_s=time.time() - t0)

        # ── Phase 4: Heuristic fallback ──
        # Refine the prior based on what we learned from failed searches
        refined = self._refine_prior(prior, features, likely_true)
        verdict = refined > 0.5
        return SolverResult(verdict, refined if verdict else 1.0 - refined,
                            "heuristic_fallback", time_s=time.time() - t0)

    def _instant_checks(
        self, eq1_str, eq2_str, eq1_idx, eq2_idx,
    ) -> Optional[SolverResult]:
        """O(1) checks that give definitive answers."""

        # Syntactic identity
        if eq1_str.strip() == eq2_str.strip():
            return SolverResult(True, 1.0, "identical")

        try:
            eq1 = parse_equation(eq1_str)
            eq2 = parse_equation(eq2_str)
        except Exception:
            return SolverResult(False, self.base_rate, "parse_error")

        lhs1, rhs1 = eq1
        lhs2, rhs2 = eq2

        # x = x (tautology)
        if lhs2 == rhs2:
            return SolverResult(True, 1.0, "eq2_tautology")
        if lhs1 == rhs1:
            return SolverResult(False, 1.0, "eq1_tautology_eq2_nontrivial")

        # x = y (singleton law) implies everything
        vars1 = get_vars(lhs1) | get_vars(rhs1)
        vars1_l = get_vars(lhs1)
        vars1_r = get_vars(rhs1)
        if isinstance(lhs1, str) and isinstance(rhs1, str) and len(vars1) == 2:
            return SolverResult(True, 1.0, "eq1_singleton")

        # Paper §2: Singleton-equivalent detection.
        # An equation with disjoint LHS/RHS variable sets and >=1 ◇ op
        # is equivalent to E2 (x=y). The 1,496 such laws form the
        # largest equivalence class; E1_singleton implies everything.
        if _is_singleton_equivalent(lhs1, rhs1, vars1_l, vars1_r):
            return SolverResult(True, 1.0, "eq1_singleton_equivalent")

        # eq2 is singleton law — only if eq1 also forces singleton
        vars2 = get_vars(lhs2) | get_vars(rhs2)
        vars2_l = get_vars(lhs2)
        vars2_r = get_vars(rhs2)
        if isinstance(lhs2, str) and isinstance(rhs2, str) and len(vars2) == 2:
            # eq2 forces |M|=1; check quickly
            if isinstance(lhs1, str) and isinstance(rhs1, str) and len(vars1) == 2:
                return SolverResult(True, 1.0, "both_singleton")
            # Most non-singleton eq1 won't imply this
            return SolverResult(False, 0.92, "eq2_singleton_eq1_not")

        # Paper §2: If eq2 is singleton-equivalent, only singleton-forcing
        # eq1 can imply it.
        if _is_singleton_equivalent(lhs2, rhs2, vars2_l, vars2_r):
            if _is_singleton_equivalent(lhs1, rhs1, vars1_l, vars1_r):
                return SolverResult(True, 1.0, "both_singleton_equivalent")
            return SolverResult(False, 0.92, "eq2_singleton_equiv_eq1_not")

        # Paper §5.2: Matching invariant refutation.
        # Variable multiplicity is preserved by rewriting. If eq1 has
        # balanced multiplicities (same total on both sides for each var)
        # but eq2 does not, then eq1 cannot imply eq2.
        if _multiplicity_refutes(eq1, eq2):
            return SolverResult(False, 0.95, "matching_invariant")

        # Paper §5.3: Canonizer refutation — if eq1's rewrite system
        # produces different normal forms for eq2's sides, FALSE.
        try:
            if canonizer_refutes(eq1, eq2):
                return SolverResult(False, 0.90, "canonizer_refutation")
        except Exception:
            pass

        # Direct specialization (fast, no search)
        if is_specialization(eq1, eq2):
            return SolverResult(True, 0.98, "specialization")

        # Graph lookup (instant if graph loaded)
        if self.impl_graph and eq1_idx and eq2_idx:
            direct = self.impl_graph.adj.get(eq1_idx, set())
            if eq2_idx in direct:
                return SolverResult(True, 0.99, "graph_direct")
            if self.impl_graph.is_known_false(eq1_idx, eq2_idx):
                return SolverResult(False, 0.99, "graph_negative")

        return None

    def _compute_prior(self, eq1_str: str, eq2_str: str) -> tuple:
        """Compute structural prior probability of TRUE.

        Uses paper-informed features (§4 spectrum, §5 syntactic invariants,
        §3 counterexample difficulty). Returns (prior, features_dict).
        """
        try:
            eq1 = parse_equation(eq1_str)
            eq2 = parse_equation(eq2_str)
        except Exception:
            return self.base_rate, {}

        lhs1, rhs1 = eq1
        lhs2, rhs2 = eq2
        vars1 = get_vars(lhs1) | get_vars(rhs1)
        vars2 = get_vars(lhs2) | get_vars(rhs2)
        ops1 = count_ops(lhs1) + count_ops(rhs1)
        ops2 = count_ops(lhs2) + count_ops(rhs2)
        depth1 = max(get_depth(lhs1), get_depth(rhs1))
        depth2 = max(get_depth(lhs2), get_depth(rhs2))

        features = {
            "n_vars1": len(vars1),
            "n_vars2": len(vars2),
            "ops1": ops1, "ops2": ops2,
            "depth1": depth1, "depth2": depth2,
            "vars_extra_in_eq2": len(vars2 - vars1),
            "ops_diff": ops1 - ops2,
            "depth_diff": depth1 - depth2,
        }

        # Heuristic scoring — calibrated to paper's 37% base rate
        score = self.base_rate

        # If eq2 uses variables not in eq1, very unlikely TRUE
        if features["vars_extra_in_eq2"] > 0:
            score *= 0.1

        # Paper §4: Same-order equations are more likely to be related.
        # If eq1 and eq2 have the same total operation count, slightly
        # higher probability of TRUE (they live in the same "slice").
        if ops1 == ops2:
            score *= 1.15
        elif ops1 > ops2:
            # Paper §1.3: More complex eq1 → more constraining → more
            # likely to imply simpler eq2
            score *= 1.3
        else:
            score *= 0.7

        # More variables in eq1 → more constraining
        if len(vars1) > len(vars2):
            score *= 1.2
        elif len(vars1) < len(vars2):
            score *= 0.6

        # Deeper eq1 → harder constraint → more likely to imply shallower eq2
        if depth1 > depth2:
            score *= 1.1

        # Self-dual equations are more likely to be involved in implications
        dual1 = (get_dual(lhs1), get_dual(rhs1))
        if dual1 == eq1 or dual1 == (rhs1, lhs1):
            score *= 1.1

        # Paper §5.2: Variable balance signal.
        # If both sides of eq1 have identical variable multisets, eq1
        # is "balanced" — these tend to imply more equations.
        vars1_set = get_vars(lhs1) | get_vars(rhs1)
        eq1_balanced = all(
            count_var_occ(lhs1, v) == count_var_occ(rhs1, v)
            for v in vars1_set
        )
        if eq1_balanced:
            score *= 1.1

        # Clamp
        score = max(0.01, min(0.99, score))
        return score, features

    def _refine_prior(self, prior: float, features: dict, tried_proof_first: bool) -> float:
        """Refine prior after both searches failed.

        Key insight: failing to find a counterexample in sizes 2-5 is
        STRONG evidence for TRUE, because most FALSE implications have
        small counterexamples. This is especially true when eq2 has
        extra variables (which makes counterexamples easier to find
        if they exist).
        """
        # Both searches failed — no proof found AND no counterexample found
        # The absence of a counterexample is very informative
        refined = 0.65  # base: lean toward TRUE (no cex is strong signal)

        # Extra vars in eq2 but no counterexample? Very strong TRUE signal.
        # Extra vars make it trivially easy to construct counterexamples
        # for FALSE implications, so their absence is highly informative.
        extra_vars = features.get("vars_extra_in_eq2", 0)
        if extra_vars > 0:
            refined = 0.80  # strongly lean TRUE despite extra vars

        # If eq1 has more ops (more constraining), lean more toward TRUE
        ops_diff = features.get("ops_diff", 0)
        if ops_diff > 0:
            refined = min(0.90, refined + 0.05)

        return refined


# ── Batch solver ─────────────────────────────────────────────────

def solve_batch(
    problems: list,
    equations: list,
    impl_graph: Optional[ImplicationGraph] = None,
    timeout_per: float = 10.0,
    verbose: bool = True,
) -> list:
    """Solve a batch of problems.

    Args:
        problems: list of (eq1_idx, eq2_idx, optional_label)
        equations: list of equation strings (0-indexed)
        impl_graph: optional preloaded implication graph
        timeout_per: seconds per problem

    Returns:
        list of SolverResult
    """
    solver = Solver(impl_graph=impl_graph, timeout=timeout_per)
    results = []
    correct = 0
    total_with_labels = 0

    for i, prob in enumerate(problems):
        eq1_idx = prob[0]
        eq2_idx = prob[1]
        label = prob[2] if len(prob) > 2 else None

        eq1_str = equations[eq1_idx - 1]
        eq2_str = equations[eq2_idx - 1]

        result = solver.solve(eq1_str, eq2_str, eq1_idx=eq1_idx, eq2_idx=eq2_idx)
        results.append(result)

        if label is not None:
            total_with_labels += 1
            if result.verdict == label:
                correct += 1

        if verbose and ((i + 1) % 10 == 0 or i == len(problems) - 1):
            acc_str = f", acc={correct/total_with_labels:.3f}" if total_with_labels > 0 else ""
            logger.info(
                f"  [{i+1}/{len(problems)}] Eq{eq1_idx}→Eq{eq2_idx} "
                f"= {'TRUE' if result.verdict else 'FALSE'} "
                f"({result.method}, {result.confidence:.2f}, {result.time_s:.2f}s)"
                f"{acc_str}"
            )

    if total_with_labels > 0 and verbose:
        acc = correct / total_with_labels
        logger.info(f"\nFinal accuracy: {correct}/{total_with_labels} = {acc:.4f}")

    return results


# ── CLI ───────────────────────────────────────────────────────────

def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Solve equational implication problems")
    parser.add_argument("--eq1", type=int, help="Equation 1 index (1-based)")
    parser.add_argument("--eq2", type=int, help="Equation 2 index (1-based)")
    parser.add_argument("--data", help="JSONL file of problems to solve in batch")
    parser.add_argument("--graph", help="Path to raw implications CSV for graph")
    parser.add_argument("--timeout", type=float, default=30.0, help="Timeout per problem (seconds)")
    parser.add_argument("--output", help="Output JSONL file for batch results")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    from analyze_equations import load_equations
    equations = load_equations()

    # Load implication graph if available
    impl_graph = None
    if args.graph:
        logger.info("Loading implication graph...")
        impl_graph = ImplicationGraph()
        impl_graph.load_from_matrix_file(args.graph)
        logger.info(f"Graph: {len(impl_graph.adj)} nodes, {impl_graph.n_edges} edges")

    if args.eq1 and args.eq2:
        # Single problem mode
        solver = Solver(impl_graph=impl_graph, timeout=args.timeout)
        result = solver.solve(
            equations[args.eq1 - 1], equations[args.eq2 - 1],
            eq1_idx=args.eq1, eq2_idx=args.eq2,
        )
        verdict = "TRUE" if result.verdict else "FALSE"
        print(f"\nEq{args.eq1}: {equations[args.eq1 - 1]}")
        print(f"Eq{args.eq2}: {equations[args.eq2 - 1]}")
        print(f"\nVERDICT: {verdict} (confidence={result.confidence:.2f})")
        print(f"Method: {result.method}")
        if result.proof:
            print(f"Proof: {result.proof}")
        print(f"Time: {result.time_s:.3f}s")

    elif args.data:
        # Batch mode
        problems = []
        with open(args.data, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                eq1 = int(rec.get('equation1_index', rec.get('eq1', 0)))
                eq2 = int(rec.get('equation2_index', rec.get('eq2', 0)))
                label = rec.get('implies', rec.get('label'))
                if label is not None:
                    problems.append((eq1, eq2, bool(label)))
                else:
                    problems.append((eq1, eq2))

        results = solve_batch(problems, equations, impl_graph=impl_graph,
                              timeout_per=args.timeout)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                for prob, res in zip(problems, results):
                    f.write(json.dumps({
                        "eq1": prob[0], "eq2": prob[1],
                        "verdict": res.verdict,
                        "confidence": res.confidence,
                        "method": res.method,
                        "time_s": res.time_s,
                    }) + '\n')
            print(f"Results written to {args.output}")
    else:
        # Interactive demo
        print("Usage:")
        print("  Single: python solver.py --eq1 4 --eq2 8")
        print("  Batch:  python solver.py --data data/normal.jsonl --graph data/exports/export_raw_implications_14_3_2026.csv")


if __name__ == "__main__":
    main()
