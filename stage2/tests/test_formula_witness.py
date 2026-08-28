"""Closed-form FALSE witnesses, and the decide-cost model that admits them.

Two changes landed together on 2026-08-27 and neither is safe without the
other, which is why they are tested in one file.

`formula_op_expr` recognises a witness table as arithmetic (affine, quadratic,
or a bare bitwise op on a power-of-two carrier) and `false_certificate_formula`
ships it as ~380 bytes of Lean instead of an O(n^2) table. Measured on the real
judge, same magma, order 17: 1,044 bytes / 19.7 s as a `List.getD` table,
382 bytes / 2.8 s as the formula.

`witness_decide_is_affordable` stopped counting `decide` applications and
started counting *work*, because a table lookup costs O(n^2) per application
and a closed form costs a constant. Before the change the solver emitted
order-30 table certificates the judge deterministically rejects on heartbeats,
and refused order-43 formula certificates it accepts in 40 s.

The invariant that ties them: the gate and the renderer must make the same
three-way choice, or one of them is guessing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import oracles

FIXTURE_PATH = (Path(__file__).resolve().parents[1]
                / "fixtures" / "judge_verified_certs.jsonl")


def _eq(solver, text: str) -> dict:
    return solver.parse_equation(text)


def _vars_equation(solver, count: int) -> dict:
    """An equation in exactly `count` distinct variables, for cost pins only."""
    names = "xyzwvu"[:count]
    lhs = names[0]
    for name in names[1:]:
        lhs = f"({lhs} ◇ {name})"
    return solver.parse_equation(f"{lhs} = {names[0]}")


def _irregular_table(n: int) -> list[list[int]]:
    """A table with no closed form, so the cost pins exercise the table branch.

    A cost pin built on `(i + j) % n` would be testing the *formula* branch by
    accident — that magma is affine, the recogniser fires, and the answer flips.
    """
    table = [[(i * i + 3 * j * j * j + 7 * i * j * j + i) % n for j in range(n)]
             for i in range(n)]
    return table


# ---------------------------------------------------------------------------
# The recogniser
# ---------------------------------------------------------------------------

def test_recogniser_reproduces_every_generated_family_table(solver):
    """Fit and rendering must agree with the table, cell for cell.

    Every family the solver generates arithmetically has to round-trip: the fit
    is solved from three or four cells, so anything that reproduces those cells
    and nothing else would silently ship a different magma than the one
    `equation_holds` approved.
    """
    families = []
    families.extend(solver.affine_family_tables(
        max_n=max(solver.AFFINE_LINEAR_SIZES)))
    families.extend(solver.quadratic_family_tables(
        max_n=max(solver.AFFINE_QUADRATIC_SIZES)))
    families.extend(solver.large_linear_family_tables())
    assert families, "no generated family tables to check"

    checked = 0
    for route, table in families:
        n = len(table)
        expr = solver.formula_op_expr(table)
        assert expr is not None, f"{route}: closed form not recognised"
        code = solver.false_certificate_formula(n, expr)
        # Recomputed by the oracle's independent interpreter, not by the
        # solver: a shared expression evaluator would let one bug pass twice.
        assert oracles._formula_table(code, n) == table, route
        checked += 1
    assert checked > 1000, checked


def test_recogniser_declines_a_table_with_no_closed_form(solver):
    """A False negative costs a fallback rendering; a False positive ships the
    wrong magma. Both directions are pinned."""
    assert solver.formula_op_expr(_irregular_table(11)) is None
    # WCG5's op is `31 - (rotl x AND rotr y)` — neither affine, quadratic nor a
    # bare bitwise op, so the recogniser must leave it to FORMULA_CERTS.
    assert solver.formula_op_expr(solver._wcg5_table()) is None


def test_bitwise_forms_are_only_claimed_on_power_of_two_carriers(solver):
    """`Nat.xor i j` can leave `Fin n` unless n is a power of two, and the
    `Nat.mod` wrapper would then silently change the magma rather than fail.

    Small carriers reach the bitwise branch only when the polynomial ones miss:
    XOR on `Fin 2` is the affine `i + j`, and AND/OR on `Fin 2` and `Fin 4` are
    quadratics. That is fine — the branch that fires is irrelevant as long as
    the recomputed magma matches — so the head is only pinned where no
    polynomial fit exists.
    """
    for n in (2, 4, 8, 16):
        for fn in (lambda x, y: x ^ y, lambda x, y: x & y, lambda x, y: x | y):
            table = [[fn(i, j) for j in range(n)] for i in range(n)]
            expr = solver.formula_op_expr(table)
            assert expr is not None, n
            assert oracles._formula_table(
                solver.false_certificate_formula(n, expr), n) == table
    for n in (8, 16):
        for head, fn in (("Nat.xor", lambda x, y: x ^ y),
                         ("Nat.land", lambda x, y: x & y),
                         ("Nat.lor", lambda x, y: x | y)):
            table = [[fn(i, j) for j in range(n)] for i in range(n)]
            assert head in solver.formula_op_expr(table), (head, n)

    # Non-power-of-two carriers must not be claimed by the bitwise branch: on
    # `Fin 6`, `Nat.lor 3 4` is 7, and a `Nat.mod` wrapper would quietly make it
    # 1 rather than reject the fit.
    table = [[(i | j) % 6 for j in range(6)] for i in range(6)]
    expr = solver.formula_op_expr(table)
    assert expr is None or "Nat.lor" not in expr


# ---------------------------------------------------------------------------
# The rendered certificate
# ---------------------------------------------------------------------------

def test_formula_certificate_is_policy_clean_and_small(solver):
    """The judge scans raw certificate text for banned tokens before Lean runs,
    and rejects anything over the FALSE byte cap outright."""
    for n, a, b in ((11, 3, 5), (17, 13, 2), (25, 7, 7), (43, 22, 32),
                    (47, 2, 45)):
        table = [[(a * i + b * j) % n for j in range(n)] for i in range(n)]
        code = solver.false_certificate(n, table)
        assert "Fin.mk" in code and "List.getD" not in code, n
        assert solver.find_judge_banned_token(code) is None, n
        size = len(code.encode("utf-8"))
        assert size <= solver.MAX_FALSE_CERT_BYTES, (n, size)
        assert size <= solver.JUDGE_MAX_FALSE_CERT_BYTES, (n, size)
        # The whole point: constant bytes, where a table is O(n^2).
        assert size < 420, (n, size)


def test_formula_shape_carries_the_options_the_judge_needed(solver):
    """`maxRecDepth 40000` + `maxHeartbeats 0` is the shape the judge accepted
    at orders 3, 13, 25, 36, 50, 60 and on the Fin 64 XOR magma. `maxHeartbeats`
    is 0 here and 1,000,000 for a table on purpose — see
    `FALSE_TABLE_HEARTBEAT_OPTION`."""
    table = [[(3 * i + 5 * j) % 13 for j in range(13)] for i in range(13)]
    code = solver.false_certificate(13, table)
    assert "set_option maxRecDepth 40000" in code
    assert "set_option maxHeartbeats 0" in code


def test_table_shapes_now_raise_the_heartbeat_budget(solver):
    """The direct cause of a measured rejection: an order-30 `List.getD` table
    inside every byte and application cap came back `LEAN_REJECTED`,
    "maximum number of heartbeats (200000)", and the identical certificate with
    this option is `accepted`."""
    memo = solver.false_certificate_memo(
        6, [[(i + j) % 6 for j in range(6)] for i in range(6)])
    assert "set_option maxHeartbeats 1000000" in memo
    lst = solver.false_certificate_list(11, _irregular_table(11))
    assert "set_option maxHeartbeats 1000000" in lst
    # Not 0: a mis-estimated table should fail in ~30 s, not burn 300 s of the
    # row's judge budget.
    assert "set_option maxHeartbeats 0" not in memo
    assert "set_option maxHeartbeats 0" not in lst


def test_legacy_orders_still_ship_the_finOpTable_shape(solver):
    """Restyling a working row buys nothing and risks everything (rail 3c):
    every judge-accepted FALSE certificate to date is a `finOpTable` table at
    order <= 10, and `(i + j) % n` is affine, so without the explicit legacy
    branch the recogniser would have restyled all of them."""
    for n in range(2, solver.LEGACY_MAX_WITNESS_ORDER + 1):
        table = [[(i + j) % n for j in range(n)] for i in range(n)]
        assert solver.formula_op_expr(table) is not None, n
        code = solver.false_certificate(n, table)
        assert "finOpTable" in code and "Fin.mk" not in code, n


def test_a_legacy_table_too_dear_for_its_own_shape_falls_back_to_the_formula(solver):
    """The one live case the removed `n <= 10` exemption was hiding.

    `evaluation_order5_0059` is refuted by `x - y = x + 3y (mod 9)` against a
    5-variable hypothesis: 59,049 applications of a `finOpTable` lookup that
    re-parses the whole table string each time — the shape the judge rejects on
    heartbeats at order 10 / 5 variables. The magma is linear, so it ships as a
    formula instead of being dropped.
    """
    n = 9
    table = [[(i + 3 * j) % n for j in range(n)] for i in range(n)]
    applications = n ** 5
    code = solver.false_certificate(n, table, decide_applications=applications)
    assert "finOpTable" not in code and "Fin.mk" in code
    assert oracles._formula_table(code, n) == table
    # ...and with a 3-variable goal the same table keeps its historic shape.
    assert "finOpTable" in solver.false_certificate(
        n, table, decide_applications=n ** 3)


def test_wcg5_certificate_is_byte_identical_to_the_pinned_one(solver):
    """WCG5 is served from `FORMULA_CERTS`, not from the recogniser, and it is
    judge-pinned. If the new renderer ever captured it the bytes would change
    and the pin would be worthless — assert the bytes, not just the route."""
    entries = [json.loads(line) for line
               in FIXTURE_PATH.read_text(encoding="utf-8").splitlines()
               if line.strip()]
    pinned = [e for e in entries if "formula:WCG5" in e.get("route", "")]
    if not pinned:
        pytest.skip("no WCG5 certificate pinned")
    table = solver._wcg5_table()
    transposed = [list(col) for col in zip(*table)]
    emitted = {solver.FORMULA_CERTS[solver.table_key(table)],
               solver.FORMULA_CERTS[solver.table_key(transposed)]}
    for entry in pinned:
        assert entry["code"] in emitted, (
            f"{entry['id']}: the WCG5 certificate the judge accepted on "
            f"{entry['verified_on']} is no longer what the solver emits")


# ---------------------------------------------------------------------------
# The cost gate
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("order,variables", [(30, 3), (36, 3), (60, 2), (10, 5)])
def test_table_witnesses_the_judge_rejects_are_refused(solver, order, variables):
    """Every one of these was measured `incorrect / LEAN_REJECTED` on a
    deterministic heartbeat timeout with the old gate letting it through:
    order 30 / 3 variables (27,000 applications, 24.3M work units, 26.7 s),
    order 36 / 3 variables, order 60 / 2 variables, and order 10 / 5 variables
    (the `finOpTable` case the blanket `n <= 10` exemption waved past).

    The tables are deliberately *not* closed-form: a linear magma at these
    sizes is affordable as a formula, and rightly so.
    """
    eq1 = _vars_equation(solver, variables)
    eq2 = _vars_equation(solver, min(variables, 2))
    table = _irregular_table(order)
    assert solver.formula_op_expr(table) is None
    assert not solver.witness_decide_is_affordable(eq1, eq2, table)


def test_closed_form_witnesses_are_admitted_where_tables_are_not(solver):
    """Same orders, same hypothesis, closed-form magma: accepted by the judge at
    216,000 applications, so the gate has to admit them."""
    eq1 = _vars_equation(solver, 3)
    eq2 = _vars_equation(solver, 2)
    for n in (30, 36, 43, 47, 50):
        table = [[(2 * i + 3 * j) % n for j in range(n)] for i in range(n)]
        assert solver.witness_decide_is_affordable(eq1, eq2, table), n
    # ...but not without limit: the bound is applications, and 60**4 is far
    # past the 262,144 the judge was measured accepting.
    wide = _vars_equation(solver, 4)
    table = [[(2 * i + 3 * j) % 60 for j in range(60)] for i in range(60)]
    assert not solver.witness_decide_is_affordable(wide, eq2, table)


def test_every_shipped_named_table_stays_affordable(solver):
    """Removing the `n <= 10` exemption must not veto a witness that works.

    Measured over 39,207 named/FP-table rows resolved from the 2026-08-26/27
    audits, the worst real pairing is order 9 against 4 variables — 1.06M work
    units against a ceiling of 8M. This pins that headroom for every table the
    solver ships, so the cost model cannot quietly start refusing them.
    """
    eq1 = _vars_equation(solver, 4)
    eq2 = _vars_equation(solver, 4)
    tables = list(solver.WITNESS_TABLES) + list(solver.FP_WITNESS_TABLES)
    tables += list(getattr(solver, "O5_WITNESS_TABLES", ()))
    assert tables
    for name, table in tables:
        assert solver.witness_decide_is_affordable(eq1, eq2, table), (
            f"{name} (order {len(table)}) is no longer shippable against a "
            f"4-variable hypothesis")


def test_the_gate_and_the_renderer_make_the_same_choice(solver):
    """A cost gate that is not the acceptance predicate is guessing
    (rail 5f-vii, rider (a)). Whatever `witness_decide_is_affordable` admits,
    `false_certificate` must be willing to render at the same cost."""
    eq2 = _vars_equation(solver, 2)
    for variables in (2, 3, 4, 5):
        eq1 = _vars_equation(solver, variables)
        for n in (5, 9, 11, 17, 25, 30, 43):
            for table in ([[(2 * i + 3 * j) % n for j in range(n)]
                           for i in range(n)], _irregular_table(n)):
                applications = n ** variables
                if not solver.witness_decide_is_affordable(eq1, eq2, table):
                    continue
                code = solver.false_certificate(
                    n, table, decide_applications=applications)
                if "Fin.mk" in code and "List.getD" not in code:
                    assert applications <= solver.FORMULA_MAX_DECIDE_APPLICATIONS
                elif "finOpTable" in code:
                    assert solver.table_decide_work_is_affordable(
                        n, applications, memo=True)
                else:
                    assert solver.table_decide_work_is_affordable(
                        n, applications, memo=False)


def test_wide_domain_orders_are_pre_checked_with_the_acceptance_predicate(solver):
    """The wide-domain tier used to search orders whose result the acceptance
    gate would then discard — up to 1,760 s per row at `deep`. The pre-check now
    uses `table_decide_work_is_affordable`, so what it searches is what it can
    ship."""
    for widest, expected in ((2, {13, 16, 20, 25, 30, 40, 50}), (3, {13, 16, 20})):
        kept = {n for n in solver.WIDE_DOMAIN_ORDERS
                if solver.table_decide_work_is_affordable(
                    n, n ** widest, memo=False)}
        assert kept == expected, (widest, kept)


# ---------------------------------------------------------------------------
# The extended linear family
# ---------------------------------------------------------------------------

def test_large_linear_sizes_reach_the_orders_the_formula_unlocked(solver):
    """`order5_18263_27751`, a real order-5 sweep miss, is refuted by
    `x ◇ y = 22x + 32y (mod 43)` — an order the old tuple could not reach and
    the old gate would have rejected anyway (79,507 > 50,000 applications)."""
    assert 43 in solver.FORMULA_LINEAR_SIZES
    assert max(solver.FORMULA_LINEAR_SIZES) == 47
    # Kept out of LARGE_LINEAR_SIZES on purpose: that tuple is bounded by
    # MAX_WITNESS_ORDER = 25, the ceiling for a *table*-rendered witness, and
    # these orders never ship as a table.
    assert max(solver.LARGE_LINEAR_SIZES) <= solver.MAX_WITNESS_ORDER
    eq1 = _eq(solver, "x = (y ◇ y) ◇ (y ◇ ((z ◇ x) ◇ z))")
    eq2 = _eq(solver, "x = ((y ◇ (x ◇ y)) ◇ y) ◇ (y ◇ y)")
    hit = None
    for route, table in solver.large_linear_family_tables(eq1, eq2):
        if solver.witness_check(eq1, eq2, table):
            hit = (route, table)
            break
    assert hit is not None, "the n=43 linear refutation is unreachable"
    route, table = hit
    assert route == "false:linear:z43:22,32"
    answer = solver.make_false_answer(
        {"id": "order5_18263_27751"}, len(table), table, equations=(eq1, eq2))
    assert answer["verdict"] == "false"
    assert len(answer["code"].encode("utf-8")) < 400
    oracles.check_false_certificate(answer["code"], eq1, eq2)


def test_large_linear_skips_orders_whose_certificate_could_not_ship(solver):
    """Rail 5f-vii: the medial law holds in every linear magma, so a 4-variable
    hypothesis makes `equation_holds` walk n**4 assignments per candidate —
    6.8 s each at order 47, measured — for a witness the gate then refuses.
    The orders are skipped before the search, not after it."""
    eq1 = _eq(solver, "(x ◇ y) ◇ (z ◇ w) = (x ◇ z) ◇ (y ◇ w)")
    eq2 = _eq(solver, "x ◇ y = y ◇ x")
    orders = {len(table) for _route, table
              in solver.large_linear_family_tables(eq1, eq2)}
    every = solver.LARGE_LINEAR_SIZES + solver.FORMULA_LINEAR_SIZES
    assert orders == {n for n in every
                      if n ** 4 <= solver.FORMULA_MAX_DECIDE_APPLICATIONS}
    assert max(orders) < max(every)
    # With no equations the generator is unfiltered, exactly as before.
    unfiltered = {len(table) for _route, table
                  in solver.large_linear_family_tables()}
    assert unfiltered == set(every)


# ---------------------------------------------------------------------------
# The offline oracle
# ---------------------------------------------------------------------------

def test_oracle_rejects_a_formula_certificate_that_is_not_a_countermodel(solver):
    """The oracle rebuilds the magma from the emitted arithmetic, so it must
    catch a formula that satisfies the goal as readily as it catches a bad
    table. Positive and negative control in one place (rail 5c)."""
    n, a, b = 17, 13, 2
    table = [[(a * i + b * j) % n for j in range(n)] for i in range(n)]
    eq1 = _eq(solver, "x = y ◇ ((z ◇ x) ◇ ((y ◇ z) ◇ y))")
    eq2 = _eq(solver, "x = (x ◇ y) ◇ ((x ◇ (x ◇ x)) ◇ x)")
    code = solver.false_certificate(n, table)
    oracles.check_false_certificate(code, eq1, eq2)          # positive control
    with pytest.raises(oracles.OracleError):                 # negative control
        oracles.check_false_certificate(code, eq1, eq1)


def test_oracle_refuses_an_unrecognised_head_in_a_closed_form(solver):
    """An unknown head must be an error, never a pass: the whole value of
    recomputing the magma is that the oracle understood every operation the
    judge will evaluate."""
    code = solver.false_certificate_formula(
        8, "Nat.mod (Nat.somethingNew (Fin.val i) (Fin.val j)) 8")
    with pytest.raises(oracles.OracleError):
        oracles._formula_table(code, 8)


# ---------------------------------------------------------------------------
# Byte pins: certificates the real Lean judge accepted on 2026-08-27
# ---------------------------------------------------------------------------
#
# These five are not in `judge_verified_certs.jsonl` on purpose. That fixture's
# test re-solves the row and compares bytes, and it *skips* when the route
# drifts — so a row whose cheapest route is something else (or which takes four
# minutes to reach its route) would be pinned as a silent skip, which reads as
# coverage and is not (rail 16). Pinning the renderer directly costs
# milliseconds and cannot skip.
#
# Judge: Lean/Mathlib v4.33.1, deployed caps (100,000 / 20,000 / 300 s), one
# call at a time, 5/5 `accepted`. The judge-seconds column is an upper bound —
# the box carried ~30 other python processes throughout (rail 22).
JUDGE_ACCEPTED_2026_08_27 = (
    ("etp_1286_3", (11, 1, 7), "lin", 8.6,
     "import JudgeProblem\nimport JudgeDecide.DecideBang\nset_option maxRecDepth 40000\nset_option maxHeartbeats 0\n\ndef submission : Goal := by\n  let m : Magma (Fin 11) := { op := fun i j => Fin.mk (Nat.mod (Nat.add (Nat.add (Nat.mul 1 (Fin.val i)) (Nat.mul 7 (Fin.val j))) 0) 11) (Nat.mod_lt _ (Nat.succ_pos 10)) }\n  refine Exists.intro (Fin 11) ?_\n  refine Exists.intro m ?_\n  decideFin!\n"),
    ("order5_10488_19656", (17, 13, 2), "lin", 8.4,
     "import JudgeProblem\nimport JudgeDecide.DecideBang\nset_option maxRecDepth 40000\nset_option maxHeartbeats 0\n\ndef submission : Goal := by\n  let m : Magma (Fin 17) := { op := fun i j => Fin.mk (Nat.mod (Nat.add (Nat.add (Nat.mul 13 (Fin.val i)) (Nat.mul 2 (Fin.val j))) 0) 17) (Nat.mod_lt _ (Nat.succ_pos 16)) }\n  refine Exists.intro (Fin 17) ?_\n  refine Exists.intro m ?_\n  decideFin!\n"),
    ("etp_556_4673", (25, 7, 7), "lin", 12.5,
     "import JudgeProblem\nimport JudgeDecide.DecideBang\nset_option maxRecDepth 40000\nset_option maxHeartbeats 0\n\ndef submission : Goal := by\n  let m : Magma (Fin 25) := { op := fun i j => Fin.mk (Nat.mod (Nat.add (Nat.add (Nat.mul 7 (Fin.val i)) (Nat.mul 7 (Fin.val j))) 0) 25) (Nat.mod_lt _ (Nat.succ_pos 24)) }\n  refine Exists.intro (Fin 25) ?_\n  refine Exists.intro m ?_\n  decideFin!\n"),
    ("order5_18263_27751", (43, 22, 32), "lin", 36.1,
     "import JudgeProblem\nimport JudgeDecide.DecideBang\nset_option maxRecDepth 40000\nset_option maxHeartbeats 0\n\ndef submission : Goal := by\n  let m : Magma (Fin 43) := { op := fun i j => Fin.mk (Nat.mod (Nat.add (Nat.add (Nat.mul 22 (Fin.val i)) (Nat.mul 32 (Fin.val j))) 0) 43) (Nat.mod_lt _ (Nat.succ_pos 42)) }\n  refine Exists.intro (Fin 43) ?_\n  refine Exists.intro m ?_\n  decideFin!\n"),
    ("etp_4320_48", (5, 2, 3, 4, 1), "quad", 6.6,
     "import JudgeProblem\nimport JudgeDecide.DecideBang\nimport JudgeFinOp.MemoFinOp\nopen MemoFinOp\nset_option maxHeartbeats 1000000\n\ndef submission : Goal := by\n  let m : Magma (Fin 5) := {\n    op := finOpTable \"[[1,4,2,0,3],[3,0,2,4,1],[0,1,2,3,4],[2,2,2,2,2],[4,3,2,1,0]]\"\n  }\n  refine Exists.intro (Fin 5) ?_\n  refine Exists.intro m ?_\n  decideFin!\n"),
)


@pytest.mark.parametrize(
    "pid,params,kind,seconds,code", JUDGE_ACCEPTED_2026_08_27,
    ids=[row[0] for row in JUDGE_ACCEPTED_2026_08_27])
def test_renderer_still_emits_the_bytes_the_judge_accepted(
        solver, pid, params, kind, seconds, code):
    """The FALSE renderers are judge-pinned, byte for byte (rail 3c).

    `order5_18263_27751` is the row this whole change exists for: a real
    order-5 sweep miss, refuted by `x ◇ y = 22x + 32y (mod 43)`, which the
    old gate rejected (79,507 applications against a 50,000 cap) and which the
    judge accepts as 383 bytes in 36 s. `order5_10488_19656` is the A/B row —
    the same magma shipped as a 1,044-byte table before this change.
    `etp_4320_48` is a quadratic-family table, pinned because the `finOpTable`
    shape gained `set_option maxHeartbeats 1000000` and every byte of it moved.
    """
    n = params[0]
    if kind == "lin":
        _n, a, b = params
        table = [[(a * i + b * j) % n for j in range(n)] for i in range(n)]
        emitted = solver.false_certificate(n, table)
    else:
        _n, a, b, q, d = params
        table = [[(a * i + b * j + q * i * j + d) % n for j in range(n)]
                 for i in range(n)]
        emitted = solver.false_certificate(n, table)
    assert emitted == code, (
        f"{pid}: the certificate the Lean judge accepted on 2026-08-27 "
        f"({seconds}s) is no longer what the renderer emits")
    assert solver.find_judge_banned_token(emitted) is None
