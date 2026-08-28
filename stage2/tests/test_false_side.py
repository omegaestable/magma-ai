"""FALSE-side scheduling fixes and the order-5 witness library (2026-08-27).

Four things are pinned here, each of which cost measured rows before it was
found:

* `local_model_counterexample` armed ONE deadline before its `for n in sizes`
  loop, and the inner restart loop can only exit on that deadline -- so every
  size but the first was unreachable code (rail 5f-iii, sixth instance).
* the cheap constraint tier shared one 3 s deadline across its whole order
  schedule, and orders 8 and 9 consumed it, so 6/4/10 were never reached.
* both last-resort FALSE searches ran after all fourteen general TRUE engines,
  so a witness the local search finds in 0.2 s cost 262.9 s end to end and was
  lost by any realistic row budget.
* the order-5 misses are dominated by a small number of very special order-8/9
  quasigroups, which ship as `O5_WITNESS_TABLES`.

Every table claim below is re-checked through `oracles.equation_holds`, which
shares no code with the solver, so a bug in a solver primitive cannot hide
itself here.
"""

from __future__ import annotations

import inspect
import time

import oracles
import pytest

# (name, eq1, eq2) for every shipped O5 table: the row the table was harvested
# from. Content, not row ids (rail 9) -- kept so the library can be revalidated
# without the offline z3 harness.
O5_SOURCES = [
    ("O5W1", "x = (y * z) * ((z * z) * (x * y))", "x * y = x * (((z * y) * z) * y)"),
    ("O5W2", "x = ((y * z) * (x * z)) * (z * y)", "x * y = z * ((z * y) * (x * z))"),
    ("O5W3", "x = (y * z) * (x * ((x * z) * y))", "x * y = (y * y) * (x * (y * x))"),
    ("O5W4", "x = (y * ((z * x) * z)) * (z * y)", "x * (y * x) = (y * (z * z)) * z"),
    ("O5W5", "x = y * ((y * ((z * z) * x)) * y)", "x = y * (y * ((y * (y * x)) * x))"),
    ("O5W6", "x = ((y * (x * y)) * y) * (z * z)", "x * x = (((y * x) * y) * z) * y"),
    ("O5W7", "x = y * (x * ((z * (z * y)) * z))", "x = y * ((y * (y * (z * z))) * y)"),
    ("O5W8", "x = y * (x * ((x * (z * y)) * z))", "x = (y * ((y * x) * z)) * z"),
    ("O5W9", "x = y * ((z * (z * x)) * (y * x))", "x * x = ((x * (x * y)) * x) * x"),
    ("O5W10", "x = x * (x * ((x * (x * x)) * y))", "x = x * (x * x)"),
    ("O5W11", "x = x * (((y * z) * (y * x)) * z)", "x = (x * (((x * y) * x) * y)) * x"),
    ("O5W12", "x = x * ((y * (x * y)) * (z * z))", "x * y = (x * (y * (z * y))) * x"),
    ("O5W13", "x * y = z * ((z * y) * (y * x))", "(x * y) * z = (x * y) * (z * z)"),
    ("O5W14", "x = (y * (z * ((x * y) * y))) * z", "x = (y * ((y * x) * (x * z))) * y"),
    ("O5W15", "x = (y * (x * (z * z))) * (x * y)", "x = (y * ((y * z) * z)) * (y * z)"),
    ("O5W16", "x = (y * z) * ((x * (z * x)) * y)", "(x * y) * z = (x * (x * x)) * z"),
    ("O5W17", "x = (y * y) * (z * (z * (x * y)))", "x = y * (((x * (y * z)) * y) * z)"),
]

# Rows whose FALSE witness the fixed schedules must find. Sources: the 47 misses
# of the fresh disjoint 2,000-row order-5 sample (seed 20260827) and the 60-row
# order-5 classification of 2026-08-27.
LM_ORDER4 = ("x = (((y * z) * (z * x)) * x) * y",
             "x = y * ((z * (x * (z * z))) * y)")            # order5_39558_13136
CP_ORDER4 = ("x = x * (x * ((x * (x * x)) * y))",
             "x = x * (x * x)")                              # order5_7327_8
CP_ORDER6 = ("x = x * (((y * z) * (y * x)) * z)",
             "x = (x * (((x * y) * x) * y)) * x")            # order5_14487_32777
LM_ORDER6 = ("x = y * ((z * (z * x)) * (y * x))",
             "x * x = ((x * (x * y)) * x) * x")              # order5_11497_52058
LM_ORDER7 = ("x = x * ((y * ((y * y) * x)) * z)",
             "x * y = (x * y) * ((z * x) * x)")              # order5_13566_47051

# z3 proved eq1 has NO model at any order <= 7 for these (`eq1_unsat_all_le7`
# in stage2/results/order5-classification-2026-08-27.jsonl), so no finite
# witness in the searched range can exist and the searches must report none.
COLLAPSE_NEGATIVE_CONTROLS = [
    ("x = (y * z) * (x * ((z * z) * z))", "x = (y * (y * (y * (z * x)))) * y"),
    ("x = (y * z) * (y * (z * (x * z)))", "x = y * ((y * (x * x)) * (x * z))"),
    ("x = (y * ((x * z) * (x * y))) * z", "x = y * ((x * (z * y)) * x)"),
]

# The two order-4 FALSE "frontier" rows that the 2026-08-27 FP library already
# closed. CLAUDE.md listed them as open; they are not (diagnosis F7).
FP6_ROWS = [
    ("x = y ◇ ((x ◇ z) ◇ (z ◇ y))",
     "x ◇ (x ◇ x) = x ◇ (y ◇ y)"),               # etp_898_4270
    ("x = (y ◇ (x ◇ (z ◇ y))) ◇ z",
     "(x ◇ y) ◇ y = (x ◇ z) ◇ z"),               # etp_2316_4656
]


def _pair(solver, texts):
    return solver.parse_equation(texts[0]), solver.parse_equation(texts[1])


# ---------------------------------------------------------------------------
# F1 -- the order-5 witness library


def test_witness_tables_have_no_duplicate_tables_or_names(solver):
    """Three table blocks are scanned in sequence on every unresolved FALSE row.
    A table repeated across them is pure cost: it can never claim a row the
    earlier block did not already claim, and it hides the fact that the library
    is smaller than its entry count suggests."""
    blocks = (solver.WITNESS_TABLES, solver.FP_WITNESS_TABLES,
              solver.O5_WITNESS_TABLES)
    seen: dict[str, str] = {}
    names: set[str] = set()
    for block in blocks:
        for name, table in block:
            assert name not in names, f"duplicate witness table name {name}"
            names.add(name)
            key = repr(table)
            assert key not in seen, f"{name} is byte-identical to {seen[key]}"
            seen[key] = name


def test_o5_tables_refute_their_source_rows_through_the_oracle(solver):
    """Independent re-verification (rail 5c positive control): for every shipped
    O5 table, eq1 must hold and eq2 must fail, checked by
    `oracles.equation_holds` rather than by the solver's own `witness_check`."""
    tables = dict(solver.O5_WITNESS_TABLES)
    assert len(tables) == len(O5_SOURCES)
    for name, eq1_text, eq2_text in O5_SOURCES:
        table = tables[name]
        eq1 = solver.parse_equation(eq1_text)
        eq2 = solver.parse_equation(eq2_text)
        assert oracles.equation_holds(
            eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table), name
        assert not oracles.equation_holds(
            eq2["lhs"], eq2["rhs"], list(eq2["variables"]), table), name


def test_o5_tables_are_shippable_certificates(solver):
    """A sound witness is not automatically a shippable one (rail 3c): the
    rendered certificate must fit the judge's FALSE cap and its `decideFin!`
    cost must fit the Lean timeout."""
    tables = dict(solver.O5_WITNESS_TABLES)
    for name, eq1_text, eq2_text in O5_SOURCES:
        table = tables[name]
        eq1 = solver.parse_equation(eq1_text)
        eq2 = solver.parse_equation(eq2_text)
        assert solver.table_is_renderable(table), name
        assert solver.witness_decide_is_affordable(eq1, eq2, table), name
        assert solver.table_is_counterexample(eq1, eq2, table), name
        code = solver.false_certificate(len(table), table)
        oracles.check_false_certificate(code, eq1, eq2)
        assert len(code.encode("utf-8")) <= solver.MAX_FALSE_CERT_BYTES, name


def test_o5_library_is_scanned_last_in_the_portfolio(solver):
    """Placement is the whole reason this block carries zero regression risk:
    it runs after every other witness family, so no route above it can lose a
    golden pin to it."""
    solver.set_effort("fast")
    eq1, eq2 = _pair(solver, LM_ORDER6)
    found = solver.find_counterexample(eq1, eq2)
    assert found is not None
    _n, table, route = found
    assert route == "false:witness:O5W9"
    assert solver.table_is_counterexample(eq1, eq2, table)


# ---------------------------------------------------------------------------
# F2 -- one deadline per size, not one per call


def test_local_model_arms_a_deadline_per_size(solver):
    """Structural pin. The failure mode is silent: with the deadline armed
    before the loop, `sizes[1:]` is unreachable and the search still *looks*
    like it is trying four sizes."""
    src = inspect.getsource(solver.local_model_counterexample)
    loop = src.index("for n in sizes:")
    assert "local_deadline(" in src[loop:], (
        "the size loop must arm its own deadline")
    assert "local_deadline(" not in src[:loop], (
        "a deadline armed before the size loop makes every later size dead code")
    assert solver.LOCAL_MODEL_SIZES == (4, 5, 6, 7)


@pytest.mark.parametrize("texts,size", [(LM_ORDER6, 6), (LM_ORDER7, 7)])
def test_local_model_reaches_the_larger_sizes(solver, texts, size):
    """Positive controls for the slice fix: both rows have a witness only at a
    size the shared deadline could never reach. Measured 2026-08-27: order 6 in
    3.0 s, order 7 in 3.3 s, against `None` at 30 s for the shipped tuple."""
    solver.set_effort("fast")
    eq1, eq2 = _pair(solver, texts)
    found = solver.local_model_counterexample(
        eq1, eq2, sizes=(size,), time_budget=25.0, unscaled=True)
    assert found is not None, f"size {size} unreachable"
    n, table, route = found
    assert n == size and route == f"false:local_model{size}"
    assert oracles.equation_holds(
        eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table)
    assert not oracles.equation_holds(
        eq2["lhs"], eq2["rhs"], list(eq2["variables"]), table)


def test_local_model_probe_is_unscaled(solver):
    """The probe slot must not grow with the effort tier: that is exactly the
    tier inversion of rail 12, where more budget makes the solver worse."""
    eq1, eq2 = _pair(solver, LM_ORDER4)
    try:
        for tier in ("fast", "standard", "deep"):
            solver.set_effort(tier)
            start = time.monotonic()
            found = solver.local_model_counterexample(
                eq1, eq2, sizes=solver.LOCAL_MODEL_PROBE_SIZES,
                time_budget=solver.LOCAL_MODEL_PROBE_BUDGET, unscaled=True)
            elapsed = time.monotonic() - start
            assert found is not None and found[2] == "false:local_model4"
            assert elapsed < 6.0, f"{tier}: probe took {elapsed:.1f} s"
    finally:
        solver.set_effort("fast")


@pytest.mark.parametrize("texts", COLLAPSE_NEGATIVE_CONTROLS)
def test_local_model_finds_nothing_on_collapse_rows(solver, texts):
    """Negative control (rail 5c). z3 proves eq1 has no model at any order <= 7
    for these, so a search that reports a witness here is reporting a bug."""
    solver.set_effort("fast")
    eq1, eq2 = _pair(solver, texts)
    assert solver.local_model_counterexample(
        eq1, eq2, time_budget=1.2, unscaled=True) is None


# ---------------------------------------------------------------------------
# F3 -- a slice per constraint order


def test_cheap_constraint_tier_is_per_order(solver):
    """Orders 8 and 9 stay first (they are what the order-4 corpus is tuned on),
    but they no longer eat the whole schedule's clock."""
    assert solver.CONSTRAINT_ORDERS[:2] == (8, 9)
    assert set(solver.CONSTRAINT_ORDERS) == {4, 5, 6, 7, 8, 9, 10}
    assert 0 < solver.CONSTRAINT_CHEAP_PER_ORDER_BUDGET <= 2.0
    src = inspect.getsource(solver.solve_problem_pass)
    cheap = src.index("constraint_countermodel(")
    assert "per_order=True" in src[cheap:cheap + 200], (
        "the cheap tier must give every order its own slice")


@pytest.mark.parametrize("texts,size", [(CP_ORDER4, 4), (CP_ORDER6, 6)])
def test_cheap_constraint_tier_reaches_late_orders(solver, texts, size):
    """Positive controls: both witnesses sit at an order the shared 3 s deadline
    never reached (measured 0/47 shared vs 3/47 per-order on the fresh
    misses)."""
    solver.set_effort("fast")
    eq1, eq2 = _pair(solver, texts)
    found = solver.constraint_countermodel(
        eq1, eq2, per_order=True,
        time_budget=solver.CONSTRAINT_CHEAP_PER_ORDER_BUDGET)
    assert found is not None
    n, table, route = found
    assert n == size and route == f"false:constraint_fin{size}"
    assert oracles.equation_holds(
        eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table)
    assert not oracles.equation_holds(
        eq2["lhs"], eq2["rhs"], list(eq2["variables"]), table)


def test_per_order_timeout_does_not_read_as_exhausted(solver):
    """Rail 5 / 5f-ii. Under a SHARED deadline a timed-out order was caught by
    the next iteration's clock check; under `per_order=True` every order gets a
    fresh deadline, so an order that merely ran out of clock would otherwise
    read as searched -- and `constraint_search_exhausted()` is what licenses a
    speculative TRUE verdict."""
    solver.set_effort("fast")
    eq1, eq2 = _pair(solver, LM_ORDER7)
    solver.reset_constraint_evidence()
    assert solver.constraint_countermodel(
        eq1, eq2, orders=(9, 10), per_order=True, time_budget=0.05) is None
    assert not solver.constraint_search_exhausted()


# ---------------------------------------------------------------------------
# F4 -- the cheap FALSE probe runs before the TRUE engines


def test_false_probe_claims_an_order4_witness_quickly(solver):
    """End-to-end. This row's witness is 0.2 s of search that used to cost
    262.9 s of scheduling, because the only local-model call sat after all
    fourteen general TRUE engines."""
    solver.set_effort("fast")
    problem = {"id": "probe_control", "equation1": LM_ORDER4[0],
               "equation2": LM_ORDER4[1]}
    start = time.monotonic()
    record = solver.solve_problem(problem, false_time_budget=5.0)
    elapsed = time.monotonic() - start
    assert record is not None
    assert record["answer"]["verdict"] == "false"
    assert elapsed < 20.0, f"probe slot did not fire: {elapsed:.1f} s"
    eq1, eq2 = _pair(solver, LM_ORDER4)
    oracles.check_false_certificate(record["answer"]["code"], eq1, eq2)


def test_false_probe_runs_before_the_true_engines(solver):
    """Placement pin: the probe must sit with the cheap constraint tier, not
    with the last-resort searches after the engine list."""
    src = inspect.getsource(solver.solve_problem_pass)
    probe = src.index("LOCAL_MODEL_PROBE_SIZES")
    engines = src.index("engines: list[Any] = [")
    late = src.rindex("local_model_counterexample(eq1, eq2)")
    assert probe < engines < late, "probe slot is in the wrong place"


# ---------------------------------------------------------------------------
# F7 -- two order-4 "frontier" rows that the FP library already closes


@pytest.mark.parametrize("texts", FP6_ROWS)
def test_order4_false_residue_rows_are_served_by_fp6(solver, texts):
    """CLAUDE.md listed six order-4 FALSE misses in 110,000 rows; two of them
    were closed by the 2026-08-27 FP table block and nobody had re-measured.
    Pinned so the win cannot silently regress and so no future session
    re-attacks them."""
    solver.set_effort("fast")
    eq1, eq2 = _pair(solver, texts)
    found = solver.find_counterexample(eq1, eq2)
    assert found is not None
    n, table, route = found
    assert route == "false:witness:FP6"
    assert oracles.equation_holds(
        eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table)
    assert not oracles.equation_holds(
        eq2["lhs"], eq2["rhs"], list(eq2["variables"]), table)
    oracles.check_false_certificate(solver.false_certificate(n, table), eq1, eq2)
