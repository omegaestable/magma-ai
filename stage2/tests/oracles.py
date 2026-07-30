"""Offline certificate oracles: no Lean required.

Two independent soundness gates for solver-emitted certificates:

1. A *proof-expression kernel*: a pure-Python checker for the restricted Lean
   proof grammar the solver's closure/CP builders emit —

       h t1 .. tk | (E).symm | (E1).trans (E2) | congrArg (fun t => CTX) (E) | rfl

   Each expression is evaluated to the equation it proves (a pair of terms).
   A certificate passes iff its `exact` expression proves exactly
   `eq2.lhs = eq2.rhs` from hypothesis instances of eq1. This catches builder
   bugs (wrong substitution, wrong congruence context, broken trans-chain)
   at the same place Lean would fail with a type mismatch.

2. A *finite-model oracle*: batteries of finite magmas satisfying eq1; any
   TRUE verdict whose goal fails in one such model is unsound (would be
   FALSE), independent of proof syntax.

Everything here is deliberately implemented independently of solver.py
internals (own term parser, own equation evaluator) so a bug in a solver
primitive cannot hide itself in the oracle.
"""

from __future__ import annotations

import json
import random
import re
import time
from itertools import product
from typing import Any

Term = tuple[Any, ...]

OP_CHARS = {"◇", "*"}


class OracleError(Exception):
    """A certificate failed oracle checking."""


# ---------------------------------------------------------------------------
# Independent term parsing / evaluation
# ---------------------------------------------------------------------------

def _strip_parens(s: str) -> str:
    s = s.strip()
    while len(s) >= 2 and s[0] == "(" and s[-1] == ")":
        depth = 0
        wraps = True
        for i, ch in enumerate(s):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if depth == 0 and i < len(s) - 1:
                wraps = False
                break
        if not wraps:
            break
        s = s[1:-1].strip()
    return s


def parse_lean_term(text: str, variables: set[str]) -> Term:
    """Parse a magma term over `variables` (multi-char identifiers allowed)."""
    s = _strip_parens(text)
    depth = 0
    last_op = -1
    for i, ch in enumerate(s):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch in OP_CHARS and depth == 0:
            last_op = i
    if last_op >= 0:
        return (
            "op",
            parse_lean_term(s[:last_op], variables),
            parse_lean_term(s[last_op + 1:], variables),
        )
    name = s.strip()
    if name and name in variables:
        return ("var", name)
    raise OracleError(f"cannot parse term: {text!r}")


def term_to_str(term: Term) -> str:
    if term[0] == "var":
        return str(term[1])
    return f"({term_to_str(term[1])} ◇ {term_to_str(term[2])})"


def substitute(term: Term, subst: dict[str, Term]) -> Term:
    if term[0] == "var":
        try:
            return subst[term[1]]
        except KeyError as exc:
            raise OracleError(f"unbound variable {term[1]!r}") from exc
    return ("op", substitute(term[1], subst), substitute(term[2], subst))


def eval_term(term: Term, env: dict[str, int], table: list[list[int]]) -> int:
    if term[0] == "var":
        return env[term[1]]
    return table[eval_term(term[1], env, table)][eval_term(term[2], env, table)]


def equation_holds(lhs: Term, rhs: Term, variables: list[str], table: list[list[int]]) -> bool:
    n = len(table)
    for values in product(range(n), repeat=len(variables)):
        env = dict(zip(variables, values))
        if eval_term(lhs, env, table) != eval_term(rhs, env, table):
            return False
    return True


# ---------------------------------------------------------------------------
# Proof-expression kernel
# ---------------------------------------------------------------------------

_REFL = ("refl",)


def _tokenize_units(s: str) -> list[str]:
    """Split a proof expression into top-level units.

    A unit is a maximal space-free run at paren depth 0; parenthesized groups
    (with attached `.symm`/`.trans` suffixes) stay together, e.g.
    `((h x y).symm).trans` is one unit, `(z ◇ w)` is one unit.
    """
    units: list[str] = []
    depth = 0
    cur: list[str] = []
    for ch in s.strip():
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise OracleError(f"unbalanced parens in {s!r}")
        if ch.isspace() and depth == 0:
            if cur:
                units.append("".join(cur))
                cur = []
            continue
        cur.append(ch)
    if depth != 0:
        raise OracleError(f"unbalanced parens in {s!r}")
    if cur:
        units.append("".join(cur))
    return units


def _split_unit(unit: str) -> tuple[str, list[str]]:
    """Split `(base).symm.trans` into ('(base)', ['symm', 'trans'])."""
    if not unit.startswith("("):
        return unit, []
    depth = 0
    end = -1
    for i, ch in enumerate(unit):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end < 0:
        raise OracleError(f"unbalanced unit: {unit!r}")
    base = unit[: end + 1]
    rest = unit[end + 1:]
    suffixes: list[str] = []
    while rest:
        if rest.startswith(".symm"):
            suffixes.append("symm")
            rest = rest[len(".symm"):]
        elif rest.startswith(".trans"):
            suffixes.append("trans")
            rest = rest[len(".trans"):]
        else:
            raise OracleError(f"unsupported suffix {rest!r} in unit {unit!r}")
    return base, suffixes


class ProofKernel:
    """Evaluates a solver proof expression to the equation it proves.

    `extra_hyps` maps additional hypothesis names to `(vars, lhs, rhs)` laws,
    so lemma-chain certificates can cite previously proven helper lemmas.
    """

    def __init__(self, eq1_vars: list[str], eq1_lhs: Term, eq1_rhs: Term,
                 goal_vars: set[str], hyp_name: str = "h",
                 extra_hyps: dict[str, tuple[list[str], Term, Term]] | None = None):
        self.eq1_vars = eq1_vars
        self.eq1_lhs = eq1_lhs
        self.eq1_rhs = eq1_rhs
        self.goal_vars = goal_vars
        self.hyp_name = hyp_name
        self.hyps: dict[str, tuple[list[str], Term, Term]] = {
            hyp_name: (eq1_vars, eq1_lhs, eq1_rhs)
        }
        for name, law in (extra_hyps or {}).items():
            if name in self.hyps:
                raise OracleError(f"duplicate hypothesis name {name!r}")
            self.hyps[name] = law

    def prove(self, expr: str) -> tuple[Term, Term] | tuple[str]:
        units = _tokenize_units(expr)
        if not units:
            raise OracleError("empty proof expression")
        if units == ["rfl"]:
            return _REFL
        value, nxt = self._eval_spine(units, 0)
        if nxt != len(units):
            raise OracleError(f"trailing units {units[nxt:]!r} in {expr!r}")
        return value

    # -- internals ---------------------------------------------------------

    def _eval_spine(self, units: list[str], i: int) -> tuple[tuple[Term, Term], int]:
        base, suffixes = _split_unit(units[i])
        if base in self.hyps and not suffixes:
            hyp_vars, hyp_lhs, hyp_rhs = self.hyps[base]
            args = units[i + 1:]
            if len(args) != len(hyp_vars):
                raise OracleError(
                    f"hypothesis {base!r} arity {len(args)} != {len(hyp_vars)}")
            subst = {
                v: parse_lean_term(a, self.goal_vars)
                for v, a in zip(hyp_vars, args)
            }
            return (substitute(hyp_lhs, subst), substitute(hyp_rhs, subst)), len(units)
        if base == "congrArg" and not suffixes:
            if len(units) - i != 3:
                raise OracleError("congrArg expects exactly two arguments")
            lam = _strip_parens(units[i + 1])
            m = re.fullmatch(r"fun\s+(\w+)\s*=>\s*(.+)", lam, re.DOTALL)
            if m is None:
                raise OracleError(f"unsupported lambda {lam!r}")
            placeholder, body = m.group(1), m.group(2)
            if placeholder in self.goal_vars:
                raise OracleError(
                    f"congrArg binder {placeholder!r} shadows a goal variable")
            ctx = parse_lean_term(body, self.goal_vars | {placeholder})
            inner = self._eval_group(units[i + 2])
            a, b = inner
            return (
                substitute(ctx, {placeholder: a} | {v: ("var", v) for v in self.goal_vars}),
                substitute(ctx, {placeholder: b} | {v: ("var", v) for v in self.goal_vars}),
            ), i + 3
        # Parenthesized proof with suffixes: (E) [.symm]* [.trans (F)]
        value = self._eval_group(base)
        j = i + 1
        for k, suf in enumerate(suffixes):
            if suf == "symm":
                value = (value[1], value[0])
            elif suf == "trans":
                if k != len(suffixes) - 1:
                    raise OracleError(".trans must be the final suffix of a unit")
                if j >= len(units):
                    raise OracleError(".trans missing its argument")
                arg_base, arg_sufs = _split_unit(units[j])
                arg = self._eval_group(arg_base)
                for asuf in arg_sufs:
                    if asuf == "symm":
                        arg = (arg[1], arg[0])
                    else:
                        raise OracleError("chained .trans on argument unit unsupported")
                j += 1
                if value[1] != arg[0]:
                    raise OracleError(
                        "trans mismatch: "
                        f"{term_to_str(value[1])} != {term_to_str(arg[0])}")
                value = (value[0], arg[1])
        return value, j

    def _eval_group(self, group: str) -> tuple[Term, Term]:
        if not (group.startswith("(") and group.endswith(")")):
            raise OracleError(f"expected parenthesized proof, got {group!r}")
        inner = group[1:-1].strip()
        units = _tokenize_units(inner)
        value, nxt = self._eval_spine(units, 0)
        if nxt != len(units):
            raise OracleError(f"trailing units in group {group!r}")
        return value


# ---------------------------------------------------------------------------
# Certificate-level checks
# ---------------------------------------------------------------------------

_EXACT_CERT_RE = re.compile(
    r"\Aimport JudgeProblem\n\n"
    r"def submission : Goal := by\n"
    r"  intro G _ h\n"
    r"(?:  intro ([a-z](?: [a-z])*)\n)?"
    r"  exact (.+)\n\Z",
    re.DOTALL,
)

_SINGLETON_CERT_RE = re.compile(
    r"\Aimport JudgeProblem\n\n"
    r"def submission : Goal := by\n"
    r"  intro G _ h\n"
    r"  have hall : ∀ a b : G, a = b := by\n"
    r"    intro a b\n"
    r"    exact ([^\n]+)\n"
    r"(?:  intro (?:[a-z](?: [a-z])*)\n)?"
    r"  exact hall _ _\n\Z",
)

_LEMMA_CERT_RE = re.compile(
    r"\Aimport JudgeProblem\n\n"
    r"def submission : Goal := by\n"
    r"  intro G _ h\n"
    r"  have hlem : ∀ ([a-z](?: [a-z])*) : G, ([^\n]+) := by\n"
    r"    intro (?:[a-z](?: [a-z])*)\n"
    r"    exact ([^\n]+)\n"
    r"(?:  intro ([a-z](?: [a-z])*)\n)?"
    r"  exact (.+)\n\Z",
    re.DOTALL,
)

_TABLE_RE = re.compile(r'finOpTable "(\[\[.*?\]\])"')
_FIN_RE = re.compile(r"Exists\.intro \(Fin (\d+)\)")

_LEMMA_CHAIN_HEAD = "import JudgeProblem\n\ndef submission : Goal := by\n  intro G _ h\n"

_HAVE_BLOCK_RE = re.compile(
    r"\A  have (hlem\d*) : ∀ ([a-z](?: [a-z])*) : G, ([^\n]+) := by\n"
    r"    intro ([a-z](?: [a-z])*)\n"
    r"    exact ([^\n]+)\n")

_LEMMA_CHAIN_TAIL_RE = re.compile(
    r"\A(?:  intro ([a-z](?: [a-z])*)\n)?  exact (.+)\n\Z", re.DOTALL)


def _parse_lemma_chain(code: str):
    """Split a lemma-chain certificate into have-blocks and the goal tail.

    Returns (blocks, intro_vars, goal_expr) or None when the code is not
    chain-shaped. Each block is (name, binder_list, statement, proof_expr).
    """
    if not code.startswith(_LEMMA_CHAIN_HEAD):
        return None
    rest = code[len(_LEMMA_CHAIN_HEAD):]
    blocks: list[tuple[str, list[str], str, str]] = []
    while True:
        m = _HAVE_BLOCK_RE.match(rest)
        if m is None:
            break
        name, binder_group, statement, intro_group, expr = m.groups()
        if intro_group.split() != binder_group.split():
            return None
        blocks.append((name, binder_group.split(), statement, expr))
        rest = rest[m.end():]
    if not blocks:
        return None
    tail = _LEMMA_CHAIN_TAIL_RE.match(rest)
    if tail is None:
        return None
    intro_group, goal_expr = tail.groups()
    intro_vars = intro_group.split() if intro_group else []
    return blocks, intro_vars, goal_expr.strip()


def classify_true_certificate(code: str) -> str:
    """Which offline checker applies to this TRUE certificate."""
    if _EXACT_CERT_RE.match(code):
        return "exact_expr"
    if _SINGLETON_CERT_RE.match(code):
        return "singleton"
    if _LEMMA_CERT_RE.match(code):
        return "lemma"
    if _parse_lemma_chain(code) is not None:
        return "lemma_chain"
    return "other"


def check_true_lemma_chain_certificate(
        code: str, eq1: dict[str, Any], eq2: dict[str, Any]) -> None:
    """Kernel-check a certificate that proves helper lemmas, then the goal.

    Each have-block is verified in the scope of `h` plus every previously
    verified lemma, and the goal body in the scope of all of them, so the
    whole chain is sound by induction: nothing is taken on trust beyond eq1.
    """
    parsed = _parse_lemma_chain(code)
    if parsed is None:
        raise OracleError("certificate does not match the lemma-chain shape")
    blocks, intro_vars, goal_expr = parsed
    if intro_vars != list(eq2["variables"]):
        raise OracleError(
            f"intro variables {intro_vars} != goal variables {eq2['variables']}")

    proven: dict[str, tuple[list[str], Term, Term]] = {}
    for name, binders, statement, expr in blocks:
        if name in proven or name == "h":
            raise OracleError(f"duplicate or reserved lemma name {name!r}")
        lhs_text, sep, rhs_text = statement.partition(" = ")
        if not sep:
            raise OracleError(f"lemma statement is not an equation: {statement!r}")
        lemma_lhs = parse_lean_term(lhs_text, set(binders))
        lemma_rhs = parse_lean_term(rhs_text, set(binders))
        kernel = ProofKernel(
            list(eq1["variables"]), eq1["lhs"], eq1["rhs"],
            set(binders), "h", extra_hyps=dict(proven))
        proved = kernel.prove(expr.strip())
        if proved == _REFL:
            if lemma_lhs != lemma_rhs:
                raise OracleError("rfl offered for a non-reflexive lemma")
        elif proved != (lemma_lhs, lemma_rhs):
            raise OracleError(
                f"lemma {name!r} body proved "
                f"{term_to_str(proved[0])} = {term_to_str(proved[1])}, but the "
                f"certificate states {term_to_str(lemma_lhs)} = {term_to_str(lemma_rhs)}")
        proven[name] = (list(binders), lemma_lhs, lemma_rhs)

    goal_kernel = ProofKernel(
        list(eq1["variables"]), eq1["lhs"], eq1["rhs"],
        set(eq2["variables"]) or set(eq1["variables"]), "h",
        extra_hyps=proven)
    proved = goal_kernel.prove(goal_expr)
    if proved == _REFL:
        if eq2["lhs"] != eq2["rhs"]:
            raise OracleError("rfl offered for a non-reflexive goal")
        return
    if proved != (eq2["lhs"], eq2["rhs"]):
        raise OracleError(
            "goal body proved wrong equation: "
            f"{term_to_str(proved[0])} = {term_to_str(proved[1])}, wanted "
            f"{term_to_str(eq2['lhs'])} = {term_to_str(eq2['rhs'])}")


def check_true_singleton_certificate(code: str, eq1: dict[str, Any]) -> None:
    """Kernel-check a collapse certificate: its body must prove a = b.

    A singleton certificate claims eq1 forces the magma to be trivial, which
    closes any goal. The checkable content is the collapse proof itself.
    """
    m = _SINGLETON_CERT_RE.match(code)
    if m is None:
        raise OracleError("certificate does not match the singleton shape")
    kernel = ProofKernel(
        list(eq1["variables"]), eq1["lhs"], eq1["rhs"], {"a", "b"}, "h")
    proved = kernel.prove(m.group(1).strip())
    if proved == _REFL:
        raise OracleError("rfl cannot prove a = b for distinct a, b")
    if proved != (("var", "a"), ("var", "b")):
        raise OracleError(
            "collapse proof proved "
            f"{term_to_str(proved[0])} = {term_to_str(proved[1])}, wanted a = b")


def check_true_exact_certificate(code: str, eq1: dict[str, Any], eq2: dict[str, Any]) -> None:
    """Kernel-check a substitution-style TRUE certificate. Raises OracleError."""
    m = _EXACT_CERT_RE.match(code)
    if m is None:
        raise OracleError("certificate does not match the exact-expr shape")
    intro_vars = m.group(1).split() if m.group(1) else []
    if intro_vars != list(eq2["variables"]):
        raise OracleError(
            f"intro variables {intro_vars} != goal variables {eq2['variables']}")
    expr = m.group(2).strip()
    kernel = ProofKernel(
        list(eq1["variables"]), eq1["lhs"], eq1["rhs"],
        set(eq2["variables"]) or set(eq1["variables"]), "h",
    )
    proved = kernel.prove(expr)
    if proved == _REFL:
        if eq2["lhs"] != eq2["rhs"]:
            raise OracleError("rfl offered for a non-reflexive goal")
        return
    if proved != (eq2["lhs"], eq2["rhs"]):
        raise OracleError(
            "proved wrong equation: "
            f"{term_to_str(proved[0])} = {term_to_str(proved[1])}, wanted "
            f"{term_to_str(eq2['lhs'])} = {term_to_str(eq2['rhs'])}")


def check_true_lemma_certificate(
        code: str, eq1: dict[str, Any], eq2: dict[str, Any]) -> None:
    """Kernel-check a certificate that proves a named lemma, then the goal.

    Two independent kernel runs, so neither half is taken on trust: the lemma
    body must prove exactly the lemma the certificate *states* from instances
    of eq1, and the goal body must prove exactly `eq2.lhs = eq2.rhs` treating
    that stated lemma as its hypothesis. The lemma statement is read back out
    of the certificate text rather than assumed, so a builder that proves one
    law and applies a different one cannot pass.
    """
    m = _LEMMA_CERT_RE.match(code)
    if m is None:
        raise OracleError("certificate does not match the lemma shape")
    binder_group, statement, lemma_expr, intro_group, body = m.groups()
    lemma_vars = binder_group.split()
    intro_vars = intro_group.split() if intro_group else []
    if intro_vars != list(eq2["variables"]):
        raise OracleError(
            f"intro variables {intro_vars} != goal variables {eq2['variables']}")

    lhs_text, sep, rhs_text = statement.partition(" = ")
    if not sep:
        raise OracleError(f"lemma statement is not an equation: {statement!r}")
    lemma_lhs = parse_lean_term(lhs_text, set(lemma_vars))
    lemma_rhs = parse_lean_term(rhs_text, set(lemma_vars))

    lemma_kernel = ProofKernel(
        list(eq1["variables"]), eq1["lhs"], eq1["rhs"], set(lemma_vars), "h")
    proved = lemma_kernel.prove(lemma_expr.strip())
    if proved == _REFL:
        if lemma_lhs != lemma_rhs:
            raise OracleError("rfl offered for a non-reflexive lemma")
    elif proved != (lemma_lhs, lemma_rhs):
        raise OracleError(
            "lemma body proved "
            f"{term_to_str(proved[0])} = {term_to_str(proved[1])}, but the "
            f"certificate states {term_to_str(lemma_lhs)} = {term_to_str(lemma_rhs)}")

    goal_kernel = ProofKernel(
        lemma_vars, lemma_lhs, lemma_rhs,
        set(eq2["variables"]) or set(lemma_vars), "hlem",
    )
    proved = goal_kernel.prove(body.strip())
    if proved == _REFL:
        if eq2["lhs"] != eq2["rhs"]:
            raise OracleError("rfl offered for a non-reflexive goal")
        return
    if proved != (eq2["lhs"], eq2["rhs"]):
        raise OracleError(
            "goal body proved wrong equation: "
            f"{term_to_str(proved[0])} = {term_to_str(proved[1])}, wanted "
            f"{term_to_str(eq2['lhs'])} = {term_to_str(eq2['rhs'])}")


# Tactics the solver's own PROMPT forbids the LLM from using, and which this
# project has field evidence against: the cloud judge rejected a `true:grind`
# certificate the local judge accepted, and broad grind produced 433 `incorrect`
# submissions before it was retired. `sanitize_lean_code` enforces this on LLM
# output but never on solver-generated code, which is how a `grind` sat inside
# `true:right_projection_collapse:left_pair_tail` unnoticed (found 2026-07-29).
# This closes that asymmetry.
_BANNED_TACTIC_RE = re.compile(r"\b(?:simp|simpa|simp_all|aesop|grind|sorry|admit)\b")

# The only routes allowed to emit a search tactic, deliberately and documented:
# `true:narrow_grind` is a demoted last-ditch attempt on known-TRUE shapes, and
# the Solo `fallback:unsolved_grind` is a speculative final guess on a row that
# is otherwise lost anyway.
GRIND_ALLOWED_ROUTES = frozenset({"true:narrow_grind", "fallback:unsolved_grind"})


def check_no_banned_tactics(code: str, route: str = "") -> None:
    """Raise if a solver-emitted certificate leans on a forbidden tactic.

    A tactic-backed proof cannot be checked by the proof kernel, so it is also
    invisible to every offline gate here. Keeping them out means the offline
    evidence actually covers what ships.
    """
    if route in GRIND_ALLOWED_ROUTES:
        return
    found = sorted({m.group() for m in _BANNED_TACTIC_RE.finditer(code)})
    if found:
        raise OracleError(
            f"certificate for route {route!r} uses banned tactic(s) "
            f"{found}: unverifiable offline and judge-rejected in the field")


# The judge reads the table with `MemoFinOp.finOpTable`, whose parser
# (`extractDigits`) keeps one value per *digit character*. A cell holding `10`
# becomes two cells, `1` and `0`, shifting everything after it — so the magma Lean
# checks is not the magma we sent. Orders 2..10 use only single-digit entries and
# round-trip cleanly; order 11+ is silently corrupted.
#
# Found 2026-07-29 by a `Fin 13` witness for `hard2_0051` that was mathematically
# correct (verified by hand and by this module) and still came back
# `LEAN_REJECTED`, with `decide` reporting the conjunction *false*. Every check in
# this file reads the parsed Python table, so nothing here could see it. This is
# the one place that models the judge's *parser* rather than its logic.
MAX_RENDERABLE_ORDER = 10


def check_false_certificate(code: str, eq1: dict[str, Any], eq2: dict[str, Any]) -> None:
    """Independently re-verify a FALSE certificate's finite witness table."""
    tm = _TABLE_RE.search(code)
    fm = _FIN_RE.search(code)
    if tm is None or fm is None:
        raise OracleError("FALSE certificate missing finOpTable/Fin markers")
    table = json.loads(tm.group(1))
    n = int(fm.group(1))
    if len(table) != n or any(len(row) != n for row in table):
        raise OracleError(f"table shape does not match Fin {n}")
    if any(not (0 <= v < n) for row in table for v in row):
        raise OracleError("table entries out of range")
    if n > MAX_RENDERABLE_ORDER or any(v > 9 for row in table for v in row):
        raise OracleError(
            f"Fin {n} witness has multi-digit entries; the judge's finOpTable "
            f"parser reads one value per digit character, so this table cannot "
            f"round-trip (max renderable order is {MAX_RENDERABLE_ORDER})")
    if not equation_holds(eq1["lhs"], eq1["rhs"], list(eq1["variables"]), table):
        raise OracleError("witness does not satisfy eq1")
    if equation_holds(eq2["lhs"], eq2["rhs"], list(eq2["variables"]), table):
        raise OracleError("witness does not refute eq2")


# ---------------------------------------------------------------------------
# Finite-model oracle
# ---------------------------------------------------------------------------

def _all_tables(n: int):
    for encoding in product(range(n), repeat=n * n):
        yield [list(encoding[r * n:(r + 1) * n]) for r in range(n)]


def _violations(lhs: Term, rhs: Term, variables: list[str],
                table: list[list[int]]) -> int:
    n = len(table)
    bad = 0
    for values in product(range(n), repeat=len(variables)):
        env = dict(zip(variables, values))
        if eval_term(lhs, env, table) != eval_term(rhs, env, table):
            bad += 1
    return bad


def search_models(eq1: dict[str, Any], *, orders: tuple[int, ...] = (4, 5),
                  restarts: int = 6, max_flips: int = 900,
                  want: int = 2, seed: int = 11,
                  time_budget: float = 0.25) -> list[list[list[int]]]:
    """Hill-climb for models of eq1 at orders where enumeration is hopeless.

    Needed because a whole family of laws (central groupoids and friends) has no
    model below order 4 — `Fin 4` alone is 4^16 ≈ 4.3e9 tables, so exhaustive
    search is out and uniform sampling essentially never hits one. Measured: this
    finds a genuine order-4 central groupoid in 0.17 s, for a law where every
    other method in this module returns nothing.

    `time_budget` matters as much as the flip caps. Two distinct families reach
    here: laws whose models start at order 4+ (search succeeds fast, if at all),
    and laws that *force the trivial magma* — every `*_singleton` / `*_collapse`
    route asserts exactly that, and for those no non-trivial model exists at any
    order, so the search can only ever fail. Failing must therefore be cheap:
    unbudgeted it cost 0.6-4.3 s per row on the singleton family. Those rows can
    only be verified by proof-checking, not model-checking.

    Deliberately implemented here rather than reused from `solver.py`: the whole
    point of this module is that a bug in a solver primitive cannot hide itself
    in the oracle.
    """
    lhs, rhs, variables = eq1["lhs"], eq1["rhs"], list(eq1["variables"])
    rng = random.Random(seed)
    found: list[list[list[int]]] = []
    deadline = time.monotonic() + time_budget if time_budget else None
    for n in orders:
        for _ in range(restarts):
            if deadline is not None and time.monotonic() >= deadline:
                return found
            table = [[rng.randrange(n) for _ in range(n)] for _ in range(n)]
            best = _violations(lhs, rhs, variables, table)
            for flip in range(max_flips):
                if best == 0:
                    break
                if (deadline is not None and not flip % 32
                        and time.monotonic() >= deadline):
                    return found
                i, j = rng.randrange(n), rng.randrange(n)
                old = table[i][j]
                new = rng.randrange(n)
                if new == old:
                    continue
                table[i][j] = new
                cand = _violations(lhs, rhs, variables, table)
                # Accept improvements; accept sideways moves sometimes to escape
                # the plateaus these laws produce. Never accept a worsening move.
                if cand < best or (cand == best and rng.random() < 0.25):
                    best = cand
                else:
                    table[i][j] = old
            if best == 0:
                found.append([row[:] for row in table])
                if len(found) >= want:
                    return found
    return found


def nontrivial_model_count(battery: list[list[list[int]]]) -> int:
    """How many models in `battery` can actually refute anything.

    The one-element magma satisfies *every* equation, so it can never witness a
    counterexample. A battery whose only member is trivial makes
    `model_check_true` vacuous — it reports success having tested nothing.
    Callers should surface this number so "model_checked" cannot be mistaken for
    evidence (see `audit_corpus.audit_row`).
    """
    return sum(1 for table in battery if len(table) > 1)


def model_battery(eq1: dict[str, Any], extra_tables: list[list[list[int]]],
                  *, fin3_samples: int = 1500, seed: int = 0,
                  search_orders: tuple[int, ...] = (4, 5)) -> list[list[list[int]]]:
    """Finite magmas satisfying eq1: all Fin2, sampled Fin3, plus extras.

    Escalates when nothing non-trivial turns up. Until 2026-07-29 the escalation
    below was unreachable dead code: the battery was pre-seeded with the trivial
    magma, so the `if not battery` guard it used could never be true. Measured
    consequence — 536 of 1889 official rows (28.4%; `normal` 431/1000,
    `hard2` 64/200) were "model_checked" against the trivial magma alone, which
    proves nothing. That is exactly the central-groupoid family behind the eight
    playground `TRUE INCORRECT` rows. The escalation now keys off the
    *non-trivial* count instead.
    """
    lhs, rhs, variables = eq1["lhs"], eq1["rhs"], list(eq1["variables"])
    # Fin1 stays in the battery: harmless, and it keeps the list non-empty for
    # laws whose only model really is trivial. It is deliberately not counted
    # towards `nontrivial_model_count`.
    battery: list[list[list[int]]] = [[[0]]]
    for table in _all_tables(2):
        if equation_holds(lhs, rhs, variables, table):
            battery.append(table)
    rng = random.Random(seed)
    for _ in range(fin3_samples):
        table = [[rng.randrange(3) for _ in range(3)] for _ in range(3)]
        if equation_holds(lhs, rhs, variables, table):
            battery.append(table)
    # Extras (named witness tables and structured families, orders up to ~9) go
    # in before the escalation decision: for central-groupoid-style laws whose
    # models live at order k^2 they are often the only non-trivial models that
    # exist below order 16, and they are free to test.
    for table in extra_tables:
        if equation_holds(lhs, rhs, variables, table):
            battery.append(table)
    if nontrivial_model_count(battery) == 0:
        # Rare laws (central groupoids, model orders k^2) have no Fin2 model and
        # essentially zero chance of a random Fin3 hit. Sweeping Fin3 exhaustively
        # is 3^9 = 19,683 tables — milliseconds — and is the cheapest chance to
        # give the oracle any teeth at all.
        for table in _all_tables(3):
            if equation_holds(lhs, rhs, variables, table):
                battery.append(table)
                if nontrivial_model_count(battery) >= 64:
                    break
    if search_orders and nontrivial_model_count(battery) == 0:
        # Still nothing: the law's smallest model is order >= 4, where neither
        # enumeration nor uniform sampling works. Hill-climb instead.
        battery.extend(search_models(eq1, orders=search_orders))
    return battery


def model_check_true(eq2: dict[str, Any], battery: list[list[list[int]]]) -> None:
    """Raise if any eq1-model refutes eq2 (TRUE verdict would be unsound)."""
    lhs, rhs, variables = eq2["lhs"], eq2["rhs"], list(eq2["variables"])
    for table in battery:
        if not equation_holds(lhs, rhs, variables, table):
            raise OracleError(
                f"TRUE verdict refuted by finite model {json.dumps(table)}")
