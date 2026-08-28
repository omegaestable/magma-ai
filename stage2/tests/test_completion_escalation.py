"""The order-5 completion escalation: unfailing superposition + the cap ladder.

Positive and negative controls for the 2026-08-27 escalation work (rail 5c) plus
the structural pins that keep it escalation-only.

Why the rows are embedded here rather than looked up: the order-5 positive
controls come from a generated sweep batch that lives in no tracked benchmark
set, and a pin that cannot resolve its row becomes a SKIP, which reads as
coverage (rail 16). Every equation this file needs is spelled out below.

Cost note: `test_escalation_respects_absolute_cap` deliberately spends the real
`COMPLETION_ESCALATION_SECONDS` (~25 s). That is the only thing that can prove
the cap binds; the other four negative controls run under a patched 2 s cap so
the gate pays for the measurement once, not five times.
"""

from __future__ import annotations

import ast
import inspect
import time
from pathlib import Path

import pytest

import oracles

# (id, equation1, equation2). All order-5, all `x = F(x,y,z)` hypotheses, all
# TRUE by collapse — z3-classified 2026-08-27, judge-accepted certificates.
POSITIVE_CONTROLS = [
    ("order5_18399_29663",
     "x = (y * z) * (x * ((z * z) * z))",
     "x = (y * (y * (y * (z * x)))) * y"),
    # The two rows that are reachable ONLY with all-orientation superposition
    # (O5-1): with `ori` alone the engine reports SATURATED on both.
    ("order5_32102_22671",
     "x = (y * ((x * (x * y)) * z)) * y",
     "x = (y * (y * z)) * ((x * z) * x)"),
    ("order5_28585_58647",
     "x = (((y * x) * x) * x) * (z * z)",
     "(x * y) * y = z * (y * (z * z))"),
]

# Known-FALSE rows (official `hard2`), so a collapse or a join on any of them
# would be a soundness bug, not a coverage win.
NEGATIVE_CONTROLS = [
    ("hard2_0041", "x = y ◇ ((y ◇ (x ◇ y)) ◇ x)",
     "x = (x ◇ (y ◇ x)) ◇ (x ◇ x)"),
    ("hard2_0150", "x = (y ◇ ((y ◇ x) ◇ x)) ◇ y",
     "x ◇ y = z ◇ (w ◇ (x ◇ z))"),
    ("hard2_0052", "x = y ◇ ((x ◇ (x ◇ y)) ◇ y)",
     "x = x ◇ (y ◇ (z ◇ (w ◇ y)))"),
    ("hard2_0014", "x = y ◇ ((x ◇ (x ◇ y)) ◇ y)",
     "(x ◇ y) ◇ z = (z ◇ y) ◇ x"),
    ("hard2_0100", "x = (x ◇ ((x ◇ y) ◇ y)) ◇ y",
     "x ◇ y = ((x ◇ y) ◇ y) ◇ x"),
]


@pytest.fixture(scope="module")
def solver_source() -> str:
    path = Path(__file__).resolve().parents[1] / "solver" / "solver.py"
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Positive controls (rail 5c)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("row_id,eq1_text,eq2_text", POSITIVE_CONTROLS,
                         ids=[r[0] for r in POSITIVE_CONTROLS])
def test_escalation_closes_order5_collapse_rows(solver, row_id, eq1_text,
                                                eq2_text):
    """Each row closes through the escalation and the certificate checks out.

    Measured 2026-08-27 in an isolated run: 0.03 s / 0.03 s / 0.60 s. The 25 s
    allowance is the escalation's own absolute cap, not an expectation.
    """
    solver.clear_term_caches()
    eq1 = solver.parse_equation(eq1_text)
    eq2 = solver.parse_equation(eq2_text)
    start = time.monotonic()
    got = solver.completion_prove(eq1, eq2, time_budget=60.0, escalate=True)
    elapsed = time.monotonic() - start
    assert got is not None, f"{row_id}: escalation failed to close the row"
    route, code = got
    assert route.startswith("true:completion:")
    assert elapsed < 25.0, f"{row_id}: took {elapsed:.1f}s"
    # The offline kernel shares no code with the solver on purpose.
    oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
    assert oracles.find_judge_banned_token(code) is None
    assert len(code.encode("utf-8")) <= solver.MAX_LEAN_CODE_BYTES


def test_positive_controls_need_the_escalation(solver):
    """Without `escalate=True` these rows are losses, so the pins above really
    measure the escalation rather than the cheap pass."""
    for row_id, eq1_text, eq2_text in POSITIVE_CONTROLS:
        solver.clear_term_caches()
        eq1 = solver.parse_equation(eq1_text)
        eq2 = solver.parse_equation(eq2_text)
        got = solver.completion_prove(eq1, eq2, time_budget=5.0, escalate=False)
        assert got is None, f"{row_id}: cheap pass unexpectedly served the row"


# --------------------------------------------------------------------------
# Negative controls (rail 5c): soundness AND cost
# --------------------------------------------------------------------------

def test_negative_controls_are_never_served(solver, monkeypatch):
    """Five known-FALSE rows must stay unserved by the escalated inference.

    The escalation clock is patched down to 2 s here: soundness does not depend
    on the budget, and `test_escalation_respects_absolute_cap` below pays for
    the real 25 s once.
    """
    monkeypatch.setattr(solver, "COMPLETION_ESCALATION_SECONDS", 2.0)
    for row_id, eq1_text, eq2_text in NEGATIVE_CONTROLS:
        solver.clear_term_caches()
        eq1 = solver.parse_equation(eq1_text)
        eq2 = solver.parse_equation(eq2_text)
        start = time.monotonic()
        got = solver.completion_prove(eq1, eq2, time_budget=30.0, escalate=True)
        elapsed = time.monotonic() - start
        assert got is None, f"{row_id}: FALSE row claimed TRUE via {got[0]}"
        assert elapsed < 20.0, f"{row_id}: patched cap did not bind ({elapsed:.1f}s)"


def test_escalation_respects_absolute_cap(solver):
    """The escalated pass is bounded by its OWN absolute clock, not by the
    route's remaining budget.

    Measured 2026-08-27 over 40 known-FALSE rows at a 60 s route budget: 16 land
    on 25.0x s exactly (the cap binding), 14 give up earlier, and the other 10
    never reach the escalation because the *cheap* pass spends the budget first.
    `hard2_0041` is one of the 16.
    """
    assert solver.COMPLETION_ESCALATION_SECONDS == 25.0
    solver.clear_term_caches()
    eq1 = solver.parse_equation(NEGATIVE_CONTROLS[0][1])
    eq2 = solver.parse_equation(NEGATIVE_CONTROLS[0][2])
    start = time.monotonic()
    got = solver.completion_prove(eq1, eq2, time_budget=60.0, escalate=True)
    elapsed = time.monotonic() - start
    assert got is None
    assert elapsed < 30.0, f"escalation overran its absolute cap: {elapsed:.1f}s"


# --------------------------------------------------------------------------
# Structural pins
# --------------------------------------------------------------------------

def _method_body(source: str, cls: str, name: str) -> ast.FunctionDef:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == name:
                    return item
    raise AssertionError(f"{cls}.{name} not found")


@pytest.mark.parametrize("name", ["subsumed", "rewrite_once", "_reduce_with"])
def test_completion_loops_poll_the_deadline(solver_source, name):
    """Twin-signature pin (rail 5f-v, CLAUDE.md next-lever #2).

    `subsumed` iterated the whole active set with no poll at all while both of
    its structural twins polled per unit of work — and `max_active` is 5x
    larger in the escalated pass. `deadline_expired` also consults the memory
    guard, so an un-polled loop has no memory guard either.
    """
    body = _method_body(solver_source, "_KBCompletion", name)
    calls = [node for node in ast.walk(body)
             if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute)
             and node.func.attr == "out_of_time"]
    assert calls, f"_KBCompletion.{name} never polls out_of_time()"
    # The poll must sit inside a loop, not merely at the function's entry.
    in_loop = False
    for node in ast.walk(body):
        if isinstance(node, (ast.For, ast.While)):
            if any(isinstance(inner, ast.Call)
                   and isinstance(inner.func, ast.Attribute)
                   and inner.func.attr == "out_of_time"
                   for inner in ast.walk(node)):
                in_loop = True
    assert in_loop, f"_KBCompletion.{name} polls out_of_time() outside its loop"


def test_probe_slot_never_escalates(solver_source):
    """Pass 1 must stay byte-identical on every row the solver already serves,
    so the unscaled probe slot may not pass `escalate`."""
    tree = ast.parse(solver_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "completion_probe_route":
            names = {kw.arg for call in ast.walk(node)
                     if isinstance(call, ast.Call) for kw in call.keywords}
            assert "escalate" not in names
            return
    raise AssertionError("completion_probe_route not found")


def test_escalation_knobs_default_off(solver):
    """Every escalation knob defaults off, so the cheap pass is unchanged."""
    params = inspect.signature(solver._KBCompletion.__init__).parameters
    for knob in ("unfailing", "norm_push", "seed_merges", "evict_passive"):
        assert params[knob].default is False, knob
    once = inspect.signature(solver._completion_prove_once).parameters
    for knob in ("unfailing", "norm_push", "seed_merges", "evict_passive"):
        assert once[knob].default is False, knob
    assert once["status"].default is None


def test_saturation_status_is_an_out_parameter(solver_source):
    """Rail 10: a module-level flag is a process-lifetime flag in Marathon, not
    a per-row one. The saturated-vs-expired report must be a parameter."""
    tree = ast.parse(solver_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_completion_prove_once":
            assert "status" in {a.arg for a in node.args.kwonlyargs}
            assert not any(isinstance(stmt, ast.Global) for stmt in ast.walk(node))
            return
    raise AssertionError("_completion_prove_once not found")


# --------------------------------------------------------------------------
# Unit pins for the four mechanisms
# --------------------------------------------------------------------------

def test_sup_ori_covers_the_inert_equations(solver):
    """`(z * z) = (z' * z')` has incomparable variable sets, so `ori` is empty
    and the equation is inert; `sup_ori` gives it both directions."""
    left = ("op", ("var", "z"), ("var", "z"))
    right = ("op", ("var", "w"), ("var", "w"))
    eq = solver._KBEquation(0, left, right, None)
    assert eq.ori == []
    assert len(eq.sup_ori) == 2
    # An orientable equation keeps exactly its rewrite orientations.
    big = ("op", ("var", "x"), ("var", "y"))
    orientable = solver._KBEquation(1, big, ("var", "x"), None)
    assert orientable.sup_ori is orientable.ori
    # The `lhs != rhs` guard only fires where `ori` is empty; a reflexive
    # equation still has its (single) rewrite orientation, and `step` never
    # builds one anyway.
    reflexive = solver._KBEquation(2, left, left, None)
    assert reflexive.sup_ori is reflexive.ori


def test_unfailing_flag_gates_the_extra_orientations(solver):
    """The extra superposition orientations appear only under `unfailing`."""
    axiom = (("op", ("var", "x"), ("var", "y")), ("var", "x"))
    inert_l = ("op", ("var", "z"), ("var", "z"))
    inert_r = ("op", ("var", "w"), ("var", "w"))
    for unfailing, want in ((False, 0), (True, 2)):
        comp = solver._KBCompletion([axiom], deadline=None, unfailing=unfailing)
        eq = solver._KBEquation(99, inert_l, inert_r, [])
        ori = eq.sup_ori if comp.unfailing else eq.ori
        assert len(ori) == want


def test_var_merges_are_the_set_partitions(solver):
    """Bell numbers, and every map idempotent (a representative maps to itself)."""
    for names, bell in ((["x"], 1), (["x", "y"], 2), (["x", "y", "z"], 5),
                        (["x", "y", "z", "w"], 15)):
        merges = solver._kb_var_merges(names)
        assert len(merges) == bell, names
        assert len({tuple(sorted(m.items())) for m in merges}) == bell
        for merge in merges:
            assert set(merge) == set(names)
            for rep in merge.values():
                assert merge[rep] == rep


def test_seed_merges_adds_axiom_instances(solver):
    """The merge instances land in `active` with a chain the renderer can emit
    (`have hlemN := h <merged args>`), and only under the flag."""
    eq1 = solver.parse_equation("x = (y * ((x * (x * y)) * z)) * y")
    axiom = [(eq1["lhs"], eq1["rhs"])]
    plain = solver._KBCompletion(axiom, deadline=None)
    seeded = solver._KBCompletion(axiom, deadline=None, seed_merges=True)
    assert len(plain.active) == 1
    assert len(seeded.active) > 1
    for eq in seeded.active[1:]:
        assert eq.chain is not None
        (path, eid, subst, direction) = eq.chain[0]
        assert path == () and direction == 1
        assert eid in seeded.axiom_ids
        assert set(subst) == set(eq1["variables"])


def test_active_full_reports_saturation_not_expiry(solver):
    """O5-4: a rule-count cap must not cancel the run — `expired` is what the
    caller polls, and setting it there skipped the goal bridge (rail 5f)."""
    eq1 = solver.parse_equation("x = (y * ((x * (x * y)) * z)) * y")
    comp = solver._KBCompletion([(eq1["lhs"], eq1["rhs"])], deadline=None,
                                max_active=1)
    comp.seed()
    seen = 0
    while comp.step() is not None:
        seen += 1
        assert seen < 50, "max_active never bound"
    assert comp.active_full is True
    assert comp.expired is False
    assert comp.step() is None


def test_passive_eviction_keeps_the_lighter_pair(solver):
    """O5-3: a full queue must not reject a pair lighter than what it holds."""
    axiom = (("op", ("var", "x"), ("var", "y")), ("var", "x"))
    heavy = ("op", ("op", ("var", "a"), ("var", "b")),
             ("op", ("var", "c"), ("var", "d")))
    light = ("op", ("var", "a"), ("var", "b"))

    reject = solver._KBCompletion([axiom], deadline=None, max_passive=1)
    reject.push(heavy, heavy, [])
    reject.push(light, light, [])
    assert len(reject.passive) == 1
    assert reject.passive[0][2] == heavy
    assert reject.n_dropped_full == 1

    evict = solver._KBCompletion([axiom], deadline=None, max_passive=1,
                                 evict_passive=True)
    evict.push(heavy, heavy, [])
    evict.push(light, light, [])
    assert len(evict.passive) == 1, "eviction must keep the queue bounded"
    assert evict.passive[0][2] == light
    assert evict.n_evicted == 1
    # A pair heavier than everything queued is still rejected, not swapped in.
    evict.push(heavy, heavy, [])
    assert evict.passive[0][2] == light
    assert evict.n_dropped_full == 1


def test_norm_push_caps_the_normal_form(solver):
    """O5-2: the weight limit belongs on the normalised pair. These hypotheses
    are strongly erasing, so a raw pair over the cap often normalises tiny."""
    eq1 = solver.parse_equation("x = (y * ((x * (x * y)) * z)) * y")
    axiom = [(eq1["lhs"], eq1["rhs"])]
    raw_lhs = eq1["lhs"]
    # `F(x,y,z) = x` rewrites the big side straight down to `x`, so the pair
    # `F(...) = F(...)`-shaped term below is over any small cap raw and trivial
    # once normalised.
    big = eq1["rhs"]
    plain = solver._KBCompletion(axiom, deadline=None, max_size=4)
    plain.push(big, raw_lhs, [])
    assert plain.n_dropped_size == 1 and not plain.passive
    normed = solver._KBCompletion(axiom, deadline=None, max_size=4,
                                  norm_push=True)
    normed.push(big, raw_lhs, [])
    # Both sides normalise to `x`, so the pair is discarded as trivial rather
    # than kept — either way it is not dropped *for size*.
    assert normed.n_dropped_size == 0
