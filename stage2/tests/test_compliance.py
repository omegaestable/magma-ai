"""Compliance of the solver with the judge's own contracts.

Three things are pinned here, all of them "quiet until catastrophic":

* the **equation grammar** the judge accepts (RC-02). `_EQUATION_TEXT_RE` in
  `vendor/stage2-official/judge/verify.py` puts `x1` and `X` inside the legal
  character class, while the solver's tokenizer used to accept only single
  lowercase letters. Measured on the real judge 2026-08-27, the *reachable*
  half of this is narrower than the grammar and more dangerous than it looks:
  `_equation_def` derives the goal's binders with the same single-letter scan,
  so a digit- or uppercase-spelled row does not compile for the judge either
  (`infra_error`) - but a variable spelled **`h`** compiles fine and collides
  with the hypothesis name our own certificates bind. The verbatim-name
  certificate for such a row is LEAN_REJECTED and the renamed one is accepted
  (pinned as `rc02_h_renamed`).
* the **lone-surrogate path** (LEAN-07). `json.loads` of LLM output can hand us
  a string that has no UTF-8 encoding at all. The two filters that gate every
  emitted certificate must answer "no", not raise.
* the **banned-token list** (TEST-3). It is hand-copied into three files
  (`judge/verify.py`, `solver.py`, `oracles.py`) and the 2026-08-21 upstream
  hardening added 12 tokens in one commit. A missed sync rejects every
  certificate before Lean ever runs, with no other local signal.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

import oracles

REPO_ROOT = Path(__file__).resolve().parents[2]
JUDGE_VERIFY = REPO_ROOT / "vendor" / "stage2-official" / "judge" / "verify.py"

DIAMOND = "◇"


# ---------------------------------------------------------------------------
# RC-02: the judge's equation grammar, not the one the public data happens to use
# ---------------------------------------------------------------------------

def _rename_map(a: dict, b: dict) -> dict[str, str]:
    return dict(zip(a["variables"], b["variables"], strict=True))


def _relabel(term, mapping):
    if term[0] == "var":
        return "var", mapping[term[1]]
    return "op", _relabel(term[1], mapping), _relabel(term[2], mapping)


def _check_true(code: str, eq1: dict, eq2: dict, route: str) -> None:
    """Dispatch to whichever offline checker covers this certificate shape."""
    oracles.check_no_banned_tactics(code, route)
    shape = oracles.classify_true_certificate(code)
    assert shape != "other", f"unrecognised certificate shape for route {route}"
    if shape == "exact_expr":
        oracles.check_true_exact_certificate(code, eq1, eq2)
    elif shape == "singleton":
        oracles.check_true_singleton_certificate(code, eq1)
    elif shape == "lemma":
        oracles.check_true_lemma_certificate(code, eq1, eq2)
    else:
        oracles.check_true_lemma_chain_certificate(code, eq1, eq2)


LEGAL_SPELLINGS = [
    ("x = y " + DIAMOND + " x", "single lowercase letters (every public set)"),
    ("x1 = y1 " + DIAMOND + " x1", "letter+digit"),
    ("X = Y " + DIAMOND + " X", "uppercase"),
    ("x0 " + DIAMOND + " x1 = x1 " + DIAMOND + " x0", "digit-suffixed, both sides"),
    ("var1 = var2 " + DIAMOND + " var1", "multi-letter identifiers"),
]


@pytest.mark.parametrize("text,label", LEGAL_SPELLINGS)
def test_parse_equation_accepts_every_spelling_the_judge_grammar_allows(solver, text, label):
    """`_EQUATION_TEXT_RE` is the contract; the public data is only a sample."""
    import re as _re

    assert _re.match(r"^[\sa-zA-Z0-9◇=()]+$", text), "test case is not legal input"
    eq = solver.parse_equation(text)
    assert eq["variables"], label
    assert eq["lhs"] is not None and eq["rhs"] is not None


def test_digit_suffixed_variables_parse_to_the_same_structure_as_plain_ones(solver):
    plain = solver.parse_equation("x = y " + DIAMOND + " x")
    suffixed = solver.parse_equation("x1 = y1 " + DIAMOND + " x1")
    upper = solver.parse_equation("X = Y " + DIAMOND + " X")
    for other in (suffixed, upper):
        mapping = _rename_map(other, plain)
        assert _relabel(other["lhs"], mapping) == plain["lhs"]
        assert _relabel(other["rhs"], mapping) == plain["rhs"]
        # The distilled-certificate key is renaming-invariant, so a row spelled
        # `x1`/`y1` must hit the same DISTILLED_CERTS entry as `x`/`y`.
        assert solver.canonical_eq_text(other) == solver.canonical_eq_text(plain)


def test_a_full_solve_of_a_digit_spelled_row_yields_an_oracle_clean_certificate(solver):
    """End to end: the parser widening has to survive the certificate builders.

    `intro x1 y1` is valid Lean, so the names go through verbatim - this test
    exists to prove they actually do, through a real route, and that the offline
    kernel accepts the result.
    """
    eq1_text = "x1 = y1 " + DIAMOND + " (x1 " + DIAMOND + " y1)"
    eq2_text = ("x1 = y1 " + DIAMOND + " ((y1 " + DIAMOND + " (x1 " + DIAMOND
                + " y1)) " + DIAMOND + " y1)")
    problem = {"id": "compliance_x1", "eq1_id": 1, "eq2_id": 2,
               "equation1": eq1_text, "equation2": eq2_text}
    solved = solver.solve_problem(problem)
    assert solved is not None, "the widened parser must not cost the row"
    code = solved["answer"]["code"]
    assert solved["answer"]["verdict"] == "true"
    assert "intro x1 y1" in code, code
    _check_true(code, solver.parse_equation(eq1_text),
                solver.parse_equation(eq2_text), str(solved["route"]))


def test_a_variable_named_h_or_G_is_renamed_before_it_can_shadow_our_binders(solver):
    """`submission_certificate` opens with `intro G _ h`.

    A problem variable spelled `h` is judgeable (single lowercase letter) and
    `intro h ...` shadows the hypothesis: every `h a b` in the proof becomes an
    element applied to elements. Real-judge evidence 2026-08-27, one variable
    renamed and nothing else: verbatim `intro h g` -> `incorrect`/LEAN_REJECTED,
    renamed `intro q0 q1` -> **accepted** in 4.6 s (`rc02_h_renamed` in
    stage2/fixtures/judge_verified_certs.jsonl). Renaming is sound because our
    own `intro` chooses the binder names, so the proposition is unchanged.
    """
    eq = solver.parse_equation("h = G " + DIAMOND + " (h " + DIAMOND + " G)")
    assert set(eq["variables"]).isdisjoint(solver.RESERVED_LEAN_NAMES)
    plain = solver.parse_equation("x = y " + DIAMOND + " (x " + DIAMOND + " y)")
    assert solver.canonical_eq_text(eq) == solver.canonical_eq_text(plain)

    problem = {"id": "compliance_shadow", "eq1_id": 1, "eq2_id": 2,
               "equation1": "h = G " + DIAMOND + " (h " + DIAMOND + " G)",
               "equation2": ("h = G " + DIAMOND + " ((G " + DIAMOND + " (h "
                             + DIAMOND + " G)) " + DIAMOND + " G)")}
    solved = solver.solve_problem(problem)
    assert solved is not None
    code = solved["answer"]["code"]
    assert "intro h G" not in code and "intro G h" not in code, code
    _check_true(code, solver.parse_equation(problem["equation1"]),
                solver.parse_equation(problem["equation2"]), str(solved["route"]))


def test_the_judges_own_binder_scan_is_still_single_lowercase_letters():
    """Rail 14 pin, and the reason the widening above is insurance, not a fix.

    `_equation_def` interpolates the equation text into Lean and builds the
    binder list with a word-bounded single-lowercase-letter scan - the same one
    the solver used to use. So a row spelled `x1 = y1 ◇ x1` produces *no*
    binders and the judge's own JudgeProblem.lean fails to compile: unjudgeable
    for every contestant, not a row we lose by refusing to parse it. If upstream
    ever widens this scan, the solver's widened parser becomes load-bearing and
    this test is the notice.
    """
    if not JUDGE_VERIFY.exists():
        pytest.skip(f"vendored judge not present at {JUDGE_VERIFY}")
    source = JUDGE_VERIFY.read_text(encoding="utf-8")
    assert "_equation_def" in source
    body = source.split("_equation_def", 1)[1].split("def _render_problem_source", 1)[0]
    assert "([a-z])" in body, (
        "judge/verify.py:_equation_def no longer derives binders with a "
        "single-lowercase-letter scan - re-check which variable spellings are "
        "actually judgeable before trusting the solver's parser assumptions")


def test_safe_variable_names_is_all_or_nothing(solver):
    """A partial rename could collide with a name it left alone."""
    assert solver.safe_variable_names(["x", "y"]) is None
    mapping = solver.safe_variable_names(["x", "h", "q0"])
    assert mapping is not None
    assert len(set(mapping.values())) == 3, mapping


# ---------------------------------------------------------------------------
# LEAN-07: a filter whose job is to fail closed must not raise
# ---------------------------------------------------------------------------

def _lone_surrogate_code() -> str:
    """A string with no UTF-8 encoding, produced the way production would."""
    escape = "\\ud83d"
    payload = json.loads('{"c": "import JudgeProblem\\ndef submission : Goal := by\\n  a'
                         + escape + 'b\\n"}')
    code = payload["c"]
    with pytest.raises(UnicodeEncodeError):
        code.encode("utf-8")
    return code


def test_judge_answer_payload_returns_none_on_a_lone_surrogate(solver):
    code = _lone_surrogate_code()
    assert solver.judge_answer_payload({"verdict": "true", "code": code}) is None
    assert solver.marathon_answer_payload(
        {"id": "row", "verdict": "true", "code": code}) is None


def test_sanitize_lean_code_returns_false_on_a_lone_surrogate(solver):
    assert solver.sanitize_lean_code(_lone_surrogate_code(), verdict="true") is False


# ---------------------------------------------------------------------------
# TEST-3: the banned-token list, in all three copies
# ---------------------------------------------------------------------------

def _ast_tuple_constant(path: Path, name: str) -> tuple[str, ...]:
    """Read a module-level tuple of string constants without importing.

    Importing `judge/verify.py` drags in the Lean plumbing; the gate is
    Lean-free by design.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return tuple(ast.literal_eval(node.value))
    raise AssertionError(f"{name} not found in {path}")


@pytest.fixture(scope="module")
def official_banned_tokens() -> tuple[str, ...]:
    if not JUDGE_VERIFY.exists():
        pytest.skip(f"vendored judge not present at {JUDGE_VERIFY}")
    return _ast_tuple_constant(JUDGE_VERIFY, "BANNED_PROOF_TOKENS")


def test_banned_token_lists_agree_across_all_three_copies(solver, official_banned_tokens):
    """Judge, solver and oracle carry the same list.

    The judge scans raw certificate text - comments included - before Lean
    runs, so one added token upstream rejects an entire certificate family
    while every offline check stays green (rail 14).
    """
    official = set(official_banned_tokens)
    assert official, "AST extraction returned nothing"
    assert set(solver.JUDGE_BANNED_TOKENS) == official, (
        "solver.JUDGE_BANNED_TOKENS drifted from judge/verify.py: "
        f"missing {sorted(official - set(solver.JUDGE_BANNED_TOKENS))}, "
        f"extra {sorted(set(solver.JUDGE_BANNED_TOKENS) - official)}")
    assert set(oracles._JUDGE_BANNED_TOKENS) == official, (
        "oracles._JUDGE_BANNED_TOKENS drifted from judge/verify.py: "
        f"missing {sorted(official - set(oracles._JUDGE_BANNED_TOKENS))}, "
        f"extra {sorted(set(oracles._JUDGE_BANNED_TOKENS) - official)}")


def _judge_matcher(tokens: tuple[str, ...]):
    """`verify.py:_find_banned_token`, re-expressed over an injected list.

    Copied deliberately rather than imported: the point of the differential is
    that the *matcher* is re-implemented in three places, so this fourth copy
    is the reference the other two are compared against, and it is 6 lines.
    """
    import re

    def find(code: str) -> str | None:
        for token in tokens:
            if token.startswith(("#", "@")) or token.endswith(" "):
                if re.search(re.escape(token), code):
                    return token
            elif re.search(rf"\b{re.escape(token)}\b", code):
                return token
        return None

    return find


def test_matcher_differential_per_token(solver, official_banned_tokens):
    """The judge scans comments too, so a comment is the honest probe."""
    judge_find = _judge_matcher(official_banned_tokens)
    for token in official_banned_tokens:
        probe = f"-- a comment mentioning {token}\ntheorem x : True := trivial\n"
        expected = judge_find(probe)
        assert expected is not None, f"probe for {token!r} does not trip the judge"
        assert solver.find_judge_banned_token(probe) == expected, token
        assert oracles.find_judge_banned_token(probe) == expected, token


def test_matcher_differential_negative_control(solver, official_banned_tokens):
    """Rail 5c: a search that always fires proves nothing. Real certs are clean."""
    judge_find = _judge_matcher(official_banned_tokens)
    eq1 = solver.parse_equation("x = y " + DIAMOND + " (x " + DIAMOND + " y)")
    eq2 = solver.parse_equation(
        "x = y " + DIAMOND + " ((y " + DIAMOND + " (x " + DIAMOND + " y)) " + DIAMOND + " y)")
    result = solver.equational_closure_route(eq1, eq2)
    assert result is not None, "closure route stopped firing; pick another probe row"
    real_certs = [result[1], solver.false_certificate(2, [[0, 1], [0, 1]])]
    for code in real_certs:
        assert judge_find(code) is None, code[:200]
        assert solver.find_judge_banned_token(code) is None
        assert oracles.find_judge_banned_token(code) is None
