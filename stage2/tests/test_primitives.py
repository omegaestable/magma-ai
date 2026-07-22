"""Unit tests for the solver's shared soundness primitives.

These primitives underwrite every generated Lean certificate: a silent bug in
any of them ships `incorrect` submissions. Each test is small, deterministic,
and Lean-free (see oracles.py for the proof kernel used here).
"""

from __future__ import annotations

import json
import random
from itertools import product

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


@pytest.mark.parametrize("case", sorted(REAL_CERT_CASES))
@pytest.mark.parametrize("mutate", [
    pytest.param(lambda c: c.replace("h ", "h y ", 1), id="extra_hypothesis_arg"),
    pytest.param(lambda c: c.replace(".symm", "", 1), id="drop_a_symm"),
    pytest.param(lambda c: c.replace(".trans", ".symm", 1), id="trans_to_symm"),
    pytest.param(lambda c: c.replace("fun t => ", "fun t => t ◇ ", 1), id="corrupt_congr_context"),
])
def test_oracle_rejects_mutated_certificates(solver, case, mutate):
    eq1, eq2, code = _real_true_certificate(solver, case)
    mutated = mutate(code)
    if mutated == code:
        pytest.skip("mutation did not apply to this certificate")
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
    problem = _llm_problem(solver, LAWS["comm"], LAWS["left_zero"])
    for tactic in ("simp_all", "aesop", "grind", "sorry"):
        code = ("import JudgeProblem\n\ndef submission : Goal := by\n"
                f"  intro G _ h\n  {tactic}\n")
        assert not solver.sanitize_lean_code(code, verdict="true"), tactic


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
