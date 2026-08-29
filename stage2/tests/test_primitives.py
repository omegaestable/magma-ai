"""Unit tests for the solver's shared soundness primitives.

These primitives underwrite every generated Lean certificate: a silent bug in
any of them ships `incorrect` submissions. Each test is small, deterministic,
and Lean-free (see oracles.py for the proof kernel used here).
"""

from __future__ import annotations

import json
import random
import re
import time
from pathlib import Path

import pytest

import oracles
from oracles import OracleError, ProofKernel

VAR_NAMES = ("x", "y", "z", "w", "u", "v")

LAWS = {
    "left_zero": "x = x ◇ y",
    "comm": "x ◇ y = y ◇ x",
    "assoc": "x ◇ (y ◇ z) = (x ◇ y) ◇ z",
    "central": "x = (y ◇ x) ◇ (x ◇ z)",
    "absorb2": "x = y ◇ (x ◇ y)",
    "deep": "x = ((y ◇ (x ◇ y)) ◇ z) ◇ w",
}


def random_term(rng: random.Random, depth: int) -> tuple:
    if depth == 0 or rng.random() < 0.35:
        return ("var", rng.choice(VAR_NAMES))
    return ("op", random_term(rng, depth - 1), random_term(rng, depth - 1))


# ---------------------------------------------------------------------------
# Parsing / rendering
# ---------------------------------------------------------------------------

def test_parse_render_round_trip_random(solver):
    rng = random.Random(1)
    for _ in range(300):
        term = random_term(rng, 4)
        rendered = solver.term_to_lean(term)
        assert solver.parse_term(rendered, set(VAR_NAMES)) == term


def test_parse_star_and_diamond_agree(solver):
    variables = {"x", "y", "z"}
    a = solver.parse_term("x ◇ (y ◇ z)", variables)
    b = solver.parse_term("x * (y * z)", variables)
    assert a == b == ("op", ("var", "x"), ("op", ("var", "y"), ("var", "z")))


def test_parse_unparenthesized_is_left_associative(solver):
    variables = {"x", "y", "z"}
    assert solver.parse_term("x ◇ y ◇ z", variables) == (
        "op", ("op", ("var", "x"), ("var", "y")), ("var", "z"))


def test_strip_outer_parens(solver):
    assert solver.strip_outer_parens("((x ◇ y))") == "x ◇ y"
    assert solver.strip_outer_parens("(x ◇ y) ◇ z") == "(x ◇ y) ◇ z"
    assert solver.strip_outer_parens("  ( x )  ") == "x"


def test_parse_equation_variable_order(solver):
    eq = solver.parse_equation("x = (y ◇ (x ◇ z)) ◇ (y ◇ w)")
    assert eq["variables"] == ["x", "y", "z", "w"]
    assert eq["lhs"] == ("var", "x")


# ---------------------------------------------------------------------------
# Substitution / matching / paths
# ---------------------------------------------------------------------------

def test_match_inverts_instantiate_on_linear_patterns(solver):
    rng = random.Random(2)
    pattern = solver.parse_equation(LAWS["central"])["rhs"]  # (y◇x)◇(x◇z): non-linear in x
    for _ in range(100):
        subst = {v: random_term(rng, 2) for v in ("x", "y", "z")}
        target = solver.instantiate_term(pattern, subst)
        recovered: dict = {}
        assert solver.match_term(pattern, target, recovered)
        assert recovered == subst


def test_match_rejects_inconsistent_nonlinear_binding(solver):
    pattern = solver.parse_term("x ◇ x", {"x"})
    target = solver.parse_term("y ◇ z", {"y", "z"})
    assert not solver.match_term(pattern, target, {})


def test_replace_subterm_round_trip(solver):
    rng = random.Random(3)
    for _ in range(100):
        term = random_term(rng, 4)
        for path in solver.subterm_paths(term):
            sub = solver.term_at_path(term, path)
            assert solver.replace_subterm(term, path, sub) == term
            marker = ("var", "u")
            replaced = solver.replace_subterm(term, path, marker)
            assert solver.term_at_path(replaced, path) == marker


def test_context_to_lean_semantics(solver):
    """C[t := subterm] must render back to the original term."""
    rng = random.Random(4)
    for _ in range(150):
        term = random_term(rng, 4)
        for path in solver.subterm_paths(term):
            ctx_str = solver.context_to_lean(term, path, "t")
            ctx = oracles.parse_lean_term(ctx_str, set(VAR_NAMES) | {"t"})
            filled = oracles.substitute(
                ctx,
                {"t": solver.term_at_path(term, path)}
                | {v: ("var", v) for v in VAR_NAMES},
            )
            assert filled == term


# ---------------------------------------------------------------------------
# Duality / evaluation
# ---------------------------------------------------------------------------

def test_dual_is_involution(solver):
    rng = random.Random(5)
    for _ in range(200):
        term = random_term(rng, 4)
        assert solver.dual_term(solver.dual_term(term)) == term


def test_dual_transpose_semantics(solver):
    """eq holds in table  <=>  dual eq holds in transposed table."""
    rng = random.Random(6)
    eqs = [solver.parse_equation(text) for text in LAWS.values()]
    for _ in range(60):
        n = rng.choice((2, 3))
        table = [[rng.randrange(n) for _ in range(n)] for _ in range(n)]
        transposed = solver.transpose_table(table)
        for eq in eqs:
            assert solver.equation_holds(eq, table) == solver.equation_holds(
                solver.dual_equation(eq), transposed)


def test_equation_holds_matches_oracle(solver):
    rng = random.Random(7)
    eqs = [solver.parse_equation(text) for text in LAWS.values()]
    for _ in range(60):
        n = rng.choice((2, 3))
        table = [[rng.randrange(n) for _ in range(n)] for _ in range(n)]
        for eq in eqs:
            assert solver.equation_holds(eq, table) == oracles.equation_holds(
                eq["lhs"], eq["rhs"], list(eq["variables"]), table)


def test_equation_holds_known_facts(solver):
    comm = solver.parse_equation(LAWS["comm"])
    assoc = solver.parse_equation(LAWS["assoc"])
    xor = [[0, 1], [1, 0]]
    lp = [[0, 0], [1, 1]]
    nimp = [[0, 0], [1, 0]]
    assert solver.equation_holds(comm, xor)
    assert not solver.equation_holds(comm, lp)
    assert solver.equation_holds(assoc, xor)
    assert not solver.equation_holds(assoc, nimp)


# ---------------------------------------------------------------------------
# Unification (critical-pair kernel)
# ---------------------------------------------------------------------------

def test_kb_unify_produces_unifier(solver):
    rng = random.Random(8)
    for _ in range(200):
        a = random_term(rng, 3)
        b = random_term(rng, 3)
        subst = solver._kb_unify(a, b, {})
        if subst is None:
            continue
        assert solver._kb_resolve(a, subst) == solver._kb_resolve(b, subst)


def test_kb_unify_occurs_check(solver):
    x = ("var", "x")
    fx = ("op", ("var", "x"), ("var", "y"))
    assert solver._kb_unify(x, fx, {}) is None
    assert solver._kb_unify(fx, x, {}) is None


def test_kb_unify_disagreement(solver):
    a = ("op", ("var", "x"), ("var", "x"))
    b = ("op", ("op", ("var", "y"), ("var", "y")), ("var", "z"))
    subst = solver._kb_unify(a, b, {})
    # x := (y◇y) and x := z unify via z := (y◇y): must produce a unifier.
    assert subst is not None
    assert solver._kb_resolve(a, subst) == solver._kb_resolve(b, subst)


# ---------------------------------------------------------------------------
# Derived critical-pair rules: the general TRUE engine's soundness contract
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("law", ["central", "absorb2", "deep", "assoc"])
def test_critical_pair_rules_are_sound_consequences(solver, law):
    """Every derived rule must hold in every finite model of eq1."""
    eq1 = solver.parse_equation(LAWS[law])
    rules = solver.critical_pair_rules(eq1)
    assert rules, f"no critical pairs derived for {law}"
    extras = [table for _name, table in solver.WITNESS_TABLES]
    extras.extend(table for _route, table in solver.structured_family_tables())
    battery = oracles.model_battery(eq1, extras, fin3_samples=400, seed=11)
    assert battery, f"no finite models found for {law}"
    for rule in rules:
        variables = list(rule.vars)
        for table in battery:
            assert oracles.equation_holds(rule.lhs, rule.rhs, variables, table), (
                f"unsound derived rule {rule.label}: "
                f"{oracles.term_to_str(rule.lhs)} = {oracles.term_to_str(rule.rhs)}")


@pytest.mark.parametrize("law", ["central", "absorb2", "deep", "assoc"])
def test_critical_pair_builders_prove_their_rules(solver, law):
    """rule.builder(subst) must prove exactly subst(lhs) = subst(rhs)."""
    eq1 = solver.parse_equation(LAWS[law])
    goal_vars = set(VAR_NAMES)
    kernel = ProofKernel(list(eq1["variables"]), eq1["lhs"], eq1["rhs"], goal_vars)
    rng = random.Random(12)
    for rule in solver.critical_pair_rules(eq1):
        for _ in range(3):
            subst = {
                v: random_term(rng, 1)
                for v in list(rule.vars) + list(rule.proof_only_vars)
            }
            proof = rule.builder(subst)
            expected = (
                solver.instantiate_term(rule.lhs, subst),
                solver.instantiate_term(rule.rhs, subst),
            )
            proved = kernel.prove(proof)
            assert proved == expected, (
                f"builder for {rule.label} proved "
                f"{oracles.term_to_str(proved[0])} = {oracles.term_to_str(proved[1])}, "
                f"expected {oracles.term_to_str(expected[0])} = "
                f"{oracles.term_to_str(expected[1])}")


@pytest.mark.parametrize("law", ["central", "absorb2", "deep"])
def test_filled_absorption_steps_proofs(solver, law):
    """Each closure step's proof must prove term = new_term."""
    eq1 = solver.parse_equation(LAWS[law])
    eq2 = solver.parse_equation("x = (y ◇ x) ◇ (x ◇ z)")
    pool = solver.absorption_term_pool(eq1, eq2, pool_limit=8)
    kernel = ProofKernel(
        list(eq1["variables"]), eq1["lhs"], eq1["rhs"], set(VAR_NAMES))
    for start in (eq2["lhs"], eq2["rhs"], eq1["rhs"]):
        steps = solver.filled_absorption_steps(
            eq1, start, pool, max_size=18, max_depth=8, max_fills=60)
        assert isinstance(steps, list)
        for new_term, proof, _route in steps[:40]:
            proved = kernel.prove(proof)
            assert proved == (start, new_term), (
                f"step proof mismatch for {proof!r}")


# ---------------------------------------------------------------------------
# Certificate templates
# ---------------------------------------------------------------------------

def test_substitution_certificate_shape_is_kernel_checkable(solver):
    eq1 = solver.parse_equation(LAWS["left_zero"])
    eq2 = solver.parse_equation("x = x ◇ x")
    # x = x◇y specialised at y := x proves x = x◇x.
    code = solver.substitution_true_certificate(eq2["variables"], "h x x")
    assert oracles.classify_true_certificate(code) == "exact_expr"
    oracles.check_true_exact_certificate(code, eq1, eq2)


def test_kernel_rejects_wrong_substitution(solver):
    eq1 = solver.parse_equation(LAWS["left_zero"])
    eq2 = solver.parse_equation("x = x ◇ x")
    code = solver.substitution_true_certificate(eq2["variables"], "h x y")
    with pytest.raises(OracleError):
        oracles.check_true_exact_certificate(code, eq1, eq2)


def test_singleton_certificate_is_kernel_checkable(solver):
    """x = y◇z forces collapse: h a b b : a = b◇b and h b b b : b = b◇b, so
    (h a b b).trans (h b b b).symm proves a = b - but only if the argument
    lists are built correctly."""
    eq1 = solver.parse_equation("x = y ◇ z")
    singleton = solver.singleton_route(eq1)
    assert singleton is not None, "x = y ◇ z must be a singleton source"
    var, on_lhs = singleton
    eq2 = solver.parse_equation("x = x ◇ x")
    code = solver.singleton_true_certificate(
        eq1["variables"], eq2["variables"], var, on_lhs)
    assert oracles.classify_true_certificate(code) == "singleton"
    oracles.check_true_singleton_certificate(code, eq1)


def test_singleton_kernel_rejects_broken_collapse(solver):
    eq1 = solver.parse_equation("x = x ◇ y")
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hall : ∀ a b : G, a = b := by\n"
        "    intro a b\n"
        "    exact (h a b).trans (h a b).symm\n"  # proves a = a, not a = b
        "  exact hall _ _\n"
    )
    with pytest.raises(OracleError):
        oracles.check_true_singleton_certificate(code, eq1)


def test_false_certificate_round_trip(solver):
    eq1 = solver.parse_equation(LAWS["comm"])       # holds on XOR
    eq2 = solver.parse_equation(LAWS["left_zero"])  # fails on XOR
    table = [[0, 1], [1, 0]]
    code = solver.false_certificate(2, table)
    oracles.check_false_certificate(code, eq1, eq2)


def test_false_certificate_oracle_rejects_bad_witness(solver):
    eq1 = solver.parse_equation(LAWS["left_zero"])
    eq2 = solver.parse_equation(LAWS["comm"])
    # LP satisfies x = x◇y... it does not; use C0 which satisfies neither side
    # of the claim: C0 satisfies eq1? (x◇y = 0) != x in general -> eq1 fails.
    code = solver.false_certificate(2, [[0, 0], [0, 0]])
    with pytest.raises(OracleError):
        oracles.check_false_certificate(code, eq1, eq2)


def test_large_false_certificate_sets_recursion_depth(solver):
    table = [[0] * 7 for _ in range(7)]
    code = solver.false_certificate(7, table)
    assert "set_option maxRecDepth 20000" in code


# ---------------------------------------------------------------------------
# Mutation tests: prove the oracles actually reject broken certificates.
# A validator that never fails provides no safety.
# ---------------------------------------------------------------------------

# Real implications whose solver certificates exercise distinct proof shapes:
# a plain trans/symm chain, and a congrArg context rewrite.
REAL_CERT_CASES = {
    "trans_chain": (
        "x = y ◇ (x ◇ y)",
        "x = y ◇ ((y ◇ (x ◇ y)) ◇ y)",
    ),
    "congr_arg": (
        "x = y ◇ ((x ◇ z) ◇ (w ◇ u))",
        "x = (((x ◇ x) ◇ x) ◇ x) ◇ x",
    ),
}


def _real_true_certificate(solver, case: str):
    """A genuine solver-produced certificate from a real implication."""
    eq1_text, eq2_text = REAL_CERT_CASES[case]
    eq1 = solver.parse_equation(eq1_text)
    eq2 = solver.parse_equation(eq2_text)
    for route in (solver.equational_closure_route, solver.derived_cp_closure_route):
        result = route(eq1, eq2)
        if result is not None:
            return eq1, eq2, result[1]
    pytest.skip(f"no closure route fired for {case}")


@pytest.mark.parametrize("case", sorted(REAL_CERT_CASES))
def test_oracle_accepts_real_closure_certificates(solver, case):
    eq1, eq2, code = _real_true_certificate(solver, case)
    assert oracles.classify_true_certificate(code) == "exact_expr"
    oracles.check_true_exact_certificate(code, eq1, eq2)


def test_congr_arg_certificate_actually_uses_congr_arg(solver):
    """Guard the mutation below stays meaningful if the engine changes."""
    _eq1, _eq2, code = _real_true_certificate(solver, "congr_arg")
    assert "congrArg" in code


# Each mutation is paired with the cases whose certificate it actually bites.
# `corrupt_congr_context` needs a `congrArg`, which the flat trans/symm chain
# does not have -- and this used to be a `pytest.skip` inside the test, i.e. a
# parametrisation that contributed no coverage while reading as one (rail 16).
# Pairing them here makes the gap explicit in the collected test ids instead.
CERT_MUTATIONS = [
    ("extra_hypothesis_arg", lambda c: c.replace("h ", "h y ", 1),
     ("trans_chain", "congr_arg")),
    ("drop_a_symm", lambda c: c.replace(".symm", "", 1),
     ("trans_chain", "congr_arg")),
    ("trans_to_symm", lambda c: c.replace(".trans", ".symm", 1),
     ("trans_chain", "congr_arg")),
    ("corrupt_congr_context", lambda c: c.replace("fun t => ", "fun t => t ◇ ", 1),
     ("congr_arg",)),
]


@pytest.mark.parametrize(
    "case,mutate",
    [pytest.param(case, mutate, id=f"{name}-{case}")
     for name, mutate, cases in CERT_MUTATIONS for case in cases],
)
def test_oracle_rejects_mutated_certificates(solver, case, mutate):
    eq1, eq2, code = _real_true_certificate(solver, case)
    mutated = mutate(code)
    # Not a skip: a mutation that does not apply proves nothing and would read
    # as coverage in the gate's pass count.
    assert mutated != code, (
        f"mutation no longer applies to the {case} certificate -- the engine "
        "changed shape, so re-pair the mutation rather than skipping it")
    with pytest.raises(OracleError):
        oracles.check_true_exact_certificate(mutated, eq1, eq2)


# ---------------------------------------------------------------------------
# Effort scaling: budgets must track the clock the track actually gives us.
# ---------------------------------------------------------------------------

def test_effort_tier_selection_from_seconds(solver):
    assert solver.effort_for_seconds(1.0) == "fast"
    assert solver.effort_for_seconds(44.0) == "fast"
    assert solver.effort_for_seconds(45.0) == "standard"
    assert solver.effort_for_seconds(239.0) == "standard"
    assert solver.effort_for_seconds(3600.0) == "deep"


def test_effort_scaling_is_monotone(solver):
    original = solver.effort_tier()
    try:
        seen = []
        for tier in ("fast", "standard", "deep"):
            solver.set_effort(tier)
            seen.append((
                solver._eff_time(8.0), solver._eff_frontier(2600),
                solver._eff_fills(1200), solver._eff_pool(16),
                solver._eff_depth(4),
            ))
        for i in range(len(seen) - 1):
            assert all(a <= b for a, b in zip(seen[i], seen[i + 1])), seen
        assert seen[0] == (8.0, 2600, 1200, 16, 4), "fast tier must be the old default"
    finally:
        solver.set_effort(original)


def test_set_effort_ignores_unknown_tier(solver):
    original = solver.effort_tier()
    try:
        solver.set_effort("nonsense")
        assert solver.effort_tier() == original
    finally:
        solver.set_effort(original)


def test_effort_ladder_is_a_cheapest_first_prefix(solver):
    assert solver.effort_ladder_to("fast") == ("fast",)
    assert solver.effort_ladder_to("standard") == ("fast", "standard")
    assert solver.effort_ladder_to("deep") == ("fast", "standard", "deep")
    # An unknown tier must not silently become a three-pass run.
    assert solver.effort_ladder_to("nonsense") == ("nonsense",)


def test_solve_problem_walks_the_effort_ladder(solver, monkeypatch):
    """Tier inversion guard: `deep` must try `fast` budgets FIRST.

    `EFFORT_TIERS` scales every engine together, so a single `deep` pass lets
    the engines that run first spend the whole per-row clock and the late ones
    never run. Measured 2026-08-12: `sample_20` is 20/20 at `fast` in 32 s and
    15/20 at `deep` under a 45 s row deadline.
    """
    original = solver.effort_tier()
    seen: list[str] = []

    def fake_pass(problem, *, false_time_budget=None):
        seen.append(solver.effort_tier())
        return None

    try:
        monkeypatch.setattr(solver, "solve_problem_pass", fake_pass)
        solver.set_hard_deadline(None)

        solver.set_effort("fast")
        seen.clear()
        assert solver.solve_problem({}) is None
        assert seen == ["fast"], "fast must stay exactly one pass"

        solver.set_effort("deep")
        seen.clear()
        assert solver.solve_problem({}) is None
        assert seen == ["fast", "standard", "deep"]
        assert solver.effort_tier() == "deep", "the caller's tier must be restored"
    finally:
        solver.set_hard_deadline(None)
        solver.set_effort(original)


def test_solve_problem_ladder_stops_at_the_first_certificate(solver, monkeypatch):
    original = solver.effort_tier()
    seen: list[str] = []

    def fake_pass(problem, *, false_time_budget=None):
        seen.append(solver.effort_tier())
        return {"answer": {}, "route": "stub", "priority": (0, 0, "")}

    try:
        monkeypatch.setattr(solver, "solve_problem_pass", fake_pass)
        solver.set_hard_deadline(None)
        solver.set_effort("deep")
        assert solver.solve_problem({})["route"] == "stub"
        assert seen == ["fast"], "a fast answer must not pay for the wider tiers"
    finally:
        solver.set_hard_deadline(None)
        solver.set_effort(original)


def test_solve_problem_ladder_does_not_escalate_into_a_spent_clock(solver, monkeypatch):
    original = solver.effort_tier()
    seen: list[str] = []

    def fake_pass(problem, *, false_time_budget=None):
        seen.append(solver.effort_tier())
        return None

    try:
        monkeypatch.setattr(solver, "solve_problem_pass", fake_pass)
        solver.set_effort("deep")
        solver.set_hard_deadline(time.monotonic() - 1.0)
        assert solver.solve_problem({}) is None
        assert seen == ["fast"], "a passed deadline must end the ladder"
    finally:
        solver.set_hard_deadline(None)
        solver.set_effort(original)


def test_solve_problem_restores_effort_when_a_pass_raises(solver, monkeypatch):
    original = solver.effort_tier()

    def boom(problem, *, false_time_budget=None):
        raise RuntimeError("engine exploded")

    try:
        monkeypatch.setattr(solver, "solve_problem_pass", boom)
        solver.set_hard_deadline(None)
        solver.set_effort("deep")
        with pytest.raises(RuntimeError):
            solver.solve_problem({})
        assert solver.effort_tier() == "deep"
    finally:
        solver.set_hard_deadline(None)
        solver.set_effort(original)


def test_marathon_row_budget_bounds_one_row(solver):
    """No row may hold the deterministic pass hostage (rail: `not_attempted`)."""
    # 1000 rows, 360 s of fair share each: a row may borrow MARATHON_ROW_BORROW
    # rows' worth, never the whole remainder.
    assert solver.marathon_row_budget(360_000.0, 1000) == pytest.approx(
        solver.MARATHON_ROW_BORROW * 360.0)
    # With nobody left to starve, the last row may use everything.
    assert solver.marathon_row_budget(100.0, 1) == pytest.approx(100.0)
    # With two left, the one behind still keeps its floor.
    assert solver.marathon_row_budget(100.0, 2) == pytest.approx(
        100.0 - solver.MARATHON_ROW_MIN_SECONDS)
    # Degenerate inputs must not produce a negative or unbounded deadline.
    assert solver.marathon_row_budget(-5.0, 10) == 0.0
    assert solver.marathon_row_budget(100.0, 0) == pytest.approx(100.0)
    assert solver.marathon_row_budget(100.0, -3) == pytest.approx(100.0)
    # The floor never exceeds what is actually left.
    assert solver.marathon_row_budget(0.4, 50) == pytest.approx(0.4)


def test_marathon_row_budget_leaves_a_tail(solver):
    """Even if EVERY row burns its full allowance, the tail still gets attempts.

    The failure this replaces is unbounded: one row took the whole remainder
    and rows 2..N were never attempted. Here the worst case is a graceful
    decay, so the last row still receives a positive budget.
    """
    remaining = 360_000.0
    total = 1000
    budgets = []
    for attempted in range(total):
        budget = solver.marathon_row_budget(remaining, total - attempted)
        budgets.append(budget)
        remaining -= budget
    assert all(b >= solver.MARATHON_ROW_MIN_SECONDS for b in budgets)
    # The first row cannot take more than three rows' worth of a 1000-row run.
    assert budgets[0] == pytest.approx(solver.MARATHON_ROW_BORROW * 360.0)
    # The pass never overspends its own clock.
    assert sum(budgets) <= 360_000.0 + 1e-6
    # Most rows still get a substantial attempt, not just the floor.
    assert sum(1 for b in budgets if b >= 60.0) > 0.5 * total


def test_marathon_budget_uses_available_clock(solver):
    """The old cap returned 4.0 s no matter how much budget existed."""
    reference = solver.marathon_reference_seconds()
    tiny = solver.marathon_per_problem_budget(3600.0, 100, reference)
    huge = solver.marathon_per_problem_budget(180_000.0, 100, reference)
    assert huge > tiny
    assert huge > 4.0, "budget must scale past the old hard cap"
    assert huge <= 60.0, "but stay bounded"


def test_marathon_budget_degenerate_inputs(solver):
    reference = solver.marathon_reference_seconds()
    assert solver.marathon_per_problem_budget(0.0, 0, reference) > 0
    assert solver.marathon_per_problem_budget(0.0, 100, reference) > 0


def test_marathon_reads_its_budget_from_the_environment(solver, monkeypatch):
    """Never hardcode a per-problem Marathon budget — the reference moved.

    The vendored `rules/evaluation.md` derived it from a 3600 s Solo reference
    (~1800 s per problem at N=100) while `scripts/run_marathon.py` used 600 s
    (~300 s per problem). The organizers settled it at 5 minutes per problem on
    2026-07-31 and withdrew `compression_ratio` entirely. Anything that reads
    the environment survived that; anything that had baked in a number did not.
    """
    reference = solver.marathon_reference_seconds()
    settled = solver.marathon_per_problem_budget(30_000.0, 100, reference)
    withdrawn = solver.marathon_per_problem_budget(180_000.0, 100, reference)
    assert 0 < settled < withdrawn, "budget must track the real clock, not a constant"

    monkeypatch.setenv("MAGMA_MARATHON_REF_SECONDS_PER_PROBLEM", "300")
    assert solver.marathon_reference_seconds() == 300.0


def test_no_judge_call_outside_solo(solver):
    """Marathon has no judge channel; a call there hangs on a DEVNULL stdin.

    `marathon_runner.py` spawns the solver with `stdin=subprocess.DEVNULL` and
    `marathon_proxy.py` serves only `/v1/chat/completions`, so the proxy
    round-trip in `judge_via_solo_proxy` has nothing to talk to. Checked
    structurally because the failure mode is a silent stall that costs the whole
    run, not one row.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(solver))
    proxy_callers = {"judge_via_solo_proxy", "send_proxy_call", "load_json_line"}
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        called = {
            child.func.id
            for child in ast.walk(node)
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
        }
        hits = called & proxy_callers
        if hits and node.name not in proxy_callers | {"run_solo"}:
            offenders.append(f"{node.name} calls {sorted(hits)}")
    assert not offenders, (
        "stdin/stdout proxy traffic must stay inside run_solo: " + "; ".join(offenders))


def test_egg_saturation_polls_the_deadline_per_match(solver):
    """Both saturation engines must poll inside the e-match loop, not outside it.

    `_egg_ematch` is a recursive generator with no bound on the substitutions a
    single e-class can yield, and when the pattern is an op the loop above it
    walks every class in the graph. A deadline polled only per class is
    therefore not polled at all (rail 5f-iv). Measured 2026-08-12 on
    `normal_0823` at `fast`: `egg_probe`'s 6.0 s budget ran 40 s (6.7x) with
    zero polls and 11,346 MB of RSS, and because the loop called neither
    `deadline_expired` nor `_engine_gate` an armed memory guard never saw it.

    The multi-rule engine was fixed for this in 2026-08-11 and the single-rule
    engine — which is what every `egg_*` route actually runs — was not. Checked
    structurally because the failure mode is silent overshoot that reads exactly
    like a hard row.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(solver))
    functions = {node.name: node for node in ast.walk(tree)
                 if isinstance(node, ast.FunctionDef)}
    for name in ("egg_saturate_prove", "_egg_run_saturation"):
        assert name in functions, f"{name} vanished; update this test deliberately"
        ematch_loops = [
            node for node in ast.walk(functions[name])
            if isinstance(node, ast.For) and isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Name)
            and node.iter.func.id == "_egg_ematch"
        ]
        assert ematch_loops, f"{name}: no `for ... in _egg_ematch(...)` loop found"
        for loop in ematch_loops:
            polls = [
                child for stmt in loop.body for child in ast.walk(stmt)
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
                and child.func.id == "deadline_expired"
            ]
            assert polls, (
                f"{name}: the `for ... in _egg_ematch(...)` loop body has no "
                "deadline_expired() call — one e-class can yield unboundedly "
                "many substitutions, so an outer poll does not bound this")


def _pep701_offenders(text: str) -> list[tuple[int, str]]:
    """Lines using f-string syntax that only parses on Python 3.12+.

    A hand-rolled scanner because there is no better option available: this
    machine has 3.12 and 3.14 but no 3.11, and `ast.parse(..., feature_version=
    (3, 11))` does **not** reject PEP 701 — it was tried, it accepts
    `f"{d["k"]}"` happily, and a test built on it is vacuous. That is the whole
    reason this function exists rather than a one-line parse.

    Detects the two relaxations that are easy to write by accident: reusing the
    f-string's own quote character inside `{...}`, and a backslash inside
    `{...}`. Both are hard SyntaxErrors on 3.11.
    """
    offenders: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), 1):
        index = 0
        while index < len(line):
            char = line[index]
            if char in "\"'":
                prefix = line[max(0, index - 2):index].lower()
                quote = char
                index += 1
                if "f" not in prefix.lstrip("rb"):
                    while index < len(line) and line[index] != quote:
                        index += 2 if line[index] == "\\" else 1
                    index += 1
                    continue
                depth = 0
                while index < len(line):
                    here = line[index]
                    if here == "{":
                        depth += 1 if line[index:index + 2] != "{{" else 0
                        index += 1 if line[index:index + 2] != "{{" else 2
                        continue
                    if here == "}" and depth:
                        depth -= 1
                    elif depth and here == quote:
                        offenders.append((number, "quote reuse inside f-string"))
                        break
                    elif depth and here == "\\":
                        offenders.append((number, "backslash inside f-string expression"))
                        break
                    elif not depth and here == quote:
                        break
                    index += 1
                index += 1
                continue
            if char == "#":
                break
            index += 1
    return offenders


def test_solver_uses_no_syntax_newer_than_the_interpreter_that_grades_it():
    """The sandbox is `python:3.11-slim`; this machine's venv is 3.14.

    Syntax newer than 3.11 is not a bad row, it is a dead submission — the whole
    file fails to import and every problem is lost. PEP 701 f-strings are the
    easy one to write by accident on 3.12+, and nothing else in this gate would
    notice, because the gate itself runs on the newer interpreter locally.

    CI pins 3.11 and would catch it, but only after a push. This is the local
    half. It is a heuristic, deliberately: see `_pep701_offenders` for why the
    obvious `feature_version=(3, 11)` approach is worthless here.
    """
    import pathlib

    # Pin non-vacuity in the test itself. The first attempt at this test used
    # `ast.parse(..., feature_version=(3, 11))`, which accepts PEP 701 without
    # complaint, so it passed on code that would not have run in the sandbox.
    # A guard that cannot fail is worse than no guard: it makes the risk look
    # checked. These two lines make sure the scanner still bites.
    quote = chr(34)
    bad = "x = f" + quote + "outer {d[" + quote + "k" + quote + "]} end" + quote
    good = "x = f" + quote + "outer {d['k']} end" + quote
    assert _pep701_offenders(bad), "the PEP 701 scanner stopped detecting anything"
    assert not _pep701_offenders(good), "false positive on 3.11-legal code"

    # Only the shipped file matters — it is the one the sandbox imports.
    source = pathlib.Path(__file__).resolve().parents[1] / "solver" / "solver.py"
    offenders = _pep701_offenders(source.read_text(encoding="utf-8"))
    assert not offenders, (
        f"solver.py uses Python 3.12+ f-string syntax at {offenders[:5]} — the "
        "grading sandbox is python:3.11-slim, so this fails the entire "
        "submission, not one row")


def test_completion_collapse_certificate_handles_the_variable_on_either_side(solver):
    """`_kb_collapse_witness` has two branches and the corpus only exercises one.

    A derived `t = v` with `v` not occurring in `t` forces the magma trivial.
    Which *side* the bare variable lands on depends on how KBO happened to orient
    the equation, and on every row measured to date (32 collapses across the
    20k-ETP-sample frontier) it is the right-hand side. The left-hand branch is
    therefore live code with zero coverage, which is exactly the shape that ships
    broken: it emits `.symm` in the opposite place, and nothing would have caught
    it being wrong.

    Built by mirroring a real collapse rather than hand-writing one, so the
    equation and its recorded proof stay genuine: reversing a rewrite chain and
    negating each step's direction is the same inverse the engine itself takes in
    `goal_join`.
    """
    eq1 = solver.parse_equation("x = y ◇ (((z ◇ x) ◇ x) ◇ y)")
    eq2 = solver.parse_equation("x = y ◇ ((z ◇ w) ◇ w)")

    comp = solver._KBCompletion([(eq1["lhs"], eq1["rhs"])],
                                deadline=solver.local_deadline(10.0))
    comp.seed()
    collapse = None
    while collapse is None:
        equation = comp.step()
        assert equation is not None, "no collapse derived; the fixture row changed"
        witness = solver._kb_collapse_witness(equation)
        if witness is not None:
            collapse = (equation, witness)
            break
        comp.interreduce(equation)
        comp.superpose(equation)

    equation, (_side, var, var_on_rhs) = collapse
    assert var_on_rhs, "fixture no longer produces the right-hand-side branch"

    forward = solver._kb_collapse_certificate(
        comp, equation, var, True, eq1, eq2)
    assert forward is not None
    oracles.check_true_lemma_chain_certificate(forward, eq1, eq2)

    # Mirror it: swap the sides and invert the chain. Same fact, same proof,
    # opposite branch.
    mirrored = solver._KBEquation(
        comp.next_id, equation.rhs, equation.lhs,
        [(path, eid, subst, -direction)
         for (path, eid, subst, direction) in reversed(equation.chain or [])])
    comp.eqs[mirrored.eid] = mirrored
    comp.next_id += 1

    witness = solver._kb_collapse_witness(mirrored)
    assert witness is not None, "mirroring lost the collapse"
    assert witness[2] is False, "mirroring did not reach the left-hand branch"

    backward = solver._kb_collapse_certificate(
        comp, mirrored, witness[1], False, eq1, eq2)
    assert backward is not None, "left-hand branch produced no certificate"
    oracles.check_true_lemma_chain_certificate(backward, eq1, eq2)


def test_completion_bridge_multi_fill_reaches_goal_constants(solver):
    """The goal bridge must try the goal's own skolem constants as fills.

    A single fill (the smallest constant of the matched subterm) provably loses
    whole families: on the 530k-row order-4 frontier (2026-08-26), every eq1
    `3569`/`3983`/`2854` miss closes under multi-fill and none closes without
    it. This row is one of the two former "structurally unreachable" survivors
    — eq1 saturates to a handful of rules in ~0.1 s, and the goal's
    fresh-variable-heavy RHS is only reachable when an unbound target-side
    variable is instantiated at a goal constant the matched subterm does not
    mention. Regression fixture, not solver policy (rail 9): the content is
    the equations, no id is consulted anywhere.
    """
    eq1 = solver.parse_equation("x ◇ y = y ◇ ((z ◇ y) ◇ x)")
    eq2 = solver.parse_equation("(x ◇ y) ◇ x = (z ◇ w) ◇ u")
    found = solver.completion_prove(eq1, eq2, time_budget=20.0)
    assert found is not None, "multi-fill bridge no longer closes the fixture row"
    route, code = found
    assert route == "true:completion:bridge"
    oracles.check_true_lemma_chain_certificate(code, eq1, eq2)

# The single-rule / multi-rule engines are twins by construction, and every
# bounding fix so far has landed on exactly one of the pair.
_ENGINE_TWINS = (
    ("_EggProver.explain", "_EggProverMulti.explain_multi"),
    ("_egg_bridge_steps", "_egg_bridge_steps_multi"),
    ("_egg_shorten_steps", "_egg_shorten_steps_multi"),
    ("_egg_render_steps", "_egg_render_steps_multi"),
)


def test_engine_twins_take_the_same_bounding_parameters(solver):
    """A twin that takes a `deadline` its pair does not is a bug, not a style.

    This is the cheapest possible guard against a mistake this repo has now made
    five times (rail 5f-v). Every instance had the same signature: two functions
    doing the same job over one rule and over many, one of them bounded and the
    other not.

    - 2026-08-11: `_egg_run_saturation` got a per-match poll, `egg_saturate_prove`
      did not. Cost: `normal_0823` ran 40 s on a 6 s budget at 11 GB RSS.
    - 2026-08-21: `_egg_bridge_steps_multi` had a `deadline` *and* a state cap,
      above a comment explaining that O(states^2) over a 1500-step chain is ~22M
      pattern matches; `_egg_bridge_steps` had neither. `explain_multi` polled a
      deadline; `explain` took no such parameter. Cost: 9 of the 205 order-5
      skip rows overran a 300 s row budget, one by 11.8x.

    Both times the fix was written down in the *other* twin's own comment before
    the bug was found. Checking the signatures costs milliseconds.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(solver))
    found: dict[str, ast.FunctionDef] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    found[f"{node.name}.{child.name}"] = child
        elif isinstance(node, ast.FunctionDef):
            found.setdefault(node.name, node)

    def params(fn: ast.FunctionDef) -> set[str]:
        args = fn.args
        return {a.arg for a in args.args + args.kwonlyargs + args.posonlyargs}

    def body_names(fn: ast.FunctionDef) -> set[str]:
        return {node.id for node in ast.walk(fn) if isinstance(node, ast.Name)}

    def bounds(fn: ast.FunctionDef) -> set[str]:
        """Which bounds this function *actually enforces*, however it gets them.

        Taking the parameter is one way; reading the module constant directly is
        another, and equally bounded — `_egg_render_steps` enforces
        `EGG_MAX_PROOF_BYTES` inline while its twin takes it as `max_bytes`.
        That is a style difference, not a missing bound, so it must not fail.
        What must fail is a twin that enforces *nothing*.
        """
        names = params(fn) | body_names(fn)
        out = set()
        if {"deadline", "deadline_expired", "local_deadline"} & names:
            out.add("time")
        if any(n == "max_bytes" or ("MAX" in n and ("BYTE" in n or "STATE" in n))
               for n in names):
            out.add("size")
        return out

    offenders = []
    for one, many in _ENGINE_TWINS:
        if one not in found or many not in found:
            continue  # a rename is a deliberate act; the poll test covers the rest
        missing = bounds(found[many]) - bounds(found[one])
        if missing:
            offenders.append(
                f"{many} enforces a {sorted(missing)} bound and its twin "
                f"{one} enforces none")
    assert not offenders, (
        "engine twins must be bounded the same way (rail 5f-v): "
        + "; ".join(offenders))

# ---------------------------------------------------------------------------
# LLM candidate parsing: the boundary where model output becomes a submission.
# ---------------------------------------------------------------------------

def _llm_problem(solver, eq1: str, eq2: str) -> dict:
    return {"id": "t", "eq1_id": 1, "eq2_id": 2, "equation1": eq1, "equation2": eq2}


def test_llm_false_table_accepted_when_genuine(solver):
    """comm holds on XOR, left_zero fails on it -> a real counterexample."""
    problem = _llm_problem(solver, LAWS["comm"], LAWS["left_zero"])
    text = '{"verdict":"false","table":[[0,1],[1,0]]}'
    candidate, reason = solver.candidate_from_llm_text_with_reason(problem, text)
    assert reason == "ok", reason
    assert candidate["answer"]["verdict"] == "false"
    eq1 = solver.parse_equation(LAWS["comm"])
    eq2 = solver.parse_equation(LAWS["left_zero"])
    oracles.check_false_certificate(candidate["answer"]["code"], eq1, eq2)


def test_llm_false_table_rejected_when_bogus(solver):
    """A table that does not satisfy eq1 must never reach the judge."""
    problem = _llm_problem(solver, LAWS["comm"], LAWS["left_zero"])
    text = '{"verdict":"false","table":[[0,0],[1,1]]}'   # LP: not commutative
    candidate, reason = solver.candidate_from_llm_text_with_reason(problem, text)
    assert candidate is None
    assert reason == "false_table_not_counterexample"


def test_llm_false_table_rejected_when_malformed(solver):
    problem = _llm_problem(solver, LAWS["comm"], LAWS["left_zero"])
    for table, expected in (
        ("[[0,1],[1]]", "false_table_invalid_shape"),
        ("[[0,5],[1,0]]", "false_table_invalid_shape"),   # entry out of range
    ):
        candidate, reason = solver.candidate_from_llm_text_with_reason(
            problem, '{"verdict":"false","table":%s}' % table)
        assert candidate is None, table
        assert reason == expected, (table, reason)


def test_llm_chain_accepted_and_kernel_verifiable(solver):
    """A correct one-step chain becomes a certificate the kernel accepts."""
    problem = _llm_problem(solver, "x = x ◇ y", "x = x ◇ (x ◇ y)")
    eq1 = solver.parse_equation(problem["equation1"])
    eq2 = solver.parse_equation(problem["equation2"])
    text = json.dumps({"verdict": "true", "proof_kind": "guided_chain",
                       "chain": ["x", "x ◇ (x ◇ y)"]})
    candidate, reason = solver.candidate_from_llm_text_with_reason(problem, text)
    if candidate is None:
        pytest.skip(f"solver could not bridge the sample chain: {reason}")
    code = candidate["answer"]["code"]
    if oracles.classify_true_certificate(code) == "exact_expr":
        oracles.check_true_exact_certificate(code, eq1, eq2)


def test_llm_bad_chain_never_yields_an_unsound_certificate(solver):
    """A chain with the wrong start must not be accepted *as given*.

    The solver may still salvage the row by treating the model's terms as
    seeds for its own closure search - that is the designed degradation. What
    must never happen is an unsound certificate, so assert on soundness rather
    than on rejection.
    """
    problem = _llm_problem(solver, "x = x ◇ y", "x = x ◇ (x ◇ y)")
    eq1 = solver.parse_equation(problem["equation1"])
    eq2 = solver.parse_equation(problem["equation2"])
    text = json.dumps({"verdict": "true", "chain": ["y", "x ◇ (x ◇ y)"]})
    candidate, _reason = solver.candidate_from_llm_text_with_reason(problem, text)
    if candidate is None:
        return
    assert candidate["route"] != "llm:true:rewrite_chain", \
        "a chain with the wrong start must not be accepted as a chain"
    code = candidate["answer"]["code"]
    if oracles.classify_true_certificate(code) == "exact_expr":
        oracles.check_true_exact_certificate(code, eq1, eq2)


def test_llm_garbage_and_prose_rejected(solver):
    problem = _llm_problem(solver, LAWS["comm"], LAWS["left_zero"])
    for text in ("I think this is true because magmas are associative.",
                 "", "{not json", '{"verdict":"maybe"}'):
        candidate, reason = solver.candidate_from_llm_text_with_reason(problem, text)
        assert candidate is None, text
        assert reason


def test_llm_raw_true_disabled_in_marathon_lane(solver):
    """Marathon must not accept unverified raw Lean from the model."""
    problem = _llm_problem(solver, LAWS["comm"], LAWS["left_zero"])
    text = json.dumps({"verdict": "true",
                       "code": "import JudgeProblem\n\ndef submission : Goal := by\n"
                               "  intro G _ h\n  intro x y\n  exact h x y\n"})
    candidate, reason = solver.candidate_from_llm_text_with_reason(
        problem, text, allow_raw_true=False)
    assert candidate is None
    assert reason == "raw_true_disabled"


def test_llm_banned_tactics_rejected(solver):
    for tactic in ("simp_all", "aesop", "grind", "sorry"):
        code = ("import JudgeProblem\n\ndef submission : Goal := by\n"
                f"  intro G _ h\n  {tactic}\n")
        assert not solver.sanitize_lean_code(code, verdict="true"), tactic


def test_solver_certificate_templates_are_tactic_free(solver):
    """The solver must hold itself to the rule it imposes on the LLM.

    `sanitize_lean_code` rejects `grind`/`simp`/`aesop` from LLM output, but it
    never sees solver-generated code — which is how a `grind` step lived inside
    `true:right_projection_collapse:left_pair_tail` until 2026-07-29. A tactic
    step cannot be proof-kernel checked, so it is invisible to every offline
    gate and rests on a tactic the cloud judge has rejected in the field.

    Static counterpart to the per-row `check_no_banned_tactics` call in
    `test_golden.py` / `audit_corpus.py`: this catches a template that no
    currently-pinned row happens to exercise.
    """
    import inspect

    source_path = Path(inspect.getfile(solver))
    lines = source_path.read_text(encoding="utf-8").splitlines()

    offenders: list[tuple[int, str]] = []
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#") or not oracles._BANNED_TACTIC_RE.search(line):
            continue
        # Emitted Lean is always a string literal carrying an explicit newline.
        # That excludes the PROMPT prose (which names the tactics in order to
        # forbid them) and the BANNED_LEAN_RE pattern (raw regex, no `\n`).
        if r"\n" not in line:
            continue
        # `grind_true_certificate` is the one sanctioned emitter: it backs
        # `true:narrow_grind` and the Solo last-resort fallback, both documented.
        context = "".join(lines[max(0, lineno - 30):lineno])
        if "def grind_true_certificate" in context:
            continue
        # Judge-pinned certificates are data, not templates: every `aus_e*`
        # entry is byte-pinned in `judge_verified_certs.jsonl` (the pin is the
        # evidence, rail 5h) and closes its case tree with `simp`.
        if "'aus_e" in line or '"aus_e' in line:
            continue
        offenders.append((lineno, stripped[:110]))

    assert not offenders, (
        "solver source emits a banned tactic outside grind_true_certificate:\n"
        + "\n".join(f"  line {n}: {t}" for n, t in offenders))


def test_check_no_banned_tactics_flags_and_exempts(solver):
    body = ("import JudgeProblem\n\ndef submission : Goal := by\n"
            "  intro G _ h\n  grind\n")
    with pytest.raises(OracleError):
        oracles.check_no_banned_tactics(body, "true:some_route")
    # The two documented exemptions must stay usable.
    for allowed in sorted(oracles.GRIND_ALLOWED_ROUTES):
        oracles.check_no_banned_tactics(body, allowed)
    # A clean certificate passes on any route.
    oracles.check_no_banned_tactics(
        "import JudgeProblem\n\ndef submission : Goal := by\n"
        "  intro G _ h\n  intro x y\n  exact h x y\n", "true:rewrite")


def test_constraint_countermodel_is_sound_and_renderable(solver, problems_by_id):
    """The constraint search may only return verified, shippable witnesses.

    `hard2_0009` is the canary: no canned family, affine family, `Fin 2..3`
    enumeration or randomized hill-climb finds its witness, and the playground
    answered it `true` (label FALSE) at 787 s. Its countermodel is order 8.
    """
    problem = problems_by_id.get("hard2_0009")
    if problem is None:
        pytest.skip("hard2_0009 not present locally")
    eq1 = solver.parse_equation(str(problem["equation1"]))
    eq2 = solver.parse_equation(str(problem["equation2"]))
    solver.set_effort("fast")
    found = solver.constraint_countermodel(eq1, eq2)
    assert found is not None, "constraint search lost hard2_0009"
    n, table, route = found
    assert route.startswith("false:constraint_fin")
    assert n <= solver.MAX_WITNESS_ORDER
    assert solver.table_is_renderable(table)
    # Independent re-verification through the oracle, not the solver's own gate.
    assert oracles.equation_holds(
        eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table)
    assert not oracles.equation_holds(
        eq2["lhs"], eq2["rhs"], list(eq2["variables"]), table)
    oracles.check_false_certificate(solver.false_certificate(n, table), eq1, eq2)


def test_constraint_countermodel_finds_nothing_on_a_true_row(solver, problems_by_id):
    """A negative control: a TRUE row has no countermodel, so the search must
    report none. Without this, a propagation bug that makes the search always
    fail looks identical to a search that is merely conservative."""
    problem = problems_by_id.get("hard2_0003")
    if problem is None or problem.get("answer") is not True:
        pytest.skip("control row unavailable")
    eq1 = solver.parse_equation(str(problem["equation1"]))
    eq2 = solver.parse_equation(str(problem["equation2"]))
    solver.set_effort("fast")
    assert solver.constraint_countermodel(eq1, eq2) is None


def test_egg_collapse_certificate_is_kernel_checkable(solver, problems_by_id):
    """`true:egg_collapse` must emit the kernel-checkable `lemma` shape.

    ETP mining showed 14 of 31 unsolved TRUE rows factor through `x = y`; this
    route proves that collapse where the critical-pair closure cannot.
    `normal_0062` is the cheapest measured instance (~12 s at standard effort).
    """
    problem = problems_by_id.get("normal_0062")
    if problem is None:
        pytest.skip("normal_0062 not present locally")
    eq1 = solver.parse_equation(str(problem["equation1"]))
    eq2 = solver.parse_equation(str(problem["equation2"]))
    solver.set_effort("standard")
    solver.clear_term_caches()
    found = solver.egg_collapse_route(eq1, eq2)
    if found is None:
        pytest.skip("egg_collapse did not fire within its budget on this machine")
    route, code = found
    assert route == "true:egg_collapse"
    assert oracles.classify_true_certificate(code) == "lemma"
    # Both halves replayed: collapse from eq1, goal from the stated collapse law.
    oracles.check_true_lemma_certificate(code, eq1, eq2)
    oracles.check_no_banned_tactics(code, route)


def test_egg_ladder_certificate_is_kernel_checkable(solver, problems_by_id):
    """`true:egg_ladder` must emit the kernel-checkable `lemma_chain` shape.

    The ladder derives a small law, binds it with `have`, and saturates again
    with that law in scope. `normal_0090` is the motivating row: single-rule egg
    cannot reach right projection there in 60 s, and the ladder closes the goal
    in ~17 s at `fast`. Every rung is verified independently by the kernel, so
    an unsound rung cannot hide behind a sound final step.
    """
    problem = problems_by_id.get("normal_0090")
    if problem is None:
        pytest.skip("normal_0090 not present locally")
    eq1 = solver.parse_equation(str(problem["equation1"]))
    eq2 = solver.parse_equation(str(problem["equation2"]))
    solver.set_effort("fast")
    solver.clear_term_caches()
    found = solver.egg_ladder_route(eq1, eq2)
    if found is None:
        pytest.skip("egg_ladder did not fire within its budget on this machine")
    route, code = found
    assert route.startswith("true:egg_ladder:")
    assert oracles.classify_true_certificate(code) == "lemma_chain"
    oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
    oracles.check_no_banned_tactics(code, route)


def test_lemma_chain_oracle_rejects_a_rung_that_is_not_proved(solver):
    """A ladder is only as sound as the weakest rung, so the oracle must check
    each `have` body against its own stated law rather than trusting the chain.

    Mutation test: build a valid two-part chain, then change one rung's
    *statement* while leaving its proof alone. That is exactly what a builder bug
    would produce — a proof of one law presented as another — and it must be
    rejected even though the final step still looks right.
    """
    eq1 = solver.parse_equation("x = y ◇ x")
    eq2 = solver.parse_equation("x ◇ y = y")
    lemma = solver.lemma_goal("a ◇ b = b")
    goal_expr = solver.lemma_applies_to_goal(lemma, eq2)
    assert goal_expr is not None
    # `lemma_applies_to_goal` always cites `hlem`, which is why the final block
    # carries that name and the rungs are `hlem0..`; build through the real
    # builder so the test cannot drift from that contract.
    rung = solver.lemma_goal("a ◇ a = a")
    code = solver.lemma_chain_certificate(
        [("hlem0", rung, "(h a a).symm")], lemma, "(h b a).symm",
        list(eq2["variables"]), goal_expr)
    assert oracles.classify_true_certificate(code) == "lemma_chain"
    oracles.check_true_lemma_chain_certificate(code, eq1, eq2)

    lied = code.replace("(a ◇ b) = b := by", "(a ◇ b) = a := by")
    assert lied != code
    with pytest.raises(OracleError):
        oracles.check_true_lemma_chain_certificate(lied, eq1, eq2)

    # And a goal citing a rung that was never proved must not slip through.
    dangling = code.replace("exact hlem ", "exact hlem9 ")
    assert dangling != code
    with pytest.raises(OracleError):
        oracles.check_true_lemma_chain_certificate(dangling, eq1, eq2)


def test_goal_generalizations_really_prove_the_goal(solver, problems_by_id):
    """Every generalisation must close the goal by instantiation alone.

    The whole point of the mechanism is that no chain search is needed — the
    proof is `hlem <args>` — which also means nothing else checks it. So each
    returned pair is verified here with the independent kernel, using the law as
    the hypothesis exactly as the certificate scopes it.
    """
    for row_id in ("hard3_0214", "hard3_0314", "hard2_0073"):
        problem = problems_by_id.get(row_id)
        if problem is None:
            continue
        eq2 = solver.parse_equation(str(problem["equation2"]))
        pivots = solver.goal_generalization_pivots(eq2)
        assert pivots, f"no generalisation found for {row_id}"
        for name, law, proof in pivots:
            kernel = ProofKernel(
                list(law["variables"]), law["lhs"], law["rhs"],
                set(eq2["variables"]), "hlem")
            proved = kernel.prove(proof)
            assert proved == (eq2["lhs"], eq2["rhs"]), (
                f"{row_id}/{name}: {law['text']} with {proof} proved "
                f"{proved}, not the goal")
            # A generalisation must be strictly more general: the goal must be an
            # instance of it, and it must not simply *be* the goal.
            assert solver.canonical_law_key(law) != solver.canonical_law_key(eq2)


def test_goal_generalization_finds_the_etp_pivot_for_hard3_0214(solver, problems_by_id):
    """`hard3_0214`'s goal is `x = ((x ◇ y) ◇ (z ◇ w)) ◇ y`. Abstracting only the
    middle subterm gives `a = ((a ◇ b) ◇ c) ◇ b` — ETP's Eq267, a genuine pivot
    for that row and weaker than the maximal generalisation `triple_left`, which
    is measured unprovable there. Losing the *partial* abstractions would quietly
    reduce this mechanism to the fixed pivot list it was built to escape."""
    problem = problems_by_id.get("hard3_0214")
    if problem is None:
        pytest.skip("hard3_0214 not present locally")
    eq2 = solver.parse_equation(str(problem["equation2"]))
    wanted = solver.canonical_law_key(solver.lemma_goal("a = ((a ◇ b) ◇ c) ◇ b"))
    keys = {solver.canonical_law_key(law)
            for _n, law, _p in solver.goal_generalization_pivots(eq2)}
    assert wanted in keys


def test_egg_multi_render_rejects_a_corrupted_step(solver):
    """The multi-rule renderer must replay every step, not trust the e-graph.

    Mutation test: take a valid one-step proof and move the rewrite position.
    The step no longer matches the term it claims to rewrite, so the renderer
    has to fail closed rather than emit a proof of something else.
    """
    eq1 = solver.parse_equation("x = y ◇ x")
    rule = solver._egg_rule_from(eq1, "h")
    a, b = ("var", "a"), ("var", "b")
    start = a
    target = ("op", b, a)
    subst = {"X": a, "Y": b}
    good = solver._egg_render_steps_multi(
        start, target, [((), 0, subst, False)], [rule], ["a", "b"],
        max_bytes=10_000)
    assert good is not None
    # Same step, but claimed at a position that does not exist in `start`.
    assert solver._egg_render_steps_multi(
        start, target, [(("L",), 0, subst, False)], [rule], ["a", "b"],
        max_bytes=10_000) is None
    # Same step, but pointing at a rule index that is not in the rule set.
    assert solver._egg_render_steps_multi(
        start, target, [((), 7, subst, False)], [rule], ["a", "b"],
        max_bytes=10_000) is None


def test_egg_multi_shorten_rejects_an_unbound_substitution(solver):
    """A step whose substitution misses a rule variable must be rejected.

    `_egg_substitute` would raise `KeyError` on it; the shortener has to catch
    that shape up front so the route returns None instead of crashing the row.
    """
    eq1 = solver.parse_equation("x = y ◇ x")
    rule = solver._egg_rule_from(eq1, "h")
    incomplete = {"X": ("var", "a")}  # "Y" missing
    assert solver._egg_shorten_steps_multi(
        ("var", "a"), [((), 0, incomplete, False)], [rule]) is None


def test_lemma_closes_goal_sees_a_reverse_reduction(solver, problems_by_id):
    """`lemma_applies_to_goal` only searches lhs -> rhs, and every remaining
    frontier goal is shaped `x = <big term>`, so the pivot has to reduce the
    *big* side. `hard3_0314` is the measured case: right projection closes its
    goal in three reductions, and the forward-only gate reports nothing, which
    is why the row never got an egg attempt at the law its eq1 is equivalent to.
    """
    problem = problems_by_id.get("hard3_0314")
    if problem is None:
        pytest.skip("hard3_0314 not present locally")
    eq2 = solver.parse_equation(str(problem["equation2"]))
    right = solver.lemma_goal("a ◇ b = b")
    assert solver.lemma_applies_to_goal(right, eq2) is None
    expr = solver.lemma_closes_goal(right, eq2)
    assert expr is not None
    # A permissive gate is worthless if the expression it hands back is not a
    # real proof: the `.symm` wrapper has to make the reversed chain prove the
    # goal in the stated direction. Checked by the independent kernel, with the
    # pivot standing in as the hypothesis exactly as the certificate scopes it.
    kernel = ProofKernel(
        list(right["variables"]), right["lhs"], right["rhs"],
        set(eq2["variables"]), "hlem")
    assert kernel.prove(expr) == (eq2["lhs"], eq2["rhs"])


def test_constraint_countermodel_reaches_five_variable_rows(solver, problems_by_id):
    """`hard2_0092` has an order-5 countermodel the search finds in ~0.3 s, and
    a blanket `> 4 variables -> return None` gate meant it never looked (rail
    5f, third instance). The wide tier now bounds cost per order instead."""
    problem = problems_by_id.get("hard2_0092")
    if problem is None:
        pytest.skip("hard2_0092 not present locally")
    eq1 = solver.parse_equation(str(problem["equation1"]))
    eq2 = solver.parse_equation(str(problem["equation2"]))
    assert len(eq1["variables"]) == 5
    solver.set_effort("fast")
    found = solver.constraint_countermodel(
        eq1, eq2, orders=(5,), time_budget=30.0, per_order=True,
        max_variables=solver.CONSTRAINT_WIDE_MAX_VARIABLES)
    assert found is not None
    n, table, route = found
    assert n == 5 and route == "false:constraint_fin5"
    # Never trusted: the table must genuinely satisfy eq1 and refute eq2.
    assert solver.table_is_counterexample(eq1, eq2, table)
    oracles.check_false_certificate(solver.false_certificate(n, table), eq1, eq2)


def test_constraint_cheap_tier_still_skips_five_variable_rows(solver):
    """The cheap tier runs on *every* row before the TRUE engines, and 168 of
    the corpus's five- and six-variable rows are TRUE, where no witness exists.
    Widening it would spend budget on all of them, so it stays at 4."""
    eq1 = solver.parse_equation("x ◇ (y ◇ z) = (w ◇ u) ◇ u")
    eq2 = solver.parse_equation("x ◇ (y ◇ z) = (y ◇ w) ◇ u")
    assert solver.CONSTRAINT_CHEAP_MAX_VARIABLES == 4
    assert solver.constraint_countermodel(eq1, eq2) is None


def test_constraint_skipped_order_does_not_count_as_exhausted(solver):
    """An order skipped for cost was never searched, so the search is not
    exhaustive — and `constraint_search_exhausted()` is what licenses a
    speculative TRUE verdict (rail 5). Reading "skipped" as "searched" would
    turn a cost cap into a wrong answer."""
    eq1 = solver.parse_equation("x ◇ (y ◇ z) = (w ◇ u) ◇ u")
    eq2 = solver.parse_equation("x ◇ (y ◇ z) = (y ◇ w) ◇ u")
    solver.set_effort("fast")
    solver.reset_constraint_evidence()
    # Every order here exceeds the instance cap for a 5-variable row.
    assert solver.constraint_countermodel(
        eq1, eq2, orders=(9, 10), time_budget=5.0,
        max_variables=solver.CONSTRAINT_WIDE_MAX_VARIABLES) is None
    assert not solver.constraint_search_exhausted()


def test_max_rec_depth_is_driven_by_decide_cost_not_order(solver):
    """`hard2_0092`'s order-6 witness, and the rule it taught us.

    A `Fin 6` table against a 5-variable goal is 6**5 = 7,776 `decideFin!`
    applications, and the judge **rejected** it (`LEAN_REJECTED`) without
    `set_option maxRecDepth`, then accepted the identical table with it
    (verified against the real judge, 2026-08-11). The same table against a
    4-variable goal, and a `Fin 5` table against the same 5-variable goal
    (3,125 applications), are accepted either way.

    So the trigger is `n ** variables`, not the order — the same mistake the
    retired order-10 ceiling made (rail 3b-ii). What must never happen again is a
    high-variable witness going out without the option, so that is what is pinned.
    """
    eq1 = solver.parse_equation("x ◇ (y ◇ z) = (w ◇ u) ◇ u")
    eq2 = solver.parse_equation("x ◇ (y ◇ z) = (y ◇ w) ◇ u")
    order6 = [[2, 3, 3, 3, 2, 3], [2, 3, 3, 3, 2, 3], [3, 5, 3, 3, 3, 3],
              [3, 3, 3, 3, 3, 3], [2, 3, 3, 3, 2, 3], [2, 3, 3, 3, 2, 3]]
    assert solver.table_is_counterexample(eq1, eq2, order6)
    assert solver.witness_decide_applications(6, eq1, eq2) == 6 ** 5

    deep = solver.false_certificate(
        6, order6, decide_applications=solver.witness_decide_applications(6, eq1, eq2))
    assert "set_option maxRecDepth" in deep

    # Order 5 at the same variable count is under the measured band, and the
    # whole accepted corpus is orders <= 6 with <= 4 variables: both must stay
    # byte-identical to what the judge has already accepted.
    order5 = [[2, 3, 3, 3, 3], [2, 3, 3, 3, 3], [3, 4, 3, 3, 3],
              [3, 3, 3, 3, 3], [2, 3, 3, 3, 3]]
    shallow = solver.false_certificate(
        5, order5, decide_applications=solver.witness_decide_applications(5, eq1, eq2))
    assert "set_option maxRecDepth" not in shallow
    assert shallow == solver.false_certificate(5, order5)

    four_vars = solver.parse_equation("x ◇ (y ◇ z) = (w ◇ y) ◇ z")
    assert solver.witness_decide_applications(6, four_vars) == 6 ** 4
    plain = solver.false_certificate(
        6, order6,
        decide_applications=solver.witness_decide_applications(6, four_vars))
    assert "set_option maxRecDepth" not in plain
    assert plain == solver.false_certificate(6, order6)


def test_solve_problem_guards_a_high_variable_witness(solver, problems_by_id):
    """End to end: whatever route claims `hard2_0092`, the emitted certificate
    must carry `maxRecDepth` if its decide cost is above the measured band. The
    renderer is reached through `make_false_answer`, so a plumbing break here is
    invisible to the unit test above."""
    problem = problems_by_id.get("hard2_0092")
    if problem is None:
        pytest.skip("hard2_0092 not present locally")
    eq1 = solver.parse_equation(str(problem["equation1"]))
    eq2 = solver.parse_equation(str(problem["equation2"]))
    solver.set_effort("fast")
    solver.clear_term_caches()
    record = solver.solve_problem(problem, false_time_budget=2.0)
    if record is None or record["answer"]["verdict"] != "false":
        pytest.skip("no FALSE witness claimed on this machine")
    code = record["answer"]["code"]
    oracles.check_false_certificate(code, eq1, eq2)
    n = int(re.search(r"Fin (\d+)", code).group(1))
    if solver.witness_decide_applications(n, eq1, eq2) > \
            solver.DECIDE_MAX_REC_DEPTH_APPLICATIONS:
        assert "set_option maxRecDepth" in code


def test_multi_digit_table_never_uses_the_finOpTable_shape(solver):
    """The `hard2_0051` witness, and the rendering rule it taught us.

    `MemoFinOp.finOpTable` keeps one value per digit character, so a cell
    holding `10` is read as two cells. This `Fin 13` witness was mathematically
    correct, passed both oracles, and was still `LEAN_REJECTED` with `decide`
    calling the conjunction false — Lean saw a different table.

    The fix is a different renderer, not a smaller witness: the table is now
    emitted with an inlined `List.getD` lookup, which the real judge accepted in
    5.8 s (2026-07-31). What must never happen again is this table going out in
    the `finOpTable` shape, so that is what is pinned here.
    """
    n = 13
    table = [[(7 * i + 7 * j) % n for j in range(n)] for i in range(n)]
    eq1 = solver.parse_equation("x = (y ◇ ((y ◇ x) ◇ x)) ◇ y")
    eq2 = solver.parse_equation("x ◇ (x ◇ y) = z ◇ (z ◇ y)")
    assert oracles.equation_holds(
        eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table)
    assert not oracles.equation_holds(
        eq2["lhs"], eq2["rhs"], list(eq2["variables"]), table)

    code = solver.false_certificate(n, table)
    assert "finOpTable" not in code, "multi-digit table rendered with the digit parser"
    # `List.getD` was the only alternative until 2026-08-27. This magma is
    # linear, so `formula_op_expr` now recognises it and it ships as ~380 bytes
    # of arithmetic instead — judge-accepted, and 7x cheaper for the judge than
    # the table of the same magma (order 17 A/B: 1,044 B / 19.7 s -> 382 B /
    # 2.8 s). What this test pins is unchanged: whatever shape is chosen, it
    # must not be the digit parser, and the oracle below must be able to read
    # the magma back out of the certificate.
    assert "List.getD" in code or "Fin.mk" in code
    assert solver.table_is_renderable(table)
    assert solver.table_is_counterexample(eq1, eq2, table)
    oracles.check_false_certificate(code, eq1, eq2)

    # The old failure mode itself: if this table ever *were* rendered through
    # finOpTable, the oracle must still catch it.
    with pytest.raises(OracleError):
        oracles.check_false_certificate(
            solver.false_certificate_memo(n, table), eq1, eq2)


def test_orders_within_the_legacy_envelope_keep_their_shape(solver):
    """Lifting the ceiling must not restyle a single already-working row.

    Every judge-accepted FALSE certificate to date is a `finOpTable` table at
    order <= 10. Those keep that exact shape; `List.getD` is for what was
    previously unreachable.
    """
    for n in range(2, solver.LEGACY_MAX_WITNESS_ORDER + 1):
        table = [[(i + j) % n for j in range(n)] for i in range(n)]
        code = solver.false_certificate(n, table)
        assert "finOpTable" in code and "List.getD" not in code, (
            f"order {n} changed rendering shape")


def test_no_complete_table_route_exceeds_the_order_ceiling(solver):
    """Every *complete-table* engine's order constants must stay <= 25.

    25 is the edge of the envelope the real judge has actually accepted: an
    order-25 table renders to 1,972 bytes of the 20,000-byte FALSE cap, and a
    3-variable goal cost 30.2 s of the 300 s Lean timeout. Neither limit binds
    at 25 any more (see MAX_WITNESS_ORDER), so it is now our bound, not a
    derived one. `WIDE_DOMAIN_ORDERS` legally
    exceeds it because that engine caps cell *values*, not order — see
    `test_wide_domain_orders_are_value_capped_not_order_capped`.
    """
    assert solver.MAX_WITNESS_ORDER == 25
    assert solver.LEGACY_MAX_WITNESS_ORDER == 10
    for name in ("CONSTRAINT_ORDERS", "CONSTRAINT_WIDE_ORDERS",
                 "AFFINE_LINEAR_SIZES", "AFFINE_QUADRATIC_SIZES",
                 "LARGE_LINEAR_SIZES", "LOCAL_MODEL_SIZES"):
        orders = getattr(solver, name)
        assert max(orders) <= solver.MAX_WITNESS_ORDER, (
            f"{name} contains an order above the measured witness ceiling: "
            f"{orders}")
    assert all(len(table) <= solver.MAX_WITNESS_ORDER
               for _name, table in solver.WITNESS_TABLES)


def test_witness_cost_gate_tracks_variables_not_just_order(solver):
    """`decideFin!` is exhaustive, so cost is `n ** variables`, not order.

    Order 25 against a 3-variable goal is 15,625 applications and measured 30.2 s
    at the real judge. The same order against a 5-variable goal is 9.7M, which
    would blow the 120 s timeout and lose the row — worse than skipping it.
    """
    two_var = solver.parse_equation("x ◇ y = y ◇ x")
    five_var = solver.parse_equation("x ◇ (y ◇ z) = (w ◇ u) ◇ x")
    table = [[(7 * i + 7 * j) % 13 for j in range(13)] for i in range(13)]
    assert solver.witness_decide_is_affordable(two_var, two_var, table)
    assert not solver.witness_decide_is_affordable(two_var, five_var, table)
    # ...but the proven envelope is never vetoed by the cost model.
    small = [[(i + j) % 10 for j in range(10)] for i in range(10)]
    assert solver.witness_decide_is_affordable(five_var, five_var, small)


def test_witness_check_applies_the_shippability_gate(solver):
    """`witness_check` must gate on shippability, not just on the mathematics.

    It historically stopped at `eq1 holds and eq2 fails`, which was safe only
    because every family feeding it topped out at order 9. Orders 11-25 make the
    difference observable: this table is a genuine counterexample that would cost
    the judge 13**5 = 371,293 decide applications, and must still be refused.
    """
    eq1 = solver.parse_equation("x ◇ y = y ◇ x")
    five_var = solver.parse_equation("x ◇ (y ◇ z) = (w ◇ u) ◇ x")
    n = 13
    table = [[(i + j) % n for j in range(n)] for i in range(n)]
    # Genuinely a counterexample: eq1 holds, eq2 does not.
    assert oracles.equation_holds(eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table)
    assert not oracles.equation_holds(
        five_var["lhs"], five_var["rhs"], list(five_var["variables"]), table)
    # ...and still refused, by both entry points.
    assert not solver.witness_check(eq1, five_var, table)
    assert not solver.table_is_counterexample(eq1, five_var, table)
    # The model counter must still have seen it — it inspected a real model of
    # eq1, which is exactly what `constraint_search_exhausted` reasoning needs.
    assert solver.hypothesis_models_seen() > 0


def test_large_linear_family_only_emits_shippable_tables(solver):
    """Every table the new above-10 family produces must clear both judge caps."""
    # Two tuples since 2026-08-27: orders through 25 can still ship as a table,
    # orders past it exist only because `formula_op_expr` renders them as
    # arithmetic (see FORMULA_LINEAR_SIZES). `table_is_renderable` measures
    # whatever `false_certificate` actually emits, so it covers both.
    every = solver.LARGE_LINEAR_SIZES + solver.FORMULA_LINEAR_SIZES
    seen_orders = set()
    for route, table in solver.large_linear_family_tables():
        n = len(table)
        seen_orders.add(n)
        assert route.startswith("false:linear:z")
        assert n in every
        assert solver.table_is_renderable(table), f"order {n} table is unshippable"
    assert seen_orders == set(every)


def test_wide_domain_orders_are_value_capped_not_order_capped(solver):
    """`WIDE_DOMAIN_ORDERS` may exceed 10 — the invariant it must respect is
    `table_is_renderable`, not `MAX_WITNESS_ORDER`."""
    assert max(solver.WIDE_DOMAIN_ORDERS) > solver.MAX_WITNESS_ORDER
    assert solver.WIDE_DOMAIN_VALUE_CAP == 10
    # A table this engine could plausibly emit: large carrier, values < 10.
    n = max(solver.WIDE_DOMAIN_ORDERS)
    table = [[(i + j) % solver.WIDE_DOMAIN_VALUE_CAP for j in range(n)]
             for i in range(n)]
    assert solver.table_is_renderable(table)
    # Cert bytes must still clear the judge's FALSE cap.
    assert len(solver.false_certificate(n, table).encode("utf-8")) <= \
        solver.JUDGE_MAX_FALSE_CERT_BYTES


def test_bare_variable_eq1_blocks_wide_domain_search(solver):
    """`eq1: x = F(...)` can never have a wide-domain witness: the bare
    variable ranges over the full carrier, but the RHS is capped < 10, so the
    equation is unsatisfiable the moment the carrier exceeds 10. This is exactly
    the shape of every currently-unsolved FALSE row, confirmed 2026-07-29.
    """
    bare = solver.parse_equation("x = (y ◇ ((y ◇ x) ◇ x)) ◇ y")
    assert solver._eq1_has_bare_variable_side(bare)
    not_bare = solver.parse_equation("x ◇ (y ◇ z) = (w ◇ u) ◇ u")
    assert not solver._eq1_has_bare_variable_side(not_bare)

    eq2 = solver.parse_equation("x ◇ (x ◇ y) = z ◇ (z ◇ y)")
    solver.set_effort("fast")
    assert solver.constraint_countermodel_wide_domain(bare, eq2) is None


def test_nontrivial_model_count_ignores_the_trivial_magma():
    """The one-element magma satisfies every law, so it can never refute one."""
    assert oracles.nontrivial_model_count([[[0]]]) == 0
    assert oracles.nontrivial_model_count([[[0]], [[0, 1], [1, 0]]]) == 1


def test_battery_is_not_vacuous_for_central_groupoids(solver):
    """Regression: the escalation used to be unreachable dead code.

    `model_battery` pre-seeded itself with the trivial magma, so its
    `if not battery` escalation could never fire — and every equation holds in
    `Fin 1`. Result: 536/1889 official rows were "model_checked" against nothing.
    Central groupoids are the worst case (no model below order 4, models only at
    order k^2) and are the family behind the eight playground `TRUE INCORRECT`
    rows, so they are the right canary.
    """
    eq1 = solver.parse_equation("y = (x ◇ y) ◇ (y ◇ z)")
    battery = oracles.model_battery(eq1, [], fin3_samples=200, seed=17)
    assert oracles.nontrivial_model_count(battery) > 0, (
        "central-groupoid battery has no non-trivial model: "
        "model_check_true would be vacuous")
    # Whatever came back must genuinely satisfy eq1.
    for table in battery:
        assert oracles.equation_holds(
            eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table)


def test_search_models_finds_an_order_four_model(solver):
    eq1 = solver.parse_equation("y = (x ◇ y) ◇ (y ◇ z)")
    models = oracles.search_models(eq1, orders=(4,), restarts=12,
                                   max_flips=3000, time_budget=5.0)
    assert models, "hill-climb found no order-4 central groupoid"
    for table in models:
        assert len(table) == 4
        assert oracles.equation_holds(
            eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table)


def test_search_models_respects_its_time_budget(solver):
    """A law forcing the trivial magma has no model to find; failing must be cheap.

    Every `*_singleton` / `*_collapse` route asserts eq1 collapses the magma, so
    for those rows the search can only ever fail. Unbudgeted it cost up to 4.3 s
    per row across ~26% of the corpus.
    """
    eq1 = solver.parse_equation("x = y ◇ ((y ◇ (x ◇ x)) ◇ z)")
    started = time.monotonic()
    models = oracles.search_models(eq1, time_budget=0.25)
    elapsed = time.monotonic() - started
    assert not models
    assert elapsed < 2.0, f"search overran its budget: {elapsed:.2f}s"


def test_model_oracle_catches_a_false_implication(solver):
    """x ◇ y = y ◇ x does NOT imply x = x ◇ y; the model oracle must say so."""
    eq1 = solver.parse_equation(LAWS["comm"])
    eq2 = solver.parse_equation(LAWS["left_zero"])
    battery = oracles.model_battery(eq1, [], fin3_samples=200, seed=3)
    with pytest.raises(OracleError):
        oracles.model_check_true(eq2, battery)


def test_model_oracle_accepts_a_true_implication(solver):
    """x = x ◇ y  implies  x = x ◇ x (instantiate y := x)."""
    eq1 = solver.parse_equation(LAWS["left_zero"])
    eq2 = solver.parse_equation("x = x ◇ x")
    battery = oracles.model_battery(eq1, [], fin3_samples=200, seed=3)
    assert battery
    oracles.model_check_true(eq2, battery)


def test_reflexive_fast_path_requires_both_equation_ids(solver):
    """A problem with no equation ids must not be treated as `EqN => EqN`.

    `problem.get("eq1_id") == problem.get("eq2_id")` reads two absent keys as
    `None == None`, which would answer `exact h` — a guaranteed rejection — for
    every row of such a manifest. The official pipeline always supplies both
    ids, so this only pins the fail-open behaviour for anything that does not.
    """
    assert solver.is_reflexive_problem({"eq1_id": 7, "eq2_id": 7})
    assert not solver.is_reflexive_problem({"eq1_id": 7, "eq2_id": 8})
    assert not solver.is_reflexive_problem({})
    assert not solver.is_reflexive_problem({"eq1_id": None, "eq2_id": None})
    assert not solver.is_reflexive_problem({"equation1": "x = y ◇ x"})

    # End to end: an id-less non-reflexive problem must not emit `exact h`.
    record = solver.solve_problem({
        "equation1": "x = y ◇ (x ◇ ((z ◇ y) ◇ y))",
        "equation2": "x = ((y ◇ z) ◇ (z ◇ z)) ◇ x",
    })
    if record is not None:
        assert record["route"] != "true:reflexive"
        assert "exact h\n" not in record["answer"]["code"]


def test_distilled_certs_are_tactic_free_and_within_judge_caps(solver):
    """Every distilled certificate, checked directly rather than via a row.

    `test_solver_certificate_templates_are_tactic_free` scans the solver source
    line by line and skips any line without a literal `\n`, on the stated
    premise that emitted Lean is always a single-line string carrying explicit
    newlines. `DISTILLED_CERTS` breaks that premise: it stores complete Lean
    files as triple-quoted literals, so none of their physical lines contain a
    literal `\n` and all of them are skipped. That is the largest block of
    emitted Lean in the file — 65 entries — invisible to the static scan.

    Verified by mutation: injecting a bare `grind` into a distilled certificate
    body leaves the line-based scan reporting zero offenders.

    The runtime path covers most of these incidentally, because pinned rows in
    `test_judge_verified.py` happen to reach them, but nothing requires a new
    entry to be reachable from a pinned row. This needs no row at all.
    """
    assert solver.DISTILLED_CERTS, "the distilled table is empty"
    for key, (verdict, name, code) in solver.DISTILLED_CERTS.items():
        label = f"{verdict}:distilled:{name}"

        # A verdict outside VALID_VERDICTS reaches the wire only through a
        # coercing else-branch. The same typo on a TRUE entry would ship
        # verdict "false" alongside a TRUE proof.
        assert verdict in solver.VALID_VERDICTS, (
            f"{label}: verdict {verdict!r} is not one of {sorted(solver.VALID_VERDICTS)}; "
            f"the dispatch coerces anything unrecognised to FALSE")

        oracles.check_no_banned_tactics(code, label)

        size = len(code.encode("utf-8"))
        assert size <= solver.JUDGE_MAX_CODE_LENGTH, (
            f"{label}: {size} bytes, over the judge's "
            f"{solver.JUDGE_MAX_CODE_LENGTH}-byte cap")
        if verdict == "false":
            assert size <= solver.JUDGE_MAX_FALSE_CERT_BYTES, (
                f"{label}: {size} bytes, over the judge's "
                f"{solver.JUDGE_MAX_FALSE_CERT_BYTES}-byte FALSE cap")
        assert isinstance(key, tuple) and len(key) == 2, (
            f"{label}: key must be a (canonical eq1, canonical eq2) pair, not a row id "
            f"(CLAUDE.md rail 9)")


def test_solver_judge_caps_match_the_vendored_official_config():
    """The solver's mirrored judge limits must equal what the runner passes.

    These were halved on 2026-07-29 to match `judge/verify.py`'s module-level
    constants, which are only the fallback for invoking the verifier with no
    config. The deployed pipeline always passes `pipeline/config.json`'s `judge`
    block instead, and nothing detected the drift for two weeks — so the solver
    enforced half its real certificate budget and discarded every proof in the
    46-96 KB band.

    Read from the vendored JSON rather than from `judge/verify.py`, because the
    Python module is exactly the wrong source: it is the fallback, not the
    deployment.
    """
    config_path = (
        Path(__file__).resolve().parents[2]
        / "vendor" / "stage2-official" / "pipeline" / "config.json"
    )
    if not config_path.exists():  # pragma: no cover - vendored snapshot absent
        pytest.skip("vendored official config not present")
    judge = json.loads(config_path.read_text(encoding="utf-8"))["judge"]

    import solver as solver_module

    assert solver_module.JUDGE_MAX_CODE_LENGTH == judge["max_code_length"]
    assert solver_module.JUDGE_MAX_FALSE_CERT_BYTES == judge["max_false_cert_bytes"]
    # Our own caps must sit strictly under the judge's, so a certificate that
    # passes locally can never be rejected on size.
    assert solver_module.MAX_LEAN_CODE_BYTES < solver_module.JUDGE_MAX_CODE_LENGTH
    assert solver_module.MAX_FALSE_CERT_BYTES < solver_module.JUDGE_MAX_FALSE_CERT_BYTES
    # And the oracle restates the same numbers independently; if it restates a
    # stale one, the gate rejects certificates the judge would accept.
    assert oracles.JUDGE_MAX_FALSE_CERT_BYTES == judge["max_false_cert_bytes"]
