"""Stage 2 solver: deterministic + LLM equational theory prover."""

from __future__ import annotations

import json
import importlib
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from itertools import product
from typing import Any, Callable


_PROCESS_START = time.monotonic()


PROMPT = """You produce proofs about magmas. A magma is a type G with one binary operation
written `a ◇ b`. You are given two equational laws and must prove the first
implies the second.

The deterministic solver already searched for a finite magma satisfying Equation1
but breaking Equation2 -- named tables, structured/affine/quadratic families,
every magma of order <= 3, duals, and a randomized order 4-6 search -- and found
none. So Equation1 very likely IMPLIES Equation2: prove it.

That search is NOT exhaustive. If you can actually exhibit a finite magma where
Equation1 HOLDS and Equation2 FAILS, send that instead of a proof:
{"verdict":"false","table":[[...],[...]]}
giving the full n x n Cayley table over {0,...,n-1} (rows = left argument).
The solver re-checks every table exhaustively before submitting, so a wrong
table is discarded harmlessly and a correct one wins the problem outright.
Only do this if you have actually verified both conditions on the table;
otherwise prove TRUE.

Problem {problem.id}: prove Equation{problem.eq1_id} implies Equation{problem.eq2_id}.
Hypothesis (Equation1):  {problem.equation1}
Goal       (Equation2):  {problem.equation2}

Deterministic solver hints:
{solver.analysis}

################  BEST WAY TO ANSWER: the rewrite chain  ################
Give the sequence of terms from the goal's left side to the goal's right side,
where EACH consecutive pair differs by exactly ONE use of the hypothesis on ONE
subterm. THE SOLVER computes the exact effect of each hypothesis application and
builds the Lean proof for you — so you never do term bookkeeping by hand (that is
the #1 source of mistakes). Use only the goal's variables.

CRITICAL: ◇ is NOT associative and NOT commutative unless the hypothesis itself
says so. Never reassociate `a ◇ (b ◇ c)` to `(a ◇ b) ◇ c`, and never reorder
`a ◇ b` to `b ◇ a`, as a chain step — those are not valid. Every step must change
exactly one subterm by matching (an instance of) one side of the hypothesis and
replacing it with the other side. Keep the full parenthesization explicit.

{"verdict":"true","proof_kind":"guided_chain","chain":["<goal-lhs>","<t1>","...","<goal-rhs>"],"key_terms":["<t>","..."]}

To design the chain, think of the hypothesis L = R as a two-way rewrite: anywhere
you see (an instance of) L you may replace it by R, and vice-versa. List the terms
you pass through. Make each step a single such replacement. Smaller steps are
safer — the solver proves each step by search, so many small steps beat few big
ones.

"key_terms" is optional but powerful: list up to 8 extra terms (goal variables
only, full parenthesization) that you believe appear somewhere in the derivation —
useful hypothesis instantiations, absorbing shapes, or halfway terms. Even if your
chain has a gap, the solver runs a bidirectional equational search SEEDED with your
chain terms and key_terms and can finish the proof. If you are unsure of the exact
chain, give your best chain AND generous key_terms.

Also optional: "peak_term" — many of these proofs EXPAND both sides to one big
common term and meet there. If you can name that single largest middle term, give
it as "peak_term":"<term>"; the solver then searches goal-lhs -> peak and
peak -> goal-rhs separately, which is much easier than the full jump.

################  OFTEN EASIER: name a lemma  ################
You do not have to prove the goal at all. If you can name a SMALL law that (a)
follows from the hypothesis and (b) makes the goal obvious, just say so:

{"verdict":"true","proof_kind":"lemma","lemma":"a ◇ b = a","lemmas":["<alt>","..."]}

Use fresh variables (a, b, c...) — the lemma is its own universally quantified
law, independent of the goal's variables. THE SOLVER proves the lemma from the
hypothesis itself and then derives the goal from it; you supply only the idea.

This is often far easier than a chain, because a small law is a much smaller
search target than the goal. Laws worth considering, strongest first:
  "a = b"            -- the hypothesis forces the magma to have one element
  "a ◇ b = a"        -- left projection      "a ◇ b = b"  -- right projection
  "a ◇ a = a"        -- idempotence
  "a ◇ b = a ◇ c"    -- the right argument never matters
  "a ◇ b = c ◇ b"    -- the left argument never matters
  "a ◇ b = b ◇ a"    -- commutativity
Any equation is allowed, not just these. Give "lemmas" as a list to offer
several; the solver tries each and keeps the first that works. A lemma that is
too strong to be true is discarded harmlessly, so guess boldly — but a lemma
must genuinely IMPLY the goal, or it is useless even if true.

################  FALLBACK: a full Lean proof  ################
Only if a chain is impossible. Return {"verdict":"true","code":"<full Lean file>"}
whose code field is exactly (newlines written as \\n inside the JSON string):

import JudgeProblem

def submission : Goal := by
  intro G _ h
  intro <goal vars>
  <steps>

After `intro G _ h`, `h` is the hypothesis law (fully quantified) and the goal is
`<Eq2-LHS> = <Eq2-RHS>`. Use ONLY these tactics:
  rw [h a b ...]           -- replace <Eq1-LHS>[a,b,...] by <Eq1-RHS>; `rw [← h ...]` reverses
  calc ... := by rw [...]   -- an explicit equational chain
  Eq.trans, Eq.symm, congrArg (fun t => t ◇ c) / (fun t => c ◇ t), exact, rfl
DO NOT use `simp`, `simpa`, `simp_all`, `aesop`, or `grind`: on these laws `simp`
loops (maximum recursion depth) and is rejected. When you write `h a b c`, the
result is <Eq1-LHS> and <Eq1-RHS> with the variables literally replaced by a,b,c;
substitute carefully or you will get a type mismatch.

Import nothing except `import JudgeProblem`. No `sorry`/`admit`. No Mathlib.

################  Learn from previous attempts ################
{history.attempts}
{solver.feedback}
If a Lean error shows a type mismatch, your hypothesis instantiation was wrong —
recompute it or switch to the rewrite chain. If a chain step was unprovable,
split it into smaller single-rewrite steps.

Output exactly ONE JSON object (first char {, last char }). No markdown, no
<think>, no prose.
"""

MAX_SUBMISSION_BYTES = 500_000

# Hard limits enforced by the official judge, mirrored from
# vendor/stage2-official/judge/verify.py (MAX_CODE_LENGTH / MAX_FALSE_CERT_BYTES).
# A certificate over these is rejected with the row scored as attempted, so
# emitting one is strictly worse than skipping. Keep these two in sync with any
# harness sync.
JUDGE_MAX_CODE_LENGTH = 50_000
JUDGE_MAX_FALSE_CERT_BYTES = 10_000

# Our own caps sit just under the judge's, so a cert that passes locally cannot
# be rejected on size. Previously 100_000 / 20_000 — both *twice* the judge's
# limit, which silently accepted certificates the judge would refuse (found
# 2026-07-29; no benchmark row was over the line, so this closes a latent hole
# rather than recovering lost rows).
MAX_LEAN_CODE_BYTES = JUDGE_MAX_CODE_LENGTH - 500
MAX_FALSE_CERT_BYTES = JUDGE_MAX_FALSE_CERT_BYTES - 500
VALID_VERDICTS = {"true", "false"}
AFFINE_LINEAR_SIZES = (2, 3, 4, 5, 7, 8, 9)
AFFINE_QUADRATIC_SIZES = (2, 3, 5, 7)
ENUMERATION_MAX_N = 3
STRUCTURED_MAX_N = 7
LOCAL_MODEL_SIZES = (4, 5)
LOCAL_MODEL_TIME_BUDGET = 6.0
LOCAL_MODEL_MAX_FLIPS = 4000
LOCAL_MODEL_NOISE = 0.25
REWRITE_CHAIN_MAX_DEPTH = 2
ABSORPTION_CHAIN_MAX_DEPTH = 3
ABSORPTION_POOL_LIMIT = 10
ABSORPTION_FRONTIER_LIMIT = 220
ABSORPTION_MAX_FILLS = 180
ABSORPTION_TERM_SLACK = 6
ABSORPTION_TIME_BUDGET = 0.05
ABSORPTION_DEEP_CHAIN_MAX_DEPTH = 3
ABSORPTION_DEEP_POOL_LIMIT = 12
ABSORPTION_DEEP_FRONTIER_LIMIT = 260
ABSORPTION_DEEP_MAX_FILLS = 120
ABSORPTION_DEEP_TERM_SLACK = 8
ABSORPTION_DEEP_TIME_BUDGET = 1.6
ABSORPTION_CONTEXT_BRIDGE_POOL_LIMIT = 16
ABSORPTION_CONTEXT_BRIDGE_SEED_LIMIT = 8
ABSORPTION_CONTEXT_BRIDGE_MAX_FILLS = 5000
ABSORPTION_CONTEXT_BRIDGE_TERM_SLACK = 12
ABSORPTION_CONTEXT_BRIDGE_DEPTH_SLACK = 4
ABSORPTION_CONTEXT_BRIDGE_TIME_BUDGET = 1.5
EQUATIONAL_CLOSURE_CHAIN_MAX_DEPTH = 4
EQUATIONAL_CLOSURE_POOL_LIMIT = 18
EQUATIONAL_CLOSURE_FRONTIER_LIMIT = 900
EQUATIONAL_CLOSURE_MAX_FILLS = 350
EQUATIONAL_CLOSURE_TERM_SLACK = 10
EQUATIONAL_CLOSURE_DEPTH_SLACK = 3
EQUATIONAL_CLOSURE_TIME_BUDGET = 0.45
GUIDED_CHAIN_MAX_DEPTH = 3
GUIDED_CHAIN_CLOSURE_TIME_BUDGET = 0.08
LLM_GUIDED_CHAIN_MAX_DEPTH = 8
LLM_GUIDED_CHAIN_CLOSURE_TIME_BUDGET = 1.0
# Frontier cap for the guided per-edge rewrite search. The model can hand us
# an unprovable edge (it sometimes answers "true" on a FALSE row), and with a
# size-increasing eq1 the depth-8 BFS then grows without bound - measured at
# 21.5 GB RSS on hard1_0022, with the memory guard armed but never consulted.
GUIDED_CHAIN_FRONTIER_LIMIT = 4000
DERIVED_CP_MAX_RULE_SIZE = 15
DERIVED_CP_MAX_RULES = 48
DERIVED_CP_CHAIN_MAX_DEPTH = 4
DERIVED_CP_POOL_LIMIT = 16
DERIVED_CP_FILL_POOL_CAP = 10
DERIVED_CP_FRONTIER_LIMIT = 2600
DERIVED_CP_MAX_FILLS = 1200
DERIVED_CP_TERM_SLACK = 10
DERIVED_CP_DEPTH_SLACK = 3
DERIVED_CP_TIME_BUDGET = 8.0
LLM_SEEDED_CLOSURE_CHAIN_MAX_DEPTH = 5
LLM_SEEDED_CLOSURE_POOL_LIMIT = 20
LLM_SEEDED_CLOSURE_FRONTIER_LIMIT = 3600
LLM_SEEDED_CLOSURE_MAX_FILLS = 3000
LLM_SEEDED_CLOSURE_TERM_SLACK = 10
LLM_SEEDED_CLOSURE_DEPTH_SLACK = 3
LLM_SEEDED_CLOSURE_TIME_BUDGET = 5.0
LLM_SEEDED_CLOSURE_MAX_SEEDS = 24
LLM_SEEDED_CLOSURE_FILL_POOL_CAP = 14
LLM_SEEDED_CLOSURE_WAYPOINT_BUDGET = 1.5
LLM_SEEDED_CLOSURE_MAX_WAYPOINTS = 5
LLM_SEEDED_CLOSURE_TOTAL_BUDGET = 14.0
LLM_MAX_ROUNDS = 6
SOLO_FALLBACK_RESERVE_SECONDS = 90.0
SOLO_DETERMINISTIC_SHARE = 0.55
SOLO_LLM_ROUND_MIN_SECONDS = 150.0
MARATHON_LLM_MAX_CALLS = 64
MARATHON_LLM_BATCH_SIZE = 8
MARATHON_REF_SECONDS_DEFAULT = 600.0
MARATHON_DETERMINISTIC_SHARE = 0.6
LLM_MAX_TABLE_N = 8
LLM_MAX_OUTPUT_TOKENS = 16384
LLM_HTTP_TIMEOUT_SECONDS = 75.0

EFFORT_TIERS = {
    #        time x   frontier x  fills x   pool +   depth +
    "fast": (1.0, 1.0, 1.0, 0, 0),
    "standard": (7.5, 4.6, 3.3, 6, 0),
    "deep": (22.0, 11.5, 6.6, 10, 1),
}
_EFFORT = "fast"


def set_effort(tier: str) -> None:
    global _EFFORT
    if tier in EFFORT_TIERS:
        _EFFORT = tier


def effort_tier() -> str:
    return _EFFORT


def effort_for_seconds(per_problem_seconds: float) -> str:
    """Pick a tier from the wall-clock actually available per problem."""
    if per_problem_seconds >= 240.0:
        return "deep"
    if per_problem_seconds >= 45.0:
        return "standard"
    return "fast"


_HARD_DEADLINE: float | None = None


def set_hard_deadline(deadline: float | None) -> None:
    global _HARD_DEADLINE
    _HARD_DEADLINE = deadline


def hard_deadline_passed() -> bool:
    if memory_exceeded():
        return True
    return _HARD_DEADLINE is not None and time.monotonic() >= _HARD_DEADLINE


def local_deadline(time_budget: float | None) -> float | None:
    """Engine-local deadline clamped to the global hard deadline."""
    local = time.monotonic() + time_budget if time_budget else None
    if _HARD_DEADLINE is None:
        return local
    if local is None:
        return _HARD_DEADLINE
    return min(local, _HARD_DEADLINE)


def _eff_time(base: float) -> float:
    return base * EFFORT_TIERS[_EFFORT][0]


def _eff_frontier(base: int) -> int:
    return int(base * EFFORT_TIERS[_EFFORT][1])


def _eff_fills(base: int) -> int:
    return int(base * EFFORT_TIERS[_EFFORT][2])


def _eff_pool(base: int) -> int:
    return base + EFFORT_TIERS[_EFFORT][3]


def _eff_depth(base: int) -> int:
    return base + EFFORT_TIERS[_EFFORT][4]

LLM_CONFIG = {
    "model": "openai/gpt-oss-120b",
    "provider": "deepinfra/bf16",
    "max_output_tokens": LLM_MAX_OUTPUT_TOKENS,
    "temperature": 0.0,
    "reasoning_effort": "medium",
    "use_seed": True,
    "seed": 0,
    "http_timeout_seconds": LLM_HTTP_TIMEOUT_SECONDS,
}

ALLOWED_IMPORTS = {
    "JudgeProblem",
    "JudgeDecide.DecideBang",
    "JudgeFinOp.MemoFinOp",
    "JudgeMagma.Magma",
}

BANNED_LEAN_RE = re.compile(
    r"\b(?:sorry|admit|sorryAx|dbg_trace|dbgTrace|run_tac|mkSorry|"
    r"initialize|builtin_initialize|axiom|unsafe|opaque|macro|elab|syntax|"
    r"aesop|grind|simp_all)\b"
    r"|#(?:eval|check|print|reduce)|\b(?:Teorth|teorth|EquationalTheories)\b"
    r"|\bEquation(?!LHS\b|RHS\b)\d+\b",
    re.IGNORECASE,
)

WITNESS_TABLES = (
    ("LP", [[0, 0], [1, 1]]),
    ("RP", [[0, 1], [0, 1]]),
    ("C0", [[0, 0], [0, 0]]),
    ("XOR", [[0, 1], [1, 0]]),
    ("AND", [[0, 0], [0, 1]]),
    ("OR", [[0, 1], [1, 1]]),
    ("XNOR", [[1, 0], [0, 1]]),
    ("NAND", [[1, 1], [1, 0]]),
    ("NOR", [[1, 0], [0, 0]]),
    ("IMP", [[1, 0], [1, 1]]),
    ("NIMP", [[0, 1], [0, 0]]),
    ("A2", [[0, 0], [1, 0]]),
    ("Z3A", [[0, 1, 2], [1, 2, 0], [2, 0, 1]]),
    ("Z3B", [[0, 2, 1], [2, 1, 0], [1, 0, 2]]),
    ("T3L", [[0, 0, 0], [0, 0, 0], [0, 1, 0]]),
    ("T3R", [[0, 0, 0], [0, 0, 0], [0, 0, 1]]),
    ("S4A", [[3, 1, 1, 3], [0, 3, 2, 3], [3, 1, 3, 3], [0, 1, 2, 3]]),
    ("S5A", [[1, 2, 3, 4, 0], [0, 4, 3, 4, 1], [4, 2, 2, 1, 0], [2, 0, 2, 3, 2], [3, 1, 3, 0, 4]]),
    ("S4B", [[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 1, 0]]),
    ("S5B", [[4, 3, 2, 2, 2], [2, 3, 2, 2, 3], [2, 2, 2, 2, 2], [2, 2, 2, 2, 2], [2, 2, 2, 2, 2]]),
    ("S5C", [[0, 0, 0, 2, 2], [4, 1, 1, 4, 1], [1, 2, 2, 1, 2], [2, 3, 3, 3, 2], [2, 4, 4, 2, 4]]),
    ("S4C", [[3, 3, 2, 2], [1, 1, 0, 0], [3, 3, 2, 2], [1, 1, 0, 0]]),
    ("S4D", [[3, 2, 3, 3], [3, 3, 3, 3], [2, 3, 3, 3], [1, 2, 3, 3]]),
    ("S4E", [[2, 2, 2, 3], [3, 3, 2, 3], [2, 2, 2, 3], [3, 3, 2, 3]]),
    ("S4F", [[0, 2, 3, 1], [3, 1, 0, 2], [1, 3, 2, 0], [2, 0, 1, 3]]),
    ("S5D", [[3, 3, 2, 2, 3], [4, 4, 2, 4, 2], [2, 2, 2, 2, 2], [2, 2, 2, 2, 2], [2, 2, 2, 2, 2]]),
    ("S4G", [[0, 3, 2, 1], [0, 3, 2, 1], [2, 1, 0, 3], [2, 1, 0, 3]]),
    ("S6A", [[4, 4, 1, 1, 4, 2], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 5, 2, 0, 2, 5], [1, 1, 3, 3, 3, 2], [4, 2, 0, 1, 3, 0]]),
    ("S9A", [[2, 8, 7, 2, 8, 8, 2, 7, 7], [1, 1, 0, 6, 6, 6, 1, 0, 0], [3, 3, 0, 6, 6, 6, 3, 0, 0], [1, 1, 0, 6, 6, 6, 1, 0, 0], [3, 3, 5, 4, 4, 4, 3, 5, 5], [2, 8, 7, 2, 8, 8, 2, 7, 7], [3, 3, 5, 4, 4, 4, 3, 5, 5], [2, 8, 7, 2, 8, 8, 2, 7, 7], [1, 1, 5, 4, 4, 4, 1, 5, 5]]),
)


def reflexive_true_certificate() -> str:
    return """import JudgeProblem

def submission : Goal := by
  intro G _ h
  exact h
"""


def false_certificate(n: int, table: list[list[int]]) -> str:
    table_str = json.dumps(table, separators=(",", ":"))
    max_rec_depth = "set_option maxRecDepth 20000\n" if n >= 7 else ""
    return (
        "import JudgeProblem\n"
        "import JudgeDecide.DecideBang\n"
        "import JudgeFinOp.MemoFinOp\n"
        "open MemoFinOp\n"
        f"{max_rec_depth}\n"
        "def submission : Goal := by\n"
        f"  let m : Magma (Fin {n}) := {{\n"
        f"    op := finOpTable \"{table_str}\"\n"
        "  }\n"
        f"  refine Exists.intro (Fin {n}) ?_\n"
        "  refine Exists.intro m ?_\n"
        "  decideFin!\n"
    )


def singleton_true_certificate(
    eq1_vars: list[str],
    eq2_vars: list[str],
    singleton_var: str,
    singleton_on_lhs: bool,
) -> str:
    if not eq1_vars:
        return reflexive_true_certificate()

    args_a: list[str] = []
    args_b: list[str] = []
    for var in eq1_vars:
        if var == singleton_var:
            args_a.append("a")
            args_b.append("b")
        else:
            args_a.append("b")
            args_b.append("b")

    call_a = "h" if not args_a else "h " + " ".join(args_a)
    call_b = "h" if not args_b else "h " + " ".join(args_b)
    if singleton_on_lhs:
        collapse = f"({call_a}).trans ({call_b}).symm"
    else:
        collapse = f"({call_a}).symm.trans ({call_b})"
    intro_vars = " ".join(eq2_vars)
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""

    return (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hall : ∀ a b : G, a = b := by\n"
        "    intro a b\n"
        f"    exact {collapse}\n"
        f"{intro_line}"
        "  exact hall _ _\n"
    )


def substitution_true_certificate(
    eq2_vars: list[str],
    call_expr: str,
) -> str:
    intro_vars = " ".join(eq2_vars)
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    return (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{intro_line}"
        f"  exact {call_expr}\n"
    )


def projection_true_certificate(eq2_vars: list[str], proof_expr: str) -> str:
    intro_vars = " ".join(eq2_vars)
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    return (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )


def grind_true_certificate(eq2_vars: list[str], *, heartbeats: int = 100000) -> str:
    intro_vars = " ".join(eq2_vars)
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    return (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{intro_line}"
        f"  set_option maxHeartbeats {heartbeats} in\n"
        "  grind\n"
    )


Term = tuple[Any, ...]


def is_reflexive_problem(problem: dict[str, Any]) -> bool:
    return problem.get("eq1_id") == problem.get("eq2_id")


def make_true_answer(problem: dict[str, Any], code: str) -> dict[str, Any]:
    return {
        "id": str(problem.get("id", "")),
        "verdict": "true",
        "code": code,
    }


def make_false_answer(problem: dict[str, Any], n: int, table: list[list[int]]) -> dict[str, Any]:
    return {
        "id": str(problem.get("id", "")),
        "verdict": "false",
        "code": false_certificate(n, table),
    }


def judge_answer_payload(answer: dict[str, Any]) -> dict[str, str] | None:
    verdict = answer.get("verdict")
    code = answer.get("code")
    if verdict not in VALID_VERDICTS or not isinstance(code, str):
        return None
    code_bytes = len(code.encode("utf-8"))
    if code_bytes > MAX_LEAN_CODE_BYTES:
        return None
    if verdict == "false" and code_bytes > MAX_FALSE_CERT_BYTES:
        return None
    return {"verdict": verdict, "code": code}


def marathon_answer_payload(answer: dict[str, Any]) -> dict[str, str] | None:
    pid = answer.get("id")
    if not isinstance(pid, str) or not pid:
        return None
    payload = judge_answer_payload(answer)
    if payload is None:
        return None
    return {"id": pid, **payload}


def strip_outer_parens(text: str) -> str:
    s = text.strip()
    while len(s) >= 2 and s[0] == "(" and s[-1] == ")":
        depth = 0
        wraps = True
        for idx, char in enumerate(s):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            if depth == 0 and idx < len(s) - 1:
                wraps = False
                break
        if not wraps:
            break
        s = s[1:-1].strip()
    return s


def parse_term(text: str, variables: set[str]) -> Term:
    s = strip_outer_parens(text)
    depth = 0
    last_op = -1
    for idx, char in enumerate(s):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char in {"◇", "*"} and depth == 0:
            last_op = idx
    if last_op >= 0:
        return ("op", parse_term(s[:last_op], variables), parse_term(s[last_op + 1 :], variables))
    if len(s) == 1 and s in variables:
        return ("var", s)
    raise ValueError(f"cannot parse term: {text!r}")


def parse_equation(text: str) -> dict[str, Any]:
    if "=" not in text:
        raise ValueError(f"cannot parse equation: {text!r}")
    variables = []
    seen: set[str] = set()
    for var in re.findall(r"\b([a-z])\b", text):
        if var not in seen:
            seen.add(var)
            variables.append(var)
    lhs_text, rhs_text = text.split("=", 1)
    lhs_text = lhs_text.strip()
    rhs_text = rhs_text.strip()
    return {
        "variables": variables,
        "lhs": parse_term(lhs_text, seen),
        "rhs": parse_term(rhs_text, seen),
        "lhs_text": lhs_text,
        "rhs_text": rhs_text,
        "text": text.strip(),
    }


NARROW_GRIND_TRUE_SHAPES = (
    ("x = y * (y * (z * (w * x)))", "x = y * (z * (w * (u * x)))"),
    ("x = (((x * y) * y) * z) * y", "x = (((x * y) * y) * x) * z"),
    ("x * y = z * ((x * z) * y)", "x * y = (z * z) * (x * y)"),
    ("x * y = (y * x) * (y * z)", "x * y = y * (y * z)"),
    ("x * y = (y * y) * (z * x)", "x * y = ((y * z) * x) * z"),
    ("x = (y * y) * (x * y)", "x = (y * x) * (y * y)"),
    ("x = y * (y * (x * z))", "x * y = y * (x * (z * z))"),
    ("x = (y * (x * z)) * (z * z)", "x * y = x * ((x * y) * x)"),
    ("x = x * (y * (z * (x * y)))", "x = x * (((y * x) * z) * w)"),
)


def equation_shape_key(eq: dict[str, Any]) -> tuple[Term, Term]:
    return eq["lhs"], eq["rhs"]


def canonical_law_key(eq: dict[str, Any]) -> tuple[Term, Term]:
    """Renaming-invariant key: `a = c` and `a = b` are the same law."""
    names: dict[str, str] = {}
    return (
        canonical_term_shape(eq["lhs"], names),
        canonical_term_shape(eq["rhs"], names),
    )


def canonical_term_shape(term: Term, names: dict[str, str]) -> Term:
    if term[0] == "var":
        var = str(term[1])
        if var not in names:
            names[var] = f"v{len(names)}"
        return "var", names[var]
    return "op", canonical_term_shape(term[1], names), canonical_term_shape(term[2], names)


def equation_pair_shape_key(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[Term, Term, Term, Term]:
    names: dict[str, str] = {}
    return (
        canonical_term_shape(eq1["lhs"], names),
        canonical_term_shape(eq1["rhs"], names),
        canonical_term_shape(eq2["lhs"], names),
        canonical_term_shape(eq2["rhs"], names),
    )


# Removed 2026-07-23: `LARGE_WITNESS_SHAPE_KEYS` pinned the 9-element witness
# `S9A` to the exact (eq1, eq2) pair it was discovered on, so it was never
# tried on any other goal. A witness table is a property of the *hypothesis*
# alone -- whether it refutes the goal is what `table_is_counterexample`
# already decides, and it short-circuits on `equation_holds(eq1, table)`, so
# the guard bought 0.021 ms/problem. It cost eight playground rows: the whole
# `eq1 = Eq168` (central groupoid) family has no model of order <= 3 and none
# in the structured/affine/quadratic families, so `S9A` was the only witness
# the solver owned for them and the gate hid it. Gate large tables on measured
# cost if they ever matter -- never on a full equation-pair shape, which is a
# benchmark id in disguise (Operational Note 2).


@lru_cache(maxsize=1)
def narrow_grind_true_shape_keys() -> frozenset[tuple[Term, Term, Term, Term]]:
    keys: set[tuple[Term, Term, Term, Term]] = set()
    for src_text, goal_text in NARROW_GRIND_TRUE_SHAPES:
        src = parse_equation(src_text)
        goal = parse_equation(goal_text)
        keys.add((*equation_shape_key(src), *equation_shape_key(goal)))
    return frozenset(keys)


@lru_cache(maxsize=None)
def term_vars_tuple(term: Term) -> tuple[str, ...]:
    if term[0] == "var":
        return (str(term[1]),)
    return tuple(set(term_vars_tuple(term[1])) | set(term_vars_tuple(term[2])))


def term_vars(term: Term) -> set[str]:
    return set(term_vars_tuple(term))


@lru_cache(maxsize=None)
def term_size(term: Term) -> int:
    if term[0] == "var":
        return 1
    return 1 + term_size(term[1]) + term_size(term[2])


@lru_cache(maxsize=None)
def term_depth(term: Term) -> int:
    if term[0] == "var":
        return 0
    return 1 + max(term_depth(term[1]), term_depth(term[2]))


@lru_cache(maxsize=None)
def term_to_lean(term: Term) -> str:
    if term[0] == "var":
        return str(term[1])
    return f"({term_to_lean(term[1])} ◇ {term_to_lean(term[2])})"


@lru_cache(maxsize=None)
def dual_term(term: Term) -> Term:
    if term[0] == "var":
        return term
    return ("op", dual_term(term[2]), dual_term(term[1]))


def dual_equation(equation: dict[str, Any]) -> dict[str, Any]:
    out = dict(equation)
    out["lhs"] = dual_term(equation["lhs"])
    out["rhs"] = dual_term(equation["rhs"])
    out["lhs_text"] = term_to_lean(out["lhs"])
    out["rhs_text"] = term_to_lean(out["rhs"])
    out["text"] = f"{out['lhs_text']} = {out['rhs_text']}"
    return out


@lru_cache(maxsize=None)
def term_subterms_tuple(term: Term) -> tuple[Term, ...]:
    out: list[Term] = [term]
    if term[0] == "op":
        out.extend(term_subterms_tuple(term[1]))
        out.extend(term_subterms_tuple(term[2]))
    return tuple(out)


def term_subterms(term: Term) -> list[Term]:
    return list(term_subterms_tuple(term))


@lru_cache(maxsize=None)
def boundary_vars(term: Term) -> tuple[str | None, str | None]:
    if term[0] == "var":
        return str(term[1]), str(term[1])
    left = boundary_vars(term[1])
    right = boundary_vars(term[2])
    return left[0], right[1]


@lru_cache(maxsize=None)
def subterm_paths_tuple(term: Term, prefix: tuple[int, ...] = ()) -> tuple[tuple[int, ...], ...]:
    paths: list[tuple[int, ...]] = [prefix]
    if term[0] == "op":
        paths.extend(subterm_paths_tuple(term[1], prefix + (0,)))
        paths.extend(subterm_paths_tuple(term[2], prefix + (1,)))
    return tuple(paths)


def subterm_paths(term: Term, prefix: tuple[int, ...] = ()) -> list[tuple[int, ...]]:
    return list(subterm_paths_tuple(term, prefix))


@lru_cache(maxsize=None)
def term_at_path(term: Term, path: tuple[int, ...]) -> Term:
    cur = term
    for part in path:
        cur = cur[1] if part == 0 else cur[2]
    return cur


@lru_cache(maxsize=None)
def replace_subterm(term: Term, path: tuple[int, ...], replacement: Term) -> Term:
    if not path:
        return replacement
    if term[0] != "op":
        return term
    head, tail = path[0], path[1:]
    if head == 0:
        return ("op", replace_subterm(term[1], tail, replacement), term[2])
    return ("op", term[1], replace_subterm(term[2], tail, replacement))


@lru_cache(maxsize=None)
def context_to_lean(term: Term, path: tuple[int, ...], placeholder: str = "t") -> str:
    if not path:
        return placeholder
    if term[0] == "var":
        return term_to_lean(term)
    head, tail = path[0], path[1:]
    if head == 0:
        left = context_to_lean(term[1], tail, placeholder)
        right = term_to_lean(term[2])
    else:
        left = term_to_lean(term[1])
        right = context_to_lean(term[2], tail, placeholder)
    return f"({left} ◇ {right})"


def eval_term(term: Term, env: dict[str, Any]) -> int:
    if term[0] == "var":
        return env[term[1]]
    return env["op"](eval_term(term[1], env), eval_term(term[2], env))


def instantiate_term(term: Term, subst: dict[str, Term]) -> Term:
    if term[0] == "var":
        return subst[term[1]]
    return ("op", instantiate_term(term[1], subst), instantiate_term(term[2], subst))


def instantiate_term_if_bound(term: Term, subst: dict[str, Term]) -> Term | None:
    if term[0] == "var":
        return subst.get(term[1])
    left = instantiate_term_if_bound(term[1], subst)
    if left is None:
        return None
    right = instantiate_term_if_bound(term[2], subst)
    if right is None:
        return None
    return ("op", left, right)


def match_term(pattern: Term, target: Term, subst: dict[str, Term]) -> bool:
    if pattern[0] == "var":
        name = pattern[1]
        bound = subst.get(name)
        if bound is None:
            subst[name] = target
            return True
        return bound == target
    if target[0] != "op":
        return False
    return match_term(pattern[1], target[1], subst) and match_term(pattern[2], target[2], subst)


def equation_holds(equation: dict[str, Any], table: list[list[int]]) -> bool:
    n = len(table)

    def op(a: int, b: int) -> int:
        return table[a][b]

    for values in product(range(n), repeat=len(equation["variables"])):
        env: dict[str, Any] = {"op": op}
        env.update(zip(equation["variables"], values))
        if eval_term(equation["lhs"], env) != eval_term(equation["rhs"], env):
            return False
    return True


def table_is_renderable(table: list[list[int]]) -> bool:
    """Can the judge actually read this table back?

    `MemoFinOp.finOpTable` parses the table string with `extractDigits`, which
    keeps one value per *digit character*. A cell holding `10` is therefore read
    as two cells, `1` and `0`, silently shifting everything after it. So only
    single-digit entries survive the round trip, which caps witness order at 10.

    This is checked here, at the gate every FALSE witness passes through, because
    every other local check reads the Python table and is blind to it: a `Fin 13`
    witness for `hard2_0051` passed both offline oracles and was still
    `LEAN_REJECTED`, with `decide` calling the conjunction false (2026-07-29).
    """
    if len(table) > MAX_WITNESS_ORDER:
        return False
    return all(0 <= value <= 9 for row in table for value in row)


def table_is_counterexample(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    table: list[list[int]],
) -> bool:
    if not table_is_renderable(table):
        return False
    return equation_holds(eq1, table) and not equation_holds(eq2, table)


# How many models of the *hypothesis* the FALSE search has inspected for the
# current problem. A failed witness search means "no counterexample among the
# models we looked at", which is evidence the row is TRUE only if we looked at
# some. On `eq1 = Eq168` the enumerated orders (<= 3) and every canned family
# contain zero models, so the search is vacuous and reports the same "None" it
# would after examining ten thousand models. Anything that reads a failed
# search as a TRUE signal has to consult this first.
_HYPOTHESIS_MODELS_SEEN = 0


def reset_hypothesis_model_count() -> None:
    global _HYPOTHESIS_MODELS_SEEN
    _HYPOTHESIS_MODELS_SEEN = 0


def hypothesis_models_seen() -> int:
    return _HYPOTHESIS_MODELS_SEEN


def note_hypothesis_model() -> None:
    global _HYPOTHESIS_MODELS_SEEN
    _HYPOTHESIS_MODELS_SEEN += 1


def witness_check(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    table: list[list[int]],
) -> bool:
    """`table_is_counterexample` plus the model bookkeeping above.

    Same short-circuit as the plain check -- a table that fails `eq1` never
    costs an `eq2` evaluation -- so the counter is free.
    """
    if not equation_holds(eq1, table):
        return False
    note_hypothesis_model()
    return not equation_holds(eq2, table)


def enumerate_tables(n: int):
    total = n ** (n * n)
    for encoding in range(total):
        yield [[(encoding // (n ** (row * n + col))) % n for col in range(n)] for row in range(n)]


def table_key(table: list[list[int]]) -> str:
    return json.dumps(table, separators=(",", ":"))


def transpose_table(table: list[list[int]]) -> list[list[int]]:
    n = len(table)
    return [[table[y][x] for y in range(n)] for x in range(n)]


def structured_family_tables(max_n: int = STRUCTURED_MAX_N):
    seen: set[str] = set()

    def emit(route: str, table: list[list[int]]):
        if not table or len(table) > max_n:
            return None
        key = table_key(table)
        if key in seen:
            return None
        seen.add(key)
        return route, table

    for n in range(2, max_n + 1):
        candidates: list[tuple[str, list[list[int]]]] = [
            (f"false:semilattice:min:z{n}", [[min(x, y) for y in range(n)] for x in range(n)]),
            (f"false:semilattice:max:z{n}", [[max(x, y) for y in range(n)] for x in range(n)]),
            (f"false:spine:leftsucc:z{n}", [[(x + 1) % n for _y in range(n)] for x in range(n)]),
            (f"false:spine:rightsucc:z{n}", [[(y + 1) % n for y in range(n)] for _x in range(n)]),
            (f"false:spine:ifleft0:z{n}", [[y if x == 0 else x for y in range(n)] for x in range(n)]),
            (f"false:spine:ifright0:z{n}", [[x if y == 0 else y for y in range(n)] for x in range(n)]),
            (f"false:central:neg_sum:z{n}", [[(-x - y) % n for y in range(n)] for x in range(n)]),
            (f"false:central:one_neg_sum:z{n}", [[(1 - x - y) % n for y in range(n)] for x in range(n)]),
        ]
        for route, table in candidates:
            item = emit(route, table)
            if item is not None:
                yield item

    for rows in range(2, max_n + 1):
        for cols in range(2, max_n + 1):
            n = rows * cols
            if n > max_n:
                continue

            def idx(row: int, col: int) -> int:
                return row * cols + col

            table = []
            for a in range(n):
                ar, _ac = divmod(a, cols)
                row = []
                for b in range(n):
                    _br, bc = divmod(b, cols)
                    row.append(idx(ar, bc))
                table.append(row)
            item = emit(f"false:rectband:{rows}x{cols}", table)
            if item is not None:
                yield item


def affine_family_tables(max_n: int = 5):
    seen: set[str] = set()
    for n in AFFINE_LINEAR_SIZES:
        if n > max_n:
            continue
        for a in range(n):
            for b in range(n):
                for c in range(n):
                    table = [[(a * x + b * y + c) % n for y in range(n)] for x in range(n)]
                    key = json.dumps(table, separators=(",", ":"))
                    if key in seen:
                        continue
                    seen.add(key)
                    if c == 0:
                        route = f"false:linear:z{n}:{a},{b}"
                    else:
                        route = f"false:affine:z{n}:{a},{b},{c}"
                    yield route, table


def quadratic_family_tables(max_n: int = STRUCTURED_MAX_N):
    seen: set[str] = set()
    for n in AFFINE_QUADRATIC_SIZES:
        if n > max_n:
            continue
        coeffs = tuple(range(n)) if n <= 3 else tuple(dict.fromkeys((0, 1, 2 % n, n - 1)))
        nonzero = tuple(c for c in coeffs if c % n != 0) or (1,)

        for a in coeffs:
            for b in coeffs:
                for c in nonzero:
                    for d in coeffs:
                        table = [[(a * x + b * y + c * x * y + d) % n for y in range(n)] for x in range(n)]
                        key = table_key(table)
                        if key in seen:
                            continue
                        seen.add(key)
                        yield f"false:quadratic_xy:z{n}:{a},{b},{c},{d}", table

        for a in coeffs:
            for b in coeffs:
                for c in nonzero:
                    table_x = [[(a * x + b * y + c * x * x) % n for y in range(n)] for x in range(n)]
                    key_x = table_key(table_x)
                    if key_x not in seen:
                        seen.add(key_x)
                        yield f"false:quadratic_x2:z{n}:{a},{b},{c}", table_x
                    table_y = [[(a * x + b * y + c * y * y) % n for y in range(n)] for x in range(n)]
                    key_y = table_key(table_y)
                    if key_y not in seen:
                        seen.add(key_y)
                        yield f"false:quadratic_y2:z{n}:{a},{b},{c}", table_y


def singleton_route(eq1: dict[str, Any]) -> tuple[str, bool] | None:
    lhs = eq1["lhs"]
    rhs = eq1["rhs"]
    if lhs[0] == "var" and lhs[1] not in term_vars(rhs):
        return str(lhs[1]), True
    if rhs[0] == "var" and rhs[1] not in term_vars(lhs):
        return str(rhs[1]), False
    return None


def nested_square_singleton_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1][0] != "var" or op_side[2][0] != "op":
            continue
        lead = str(op_side[1][1])
        tail = op_side[2]
        if tail[1][0] != "op" or tail[2][0] != "var":
            continue
        extra = str(tail[2][1])
        middle = tail[1]
        if middle[1] != ("var", lead) or middle[2][0] != "op":
            continue
        square = middle[2]
        if square[1] != ("var", root) or square[2] != ("var", root):
            continue
        if len({root, lead, extra}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def singleton_from_1111_block(source_name: str) -> str:
    return (
        "  have hall : ∀ x y : G, x = y := by\n"
        "    intro x y\n"
        "    let v0 := M y y\n"
        "    let v1 := M y v0\n"
        f"    have h2 := {source_name} y y v1\n"
        "    have h3 := R x\n"
        "    let v4 := M x v0\n"
        f"    have h5 := {source_name} y x v4\n"
        "    have h6 := S h5\n"
        "    let v7 := M v4 x\n"
        "    let v8 := M (M x (M v7 v7)) x\n"
        "    let v9 := M x x\n"
        "    let v10 := M y v9\n"
        f"    have h11 := {source_name} x y v10\n"
        "    let v12 := M x v9\n"
        f"    have h13 := {source_name} x x v12\n"
        "    have h14 := S h13\n"
        "    let v15 := M v12 x\n"
        "    let v16 := M (M x (M v15 v15)) x\n"
        f"    exact T (T (T ({source_name} x x v8) (C h3 (T (T (T (C (T (T (T ({source_name} v12 x v16) (C h3 (T (T (T (C h14 (R v16)) (S ({source_name} v15 x x))) (C (C h3 (C h13 h13)) h3)) (C (T (T (C h3 (C h14 h14)) ({source_name} v12 x x)) (C h3 (C (T h14 h11) h11))) h3)))) (S ({source_name} (M y (M v10 v10)) x x))) (S h11)) (R v8)) (S ({source_name} v7 x x))) (C (C h3 (C h5 h5)) h3)) (C (T (T (C h3 (C h6 h6)) ({source_name} v4 x y)) (C h3 (C (T h6 h2) h2))) h3)))) (S ({source_name} (M y (M v1 v1)) x x))) (S h2)\n"
    )


def tail_square_singleton_source(eq1: dict[str, Any]) -> tuple[str, str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1][0] != "var" or op_side[2][0] != "op":
            continue
        lead = str(op_side[1][1])
        tail = op_side[2]
        if tail[1][0] != "op" or tail[2][0] != "var":
            continue
        extra_tail = str(tail[2][1])
        middle = tail[1]
        if middle[1][0] != "op" or middle[2][0] != "var":
            continue
        extra = str(middle[2][1])
        square = middle[1]
        if square[1] != ("var", root) or square[2] != ("var", root):
            continue
        if len({root, lead, extra}) != 3 or extra_tail in {root, lead}:
            continue
        if set(eq1["variables"]) != {root, lead, extra, extra_tail}:
            continue
        return root, lead, extra, extra_tail, swapped
    return None


def singleton_from_1283_block(source_name: str) -> str:
    return (
        "  have hall : ∀ x y : G, x = y := by\n"
        "    intro x y\n"
        "    let v0 := M x x\n"
        "    let v1 := M (M v0 x) x\n"
        "    let v2 := M v1 v1\n"
        "    let v3 := M v2 y\n"
        "    let v4 := M (M v3 v3) x\n"
        "    let v5 := M (M (M y y) y) y\n"
        "    have h6 := R x\n"
        f"    have h7 := {source_name} x v1 x\n"
        "    have h8 := S h7\n"
        "    have h9 := R v2\n"
        "    let v10 := M (M v0 y) y\n"
        f"    have h11 := {source_name} x v10 y\n"
        "    have h12 := S h11\n"
        "    have h13 := T (C (T (C (C (T h12 h7) h12) h6) (C (C h9 h7) h6)) h6) (C (C (C h8 h8) h6) h6)\n"
        "    let v14 := M v10 v10\n"
        f"    have h15 := {source_name} v14 x x\n"
        "    have h16 := R v4\n"
        "    have h17 := R y\n"
        "    have h18 := S h15\n"
        "    have h19 := T (C (C (C h7 h7) h6) h6) (C (T (C (C h9 h8) h6) (C (C (T h8 h11) h11) h6)) h6)\n"
        f"    exact T (T (T ({source_name} x y x) (C h17 (T ({source_name} v1 v4 v1) (C h16 (T (T (C (T (T (C h8 h19) h18) h12) h19) h18) h12))))) (C h17 (T (C h16 (T (T h11 h15) (C (T (T h11 ({source_name} v14 y x)) (C ({source_name} y v5 y) h13)) h13))) (S ({source_name} v5 v4 v1))))) (S ({source_name} y y y))\n"
    )


def paired_tail_singleton_source(eq1: dict[str, Any]) -> tuple[str, str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1][0] != "op" or op_side[2][0] != "op":
            continue
        left = op_side[1]
        right = op_side[2]
        if left[1][0] != "var" or left[2][0] != "op":
            continue
        lead = str(left[1][1])
        left_tail = left[2]
        if left_tail[1] != ("var", root) or left_tail[2][0] != "var":
            continue
        extra = str(left_tail[2][1])
        if right[1] != ("var", root) or right[2][0] != "var":
            continue
        extra_tail = str(right[2][1])
        if len({root, lead, extra, extra_tail}) != 4:
            continue
        if set(eq1["variables"]) != {root, lead, extra, extra_tail}:
            continue
        return root, lead, extra, extra_tail, swapped
    return None


def singleton_from_1906_block(source_name: str) -> str:
    return (
        "  have hall : ∀ x y : G, x = y := by\n"
        "    intro x y\n"
        "    let v0 := M y y\n"
        f"    have h1 := {source_name} y (M x v0) y\n"
        "    have h2 := S h1\n"
        "    have h3 := R v0\n"
        f"    have h4 := {source_name} y x y\n"
        "    have h5 := C h4 h3\n"
        f"    have h6 := S ({source_name} (M y v0) y x)\n"
        "    have h7 := R x\n"
        "    let v8 := M y x\n"
        f"    have h9 := {source_name} y (M x v8) x\n"
        "    have h10 := R v8\n"
        f"    have h11 := {source_name} y x x\n"
        f"    have h12 := {source_name} v8 y y\n"
        "    have h13 := T (T (S h12) (C (T h9 (C (S h11) h10)) h7)) (C (T (T (T (C h11 h10) (S h9)) h1) (C (S h4) h3)) h7)\n"
        "    have h14 := R y\n"
        "    have h15 := C (C h14 h13) h13\n"
        "    let v16 := M v8 y\n"
        f"    have h17 := {source_name} (M y v16) y v16\n"
        "    let v18 := M x x\n"
        "    have h19 := R v18\n"
        f"    have h20 := {source_name} x x x\n"
        f"    have h21 := {source_name} x (M x v18) x\n"
        "    have h22 := T h21 (C (S h20) h19)\n"
        "    let v23 := M x y\n"
        f"    have h24 := {source_name} x (M x v23) y\n"
        "    have h25 := R v23\n"
        f"    have h26 := {source_name} x x y\n"
        "    have h27 := S h21\n"
        "    have h28 := C h20 h19\n"
        "    let v29 := M v18 x\n"
        f"    have h30 := {source_name} v18 y x\n"
        f"    exact T (T (T (T (T (T (T (T (T (T h21 (C (T (C (T h28 h27) h19) (C h7 h30)) h30)) (S ({source_name} (M y v29) x v29))) (C h14 (T (C (T (T (C h22 h7) (C (T (T (T h28 h27) h24) (C (S h26) h25)) h7)) (C (T (C h26 h25) (S h24)) h22)) h22) (S ({source_name} x x v18))))) h12) (C (T (T (T (T h17 h15) h6) h5) h2) (R v16))) h17) h15) h6) h5) h2\n"
    )


def wrapped_tail_singleton_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1][0] != "var" or op_side[2][0] != "op":
            continue
        lead = str(op_side[1][1])
        tail = op_side[2]
        if tail[1][0] != "op" or tail[2][0] != "var":
            continue
        extra = str(tail[2][1])
        inner = tail[1]
        if inner[1] != ("var", extra) or inner[2] != ("var", root):
            continue
        if len({root, lead, extra}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def singleton_from_1773_block(source_name: str) -> str:
    return (
        "  have hall : ∀ x y : G, x = y := by\n"
        "    intro x y\n"
        f"    have h0 := S ({source_name} y x y)\n"
        "    have h1 := R x\n"
        "    let v2 := M x y\n"
        "    have h3 := R v2\n"
        f"    have h4 := {source_name} x x y\n"
        "    let v5 := M x x\n"
        "    let v6 := M v5 x\n"
        "    let v7 := M v2 x\n"
        f"    exact T (T h4 (C h3 (C (T (T ({source_name} v5 y y) (C (R (M y y)) (C (T (T ({source_name} (M y v5) x y) (C h3 (C (T (T (T (C ({source_name} x x x) (C ({source_name} y x x) (R v5))) (S ({source_name} v7 v5 v6))) ({source_name} v7 v2 v6)) (C (S h4) (C h0 h3))) h1))) (S ({source_name} (M y v2) x y))) (R y)))) (S ({source_name} v2 y y))) h1))) h0\n"
    )


def nested_square_singleton_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = nested_square_singleton_source(eq1)
    if source is None:
        return None
    root, lead, extra, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have h1111 : ∀ x y z : G, x = y ◇ ((y ◇ (x ◇ x)) ◇ z) := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{singleton_from_1111_block('h1111')}"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:nested_square_singleton", code


def tail_square_singleton_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = tail_square_singleton_source(eq1)
    if source is None:
        return None
    root, lead, extra, extra_tail, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z", extra_tail: "z"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have h1283 : ∀ x y z : G, x = y ◇ (((x ◇ x) ◇ z) ◇ z) := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{singleton_from_1283_block('h1283')}"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:tail_square_singleton", code


def paired_tail_singleton_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = paired_tail_singleton_source(eq1)
    if source is None:
        return None
    root, lead, extra, extra_tail, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z", extra_tail: "z"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have h1906 : ∀ x y z : G, x = (y ◇ (x ◇ z)) ◇ (x ◇ z) := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{singleton_from_1906_block('h1906')}"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:paired_tail_singleton", code


def wrapped_tail_singleton_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = wrapped_tail_singleton_source(eq1)
    if source is None:
        return None
    root, lead, extra, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "(y ◇ z)", extra: "y"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have h1773 : ∀ x y z : G, x = (y ◇ z) ◇ ((y ◇ x) ◇ y) := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{singleton_from_1773_block('h1773')}"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:wrapped_tail_singleton", code


def deep_repeat_singleton_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1][0] != "var" or op_side[2][0] != "op" or op_side[2][1][0] != "var":
            continue
        lead = str(op_side[1][1])
        repeat = str(op_side[2][1][1])
        root_term = ("var", root)
        repeat_term = ("var", repeat)
        expected = (
            "op",
            ("var", lead),
            ("op", repeat_term, ("op", root_term, ("op", root_term, repeat_term))),
        )
        if op_side != expected or len({root, lead, repeat}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, repeat}:
            continue
        return root, lead, repeat, swapped
    return None


def singleton_from_deep_repeat_block(source_name: str) -> str:
    return (
        "  have hall : ∀ x y : G, x = y := by\n"
        "    intro x y\n"
        "    let v0 := M x (M y (M y x))\n"
        "    let v1 := M x (M v0 (M v0 x))\n"
        "    have h2 := R v1\n"
        f"    exact T (T (T ({source_name} x v1 v1) (C h2 (C h2 (T (C (R x) (S ({source_name} v0 x x))) (S ({source_name} y x x)))))) (C h2 (C h2 (T ({source_name} y y x) (C (R y) ({source_name} v0 y x)))))) (S ({source_name} y v1 v1))\n"
    )


def deep_repeat_singleton_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = deep_repeat_singleton_source(eq1)
    if source is None:
        return None
    root, lead, repeat, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", repeat: "z"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have hsource : ∀ x y z : G, x = y ◇ (z ◇ (x ◇ (x ◇ z))) := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{singleton_from_deep_repeat_block('hsource')}"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:deep_repeat_singleton", code


def sandwich_repeat_singleton_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op" or op_side[1][0] != "var":
            continue
        root = str(variable_side[1])
        lead = str(op_side[1][1])
        tail = op_side[2]
        if tail[0] != "op" or tail[1][0] != "op" or tail[2] != ("var", lead):
            continue
        inner = tail[1]
        if inner[1] != ("var", lead) or inner[2][0] != "op":
            continue
        root_tail = inner[2]
        if root_tail[1] != ("var", root) or root_tail[2][0] != "var":
            continue
        extra = str(root_tail[2][1])
        if len({root, lead, extra}) != 3 or set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def singleton_from_sandwich_repeat_block(source_name: str) -> str:
    return (
        "  have hall : ∀ x y : G, x = y := by\n"
        "    intro x y\n"
        "    let v0 := M x x\n"
        "    have h1 := R x\n"
        f"    exact T (T ({source_name} x x x) (C h1 (C (C h1 ({source_name} v0 y x)) h1))) (S ({source_name} y x (M (M y (M v0 x)) y)))\n"
    )


def sandwich_repeat_singleton_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = sandwich_repeat_singleton_source(eq1)
    if source is None:
        return None
    root, lead, extra, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have hsource : ∀ x y z : G, x = y ◇ ((y ◇ (x ◇ z)) ◇ y) := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{singleton_from_sandwich_repeat_block('hsource')}"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:sandwich_repeat_singleton", code


def repeated_prefix_product_constancy_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op" or op_side[2][0] != "var":
            continue
        root = str(variable_side[1])
        tail = str(op_side[2][1])
        prefix = op_side[1]
        if prefix[0] != "op" or prefix[1][0] != "var" or prefix[2][0] != "op":
            continue
        repeat = str(prefix[1][1])
        root_term = ("var", root)
        repeat_term = ("var", repeat)
        expected = (
            "op",
            ("op", repeat_term, ("op", repeat_term, ("op", root_term, root_term))),
            ("var", tail),
        )
        if op_side != expected or len({root, repeat, tail}) != 3:
            continue
        if set(eq1["variables"]) != {root, repeat, tail}:
            continue
        return root, repeat, tail, swapped
    return None


def repeated_prefix_product_constancy_route(
    eq1: dict[str, Any], eq2: dict[str, Any]
) -> tuple[str, str] | None:
    source = repeated_prefix_product_constancy_source(eq1)
    if source is None or eq2["lhs"][0] != "op" or eq2["rhs"][0] != "op":
        return None
    root, repeat, tail, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", repeat: "y", tail: "z"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hsource : ∀ x y z : G, x = (y ◇ (y ◇ (x ◇ x))) ◇ z := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        "  have hconst : ∀ a b c d : G, a ◇ b = c ◇ d := by\n"
        "    intro a\n"
        "    repeat intro\n"
        "    try { rw [hsource a, ← hsource] }\n"
        "    try { rw [hsource a a, ← hsource] }\n"
        f"{intro_line}"
        "  exact hconst _ _ _ _\n"
    )
    return "true:repeated_prefix_product_constancy", code


def reverse_deep_repeat_singleton_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op" or op_side[2][0] != "var":
            continue
        root = str(variable_side[1])
        tail = str(op_side[2][1])
        prefix = op_side[1]
        if prefix[0] != "op" or prefix[2][0] != "var" or prefix[1][0] != "op":
            continue
        repeat = str(prefix[2][1])
        root_term = ("var", root)
        repeat_term = ("var", repeat)
        expected = (
            "op",
            ("op", ("op", ("op", repeat_term, root_term), root_term), repeat_term),
            ("var", tail),
        )
        if op_side != expected or len({root, repeat, tail}) != 3:
            continue
        if set(eq1["variables"]) != {root, repeat, tail}:
            continue
        return root, repeat, tail, swapped
    return None


def singleton_from_reverse_deep_repeat_block(source_name: str) -> str:
    return (
        "  have hall : ∀ x y : G, x = y := by\n"
        "    intro x y\n"
        "    let v0 := M (M (M x x) x) x\n"
        "    let v1 := M (M (M x v0) v0) x\n"
        "    have h2 := R v1\n"
        f"    exact T (T (T ({source_name} x v1 v1) (C (C (T (C (S ({source_name} v0 x x)) (R x)) (S ({source_name} x x x))) h2) h2)) (C (C (T ({source_name} x x y) (C ({source_name} v0 x y) (R y))) h2) h2)) (S ({source_name} y v1 v1))\n"
    )


def reverse_deep_repeat_singleton_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = reverse_deep_repeat_singleton_source(eq1)
    if source is None:
        return None
    root, repeat, tail, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", repeat: "y", tail: "z"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have hsource : ∀ x y z : G, x = (((y ◇ x) ◇ x) ◇ y) ◇ z := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{singleton_from_reverse_deep_repeat_block('hsource')}"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:reverse_deep_repeat_singleton", code


def outer_sandwich_singleton_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op" or op_side[2][0] != "var":
            continue
        root = str(variable_side[1])
        surround = str(op_side[2][1])
        prefix = op_side[1]
        if prefix[0] != "op" or prefix[1] != ("var", surround) or prefix[2][0] != "op":
            continue
        inner = prefix[2]
        if inner[1][0] != "op" or inner[2] != ("var", surround):
            continue
        pair = inner[1]
        if pair[1][0] != "var" or pair[2] != ("var", root):
            continue
        extra = str(pair[1][1])
        expected = (
            "op",
            (
                "op",
                ("var", surround),
                ("op", ("op", ("var", extra), ("var", root)), ("var", surround)),
            ),
            ("var", surround),
        )
        if op_side != expected or len({root, surround, extra}) != 3:
            continue
        if set(eq1["variables"]) != {root, surround, extra}:
            continue
        return root, surround, extra, swapped
    return None


def singleton_from_outer_sandwich_block(source_name: str) -> str:
    return (
        "  have hall : ∀ x y : G, x = y := by\n"
        "    intro x y\n"
        "    let v0 := M x x\n"
        "    have h1 := R x\n"
        f"    exact T (T ({source_name} x x x) (C (C h1 (C ({source_name} v0 y x) h1)) h1)) (S ({source_name} y x (M y (M (M x v0) y))))\n"
    )


def outer_sandwich_singleton_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = outer_sandwich_singleton_source(eq1)
    if source is None:
        return None
    root, surround, extra, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", surround: "y", extra: "z"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have hsource : ∀ x y z : G, x = (y ◇ ((z ◇ x) ◇ y)) ◇ y := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{singleton_from_outer_sandwich_block('hsource')}"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:outer_sandwich_singleton", code


def forked_square_singleton_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var":
            continue
        root = str(variable_side[1])
        if op_side[0] != "op" or op_side[1][0] != "var":
            continue
        lead = str(op_side[1][1])
        root_term = ("var", root)
        tail = op_side[2]
        if tail[0] != "op" or tail[1] != ("op", root_term, root_term):
            continue
        fork = tail[2]
        if fork[0] != "op" or fork[1] != root_term or fork[2][0] != "var":
            continue
        extra = str(fork[2][1])
        if len({root, lead, extra}) != 3 or set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def singleton_from_forked_square_block() -> str:
    return (
        "  have hall : ∀ x y : G, x = y := by\n"
        "    intro x y\n"
        "    let v0 := M x y\n"
        "    let v1 := M x x\n"
        "    let v2 := M v1 v0\n"
        "    let v3 := M y y\n"
        "    have h4 := R v3\n"
        "    let v5 := M v1 v1\n"
        "    have h6 := hsource x v5 x\n"
        "    have h7 := S h6\n"
        "    let v8 := M v3 v3\n"
        "    have h9 := hsource x v5 (M v3 (M y x))\n"
        "    have h10 := S h9\n"
        "    have h11 := hsource y x x\n"
        "    have h12 := R v1\n"
        "    have h13 := R v5\n"
        "    have h14 := C h13 (C h12 h11)\n"
        "    have h15 := R y\n"
        "    have h16 := C h13 (C h12 (S h11))\n"
        "    have h17 := hsource x v5 v5\n"
        "    have h18 := S h17\n"
        "    have h19 := hsource x x x\n"
        "    have h20 := C h13 (C h12 h19)\n"
        "    have h21 := R x\n"
        "    have h22 := hsource v1 y x\n"
        "    have h23 := S h22\n"
        "    have h24 := C h12 (S h19)\n"
        "    have h25 := C h13 h24\n"
        "    have h26 := T h17 h25\n"
        "    have h27 := C h15 h26\n"
        "    have h28 := T h27 h23\n"
        "    have h29 := hsource x v2 y\n"
        "    have h30 := S h29\n"
        "    have h31 := C h30 h21\n"
        "    have h32 := R (M v2 v2)\n"
        "    have h33 := C h32 h30\n"
        "    have h34 := C (T h7 h29) h29\n"
        "    have h35 := R (M v5 v5)\n"
        "    have h36 := C h35 h7\n"
        "    have h37 := C (T (T h20 h18) h6) h6\n"
        "    have h38 := T h20 h18\n"
        "    have h39 := R (M v5 (M v1 x))\n"
        "    have h40 := C h39 h38\n"
        "    have h41 := T (T h7 h17) h25\n"
        "    have h42 := C h41 h7\n"
        "    have h43 := C h35 h6\n"
        "    have h44 := T h30 h6\n"
        "    have h45 := C h44 h30\n"
        "    have h46 := C h32 h29\n"
        "    have h47 := C h29 h21\n"
        "    have h48 := C h39 h26\n"
        "    have h49 := T (T (T (C (T (T (T (T (T (T (T h27 h23) h47) h46) h45) h43) h42) h48) (T (T (T (T (T (T h27 h23) h47) h46) h45) h43) h42)) (C (T h40 h37) (T h37 h36))) (C (T h36 h34) (T h34 h33))) (C (T h33 h31) h31)\n"
        "    have h50 := C h15 h38\n"
        "    have h51 := T h22 h50\n"
        "    have h52 := C h51 h21\n"
        "    have h53 := T (T (T (C (T h47 h46) h47) (C (T h45 h43) (T h46 h45))) (C (T h42 h48) (T h43 h42))) (C (T (T (T (T (T (T (T h40 h37) h36) h34) h33) h31) h22) h50) (T (T (T (T (T (T h37 h36) h34) h33) h31) h22) h50))\n"
        "    exact T (T (hsource x v1 v5) (C h12 (T (T (T (T (T (T h24 h52) (C h28 h6)) (S (hsource v1 v1 v1))) (hsource v1 v0 v1)) (C (T (T (T (T (T (T (T (C h29 h15) (C h44 h15)) (C h41 h15)) (C (T (T (T (T h20 h18) h9) h16) (C h53 (C h51 h15))) h15)) (C (T (T (T (T (T (C h49 (C h28 h15)) h14) h10) h17) h25) (C h53 h52)) h15)) (C (T (T (T (T (C h49 (C h28 h21)) h20) h18) h9) h16) h15)) (C (T h14 h10) (T (hsource y v8 v5) (C (R v8) (C h4 (S (hsource x y x))))))) (S (hsource v3 x x))) h7)) (C h4 (hsource x y y))))) (S (hsource y v1 v2))\n"
    )


def forked_square_singleton_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = forked_square_singleton_source(eq1)
    if source is None:
        return None
    root, lead, extra, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z"})
    if swapped:
        call = f"S ({call})"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have hsource : ∀ x y z : G, x = y ◇ ((x ◇ x) ◇ (x ◇ z)) := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{singleton_from_forked_square_block()}"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:forked_square_singleton", code


def crossed_pair_singleton_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var":
            continue
        root = str(variable_side[1])
        if op_side[0] != "op" or op_side[1][0] != "op" or op_side[2][0] != "op":
            continue
        left_pair = op_side[1]
        right_pair = op_side[2]
        if left_pair[1][0] != "var" or left_pair[2] != ("var", root):
            continue
        lead = str(left_pair[1][1])
        if right_pair[1] != ("op", ("var", root), ("var", lead)) or right_pair[2][0] != "var":
            continue
        extra = str(right_pair[2][1])
        if len({root, lead, extra}) != 3 or set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def singleton_from_crossed_pair_block() -> str:
    return (
        "  have hall : ∀ x y : G, x = y := by\n"
        "    intro x y\n"
        "    let v0 := M x y\n"
        "    let v1 := M y x\n"
        "    have h2 := R y\n"
        "    let v3 := M x x\n"
        "    have h4 := hsource x x (M v3 x)\n"
        "    have h5 := hsource x x x\n"
        "    have h6 := R v3\n"
        "    have h7 := T (C h6 h5) (S h4)\n"
        "    have h8 := hsource y x (M v0 x)\n"
        "    have h9 := hsource x y x\n"
        "    have h10 := R v0\n"
        "    have h11 := T (C h10 h9) (S h8)\n"
        "    have h12 := T h4 (C h6 (S h5))\n"
        "    have h13 := T h8 (C h10 (S h9))\n"
        "    have h14 := hsource x y (M v1 x)\n"
        "    have h15 := hsource y x x\n"
        "    have h16 := R v1\n"
        "    have h17 := T (C h16 h15) (S h14)\n"
        "    have h18 := R (M y v1)\n"
        "    have h19 := T h14 (C h16 (S h15))\n"
        "    have h20 := C h2 h7\n"
        "    have h21 := C h11 h12\n"
        "    have h22 := C h13 h17\n"
        "    let v23 := M y y\n"
        "    have h24 := hsource y y (M v23 x)\n"
        "    have h25 := S h24\n"
        "    have h26 := hsource y y x\n"
        "    have h27 := R v23\n"
        "    have h28 := C h27 h26\n"
        "    have h29 := T h28 h25\n"
        "    have h30 := C h29 h19\n"
        "    have h31 := R x\n"
        "    have h32 := C h27 (S h26)\n"
        "    have h33 := hsource y v23 v23\n"
        "    have h34 := S h33\n"
        "    have h35 := hsource v23 y x\n"
        "    have h36 := T h24 h32\n"
        "    have h37 := C h13 h7\n"
        "    have h38 := C h2 h12\n"
        "    have h39 := R (M y v23)\n"
        "    have h40 := C h29 (T (C h39 (T (T (T h38 h37) (C h11 h19)) (C h36 h17))) (S h35))\n"
        "    have h41 := hsource y v23 v1\n"
        "    have h42 := C h36 (T (T (T (T h28 h25) h41) h40) (C (T h41 h40) h27))\n"
        "    have h43 := hsource y v1 v3\n"
        "    have h44 := hsource v1 y x\n"
        "    have h45 := T (C h19 (T h44 (C h18 (T (T (T (C h17 h19) (C h12 h17)) (C h7 h12)) (C h31 h7))))) (S h43)\n"
        "    have h46 := C h45 h36\n"
        "    have h47 := C h12 h7\n"
        "    have h48 := C h31 h12\n"
        "    have h49 := C h17 (T (C h18 (T (T (T h48 h47) (C h7 h19)) (C h19 h17))) (S h44))\n"
        "    have h50 := S h41\n"
        "    have h51 := C h36 (T h35 (C h39 (T (T (T h30 h22) h21) h20)))\n"
        "    have h52 := S (hsource v3 x x)\n"
        "    have h53 := T h48 h47\n"
        "    have h54 := C h7 (T (C (R (M x v3)) h53) h52)\n"
        "    have h55 := hsource x v3 v3\n"
        "    exact T (T (T (T (T (T h55 h54) (C (T h55 h54) h53)) h52) (C h31 (T (hsource x v0 v1) (C h11 (T (C (R (M x v0)) (T h38 h37)) (S (hsource v0 x x))))))) (C h19 (T (C (T (T (T h43 h49) (hsource (M x v1) y x)) (C (T (T (T (T (C (T (T h33 (C h29 (T (T (T (T (C (T h51 h50) h27) h51) h50) h24) h32))) (C (T h43 h49) h29)) h45) (C (T (T (T (T h46 h42) h34) h43) h49) h2)) h46) h42) h34) (T (T (T (T (C (T (T (T (T h46 h42) h34) h24) h32) h31) h30) h22) h21) h20))) (T (T (C h12 h2) (C h7 h13)) (C h19 h11))) (C h18 (T (T (C h17 h13) (C h12 h11)) (C h7 h2)))))) (S (hsource y v1 v0))\n"
    )


def crossed_pair_singleton_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = crossed_pair_singleton_source(eq1)
    if source is None:
        return None
    root, lead, extra, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z"})
    if swapped:
        call = f"S ({call})"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have hsource : ∀ x y z : G, x = (y ◇ x) ◇ ((x ◇ y) ◇ z) := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{singleton_from_crossed_pair_block()}"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:crossed_pair_singleton", code


def double_tail_square_product_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, product_side, nested_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if product_side[0] != "op" or product_side[1][0] != "var" or product_side[2][0] != "var":
            continue
        left = str(product_side[1][1])
        right = str(product_side[2][1])
        if left == right or nested_side[0] != "op" or nested_side[2] != ("var", left):
            continue
        prefix = nested_side[1]
        if prefix[0] != "op" or prefix[2] != ("var", left) or prefix[1][0] != "op":
            continue
        inner = prefix[1]
        if inner[1][0] != "var" or inner[2] != ("var", right):
            continue
        extra = str(inner[1][1])
        if len({left, right, extra}) != 3 or set(eq1["variables"]) != {left, right, extra}:
            continue
        return left, right, extra, swapped
    return None


def square_product_basis_goal(eq2: dict[str, Any]) -> tuple[Term, Term, Term, bool] | None:
    for swapped, square_side, product_side in (
        (False, eq2["lhs"], eq2["rhs"]),
        (True, eq2["rhs"], eq2["lhs"]),
    ):
        if square_side[0] != "op" or square_side[1] != square_side[2]:
            continue
        if product_side[0] != "op":
            continue
        return square_side[1], product_side[1], product_side[2], swapped
    return None


def square_product_from_double_tail_block() -> str:
    return (
        "  have h41 : ∀ x y z : G, x ◇ x = y ◇ z := by\n"
        "    intro x y z\n"
        "    let v0 := M x x\n"
        "    have h1 := R y\n"
        "    have h2 := S (hsource (M v0 z) y x)\n"
        "    have h3 := hsource v0 z z\n"
        "    have h4 := R v0\n"
        "    let v5 := M y z\n"
        "    have h6 := hsource z z v5\n"
        "    have h7 := R z\n"
        "    have h8 := hsource z z y\n"
        "    have h9 := S h8\n"
        "    have h10 := hsource v5 z x\n"
        "    have h11 := R v5\n"
        "    have h12 := hsource x z x\n"
        "    have h13 := S h12\n"
        "    have h14 := R x\n"
        "    let v15 := M x z\n"
        "    have h16 := hsource x x v15\n"
        "    have h17 := C (T h16 (C h13 h14)) h14\n"
        "    have h18 := hsource x x x\n"
        "    have h19 := C (S h18) h14\n"
        "    have h20 := hsource x x v0\n"
        "    have h21 := hsource v5 x x\n"
        "    have h22 := hsource z x v5\n"
        "    have h23 := hsource v0 x z\n"
        "    have h24 := T (T (T (T h20 h19) h23) (C (C (T (T (T h22 (C (T (C (T (T h21 (C (C (T (T (T h20 h19) h17) h13) h11) h11)) (S h10)) h7) h9) h7)) (C h8 h7)) (S h6)) h4) h4)) (S h3)\n"
        "    have h25 := C (C (T (T (T (T (T (T h20 h19) h17) h13) (hsource x z y)) (C (C (hsource y z x) h14) h14)) (S (hsource x y (M v15 y)))) h24) h24\n"
        "    have h26 := hsource v0 x x\n"
        "    exact T (T (T (T (T (T (T (hsource x x (M v5 x)) (C (S (hsource x x v5)) h14)) h26) h25) h2) (C (T (T h3 (C (C (T (T (T h6 (C h9 h7)) (C (T h8 (C (T (T h10 (C (C (T (T (T h12 (C (T (C h12 h14) (S h16)) h14)) (C h18 h14)) (S h20)) h11) h11)) (S h21)) h7)) h7)) (S h22)) h4) h4)) (S h23)) h1)) (C (T (T h26 h25) h2) h1)) (S (hsource y z v0))\n"
    )


def double_tail_square_product_route(
    eq1: dict[str, Any], eq2: dict[str, Any]
) -> tuple[str, str] | None:
    source = double_tail_square_product_source(eq1)
    goal = square_product_basis_goal(eq2)
    if source is None or goal is None:
        return None
    left, right, extra, source_swapped = source
    square_arg, product_left, product_right, goal_swapped = goal
    call = call_expression_lean_args(eq1["variables"], {left: "x", right: "y", extra: "z"})
    if source_swapped:
        call = f"S ({call})"
    proof_expr = (
        f"h41 {term_to_lean(square_arg)} {term_to_lean(product_left)} {term_to_lean(product_right)}"
    )
    if goal_swapped:
        proof_expr = f"S ({proof_expr})"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have hsource : ∀ x y z : G, x ◇ y = ((z ◇ y) ◇ x) ◇ x := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{square_product_from_double_tail_block()}"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )
    return "true:double_tail_square_product", code


def middle_self_collapse_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op" or op_side[1][0] != "op" or op_side[2][0] != "var":
            continue
        root = str(variable_side[1])
        inner = op_side[1]
        tail = op_side[2]
        if inner[1][0] != "var" or inner[2] != ("var", root):
            continue
        lead = str(inner[1][1])
        tail_name = str(tail[1])
        if len({root, lead, tail_name}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, tail_name}:
            continue
        return root, lead, tail_name, swapped
    return None


def middle_self_collapse_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = middle_self_collapse_source(eq1)
    if source is None:
        return None
    root, lead, tail, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "a", lead: "b", tail: "c"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hc : ∀ a b c : G, a = (b ◇ a) ◇ c := by\n"
        "    intro a b c\n"
        f"    exact {call}\n"
        "  have hright : ∀ a b c : G, b = a ◇ c := by\n"
        "    intro a b c\n"
        "    have h1 : a = (b ◇ a) ◇ b := hc a b b\n"
        "    have h2 : b = ((b ◇ a) ◇ b) ◇ c := hc b (b ◇ a) c\n"
        "    exact h2.trans (congrArg (fun t => t ◇ c) h1.symm)\n"
        "  have hall : ∀ a b : G, a = b := by\n"
        "    intro a b\n"
        "    have hb : b = a := by\n"
        "      exact (hright a b a).trans (hright a a a).symm\n"
        "    exact hb.symm\n"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:middle_self_collapse", code


def front_double_self_collapse_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op" or op_side[1][0] != "var":
            continue
        root = str(variable_side[1])
        lead = str(op_side[1][1])
        middle = op_side[2]
        if middle[0] != "op" or middle[1] != ("var", root):
            continue
        tail = middle[2]
        if tail[0] != "op" or tail[1] != ("var", root) or tail[2][0] != "var":
            continue
        tail_name = str(tail[2][1])
        if len({root, lead, tail_name}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, tail_name}:
            continue
        return root, lead, tail_name, swapped
    return None


def front_double_self_collapse_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = front_double_self_collapse_source(eq1)
    if source is None:
        return None
    root, lead, tail, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "a", lead: "b", tail: "c"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hc : ∀ a b c : G, a = b ◇ (a ◇ (a ◇ c)) := by\n"
        "    intro a b c\n"
        f"    exact {call}\n"
        "  have hall : ∀ a b : G, a = b := by\n"
        "    have hrow : ∀ a b c : G, a ◇ b = a ◇ (a ◇ c) := by\n"
        "      intro a b c\n"
        "      have ha : a = (b ◇ (b ◇ c)) ◇ (a ◇ (a ◇ c)) := by\n"
        "        exact hc a (b ◇ (b ◇ c)) c\n"
        "      have ht : b ◇ (b ◇ c) = (a ◇ (a ◇ c)) ◇ ((b ◇ (b ◇ c)) ◇ a) := by\n"
        "        exact (hc (b ◇ (b ◇ c)) (a ◇ (a ◇ c)) (a ◇ (a ◇ c))).trans (congrArg (fun t => (a ◇ (a ◇ c)) ◇ ((b ◇ (b ◇ c)) ◇ t)) ha.symm)\n"
        "      have hb : b = (a ◇ (a ◇ c)) ◇ ((a ◇ (a ◇ c)) ◇ ((b ◇ (b ◇ c)) ◇ a)) := by\n"
        "        exact (hc b (a ◇ (a ◇ c)) c).trans (congrArg (fun t => (a ◇ (a ◇ c)) ◇ t) ht)\n"
        "      have hs : a ◇ (a ◇ c) = a ◇ b := by\n"
        "        exact (hc (a ◇ (a ◇ c)) a ((b ◇ (b ◇ c)) ◇ a)).trans (congrArg (fun t => a ◇ t) hb.symm)\n"
        "      exact hs.symm\n"
        "    intro a b\n"
        "    have ha : a = (b ◇ b) ◇ (a ◇ a) := by\n"
        "      exact (hc a (b ◇ b) b).trans (congrArg (fun t => (b ◇ b) ◇ t) (hrow a a b).symm)\n"
        "    have hb : b = (b ◇ b) ◇ (b ◇ b) := by\n"
        "      exact (hc b (b ◇ b) b).trans (congrArg (fun t => (b ◇ b) ◇ t) (hrow b b b).symm)\n"
        "    have hsame : (b ◇ b) ◇ (a ◇ a) = (b ◇ b) ◇ (b ◇ b) := by\n"
        "      exact (hrow (b ◇ b) (a ◇ a) b).trans (hrow (b ◇ b) (b ◇ b) b).symm\n"
        "    exact ha.trans (hsame.trans hb.symm)\n"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:front_double_self_collapse", code


def alternating_front_self_collapse_source(eq1: dict[str, Any]) -> tuple[str, str, str] | None:
    for variable_side, op_side in ((eq1["lhs"], eq1["rhs"]), (eq1["rhs"], eq1["lhs"])):
        if variable_side[0] != "var" or op_side[0] != "op" or op_side[1][0] != "var":
            continue
        root = str(variable_side[1])
        lead = str(op_side[1][1])
        middle = op_side[2]
        if middle[0] != "op" or middle[1] != ("var", root):
            continue
        tail = middle[2]
        if tail[0] != "op" or tail[1] != ("var", lead) or tail[2][0] != "var":
            continue
        tail_name = str(tail[2][1])
        if len({root, lead, tail_name}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, tail_name}:
            continue
        return root, lead, tail_name
    return None


def alternating_front_self_collapse_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = alternating_front_self_collapse_source(eq1)
    if source is None:
        return None
    root, lead, _tail = source
    singleton_goal = {
        "lhs": ("var", root),
        "rhs": ("var", lead),
        "variables": [root, lead],
        "lhs_text": root,
        "rhs_text": lead,
        "text": f"{root} = {lead}",
    }
    result = _closure_proof_expr_impl(
        eq1,
        singleton_goal,
        route_name="true:alternating_front_self_collapse:hall",
        chain_max_depth=EQUATIONAL_CLOSURE_CHAIN_MAX_DEPTH,
        pool_limit=EQUATIONAL_CLOSURE_POOL_LIMIT,
        frontier_limit=EQUATIONAL_CLOSURE_FRONTIER_LIMIT,
        max_fills=EQUATIONAL_CLOSURE_MAX_FILLS,
        term_slack=EQUATIONAL_CLOSURE_TERM_SLACK,
        depth_slack=EQUATIONAL_CLOSURE_DEPTH_SLACK,
        time_budget=0.08,
    )
    if result is None:
        return None
    _route, proof_expr = result
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"  have hall : ∀ {root} {lead} : G, {root} = {lead} := by\n"
        f"    intro {root} {lead}\n"
        f"    exact {proof_expr}\n"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:alternating_front_self_collapse", code


def mirrored_alternating_front_self_collapse_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op" or op_side[1][0] != "var":
            continue
        root = str(variable_side[1])
        lead = str(op_side[1][1])
        middle = op_side[2]
        if middle[0] != "op" or middle[1] != ("var", root):
            continue
        tail = middle[2]
        if tail[0] != "op" or tail[1][0] != "var" or tail[2] != ("var", lead):
            continue
        tail_name = str(tail[1][1])
        if len({root, lead, tail_name}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, tail_name}:
            continue
        return root, lead, tail_name, swapped
    return None


def mirrored_alternating_front_self_collapse_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = mirrored_alternating_front_self_collapse_source(eq1)
    if source is None:
        return None
    root, lead, tail, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "a", lead: "b", tail: "c"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hsrc : ∀ a b c : G, a = b ◇ (a ◇ (c ◇ b)) := by\n"
        "    intro a b c\n"
        f"    exact {call}\n"
        "  have hall : ∀ a b : G, a = b := by\n"
        "    intro a b\n"
        "    have hc : ∀ x y z : G, x = (y ◇ x) ◇ z := by\n"
        "      intro x y z\n"
        "      exact (hsrc x (y ◇ x) z).trans (congrArg (fun t => (y ◇ x) ◇ t) (hsrc z x y).symm)\n"
        "    have hright : ∀ x y z : G, y = x ◇ z := by\n"
        "      intro x y z\n"
        "      have h1 : x = (y ◇ x) ◇ y := hc x y y\n"
        "      have h2 : y = ((y ◇ x) ◇ y) ◇ z := hc y (y ◇ x) z\n"
        "      exact h2.trans (congrArg (fun t => t ◇ z) h1.symm)\n"
        "    exact ((hright a b a).trans (hright a a a).symm).symm\n"
        f"{intro_line}"
        "  exact hall _ _\n"
    )
    return "true:mirrored_alternating_front_self_collapse", code


def sandwich_left_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        root_term = ("var", root)
        if op_side[1] != root_term:
            continue
        tail = op_side[2]
        if tail[0] != "op" or tail[1][0] != "var":
            continue
        lead = str(tail[1][1])
        inner = tail[2]
        if inner[0] != "op" or inner[1][0] != "var" or inner[2] != ("var", lead):
            continue
        middle = str(inner[1][1])
        if len({root, lead, middle}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, middle}:
            continue
        return root, lead, middle, swapped
    return None


def projection_proof_expr_from_law(
    eq2: dict[str, Any],
    side: str,
    *,
    hypothesis_name: str,
) -> str | None:
    law = parse_equation("x = x ◇ y" if side == "left" else "x = y ◇ x")
    left = projection_term_proof(law, eq2["lhs"], side, hypothesis_name=hypothesis_name)
    right = projection_term_proof(law, eq2["rhs"], side, hypothesis_name=hypothesis_name)
    if left is None or right is None:
        return None
    left_proof, left_target = left
    right_proof, right_target = right
    if left_target != right_target:
        return None
    if left_proof == "rfl":
        return f"({right_proof}).symm" if right_proof != "rfl" else "rfl"
    if right_proof == "rfl":
        return left_proof
    return f"({left_proof}).trans ({right_proof}).symm"


def sandwich_left_projection_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = sandwich_left_projection_source(eq1)
    if source is None:
        return None
    proof_expr = projection_proof_expr_from_law(eq2, "left", hypothesis_name="hleft")
    if proof_expr is None:
        return None
    root, lead, middle, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "a", lead: "b", middle: "c"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hsrc : ∀ a b c : G, a = a ◇ (b ◇ (c ◇ b)) := by\n"
        "    intro a b c\n"
        f"    exact {call}\n"
        "  have hleft : ∀ a b : G, a = a ◇ b := by\n"
        "    intro a b\n"
        "    exact\n"
        "      ((hsrc a b a).trans\n"
        "        (congrArg (fun t => a ◇ (b ◇ t)) (hsrc (a ◇ b) b a))).trans\n"
        "        ((congrArg (fun t => a ◇ t) (hsrc b (a ◇ b) b)).symm)\n"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )
    return "true:sandwich_left_projection", code


def left_row_constancy_source(eq1: dict[str, Any]) -> tuple[str, str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        left = op_side[1]
        extra = op_side[2]
        if left[0] != "op" or extra[0] != "var":
            continue
        left_left = left[1]
        left_right = left[2]
        if left_left[0] != "op" or left_right[0] != "op":
            continue
        if left_left[1] != ("var", root) or left_left[2][0] != "var":
            continue
        bridge = str(left_left[2][1])
        if left_right[1] != ("var", bridge) or left_right[2][0] != "var":
            continue
        tail = str(left_right[2][1])
        extra_name = str(extra[1])
        if len({root, bridge, tail, extra_name}) != 4:
            continue
        if set(eq1["variables"]) != {root, bridge, tail, extra_name}:
            continue
        return root, bridge, tail, extra_name, swapped
    return None


@lru_cache(maxsize=None)
def left_row_constancy_key(term: Term) -> Term:
    if term[0] == "var":
        return term
    return "op", left_row_constancy_key(term[1]), "_"


def left_row_constancy_term_proof(src: Term, dst: Term, *, hypothesis_name: str = "hrow") -> str | None:
    if src == dst:
        return "rfl"
    if left_row_constancy_key(src) != left_row_constancy_key(dst):
        return None
    if src[0] != "op" or dst[0] != "op":
        return None
    left_proof = left_row_constancy_term_proof(src[1], dst[1], hypothesis_name=hypothesis_name)
    if left_proof is None:
        return None
    proof_expr: str | None = None
    left_dst = dst[1]
    if left_proof != "rfl":
        proof_expr = f"congrArg (fun t => t ◇ {term_to_lean(src[2])}) ({left_proof})"
    row_step = f"{hypothesis_name} {term_to_lean(left_dst)} {term_to_lean(src[2])} {term_to_lean(dst[2])}"
    return chain_trans(proof_expr, row_step)


def left_row_constancy_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = left_row_constancy_source(eq1)
    if source is None:
        return None
    proof_expr = left_row_constancy_term_proof(eq2["lhs"], eq2["rhs"])
    if proof_expr is None:
        return None
    root, bridge, tail, extra, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "a", bridge: "b", tail: "c", extra: "d"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hsrc : ∀ a b c d : G, a = ((a ◇ b) ◇ (b ◇ c)) ◇ d := by\n"
        "    intro a b c d\n"
        f"    exact {call}\n"
        "  have hrow : ∀ a b c : G, a ◇ b = a ◇ c := by\n"
        "    intro a b c\n"
        "    exact (hsrc (a ◇ b) (b ◇ a) a c).trans (congrArg (fun t => t ◇ c) (hsrc a b a ((b ◇ a) ◇ a))).symm\n"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )
    return "true:left_row_constancy", code


def product_constancy_source(eq1: dict[str, Any]) -> tuple[str, str, str, str, bool] | None:
    for swapped, source_lhs, source_rhs in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if source_lhs[0] != "op" or source_rhs[0] != "op":
            continue
        if source_lhs[1][0] != "var" or source_lhs[2][0] != "var":
            continue
        left_name = str(source_lhs[1][1])
        right_name = str(source_lhs[2][1])
        square = source_rhs[1]
        tail = source_rhs[2]
        if left_name == right_name:
            continue
        if square != ("op", ("var", right_name), ("var", right_name)):
            continue
        if tail[0] != "op" or tail[1][0] != "var" or tail[2][0] != "var":
            continue
        tail_left = str(tail[1][1])
        tail_right = str(tail[2][1])
        if len({left_name, right_name, tail_left, tail_right}) != 4:
            continue
        if set(eq1["variables"]) != {left_name, right_name, tail_left, tail_right}:
            continue
        return left_name, right_name, tail_left, tail_right, swapped
    return None


def product_constancy_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = product_constancy_source(eq1)
    if source is None or eq2["lhs"][0] != "op" or eq2["rhs"][0] != "op":
        return None
    left_name, right_name, tail_left, tail_right, swapped = source
    call = call_expression_lean_args(
        eq1["variables"],
        {left_name: "a", right_name: "b", tail_left: "c", tail_right: "d"},
    )
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    lhs_left = term_to_lean(eq2["lhs"][1])
    lhs_right = term_to_lean(eq2["lhs"][2])
    rhs_left = term_to_lean(eq2["rhs"][1])
    rhs_right = term_to_lean(eq2["rhs"][2])
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hsrc : ∀ a b c d : G, a ◇ b = (b ◇ b) ◇ (c ◇ d) := by\n"
        "    intro a b c d\n"
        f"    exact {call}\n"
        "  have hprod : ∀ a b c d : G, a ◇ b = c ◇ d := by\n"
        "    intro a b c d\n"
        "    exact ((hsrc a b d d).trans (hsrc (b ◇ b) (d ◇ d) d d)).trans ((hsrc c d d d).trans (hsrc (d ◇ d) (d ◇ d) d d)).symm\n"
        f"{intro_line}"
        f"  exact hprod {lhs_left} {lhs_right} {rhs_left} {rhs_right}\n"
    )
    return "true:product_constancy", code


def square_twist_comm_source(eq1: dict[str, Any]) -> tuple[str, str, bool] | None:
    for swapped, source_lhs, source_rhs in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if source_lhs[0] != "op" or source_rhs[0] != "op" or source_rhs[1][0] != "op":
            continue
        if source_lhs[1][0] != "var" or source_lhs[2][0] != "var" or source_rhs[2][0] != "var":
            continue
        left_name = str(source_lhs[1][1])
        right_name = str(source_lhs[2][1])
        square = source_rhs[1]
        tail_name = str(source_rhs[2][1])
        if left_name == right_name or tail_name != left_name:
            continue
        if square != ("op", ("var", right_name), ("var", right_name)):
            continue
        if set(eq1["variables"]) != {left_name, right_name}:
            continue
        return left_name, right_name, swapped
    return None


@lru_cache(maxsize=None)
def commutative_term_key(term: Term) -> Term:
    if term[0] == "var":
        return term
    left = commutative_term_key(term[1])
    right = commutative_term_key(term[2])
    if repr(right) < repr(left):
        left, right = right, left
    return "op", left, right


_TERM_CACHE_FUNCS = (
    term_vars_tuple,
    term_size,
    term_depth,
    term_to_lean,
    dual_term,
    term_subterms_tuple,
    boundary_vars,
    subterm_paths_tuple,
    term_at_path,
    replace_subterm,
    context_to_lean,
    left_row_constancy_key,
    commutative_term_key,
)


def clear_term_caches() -> None:
    for cached in _TERM_CACHE_FUNCS:
        cached.cache_clear()


def combine_binary_congr(
    left_src: Term,
    right_src: Term,
    left_dst: Term,
    left_proof: str,
    right_proof: str,
) -> str:
    proof_expr: str | None = None
    if left_proof != "rfl":
        proof_expr = f"congrArg (fun t => t ◇ {term_to_lean(right_src)}) ({left_proof})"
    if right_proof != "rfl":
        proof = f"congrArg (fun t => {term_to_lean(left_dst)} ◇ t) ({right_proof})"
        proof_expr = chain_trans(proof_expr, proof)
    return proof_expr or "rfl"


def commutative_term_proof(src: Term, dst: Term, *, hypothesis_name: str = "hcomm") -> str | None:
    if src == dst:
        return "rfl"
    if src[0] != "op" or dst[0] != "op":
        return None

    left_direct = commutative_term_proof(src[1], dst[1], hypothesis_name=hypothesis_name)
    if left_direct is not None:
        right_direct = commutative_term_proof(src[2], dst[2], hypothesis_name=hypothesis_name)
        if right_direct is not None:
            return combine_binary_congr(src[1], src[2], dst[1], left_direct, right_direct)

    left_swapped = commutative_term_proof(src[2], dst[1], hypothesis_name=hypothesis_name)
    if left_swapped is None:
        return None
    right_swapped = commutative_term_proof(src[1], dst[2], hypothesis_name=hypothesis_name)
    if right_swapped is None:
        return None
    swap_proof = f"{hypothesis_name} {term_to_lean(src[1])} {term_to_lean(src[2])}"
    rest = combine_binary_congr(src[2], src[1], dst[1], left_swapped, right_swapped)
    return chain_trans(swap_proof, rest)


def square_twist_comm_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = square_twist_comm_source(eq1)
    if source is None or commutative_term_key(eq2["lhs"]) != commutative_term_key(eq2["rhs"]):
        return None
    left_name, right_name, swapped = source
    call = call_expression_lean_args(eq1["variables"], {left_name: "a", right_name: "b"})
    if swapped:
        call = f"({call}).symm"
    proof_expr = commutative_term_proof(eq2["lhs"], eq2["rhs"])
    if proof_expr is None:
        return None
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hc : ∀ a b : G, a ◇ b = (b ◇ b) ◇ a := by\n"
        "    intro a b\n"
        f"    exact {call}\n"
        "  have hsq : ∀ a : G, a ◇ a = (a ◇ a) ◇ (a ◇ a) := by\n"
        "    intro a\n"
        "    exact (hc a a).trans (hc (a ◇ a) a)\n"
        "  have hcomm : ∀ a b : G, a ◇ b = b ◇ a := by\n"
        "    intro a b\n"
        "    have h1 : a ◇ b = (b ◇ b) ◇ a := hc a b\n"
        "    have h2 : (b ◇ b) ◇ a = (a ◇ a) ◇ (b ◇ b) := hc (b ◇ b) a\n"
        "    have h3 : (a ◇ a) ◇ (b ◇ b) = (b ◇ b) ◇ (a ◇ a) := by\n"
        "      exact (hc (a ◇ a) (b ◇ b)).trans (congrArg (fun t => t ◇ (a ◇ a)) (hsq b).symm)\n"
        "    have h4 : (b ◇ b) ◇ (a ◇ a) = (a ◇ a) ◇ b := (hc (a ◇ a) b).symm\n"
        "    exact h1.trans (h2.trans (h3.trans (h4.trans (hc b a).symm)))\n"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )
    return "true:square_twist_comm", code


def projection_from_lemma_term_proof(
    term: Term,
    side: str,
    *,
    hypothesis_name: str,
) -> tuple[str, str] | None:
    if term[0] == "var":
        return "rfl", str(term[1])
    if term[0] != "op":
        return None
    projected = term[1] if side == "left" else term[2]
    step = f"{hypothesis_name} {term_to_lean(term[1])} {term_to_lean(term[2])}"
    rest = projection_from_lemma_term_proof(projected, side, hypothesis_name=hypothesis_name)
    if rest is None:
        return None
    rest_proof, target_var = rest
    if rest_proof != "rfl":
        step = f"({step}).trans ({rest_proof})"
    return step, target_var


def projection_from_lemma_goal_proof(eq2: dict[str, Any], side: str, *, hypothesis_name: str) -> str | None:
    left = projection_from_lemma_term_proof(eq2["lhs"], side, hypothesis_name=hypothesis_name)
    right = projection_from_lemma_term_proof(eq2["rhs"], side, hypothesis_name=hypothesis_name)
    if left is None or right is None:
        return None
    left_proof, left_target = left
    right_proof, right_target = right
    if left_target != right_target:
        return None
    if left_proof == "rfl":
        return f"({right_proof}).symm" if right_proof != "rfl" else "rfl"
    if right_proof == "rfl":
        return left_proof
    return f"({left_proof}).trans ({right_proof}).symm"


def tail_square_right_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[2] != ("var", root) or op_side[1][0] != "op":
            continue
        middle = op_side[1]
        if middle[2][0] != "var" or middle[1][0] != "op":
            continue
        repeat = str(middle[2][1])
        inner = middle[1]
        if inner[1][0] != "var" or inner[2] != ("var", repeat):
            continue
        lead = str(inner[1][1])
        if len({root, lead, repeat}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, repeat}:
            continue
        return root, lead, repeat, swapped
    return None


def nested_tail_right_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[2] != ("var", root) or op_side[1][0] != "op":
            continue
        middle = op_side[1]
        if middle[2][0] != "var" or middle[1][0] != "op":
            continue
        repeat = str(middle[2][1])
        left = middle[1]
        if left[1][0] != "var" or left[2][0] != "op":
            continue
        lead = str(left[1][1])
        tail = left[2]
        if tail[1][0] != "var" or tail[2] != ("var", repeat):
            continue
        middle_var = str(tail[1][1])
        if len({root, lead, middle_var, repeat}) != 4:
            continue
        if set(eq1["variables"]) != {root, lead, middle_var, repeat}:
            continue
        return root, lead, middle_var, repeat, swapped
    return None


def left_pair_tail_right_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[2][0] != "var" or op_side[1][0] != "op":
            continue
        lead = str(op_side[2][1])
        body = op_side[1]
        if body[1][0] != "op" or body[2][0] != "op":
            continue
        left = body[1]
        right = body[2]
        if left[1] != ("var", lead) or left[2][0] != "var":
            continue
        extra = str(left[2][1])
        if right[1] != ("var", lead) or right[2] != ("var", root):
            continue
        if len({root, lead, extra}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def nested_left_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1] != ("var", root) or op_side[2][0] != "op":
            continue
        tail = op_side[2]
        if tail[1][0] != "var" or tail[2][0] != "op":
            continue
        lead = str(tail[1][1])
        inner = tail[2]
        if inner[1][0] != "op" or inner[2][0] != "var":
            continue
        extra_tail = str(inner[2][1])
        pair = inner[1]
        if pair[1] != ("var", lead) or pair[2][0] != "var":
            continue
        extra = str(pair[2][1])
        if len({root, lead, extra, extra_tail}) != 4:
            continue
        if set(eq1["variables"]) != {root, lead, extra, extra_tail}:
            continue
        return root, lead, extra, extra_tail, swapped
    return None


def right_nested_tail_left_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1] != ("var", root) or op_side[2][0] != "op":
            continue
        tail = op_side[2]
        if tail[1][0] != "op" or tail[2][0] != "var":
            continue
        extra_tail = str(tail[2][1])
        pair = tail[1]
        if pair[1][0] != "var" or pair[2][0] != "op":
            continue
        lead = str(pair[1][1])
        inner = pair[2]
        if inner[1][0] != "var" or inner[2][0] != "var":
            continue
        extra = str(inner[1][1])
        repeat = str(inner[2][1])
        if repeat != extra_tail:
            continue
        if len({root, lead, extra, repeat}) != 4:
            continue
        if set(eq1["variables"]) != {root, lead, extra, repeat}:
            continue
        return root, lead, extra, repeat, extra_tail, swapped
    return None


def bracket_tail_left_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1] != ("var", root) or op_side[2][0] != "op":
            continue
        tail = op_side[2]
        if tail[1][0] != "op" or tail[2][0] != "var":
            continue
        final = str(tail[2][1])
        left = tail[1]
        if left[1][0] != "op" or left[2][0] != "var":
            continue
        repeat = str(left[2][1])
        pair = left[1]
        if pair[1][0] != "var" or pair[2][0] != "var":
            continue
        lead = str(pair[1][1])
        extra = str(pair[2][1])
        if len({root, lead, extra, repeat, final}) != 5:
            continue
        if set(eq1["variables"]) != {root, lead, extra, repeat, final}:
            continue
        return root, lead, extra, repeat, final, swapped
    return None


def pair_square_left_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1] != ("var", root) or op_side[2][0] != "op":
            continue
        tail = op_side[2]
        if tail[1][0] != "op" or tail[2][0] != "op":
            continue
        left = tail[1]
        right = tail[2]
        if left[1][0] != "var" or left[2][0] != "var" or right[1][0] != "var" or right[2][0] != "var":
            continue
        lead = str(left[1][1])
        extra = str(left[2][1])
        square_left = str(right[1][1])
        square_right = str(right[2][1])
        if len({root, lead, extra, square_left, square_right}) != 5:
            continue
        if set(eq1["variables"]) != {root, lead, extra, square_left, square_right}:
            continue
        return root, lead, extra, square_left, square_right, swapped
    return None


def sandwich_tail_right_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[2] != ("var", root) or op_side[1][0] != "op":
            continue
        tail = op_side[1]
        if tail[2][0] != "var" or tail[1][0] != "op":
            continue
        lead = str(tail[2][1])
        middle = tail[1]
        if middle[2][0] != "var" or middle[1][0] != "op":
            continue
        extra = str(middle[2][1])
        pair = middle[1]
        if pair[1] != ("var", lead) or pair[2] != ("var", root):
            continue
        if len({root, lead, extra}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def right_projection_local_helpers() -> str:
    return (
        "  let T := @Eq.trans\n"
        "  let S := @Eq.symm\n"
        "  let R := @Eq.refl\n"
        "  let M := @Magma.op\n"
        "  have C : {a b c d : G} -> a = b -> c = d -> a ◇ c = b ◇ d := by\n"
        "    intro a b c d h1 h2\n"
        "    rw [h1, h2]\n"
    )


def right_projection_from_3218_block() -> str:
    return (
        "  have hproj : ∀ x y : G, x = y ◇ x := by\n"
        "    intro x y\n"
        "    let v0 := M y x\n"
        "    have h1 := R y\n"
        "    have h2 := S (h3218 v0 v0 v0)\n"
        "    have h3 := R v0\n"
        "    have h4 := S (h3218 v0 v0 x)\n"
        "    have h5 := C (h3218 x y x) h3\n"
        "    have h6 := C (C (C (T h5 h4) h3) h3) h3\n"
        "    have h7 := h3218 v0 x v0\n"
        "    exact T (h3218 x y y) (C (T (C (C (C (T (h3218 y x v0) (C (T (C (T (T (T (C (T (T (T h5 h4) h7) h6) h3) h2) h7) h6) h3) h2) h1)) h1) h1) h1) (S (h3218 y v0 y))) (R x))\n"
    )


def left_projection_from_641_block(source_name: str) -> str:
    return (
        "  have hproj : ∀ x y : G, x = x ◇ y := by\n"
        "    intro x y\n"
        "    let v0 := M x y\n"
        f"    have h1 := {source_name} y x (M (M v0 x) x)\n"
        f"    have h2 := {source_name} x v0 x\n"
        "    have h3 := R y\n"
        "    have h4 := T (C h3 h2) (S h1)\n"
        "    have h5 := R x\n"
        f"    have h6 := {source_name} y v0 y\n"
        "    have h7 := C h3 (S h2)\n"
        f"    exact T (T ({source_name} x y (M (M y y) y)) (C h5 (T (C (T h1 h7) (C h4 (C (T (C h3 (T (T h1 h7) (C h6 h5))) (C h3 (C (S h6) h5))) h3))) (S ({source_name} (M y x) y y))))) (C h5 h4)\n"
    )


def left_projection_from_1065_block(source_name: str) -> str:
    return (
        "  have hproj : ∀ x y : G, x = x ◇ y := by\n"
        "    intro x y\n"
        f"    have h0 := S ({source_name} y x x)\n"
        "    let v1 := M (M x (M x x)) x\n"
        f"    exact T ({source_name} x y v1) (C (R x) (T (C (T (C (R y) (S ({source_name} v1 x x))) h0) (R v1)) h0))\n"
    )


def left_projection_from_1268_block(source_name: str) -> str:
    return (
        "  have hproj : ∀ x y : G, x = x ◇ y := by\n"
        "    intro x y\n"
        f"    have h0 := S ({source_name} y x x)\n"
        "    let v1 := M (M (M x x) x) x\n"
        "    have h2 := R v1\n"
        f"    exact T ({source_name} x y v1) (C (R x) (T (C (T (C h0 h2) h0) h2) h0))\n"
    )


def left_projection_from_857_block(source_name: str) -> str:
    return (
        "  have hproj : ∀ x y : G, x = x ◇ y := by\n"
        "    intro x y\n"
        "    let v0 := M x x\n"
        "    let v1 := M v0 v0\n"
        f"    have h2 := {source_name} v0 x x\n"
        "    let v3 := M x y\n"
        "    let v4 := M y y\n"
        "    let v5 := M y v3\n"
        f"    exact T ({source_name} x y v3) (C (R x) (T (T (T (C (R v5) (T ({source_name} v4 y y) (C ({source_name} v4 x x) (R (M v4 v4))))) (S ({source_name} v5 v4 v1))) (C (R y) (T ({source_name} v3 x x) (C (R v3) (T (C (R v0) (T h2 (C h2 (R v1)))) (S ({source_name} v0 v0 v1))))))) (S ({source_name} y x y))))\n"
    )


def right_projection_from_2927_block() -> str:
    return (
        "  have hproj : ∀ x y : G, x = y ◇ x := by\n"
        "    intro x y\n"
        "    have h0 := R x\n"
        "    let v1 := M y x\n"
        "    have h2 := h2927 y (M x (M x v1)) x\n"
        "    have h3 := S h2\n"
        "    have h4 := R y\n"
        "    have h5 := h2927 x x v1\n"
        "    have h6 := C h5 h4\n"
        "    have h7 := T h6 h3\n"
        "    have h8 := C (S h5) h4\n"
        "    have h9 := h2927 y v1 y\n"
        "    have h10 := S h9\n"
        "    have h11 := T (T (C h0 h10) h6) h3\n"
        "    have h12 := C h11 h4\n"
        "    have h13 := T (T h2 h8) (C h0 h9)\n"
        "    have h14 := C h13 h7\n"
        "    have h15 := T h2 h8\n"
        "    have h16 := C h11 h15\n"
        "    have h17 := C h13 h4\n"
        "    have h18 := C h4 h10\n"
        "    have h19 := C h4 h9\n"
        "    exact T (T (h2927 x (M y y) y) (C (T (T (T (T (C (T (C h19 h7) (C (T (T h18 h17) h16) h4)) h4) (C (T (C (T (T h14 h12) h19) h4) (C (T (T (T (T (T h18 h17) h16) (C (T (T h2 h8) (C h0 h15)) h7)) (h2927 (M (M x (M x y)) y) y x)) (C (C (C h4 (S (h2927 x x y))) h0) (T (T (C (T (T (C h0 h7) h6) h3) h15) h14) h12))) h4)) h4)) (S (h2927 y (M v1 x) y))) h2) h8) h0)) (C h7 h0)\n"
    )


def right_projection_from_3126_block(source_name: str) -> str:
    return (
        "  have hproj : ∀ x y : G, x = y ◇ x := by\n"
        "    intro x y\n"
        "    have h0 := R x\n"
        "    let v1 := M y x\n"
        "    let v2 := M v1 v1\n"
        f"    have h3 := {source_name} y v2 x\n"
        "    have h4 := R y\n"
        "    have h5 := R v2\n"
        f"    have h6 := {source_name} x y v1\n"
        "    let v7 := M v1 y\n"
        f"    have h8 := {source_name} y v7 x\n"
        "    have h9 := R v7\n"
        f"    have h10 := {source_name} x y y\n"
        "    let v11 := M v1 x\n"
        f"    have h12 := {source_name} y v11 x\n"
        "    have h13 := R v11\n"
        f"    have h14 := {source_name} x y x\n"
        "    let v15 := M (M (M x y) v1) x\n"
        f"    exact T (T (T (T ({source_name} x y v15) (C (T (T (T (C (C (C ({source_name} y x v1) h0) (R v15)) h4) (S ({source_name} y v15 x))) h12) (C (C (S h14) h13) h4)) h0)) (C (T (T (T (C (C h14 h13) h4) (S h12)) h8) (C (C (S h10) h9) h4)) h0)) (C (T (T (T (C (C h10 h9) h4) (S h8)) h3) (C (C (S h6) h5) h4)) h0)) (C (T (C (C h6 h5) h4) (S h3)) h0)\n"
    )


def right_projection_from_2788_block(source_name: str) -> str:
    return (
        "  have eq9 (X0 X1 X2 : G) : (((X1 ◇ X2) ◇ (X1 ◇ X0)) ◇ X1) = X0 := by\n"
        f"    exact ({source_name} X0 X1 X2).symm\n"
        "  have eq11 (X0 X1 X2 X3 : G) : ((X2 ◇ (((X0 ◇ X1) ◇ (X0 ◇ X2)) ◇ X3)) ◇ ((X0 ◇ X1) ◇ (X0 ◇ X2))) = X3 := by\n"
        "    have hb : (((X0 ◇ X1) ◇ (X0 ◇ X2)) ◇ X0) = X2 := eq9 X2 X0 X1\n"
        "    have hx : (((((X0 ◇ X1) ◇ (X0 ◇ X2)) ◇ X0) ◇ (((X0 ◇ X1) ◇ (X0 ◇ X2)) ◇ X3)) ◇ ((X0 ◇ X1) ◇ (X0 ◇ X2))) = X3 := eq9 X3 ((X0 ◇ X1) ◇ (X0 ◇ X2)) X0\n"
        "    exact (congrArg (fun t => (t ◇ (((X0 ◇ X1) ◇ (X0 ◇ X2)) ◇ X3)) ◇ ((X0 ◇ X1) ◇ (X0 ◇ X2))) hb).symm.trans hx\n"
        "  have eq13 (X0 X1 X2 : G) : ((X2 ◇ X2) ◇ ((X0 ◇ X1) ◇ (X0 ◇ X2))) = X0 := by\n"
        "    have hb : (((X0 ◇ X1) ◇ (X0 ◇ X2)) ◇ X0) = X2 := eq9 X2 X0 X1\n"
        "    have hx : ((X2 ◇ (((X0 ◇ X1) ◇ (X0 ◇ X2)) ◇ X0)) ◇ ((X0 ◇ X1) ◇ (X0 ◇ X2))) = X0 := eq11 X0 X1 X2 X0\n"
        "    exact (congrArg (fun t => (X2 ◇ t) ◇ ((X0 ◇ X1) ◇ (X0 ◇ X2))) hb).symm.trans hx\n"
        "  have eq19 (X0 X1 X2 : G) : (X0 ◇ (X0 ◇ X1)) = (X2 ◇ (X0 ◇ X1)) := by\n"
        "    have h11 : (((X0 ◇ X1) ◇ (((X0 ◇ X1) ◇ (X0 ◇ (X0 ◇ X1))) ◇ X2)) ◇ ((X0 ◇ X1) ◇ (X0 ◇ (X0 ◇ X1)))) = X2 := eq11 X0 X1 (X0 ◇ X1) X2\n"
        "    have h9 : (((((X0 ◇ X1) ◇ (((X0 ◇ X1) ◇ (X0 ◇ (X0 ◇ X1))) ◇ X2)) ◇ ((X0 ◇ X1) ◇ (X0 ◇ (X0 ◇ X1)))) ◇ (X0 ◇ X1)) = X0 ◇ (X0 ◇ X1)) := eq9 (X0 ◇ (X0 ◇ X1)) (X0 ◇ X1) (((X0 ◇ X1) ◇ (X0 ◇ (X0 ◇ X1))) ◇ X2)\n"
        "    exact h9.symm.trans (congrArg (fun t => t ◇ (X0 ◇ X1)) h11)\n"
        "  have eq22 (X0 X1 : G) : ((X1 ◇ (X1 ◇ X0)) ◇ X1) = X0 := by\n"
        "    have h19 : X1 ◇ (X1 ◇ X0) = (X1 ◇ X0) ◇ (X1 ◇ X0) := eq19 X1 X0 (X1 ◇ X0)\n"
        "    have h9 : (((X1 ◇ X0) ◇ (X1 ◇ X0)) ◇ X1) = X0 := eq9 X0 X1 X0\n"
        "    exact (congrArg (fun t => t ◇ X1) h19).trans h9\n"
        "  have eq25 (X0 X2 : G) : ((X2 ◇ X2) ◇ (X0 ◇ (X0 ◇ X2))) = X0 := by\n"
        "    have h19 : X0 ◇ (X0 ◇ X2) = (X0 ◇ X2) ◇ (X0 ◇ X2) := eq19 X0 X2 (X0 ◇ X2)\n"
        "    have h13 : ((X2 ◇ X2) ◇ ((X0 ◇ X2) ◇ (X0 ◇ X2))) = X0 := eq13 X0 X2 X2\n"
        "    exact (congrArg (fun t => (X2 ◇ X2) ◇ t) h19).trans h13\n"
        "  have eq33 (X0 X1 : G) : (((X0 ◇ (X0 ◇ X1)) ◇ X1) ◇ (X0 ◇ (X0 ◇ X1))) = X0 := by\n"
        "    let P : G := X0 ◇ (X0 ◇ X1)\n"
        "    have hinner : P ◇ X0 = X1 := eq22 X1 X0\n"
        "    have hbase : (P ◇ (P ◇ X0)) ◇ P = X0 := eq22 X0 P\n"
        "    exact (congrArg (fun t => (P ◇ t) ◇ P) hinner).symm.trans hbase\n"
        "  have eq34 (X0 : G) : X0 ◇ (X0 ◇ (X0 ◇ X0)) = X0 := by\n"
        "    let P : G := X0 ◇ (X0 ◇ X0)\n"
        "    have h22 : P ◇ X0 = X0 := eq22 X0 X0\n"
        "    have h33 : (P ◇ X0) ◇ P = X0 := eq33 X0 X0\n"
        "    exact (congrArg (fun t => t ◇ P) h22).symm.trans h33\n"
        # Derived rather than discharged by `grind` (2026-07-29). The old body
        # was `by grind`, which cost 37.0 s of the judge's 120 s Lean timeout,
        # needed `set_option maxHeartbeats 5000000`, and rested on a tactic this
        # project has field evidence against (the cloud judge rejected a
        # `narrow_grind` cert the local judge accepted). The derivation below
        # uses only eq19/eq22/eq34, already proven above.
        #
        # Write P := X0 ◇ (X0 ◇ X0).
        #   eq19 X0 (X0◇X0) t  :  X0 ◇ P = t ◇ P        (left factor is free)
        #   eq34 X0            :  X0 ◇ P = X0
        #   => (*) ∀ t, t ◇ P = X0
        #   (*) at t := P      :  P ◇ P = X0
        #   eq22 P P           :  (P ◇ (P ◇ P)) ◇ P = P
        #   rewrite by P◇P=X0  :  (P ◇ X0) ◇ P = P
        #   (*) at t := P ◇ X0 :  (P ◇ X0) ◇ P = X0      => P = X0  ∎
        #
        # Real-judge measured: accepted in 4.8 s (was 37.0 s with `grind`).
        "  have eq42 (X0 : G) : X0 ◇ (X0 ◇ X0) = X0 := by\n"
        "    have hstar : ∀ t : G, t ◇ (X0 ◇ (X0 ◇ X0)) = X0 := by\n"
        "      intro t\n"
        "      exact (eq19 X0 (X0 ◇ X0) t).symm.trans (eq34 X0)\n"
        "    have hPP : (X0 ◇ (X0 ◇ X0)) ◇ (X0 ◇ (X0 ◇ X0)) = X0 :=\n"
        "      hstar (X0 ◇ (X0 ◇ X0))\n"
        "    have h22 := eq22 (X0 ◇ (X0 ◇ X0)) (X0 ◇ (X0 ◇ X0))\n"
        "    have hrw := (congrArg\n"
        "      (fun t => ((X0 ◇ (X0 ◇ X0)) ◇ t) ◇ (X0 ◇ (X0 ◇ X0))) hPP).symm.trans h22\n"
        "    exact hrw.symm.trans (hstar ((X0 ◇ (X0 ◇ X0)) ◇ X0))\n"
        "  have eq43 (X0 : G) : X0 ◇ X0 = X0 := by\n"
        "    exact (congrArg (fun t => X0 ◇ t) (eq42 X0)).symm.trans (eq34 X0)\n"
        "  have hright : ∀ a b : G, a ◇ b = b := by\n"
        "    intro a b\n"
        "    have h19 : b ◇ (b ◇ b) = a ◇ (b ◇ b) := eq19 b b a\n"
        "    have hb : b ◇ (b ◇ b) = b := eq42 b\n"
        "    have hbb : b ◇ b = b := eq43 b\n"
        "    have hr : a ◇ (b ◇ b) = a ◇ b := congrArg (fun t => a ◇ t) hbb\n"
        "    exact hr.symm.trans (h19.symm.trans hb)\n"
    )


def right_projection_collapse_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    proof_expr = projection_from_lemma_goal_proof(eq2, "right", hypothesis_name="hright")
    if proof_expr is None:
        return None

    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    tail_source = tail_square_right_projection_source(eq1)
    if tail_source is not None:
        root, lead, repeat, swapped = tail_source
        call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "(y ◇ z)", repeat: "z"})
        if swapped:
            call = f"({call}).symm"
        code = (
            "import JudgeProblem\n\n"
            "def submission : Goal := by\n"
            "  intro G _ h\n"
            f"{right_projection_local_helpers()}"
            "  have h3218 : ∀ x y z : G, x = (((y ◇ z) ◇ z) ◇ z) ◇ x := by\n"
            "    intro x y z\n"
            f"    exact {call}\n"
            f"{right_projection_from_3218_block()}"
            "  have hright : ∀ a b : G, a ◇ b = b := by\n"
            "    intro a b\n"
            "    exact (hproj b a).symm\n"
            f"{intro_line}"
            f"  exact {proof_expr}\n"
        )
        return "true:right_projection_collapse:tail_square", code

    nested_source = nested_tail_right_projection_source(eq1)
    if nested_source is not None:
        root, lead, middle, repeat, swapped = nested_source
        call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", middle: "x", repeat: "z"})
        if swapped:
            call = f"({call}).symm"
        code = (
            "import JudgeProblem\n\n"
            "def submission : Goal := by\n"
            "  intro G _ h\n"
            f"{right_projection_local_helpers()}"
            "  have h2927 : ∀ x y z : G, x = ((y ◇ (x ◇ z)) ◇ z) ◇ x := by\n"
            "    intro x y z\n"
            f"    exact {call}\n"
            f"{right_projection_from_2927_block()}"
            "  have hright : ∀ a b : G, a ◇ b = b := by\n"
            "    intro a b\n"
            "    exact (hproj b a).symm\n"
            f"{intro_line}"
            f"  exact {proof_expr}\n"
        )
        return "true:right_projection_collapse:nested_tail", code

    sandwich_source = sandwich_tail_right_projection_source(eq1)
    if sandwich_source is not None:
        root, lead, extra, swapped = sandwich_source
        call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z"})
        if swapped:
            call = f"({call}).symm"
        code = (
            "import JudgeProblem\n\n"
            "def submission : Goal := by\n"
            "  intro G _ h\n"
            f"{right_projection_local_helpers()}"
            "  have h3126 : ∀ x y z : G, x = (((y ◇ x) ◇ z) ◇ y) ◇ x := by\n"
            "    intro x y z\n"
            f"    exact {call}\n"
            f"{right_projection_from_3126_block('h3126')}"
            "  have hright : ∀ a b : G, a ◇ b = b := by\n"
            "    intro a b\n"
            "    exact (hproj b a).symm\n"
            f"{intro_line}"
            f"  exact {proof_expr}\n"
        )
        return "true:right_projection_collapse:sandwich_tail", code

    left_pair_source = left_pair_tail_right_projection_source(eq1)
    if left_pair_source is not None:
        root, lead, extra, swapped = left_pair_source
        call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z"})
        if swapped:
            call = f"({call}).symm"
        # No `set_option maxHeartbeats` here: the only step that needed a raised
        # budget was the `grind` in right_projection_from_2788_block, now a
        # derived proof term (2026-07-29).
        code = (
            "import JudgeProblem\n\n"
            "def submission : Goal := by\n"
            "  intro G _ h\n"
            "  have h2788 : ∀ x y z : G, x = ((y ◇ z) ◇ (y ◇ x)) ◇ y := by\n"
            "    intro x y z\n"
            f"    exact {call}\n"
            f"{right_projection_from_2788_block('h2788')}"
            f"{intro_line}"
            f"  exact {proof_expr}\n"
        )
        return "true:right_projection_collapse:left_pair_tail", code

    return None


def nested_left_projection_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = nested_left_projection_source(eq1)
    if source is None:
        return None
    proof_expr = projection_from_lemma_goal_proof(eq2, "left", hypothesis_name="hleft")
    if proof_expr is None:
        return None
    root, lead, extra, extra_tail, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "x", extra_tail: "z"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{right_projection_local_helpers()}"
        "  have h641 : ∀ x y z : G, x = x ◇ (y ◇ ((y ◇ x) ◇ z)) := by\n"
        "    intro x y z\n"
        f"    exact {call}\n"
        f"{left_projection_from_641_block('h641')}"
        "  have hleft : ∀ a b : G, a ◇ b = a := by\n"
        "    intro a b\n"
        "    exact (hproj a b).symm\n"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )
    return "true:nested_left_projection", code


def specialized_left_projection_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    proof_expr = projection_from_lemma_goal_proof(eq2, "left", hypothesis_name="hleft")
    if proof_expr is None:
        return None
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""

    def make_code(source_name: str, source_statement: str, call: str, block: str) -> str:
        return (
            "import JudgeProblem\n\n"
            "def submission : Goal := by\n"
            "  intro G _ h\n"
            f"{right_projection_local_helpers()}"
            f"  have {source_name} : {source_statement} := by\n"
            f"{call}"
            f"{block}"
            "  have hleft : ∀ a b : G, a ◇ b = a := by\n"
            "    intro a b\n"
            "    exact (hproj a b).symm\n"
            f"{intro_line}"
            f"  exact {proof_expr}\n"
        )

    right_nested = right_nested_tail_left_projection_source(eq1)
    if right_nested is not None:
        root, lead, extra, repeat, extra_tail, swapped = right_nested
        call_expr = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z", repeat: "z", extra_tail: "z"})
        if swapped:
            call_expr = f"({call_expr}).symm"
        code = make_code(
            "h1065",
            "∀ x y z : G, x = x ◇ ((y ◇ (z ◇ z)) ◇ z)",
            "    intro x y z\n"
            f"    exact {call_expr}\n",
            left_projection_from_1065_block("h1065"),
        )
        return "true:left_projection_collapse:right_nested_tail", code

    bracket_tail = bracket_tail_left_projection_source(eq1)
    if bracket_tail is not None:
        root, lead, extra, repeat, final, swapped = bracket_tail
        call_expr = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z", repeat: "z", final: "z"})
        if swapped:
            call_expr = f"({call_expr}).symm"
        code = make_code(
            "h1268",
            "∀ x y z : G, x = x ◇ (((y ◇ z) ◇ z) ◇ z)",
            "    intro x y z\n"
            f"    exact {call_expr}\n",
            left_projection_from_1268_block("h1268"),
        )
        return "true:left_projection_collapse:bracket_tail", code

    pair_square = pair_square_left_projection_source(eq1)
    if pair_square is not None:
        root, lead, extra, square_left, square_right, swapped = pair_square
        call_expr = call_expression_lean_args(eq1["variables"], {root: "x", lead: "y", extra: "z", square_left: "y", square_right: "y"})
        if swapped:
            call_expr = f"({call_expr}).symm"
        code = make_code(
            "h857",
            "∀ x y z : G, x = x ◇ ((y ◇ z) ◇ (y ◇ y))",
            "    intro x y z\n"
            f"    exact {call_expr}\n",
            left_projection_from_857_block("h857"),
        )
        return "true:left_projection_collapse:pair_square", code

    return None


def derived_left_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1] != ("var", root) or op_side[2][0] != "op":
            continue
        tail1 = op_side[2]
        if tail1[1][0] != "var" or tail1[2][0] != "op":
            continue
        lead = str(tail1[1][1])
        tail2 = tail1[2]
        if tail2[1] != ("var", root) or tail2[2][0] != "op":
            continue
        tail3 = tail2[2]
        if tail3[1] != ("var", lead) or tail3[2][0] != "var":
            continue
        extra = str(tail3[2][1])
        if len({root, lead, extra}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def derived_left_projection_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = derived_left_projection_source(eq1)
    if source is None:
        return None
    left = projection_from_lemma_term_proof(eq2["lhs"], "left", hypothesis_name="hleft")
    right = projection_from_lemma_term_proof(eq2["rhs"], "left", hypothesis_name="hleft")
    if left is None or right is None:
        return None
    left_proof, left_target = left
    right_proof, right_target = right
    if left_target != right_target:
        return None
    if left_proof == "rfl":
        proof_expr = f"({right_proof}).symm" if right_proof != "rfl" else "rfl"
    elif right_proof == "rfl":
        proof_expr = left_proof
    else:
        proof_expr = f"({left_proof}).trans ({right_proof}).symm"
    root, lead, extra, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "a", lead: "b", extra: "c"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hsrc : ∀ a b c : G, a = a ◇ (b ◇ (a ◇ (b ◇ c))) := by\n"
        "    intro a b c\n"
        f"    exact {call}\n"
        "  have hp : ∀ a b : G, a ◇ (b ◇ a) = a := by\n"
        "    intro a b\n"
        "    let T : G := a ◇ (b ◇ a)\n"
        "    have h1 : a = a ◇ (b ◇ T) := hsrc a b a\n"
        "    have h2 : a = a ◇ (b ◇ (a ◇ (b ◇ T))) := hsrc a b T\n"
        "    exact (congrArg (fun t => a ◇ (b ◇ t)) h1).trans h2.symm\n"
        "  have hmid : ∀ a b : G, a ◇ (b ◇ (a ◇ b)) = a := by\n"
        "    intro a b\n"
        "    have inner : b ◇ (a ◇ b) = b := hp b a\n"
        "    have hbig : a = a ◇ (b ◇ (a ◇ (b ◇ (a ◇ b)))) := hsrc a b (a ◇ b)\n"
        "    exact (hbig.trans (congrArg (fun t => a ◇ (b ◇ (a ◇ t))) inner)).symm\n"
        "  have hleft : ∀ a b : G, a ◇ b = a := by\n"
        "    intro a b\n"
        "    have inner : b ◇ (a ◇ b) = b := hp b a\n"
        "    exact (congrArg (fun t => a ◇ t) inner).symm.trans (hmid a b)\n"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )
    return "true:derived_left_projection", code


def derived_right_projection_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[2] != ("var", root) or op_side[1][0] != "op":
            continue
        prefix = op_side[1]
        if prefix[1][0] != "op" or prefix[2][0] != "var":
            continue
        square = prefix[1]
        if square[1][0] != "var" or square[2] != square[1]:
            continue
        lead = str(square[1][1])
        extra = str(prefix[2][1])
        if len({root, lead, extra}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def derived_right_projection_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = derived_right_projection_source(eq1)
    if source is None:
        return None
    left = projection_from_lemma_term_proof(eq2["lhs"], "right", hypothesis_name="hright")
    right = projection_from_lemma_term_proof(eq2["rhs"], "right", hypothesis_name="hright")
    if left is None or right is None:
        return None
    left_proof, left_target = left
    right_proof, right_target = right
    if left_target != right_target:
        return None
    if left_proof == "rfl":
        proof_expr = f"({right_proof}).symm" if right_proof != "rfl" else "rfl"
    elif right_proof == "rfl":
        proof_expr = left_proof
    else:
        proof_expr = f"({left_proof}).trans ({right_proof}).symm"
    root, lead, extra, swapped = source
    call = call_expression_lean_args(eq1["variables"], {root: "a", lead: "b", extra: "c"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hsrc : ∀ a b c : G, a = ((b ◇ b) ◇ c) ◇ a := by\n"
        "    intro a b c\n"
        f"    exact {call}\n"
        "  have hright : ∀ a b : G, a ◇ b = b := by\n"
        "    intro a b\n"
        "    let E : G := (a ◇ a) ◇ b\n"
        "    have hEE : E ◇ E = E := (hsrc E a b).symm\n"
        "    have ha : a = E ◇ a := hsrc a a b\n"
        "    exact (congrArg (fun t => t ◇ b) ha).trans\n"
        "      ((congrArg (fun t => (t ◇ a) ◇ b) hEE.symm).trans\n"
        "        ((hsrc b E a).symm))\n"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )
    return "true:derived_right_projection", code


def square_to_right_product_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1][0] != "op" or op_side[2][0] != "op":
            continue
        left = op_side[1]
        right = op_side[2]
        if left[1] != ("var", root) or left[2][0] != "var":
            continue
        lead = str(left[2][1])
        if right[1][0] != "var" or right[2] != right[1]:
            continue
        extra = str(right[1][1])
        if len({root, lead, extra}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def square_to_right_product_goal(eq2: dict[str, Any]) -> tuple[str, Term, Term, bool] | None:
    for swapped, square_side, product_side in (
        (False, eq2["lhs"], eq2["rhs"]),
        (True, eq2["rhs"], eq2["lhs"]),
    ):
        if square_side[0] != "op" or square_side[1][0] != "var" or square_side[2] != square_side[1]:
            continue
        root = str(square_side[1][1])
        if product_side[0] != "op" or product_side[1] != ("var", root) or product_side[2][0] != "op":
            continue
        return root, product_side[2][1], product_side[2][2], swapped
    return None


def square_to_right_product_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = square_to_right_product_source(eq1)
    goal = square_to_right_product_goal(eq2)
    if source is None or goal is None:
        return None
    root, lead, extra, source_swapped = source
    goal_root, first, second, goal_swapped = goal
    if goal_root != root:
        return None
    call = call_expression_lean_args(eq1["variables"], {root: "a", lead: "b", extra: "c"})
    if source_swapped:
        call = f"({call}).symm"
    proof_expr = f"hprod {root} {term_to_lean(first)} {term_to_lean(second)}"
    if goal_swapped:
        proof_expr = f"({proof_expr}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hsrc : ∀ a b c : G, a = (a ◇ b) ◇ (c ◇ c) := by\n"
        "    intro a b c\n"
        f"    exact {call}\n"
        "  have hprod : ∀ a b c : G, a ◇ a = a ◇ (b ◇ c) := by\n"
        "    intro a b c\n"
        "    exact ((congrArg (fun t => a ◇ t) (hsrc a a a)).trans\n"
        "      (congrArg (fun t => t ◇ ((a ◇ a) ◇ (a ◇ a))) (hsrc a (b ◇ c) a))).trans\n"
        "      (hsrc (a ◇ (b ◇ c)) (a ◇ a) (a ◇ a)).symm\n"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )
    return "true:square_to_right_product", code


def right_self_absorption_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[1] != ("var", root) or op_side[2][0] != "op":
            continue
        tail1 = op_side[2]
        if tail1[1][0] != "var" or tail1[2][0] != "op":
            continue
        lead = str(tail1[1][1])
        tail2 = tail1[2]
        if tail2[1] != ("var", root) or tail2[2][0] != "op":
            continue
        tail3 = tail2[2]
        if tail3[1] != ("var", root) or tail3[2][0] != "var":
            continue
        extra = str(tail3[2][1])
        if len({root, lead, extra}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def right_self_absorption_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = right_self_absorption_source(eq1)
    if source is None:
        return None
    root, lead, extra, swapped = source
    root_term = ("var", root)
    rhs = eq2["rhs"]
    if eq2["lhs"] != root_term or rhs[0] != "op" or rhs[1] != ("op", root_term, root_term):
        return None
    if rhs[2][0] != "op" or rhs[2][2] != root_term:
        return None
    goal_lead = rhs[2][1]
    if goal_lead[0] != "var":
        return None
    goal_lead_name = str(goal_lead[1])
    call = call_expression_lean_args(eq1["variables"], {root: "a", lead: "b", extra: "c"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hsrc : ∀ a b c : G, a = a ◇ (b ◇ (a ◇ (a ◇ c))) := by\n"
        "    intro a b c\n"
        f"    exact {call}\n"
        f"{intro_line}"
        f"  exact ((hsrc {root} {goal_lead_name} ({root} ◇ ({root} ◇ {root}))).trans "
        f"(congrArg (fun t => {root} ◇ ({goal_lead_name} ◇ t)) ((hsrc {root} {root} {root}).symm))).trans "
        f"((congrArg (fun t => (({root} ◇ t) ◇ ({goal_lead_name} ◇ {root}))) (hsrc {root} {root} {root})).trans "
        f"(congrArg (fun t => (t ◇ ({goal_lead_name} ◇ {root}))) ((hsrc {root} {root} ({root} ◇ {root})).symm))).symm\n"
    )
    return "true:right_self_absorption", code


def repeated_right_square_source(eq1: dict[str, Any]) -> tuple[str, str] | None:
    lhs = eq1["lhs"]
    rhs = eq1["rhs"]
    if lhs[0] != "var" or rhs[0] != "op":
        return None
    root = str(lhs[1])
    left = rhs[1]
    right = rhs[2]
    if right[0] != "op" or right[1][0] != "var" or right[2][0] != "var":
        return None
    param = str(right[1][1])
    if right[2] != ("var", param):
        return None
    if left != ("op", ("op", ("var", root), ("var", param)), ("var", param)):
        return None
    if root == param or set(eq1["variables"]) != {root, param}:
        return None
    return root, param


def repeated_right_square_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = repeated_right_square_source(eq1)
    if source is None:
        return None
    root, param = source
    root_term = ("var", root)
    rhs = eq2["rhs"]
    if eq2["lhs"] != root_term or rhs[0] != "op" or rhs[2][0] != "var" or rhs[1][0] != "op":
        return None
    goal_param = str(rhs[2][1])
    if rhs[1] != ("op", ("op", root_term, ("op", ("var", goal_param), ("var", goal_param))), ("var", goal_param)):
        return None
    if root == goal_param:
        return None
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{intro_line}"
        f"  let v0 : G := {goal_param} ◇ {goal_param}\n"
        f"  let v1 : G := {root} ◇ v0\n"
        "  have p1 : "
        f"{root} = (v1 ◇ v0) ◇ (v0 ◇ v0) := h {root} v0\n"
        "  have p2 : v1 = ((v1 ◇ "
        f"{goal_param}) ◇ {goal_param}) ◇ v0 := h v1 {goal_param}\n"
        "  have p3 : (v1 ◇ v0) ◇ (v0 ◇ v0) = ((((v1 ◇ "
        f"{goal_param}) ◇ {goal_param}) ◇ v0) ◇ v0) ◇ (v0 ◇ v0) :=\n"
        "    congrArg (fun t => (t ◇ v0) ◇ (v0 ◇ v0)) p2\n"
        "  have p4 : ((((v1 ◇ "
        f"{goal_param}) ◇ {goal_param}) ◇ v0) ◇ v0) ◇ (v0 ◇ v0) = (v1 ◇ {goal_param}) ◇ {goal_param} :=\n"
        f"    (h ((v1 ◇ {goal_param}) ◇ {goal_param}) v0).symm\n"
        "  exact p1.trans (p3.trans p4)\n"
    )
    return "true:repeated_right_square", code


def self_tail_triple_source(eq1: dict[str, Any]) -> tuple[str, str] | None:
    lhs = eq1["lhs"]
    rhs = eq1["rhs"]
    if lhs[0] != "var" or rhs[0] != "op" or rhs[2] != lhs:
        return None
    root = str(lhs[1])
    mid = rhs[1]
    if mid[0] != "op" or mid[2] != lhs:
        return None
    head = mid[1]
    if head[0] != "op" or head[1][0] != "var" or head[2] != ("op", ("var", head[1][1]), lhs):
        return None
    lead = str(head[1][1])
    if root == lead or set(eq1["variables"]) != {root, lead}:
        return None
    return root, lead


def self_tail_triple_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = self_tail_triple_source(eq1)
    if source is None:
        return None
    root, _lead = source
    root_term = ("var", root)
    if eq2["lhs"] != root_term or eq2["rhs"] != ("op", ("op", root_term, root_term), root_term):
        return None
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{intro_line}"
        f"  let v2 : G := ({root} ◇ ({root} ◇ {root})) ◇ {root}\n"
        f"  have h1 : v2 ◇ {root} = {root} := (h {root} {root}).symm\n"
        f"  have p1 : v2 ◇ (v2 ◇ {root}) = {root} := (congrArg (fun t => v2 ◇ t) h1).trans h1\n"
        f"  have p2 : ((v2 ◇ (v2 ◇ {root})) ◇ {root}) ◇ {root} = (({root} ◇ {root}) ◇ {root}) :=\n"
        f"    congrArg (fun t => (t ◇ {root}) ◇ {root}) p1\n"
        f"  exact (h {root} v2).trans p2\n"
    )
    return "true:self_tail_triple", code


def nested_left_absorption_source(eq1: dict[str, Any]) -> tuple[str, str, str, bool] | None:
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        if op_side[2] != ("var", root) or op_side[1][0] != "op":
            continue
        head = op_side[1]
        if head[1][0] != "var" or head[2][0] != "op":
            continue
        lead = str(head[1][1])
        tail = head[2]
        if tail[1] != ("var", lead) or tail[2][0] != "var":
            continue
        extra = str(tail[2][1])
        if len({root, lead, extra}) != 3:
            continue
        if set(eq1["variables"]) != {root, lead, extra}:
            continue
        return root, lead, extra, swapped
    return None


def nested_left_absorption_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = nested_left_absorption_source(eq1)
    if source is None:
        return None
    root, lead, extra, swapped = source
    root_term = ("var", root)
    if eq2["lhs"] != root_term:
        return None
    rhs = eq2["rhs"]
    if rhs[0] != "op" or rhs[2] != root_term:
        return None
    tail1 = rhs[1]
    if tail1[0] != "op" or tail1[2] != root_term:
        return None
    tail2 = tail1[1]
    if tail2[0] != "op" or tail2[2] != root_term:
        return None
    tail3 = tail2[1]
    if tail3[0] != "op" or tail3[1] != root_term or tail3[2][0] != "var":
        return None
    goal_param = str(tail3[2][1])
    if goal_param == root:
        return None
    call = call_expression_lean_args(eq1["variables"], {root: "a", lead: "b", extra: "c"})
    if swapped:
        call = f"({call}).symm"
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        "  have hsrc : ∀ a b c : G, a = (b ◇ (b ◇ c)) ◇ a := by\n"
        "    intro a b c\n"
        f"    exact {call}\n"
        f"{intro_line}"
        f"  exact (hsrc {root} ({root} ◇ ({root} ◇ {goal_param})) ((({root} ◇ {goal_param}) ◇ {root}) ◇ {root})).trans "
        f"((congrArg (fun t => (t ◇ {root})) (hsrc ((({root} ◇ {goal_param}) ◇ {root}) ◇ {root}) {root} {goal_param})).trans "
        f"(congrArg (fun t => (t ◇ {root})) (hsrc (({root} ◇ ({root} ◇ {goal_param})) ◇ ((({root} ◇ {goal_param}) ◇ {root}) ◇ {root})) {root} {goal_param}))).symm\n"
    )
    return "true:nested_left_absorption", code


def narrow_grind_true_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    key = (*equation_shape_key(eq1), *equation_shape_key(eq2))
    if key not in narrow_grind_true_shape_keys():
        return None
    return "true:narrow_grind", grind_true_certificate(eq2["variables"])


def direct_substitution_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, dict[str, Term]] | None:
    for swapped in (False, True):
        source_lhs = eq1["rhs"] if swapped else eq1["lhs"]
        source_rhs = eq1["lhs"] if swapped else eq1["rhs"]
        subst: dict[str, Term] = {}
        if match_term(source_lhs, eq2["lhs"], subst) and match_term(source_rhs, eq2["rhs"], subst):
            return ("symm" if swapped else "direct"), subst
    return None


def bridge_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, dict[str, Term], dict[str, Term]] | None:
    eq1_sides = (eq1["lhs"], eq1["rhs"])
    for left_source in (0, 1):
        left_subst: dict[str, Term] = {}
        if not match_term(eq1_sides[left_source], eq2["lhs"], left_subst):
            continue
        left_other = instantiate_term_if_bound(eq1_sides[1 - left_source], left_subst)
        if left_other is None:
            continue
        for right_source in (0, 1):
            right_subst: dict[str, Term] = {}
            if not match_term(eq1_sides[right_source], eq2["rhs"], right_subst):
                continue
            right_other = instantiate_term_if_bound(eq1_sides[1 - right_source], right_subst)
            if right_other is None:
                continue
            if left_other != right_other:
                continue
            return (f"true:bridge:{left_source}{right_source}", left_subst, right_subst)
    return None


def projection_law_route(eq1: dict[str, Any]) -> str | None:
    for variable_side, op_side in ((eq1["lhs"], eq1["rhs"]), (eq1["rhs"], eq1["lhs"])):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        projected = str(variable_side[1])
        left, right = op_side[1], op_side[2]
        if right == ("var", projected) and left[0] == "var" and left[1] != projected:
            return "right"
        if left == ("var", projected) and right[0] == "var" and right[1] != projected:
            return "left"
    return None


def goal_term_pool(eq2: dict[str, Any]) -> list[Term]:
    pool: list[Term] = []
    seen: set[Term] = set()
    lhs_subterms = term_subterms_tuple(eq2["lhs"])
    rhs_subterms = term_subterms_tuple(eq2["rhs"])
    for term in (eq2["lhs"], eq2["rhs"], *lhs_subterms[1:], *rhs_subterms[1:]):
        if term not in seen:
            seen.add(term)
            pool.append(term)
    for var in eq2["variables"]:
        term = ("var", var)
        if term not in seen:
            seen.add(term)
            pool.append(term)
    return pool or [("var", "x")]


def completed_bridge_route(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    max_trials: int = 2500,
) -> tuple[str, dict[str, Term], dict[str, Term]] | None:
    eq1_sides = (eq1["lhs"], eq1["rhs"])
    pool = goal_term_pool(eq2)
    for left_source in (0, 1):
        left_subst_base: dict[str, Term] = {}
        if not match_term(eq1_sides[left_source], eq2["lhs"], left_subst_base):
            continue
        for right_source in (0, 1):
            right_subst_base: dict[str, Term] = {}
            if not match_term(eq1_sides[right_source], eq2["rhs"], right_subst_base):
                continue
            missing: list[tuple[str, str]] = []
            for var in eq1["variables"]:
                if var not in left_subst_base:
                    missing.append(("L", var))
                if var not in right_subst_base:
                    missing.append(("R", var))
            if not missing:
                continue
            trials = 0
            for fills in product(pool, repeat=len(missing)):
                trials += 1
                if trials > max_trials:
                    break
                left_subst = dict(left_subst_base)
                right_subst = dict(right_subst_base)
                for (side, var), value in zip(missing, fills):
                    if side == "L":
                        left_subst[var] = value
                    else:
                        right_subst[var] = value
                left_other = instantiate_term(eq1_sides[1 - left_source], left_subst)
                right_other = instantiate_term(eq1_sides[1 - right_source], right_subst)
                if left_other == right_other:
                    return (f"true:constancy:{left_source}{right_source}", left_subst, right_subst)
    return None


def simple_true_proof_expr(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    hypothesis_name: str = "h",
) -> tuple[str, str] | None:
    direct = direct_substitution_route(eq1, eq2)
    if direct is not None:
        mode, subst = direct
        call_expr = call_expression(eq1["variables"], subst, hypothesis_name)
        if mode == "symm":
            call_expr = f"({call_expr}).symm"
        return "true:rewrite" if mode == "direct" else "true:rewrite:symm", call_expr

    bridge = bridge_route(eq1, eq2)
    if bridge is None:
        bridge = completed_bridge_route(eq1, eq2)
    if bridge is not None:
        bridge_name, left_subst, right_subst = bridge
        left_call = call_expression(eq1["variables"], left_subst, hypothesis_name)
        right_call = call_expression(eq1["variables"], right_subst, hypothesis_name)
        left_source = int(bridge_name[-2])
        right_source = int(bridge_name[-1])
        left_to_mid = left_call if left_source == 0 else f"({left_call}).symm"
        mid_to_right = f"({right_call}).symm" if right_source == 0 else right_call
        return bridge_name, f"({left_to_mid}).trans ({mid_to_right})"

    return None


def call_expression(eq1_vars: list[str], subst: dict[str, Term], name: str = "h") -> str:
    args = [term_to_lean(subst[var]) for var in eq1_vars]
    return name if not args else name + " " + " ".join(args)


def call_expression_lean_args(eq1_vars: list[str], subst: dict[str, str], name: str = "h") -> str:
    args = [subst[var] for var in eq1_vars]
    return name if not args else name + " " + " ".join(args)


def self_square_absorption_source(eq1: dict[str, Any]) -> tuple[str, str] | None:
    lhs = eq1["lhs"]
    rhs = eq1["rhs"]
    if lhs[0] != "var" or rhs[0] != "op" or rhs[1] != rhs[2]:
        return None
    root = str(lhs[1])
    square_root = rhs[1]
    if square_root[0] != "op" or square_root[2] != ("var", root) or square_root[1][0] != "var":
        return None
    square_var = str(square_root[1][1])
    if square_var == root or set(eq1["variables"]) != {root, square_var}:
        return None
    return root, square_var


def self_square_absorption_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = self_square_absorption_source(eq1)
    if source is None:
        return None
    root, square_var = source
    if eq2["lhs"] != ("var", root):
        return None
    rhs = eq2["rhs"]
    if rhs[0] != "op" or rhs[2][0] != "op" or rhs[2][2] != ("var", root):
        return None

    target_left = rhs[1]
    target_tail = rhs[2]
    tail_left = target_tail[1]
    root_term = ("var", root)
    first_call = call_expression_lean_args(
        eq1["variables"],
        {root: term_to_lean(root_term), square_var: term_to_lean(tail_left)},
    )
    second_call = call_expression_lean_args(eq1["variables"], {root: "B", square_var: "A"})
    third_call = call_expression_lean_args(eq1["variables"], {root: "C", square_var: "C"})
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{intro_line}"
        f"  let A : G := {term_to_lean(target_left)}\n"
        f"  let B : G := {term_to_lean(target_tail)}\n"
        "  let C : G := A ◇ B\n"
        "  calc\n"
        f"    {root} = B ◇ B := {first_call}\n"
        f"    _ = (C ◇ C) ◇ (C ◇ C) := congrArg (fun t => t ◇ t) ({second_call})\n"
        f"    _ = C := ({third_call}).symm\n"
    )
    return "true:self_square_absorption", code


def repeat_tail_absorption_source(eq1: dict[str, Any]) -> tuple[str, str, str] | None:
    lhs = eq1["lhs"]
    rhs = eq1["rhs"]
    if lhs[0] != "var" or rhs[0] != "op":
        return None
    root_name = str(lhs[1])
    lead_term = rhs[1]
    tail = rhs[2]
    if lead_term[0] != "var" or tail[0] != "op":
        return None
    repeat_term = tail[1]
    repeated_tail = tail[2]
    if repeat_term[0] != "var" or repeated_tail[0] != "op":
        return None
    if repeated_tail[1] != repeat_term or repeated_tail[2] != ("var", root_name):
        return None
    lead_name = str(lead_term[1])
    repeat_name = str(repeat_term[1])
    if len({root_name, lead_name, repeat_name}) != 3:
        return None
    if set(eq1["variables"]) != {root_name, lead_name, repeat_name}:
        return None
    return root_name, lead_name, repeat_name


def repeat_tail_absorption_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    source = repeat_tail_absorption_source(eq1)
    if source is None:
        return None
    root_name, lead_name, repeat_name = source
    root_term = ("var", root_name)
    if eq2["lhs"] != root_term:
        return None
    rhs = eq2["rhs"]
    if rhs[0] != "op" or rhs[1] != ("op", root_term, root_term) or rhs[2][0] != "op" or rhs[2][1] != root_term:
        return None
    target_tail = rhs[2][2]
    if target_tail[0] != "op" or target_tail[2] != root_term:
        return None

    pivot_term = target_tail[1]
    pivot_lean = term_to_lean(pivot_term)
    root_lean = term_to_lean(root_term)
    root_square_lean = term_to_lean(("op", root_term, root_term))
    first_mid = ("op", pivot_term, ("op", pivot_term, ("op", pivot_term, root_term)))
    first_call = call_expression_lean_args(
        eq1["variables"],
        {root_name: root_lean, lead_name: pivot_lean, repeat_name: pivot_lean},
    )
    second_call = call_expression_lean_args(
        eq1["variables"],
        {root_name: term_to_lean(first_mid), lead_name: root_square_lean, repeat_name: root_lean},
    )
    third_call = call_expression_lean_args(
        eq1["variables"],
        {root_name: term_to_lean(target_tail), lead_name: root_lean, repeat_name: pivot_lean},
    )
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    context = f"(({root_lean} ◇ {root_lean}) ◇ ({root_lean} ◇ t))"
    proof_expr = f"(({first_call}).trans ({second_call})).trans (congrArg (fun t => {context}) ({third_call})).symm"
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )
    return "true:repeat_tail_absorption", code


def c9_e1072_shape_root(eq1: dict[str, Any]) -> str | None:
    lhs = eq1["lhs"]
    rhs = eq1["rhs"]
    if lhs[0] != "var" or rhs[0] != "op" or rhs[1][0] != "var":
        return None
    root = str(lhs[1])
    root_term = ("var", root)
    tail = ("op", ("op", root_term, ("op", root_term, root_term)), root_term)
    if rhs[2] != tail:
        return None
    return root


def c9_e1072_to_e19_lemma(eq1: dict[str, Any], root: str) -> str | None:
    lead = eq1["rhs"][1]
    if lead[0] != "var":
        return None
    lead_name = str(lead[1])
    if lead_name == root:
        return None
    a = ("var", "a")
    b = ("var", "b")
    c = ("var", "c")
    v0 = ("var", "v0")
    v0_tail = ("op", v0, ("op", v0, v0))
    first = call_expression(eq1["variables"], {root: a, lead_name: b})
    second = call_expression(eq1["variables"], {root: v0, lead_name: c})
    third = call_expression(eq1["variables"], {root: a, lead_name: v0_tail})
    return (
        "  have h19 : ∀ a b c : G, a = b ◇ (c ◇ a) := by\n"
        "    intro a b c\n"
        "    let v0 : G := ((a ◇ (a ◇ a)) ◇ a)\n"
        f"    exact ({first}).trans (congrArg (fun t => b ◇ t) "
        f"(({second}).trans (congrArg (fun t => c ◇ t) (({third}).symm))))\n"
    )


def c9_e1072_collapse_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    root = c9_e1072_shape_root(eq1)
    if root is None:
        return None
    lemma = c9_e1072_to_e19_lemma(eq1, root)
    if lemma is None:
        return None
    e19 = parse_equation("x = y ◇ (z ◇ x)")
    composed = simple_true_proof_expr(e19, eq2, hypothesis_name="h19")
    if composed is None:
        return None
    route, proof_expr = composed
    intro_vars = " ".join(eq2["variables"])
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    code = (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"{lemma}"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )
    return f"true:c9_e1072_collapse:{route}", code


def rewrite_steps_from_term(
    eq1: dict[str, Any],
    term: Term,
    *,
    hypothesis_name: str = "h",
) -> list[tuple[Term, str, str]]:
    steps: list[tuple[Term, str, str]] = []
    sides = (eq1["lhs"], eq1["rhs"])
    for path in subterm_paths(term):
        subterm = term_at_path(term, path)
        for source_idx in (0, 1):
            subst: dict[str, Term] = {}
            if not match_term(sides[source_idx], subterm, subst):
                continue
            replacement = instantiate_term_if_bound(sides[1 - source_idx], subst)
            if replacement is None:
                continue
            new_term = replace_subterm(term, path, replacement)
            if new_term == term:
                continue
            call = call_expression(eq1["variables"], subst, hypothesis_name)
            proof = call if source_idx == 0 else f"({call}).symm"
            if path:
                context = context_to_lean(term, path, "t")
                proof = f"congrArg (fun t => {context}) ({proof})"
            steps.append((new_term, proof, f"rewrite:{source_idx}:{len(path)}"))
    return steps


def proof_between_terms(
    eq1: dict[str, Any],
    src: Term,
    dst: Term,
    *,
    hypothesis_name: str = "h",
) -> tuple[str, str] | None:
    sides = (eq1["lhs"], eq1["rhs"])
    for source_idx in (0, 1):
        subst: dict[str, Term] = {}
        if match_term(sides[source_idx], src, subst) and match_term(sides[1 - source_idx], dst, subst):
            call = call_expression(eq1["variables"], subst, hypothesis_name)
            proof = call if source_idx == 0 else f"({call}).symm"
            return proof, f"rewrite_whole:{source_idx}"
    for new_term, proof, route in rewrite_steps_from_term(eq1, src, hypothesis_name=hypothesis_name):
        if new_term == dst:
            return proof, route
    return None


def projection_term_proof(
    eq1: dict[str, Any],
    term: Term,
    side: str,
    *,
    hypothesis_name: str = "h",
) -> tuple[str, str] | None:
    if term[0] == "var":
        return "rfl", str(term[1])
    projected = term[2] if side == "right" else term[1]
    immediate = proof_between_terms(eq1, term, projected, hypothesis_name=hypothesis_name)
    if immediate is None:
        return None
    proof_expr = immediate[0]
    rest = projection_term_proof(eq1, projected, side, hypothesis_name=hypothesis_name)
    if rest is None:
        return None
    rest_proof, target_var = rest
    if rest_proof != "rfl":
        proof_expr = f"({proof_expr}).trans ({rest_proof})"
    return proof_expr, target_var


def projection_true_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    side = projection_law_route(eq1)
    if side is None:
        return None
    left = projection_term_proof(eq1, eq2["lhs"], side)
    right = projection_term_proof(eq1, eq2["rhs"], side)
    if left is None or right is None:
        return None
    left_proof, left_target = left
    right_proof, right_target = right
    if left_target != right_target:
        return None
    if left_proof == "rfl":
        proof_expr = f"({right_proof}).symm" if right_proof != "rfl" else "rfl"
    elif right_proof == "rfl":
        proof_expr = left_proof
    else:
        proof_expr = f"({left_proof}).trans ({right_proof}).symm"
    return f"true:projection:{side}", projection_true_certificate(eq2["variables"], proof_expr)


UNIVERSAL_IDENTITY_MAX_PATTERN_VARS = 6
# Was 60000 — above the judge's own 50_000 cap, so an oversized cert would have
# been emitted and then rejected. Bounded by the shared cap instead (2026-07-29).
UNIVERSAL_IDENTITY_MAX_CODE = MAX_LEAN_CODE_BYTES


def universal_identity_source(eq1: dict[str, Any]) -> tuple[str, str, Term, bool] | None:
    """Detect a universal one-sided identity family in eq1.

    `("right", root, A, swapped)` means eq1 says `root = root ◇ A` with `root`
    absent from `A`, i.e. every element of the form `A(...)` is a right
    identity; `"left"` is the mirror. `swapped` records that the bare variable
    sits on eq1's right-hand side.
    """
    for swapped, variable_side, op_side in (
        (False, eq1["lhs"], eq1["rhs"]),
        (True, eq1["rhs"], eq1["lhs"]),
    ):
        if variable_side[0] != "var" or op_side[0] != "op":
            continue
        root = str(variable_side[1])
        left, right = op_side[1], op_side[2]
        if left == ("var", root) and root not in term_vars(right):
            return "right", root, right, swapped
        if right == ("var", root) and root not in term_vars(left):
            return "left", root, left, swapped
    return None


class UniversalIdentityCalculus:
    """Derives a projection law from a universal one-sided identity family.

    Every proof string produced here is a *group* — parenthesised, with a
    well-formed spine inside — so it can be dropped into `congrArg` or `.trans`
    argument position without re-bracketing.
    """

    def __init__(
        self,
        eq1: dict[str, Any],
        side: str,
        root: str,
        pattern: Term,
        swapped: bool,
        goal_vars: list[str],
    ) -> None:
        self.eq1 = eq1
        self.side = side
        self.root = root
        self.pattern = pattern
        self.swapped = swapped
        self.pattern_vars = sorted(term_vars(pattern))
        self.binder = next(
            (name for name in ("t", "s", "q", "tt", "ss", "zz") if name not in set(goal_vars)),
            "zz",
        )

    def hypothesis(self, carrier: Term, subst: dict[str, Term]) -> str:
        """Prove `carrier ◇ A[subst] = carrier` (right) or its mirror (left)."""
        full: dict[str, Term] = {self.root: carrier}
        full.update(subst)
        for name in self.eq1["variables"]:
            full.setdefault(name, carrier)
        call = call_expression(self.eq1["variables"], full, "h")
        return f"({call})" if self.swapped else f"(({call}).symm)"

    def _congr(self, context: str, proof: str) -> str:
        return f"(congrArg (fun {self.binder} => {context}) {proof})"

    @staticmethod
    def _symm(proof: str) -> str:
        return f"(({proof}).symm)"

    @staticmethod
    def _trans(first: str | None, second: str) -> str:
        return second if first is None else f"(({first}).trans {second})"

    def _identity_instance(self, term: Term) -> dict[str, Term] | None:
        subst: dict[str, Term] = {}
        if match_term(self.pattern, term, subst):
            return subst
        return None

    def reduce(self, term: Term) -> tuple[Term, str | None]:
        """Normalise by deleting one-sided identity factors.

        Returns the normal form and a proof that `term` equals it (`None` when
        the term is already normal).
        """
        if term[0] != "op":
            return term, None
        left, left_proof = self.reduce(term[1])
        right, right_proof = self.reduce(term[2])
        proof: str | None = None
        if left_proof is not None:
            proof = self._congr(f"{self.binder} ◇ {term_to_lean(term[2])}", left_proof)
        if right_proof is not None:
            proof = self._trans(
                proof, self._congr(f"{term_to_lean(left)} ◇ {self.binder}", right_proof))
        cut, keep = (right, left) if self.side == "right" else (left, right)
        subst = self._identity_instance(cut)
        if subst is None:
            return ("op", left, right), proof
        return keep, self._trans(proof, self.hypothesis(keep, subst))

    def projection_proof(self, left: Term, right: Term, identity: Term) -> str | None:
        """Prove `left ◇ right = left` (right family) or `= right` (left family).

        Instantiates the identity family with the surviving side and with
        `identity`, then checks the normal form is exactly that side. Every
        such instance is a one-sided identity, so the step is sound by
        construction; the offline kernel re-checks the emitted proof.
        """
        target = right if self.side == "right" else left
        for choice in product((identity, target), repeat=len(self.pattern_vars)):
            subst = dict(zip(self.pattern_vars, choice))
            normal, proof = self.reduce(instantiate_term(self.pattern, subst))
            if normal != target:
                continue
            carrier = left if self.side == "right" else right
            applied = self.hypothesis(carrier, subst)
            if proof is None:
                return applied
            if self.side == "right":
                context = f"{term_to_lean(left)} ◇ {self.binder}"
            else:
                context = f"{self.binder} ◇ {term_to_lean(right)}"
            return self._trans(self._congr(context, self._symm(proof)), applied)
        return None


def universal_identity_term_proof(
    term: Term,
    keep_left: bool,
    projection: Callable[[Term, Term], str | None],
) -> tuple[str, str] | None:
    if term[0] == "var":
        return "rfl", str(term[1])
    if term[0] != "op":
        return None
    projected = term[1] if keep_left else term[2]
    step = projection(term[1], term[2])
    if step is None:
        return None
    rest = universal_identity_term_proof(projected, keep_left, projection)
    if rest is None:
        return None
    rest_proof, target_var = rest
    if rest_proof != "rfl":
        step = f"({step}).trans ({rest_proof})"
    return step, target_var


def universal_identity_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    """Prove eq2 from a universal one-sided identity family in eq1.

    If eq1 states `x = x ◇ A(ȳ)` with `x` absent from `A`, then every `A(ȳ)` is
    a right identity. Writing `E` for `A` with all its variables set to a goal
    variable, `E` is itself such an identity, so instantiating `A`'s variables
    with `E` and with an arbitrary `b` and cancelling identity factors can
    collapse `A` to `b` alone — which upgrades the hypothesis to the left
    projection law `a ◇ b = a`. The mirror shape yields right projection.
    Under a projection law eq2 holds exactly when both sides project to the
    same variable.
    """
    source = universal_identity_source(eq1)
    if source is None:
        return None
    side, root, pattern, swapped = source
    goal_vars = list(eq2["variables"])
    if not goal_vars:
        return None
    calculus = UniversalIdentityCalculus(eq1, side, root, pattern, swapped, goal_vars)
    if len(calculus.pattern_vars) > UNIVERSAL_IDENTITY_MAX_PATTERN_VARS:
        return None
    seed: Term = ("var", goal_vars[0])
    identity = instantiate_term(pattern, {name: seed for name in calculus.pattern_vars})

    def projection(left: Term, right: Term) -> str | None:
        return calculus.projection_proof(left, right, identity)

    keep_left = side == "right"
    left = universal_identity_term_proof(eq2["lhs"], keep_left, projection)
    right = universal_identity_term_proof(eq2["rhs"], keep_left, projection)
    if left is None or right is None:
        return None
    left_proof, left_target = left
    right_proof, right_target = right
    if left_target != right_target:
        return None
    if left_proof == "rfl":
        proof_expr = f"({right_proof}).symm" if right_proof != "rfl" else "rfl"
    elif right_proof == "rfl":
        proof_expr = left_proof
    else:
        proof_expr = f"({left_proof}).trans ({right_proof}).symm"
    code = projection_true_certificate(goal_vars, proof_expr)
    if len(code) > UNIVERSAL_IDENTITY_MAX_CODE:
        return None
    law = "left" if keep_left else "right"
    return f"true:universal_identity:{law}", code


def find_rewrite_chain(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    max_depth: int = REWRITE_CHAIN_MAX_DEPTH,
    hypothesis_name: str = "h",
    deadline: float | None = None,
    frontier_limit: int | None = None,
) -> tuple[list[str], str] | None:
    """Breadth-first rewrite search from eq2.lhs to eq2.rhs.

    `deadline` / `frontier_limit` default to None, which reproduces the
    original unbounded behaviour for the shallow callers (depth 2-3). They
    exist for the guided-chain path, which runs at depth 8+: on a
    size-increasing eq1 every level both multiplies the frontier and grows
    the terms, so an unbounded search there can allocate tens of GB before
    any wall-clock check would have fired.
    """
    target = eq2["rhs"]
    queue: list[tuple[Term, list[str], list[str]]] = [(eq2["lhs"], [], [])]
    seen: set[Term] = {eq2["lhs"]}
    for _depth in range(max_depth):
        next_queue: list[tuple[Term, list[str], list[str]]] = []
        for term, proofs, routes in queue:
            # Bounded work per check: rewrite_steps_from_term is finite in the
            # size of `term`, so polling once per frontier node is enough.
            if deadline_expired(deadline):
                return None
            for new_term, proof, route in rewrite_steps_from_term(
                    eq1, term, hypothesis_name=hypothesis_name):
                if new_term in seen:
                    continue
                new_proofs = proofs + [proof]
                new_routes = routes + [route]
                if new_term == target:
                    expr = new_proofs[0]
                    for later in new_proofs[1:]:
                        expr = f"({expr}).trans ({later})"
                    return new_routes, expr
                seen.add(new_term)
                next_queue.append((new_term, new_proofs, new_routes))
            if frontier_limit is not None and len(next_queue) >= frontier_limit:
                break
        queue = next_queue
    return None


def proof_between_terms_guided(
    eq1: dict[str, Any],
    variables: list[str],
    src: Term,
    dst: Term,
    *,
    max_depth: int = GUIDED_CHAIN_MAX_DEPTH,
    closure_time_budget: float | None = GUIDED_CHAIN_CLOSURE_TIME_BUDGET,
) -> tuple[str, str] | None:
    if src == dst:
        return "rfl", "guided:rfl"

    direct = proof_between_terms(eq1, src, dst)
    if direct is not None:
        proof, route = direct
        return proof, route

    edge_eq = {"lhs": src, "rhs": dst, "variables": variables}
    chain = find_rewrite_chain(
        eq1,
        edge_eq,
        max_depth=max_depth,
        deadline=local_deadline(closure_time_budget),
        frontier_limit=GUIDED_CHAIN_FRONTIER_LIMIT,
    )
    if chain is not None:
        routes, proof_expr = chain
        return proof_expr, "guided:rewrite_chain:" + ",".join(routes)

    closure = _closure_proof_expr_impl(
        eq1,
        edge_eq,
        route_name="guided:equational_closure",
        chain_max_depth=2,
        pool_limit=12,
        frontier_limit=180,
        max_fills=80,
        term_slack=6,
        depth_slack=2,
        time_budget=closure_time_budget,
    )
    if closure is not None:
        route, proof_expr = closure
        return proof_expr, route
    return None


def absorption_hypothesis(eq1: dict[str, Any]) -> bool:
    lhs = eq1["lhs"]
    rhs = eq1["rhs"]
    if lhs[0] == "var" and lhs[1] in term_vars(rhs):
        return True
    if rhs[0] == "var" and rhs[1] in term_vars(lhs):
        return True
    return False


def absorption_term_pool(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    pool_limit: int = ABSORPTION_POOL_LIMIT,
) -> list[Term]:
    allowed_vars = set(eq2["variables"])
    seen: set[Term] = set()
    pool: list[Term] = []

    def add(term: Term) -> None:
        if term in seen or not term_vars(term).issubset(allowed_vars):
            return
        seen.add(term)
        pool.append(term)

    for var in eq2["variables"]:
        add(("var", var))
    eq2_lhs_subterms = term_subterms_tuple(eq2["lhs"])
    eq2_rhs_subterms = term_subterms_tuple(eq2["rhs"])
    for term in (eq2["lhs"], eq2["rhs"], *eq2_lhs_subterms[1:], *eq2_rhs_subterms[1:]):
        add(term)
    eq1_lhs_subterms = term_subterms_tuple(eq1["lhs"])
    eq1_rhs_subterms = term_subterms_tuple(eq1["rhs"])
    for term in (eq1["lhs"], eq1["rhs"], *eq1_lhs_subterms[1:], *eq1_rhs_subterms[1:]):
        add(term)

    small = list(pool)
    for left in small:
        for right in small:
            candidate = ("op", left, right)
            if term_size(candidate) <= 7 and term_depth(candidate) <= 3:
                add(candidate)

    pool.sort(key=lambda term: (term_size(term), term_depth(term), term_to_lean(term)))
    return pool[:pool_limit]


def absorption_context_bridge_pool(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    pool_limit: int = ABSORPTION_CONTEXT_BRIDGE_POOL_LIMIT,
    seed_limit: int = ABSORPTION_CONTEXT_BRIDGE_SEED_LIMIT,
) -> list[Term]:
    pool = absorption_term_pool(eq1, eq2, pool_limit=pool_limit)
    if not pool:
        return []
    allowed_vars = set(eq2["variables"])
    seen: set[Term] = set(pool)
    frontier = list(pool[:seed_limit])
    for left in frontier:
        for right in frontier:
            candidate = ("op", left, right)
            if candidate in seen or not term_vars(candidate).issubset(allowed_vars):
                continue
            if term_size(candidate) <= 7 and term_depth(candidate) <= 3:
                seen.add(candidate)
    extended = sorted(seen, key=lambda term: (term_size(term), term_depth(term), term_to_lean(term)))
    return extended[:pool_limit]


MEMORY_CAP_MB_DEFAULT = 1600.0
_MEM_CHECK_EVERY = 4096
_mem_check_counter = 0
_mem_exceeded = False
_MEMORY_GUARD_ARMED = False


def arm_memory_guard(armed: bool = True) -> None:
    global _MEMORY_GUARD_ARMED, _mem_exceeded
    _MEMORY_GUARD_ARMED = armed
    _mem_exceeded = False


def _memory_cap_bytes() -> float:
    try:
        cap_mb = float(os.environ.get("MAGMA_MEMORY_CAP_MB", MEMORY_CAP_MB_DEFAULT))
    except ValueError:
        cap_mb = MEMORY_CAP_MB_DEFAULT
    return cap_mb * 1024 * 1024


def _process_rss_bytes() -> int | None:
    try:
        with open("/proc/self/statm", "rb") as statm:
            fields = statm.read().split()
        return int(fields[1]) * (os.sysconf("SC_PAGESIZE") if hasattr(os, "sysconf") else 4096)
    except (OSError, ValueError, IndexError):
        pass
    try:
        import ctypes

        class _PMC(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_uint32), ("PageFaultCount", ctypes.c_uint32),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        pmc = _PMC()
        pmc.cb = ctypes.sizeof(_PMC)
        kernel32 = ctypes.windll.kernel32
        get_info = getattr(kernel32, "K32GetProcessMemoryInfo", None)
        if get_info is None:
            get_info = ctypes.windll.psapi.GetProcessMemoryInfo
        # GetCurrentProcess() through ctypes truncates the pseudo-handle on
        # 64-bit Python; pass it with pointer width explicitly.
        current_process = ctypes.c_void_p(-1)
        if get_info(current_process, ctypes.byref(pmc), pmc.cb):
            return int(pmc.WorkingSetSize)
    except Exception:  # noqa: BLE001 - the guard must never crash the solver
        pass
    return None


def memory_exceeded() -> bool:
    """Throttled RSS check. Sticky within a throttle window only."""
    global _mem_check_counter, _mem_exceeded
    if not _MEMORY_GUARD_ARMED:
        return False
    _mem_check_counter += 1
    if _mem_check_counter % _MEM_CHECK_EVERY:
        return _mem_exceeded
    rss = _process_rss_bytes()
    _mem_exceeded = rss is not None and rss > _memory_cap_bytes()
    return _mem_exceeded


_mem_reclaims_left = 3


def try_reclaim_memory() -> bool:
    """Free term caches after a memory trip so later (cheaper) engines can
    still run. Returns True when the process is back under the cap."""
    global _mem_check_counter, _mem_exceeded, _mem_reclaims_left
    if not _MEMORY_GUARD_ARMED or not _mem_exceeded:
        return not _mem_exceeded
    if _mem_reclaims_left <= 0:
        return False
    _mem_reclaims_left -= 1
    clear_term_caches()
    import gc

    gc.collect()
    _mem_check_counter = -1
    return not memory_exceeded()


def deadline_expired(deadline: float | None) -> bool:
    if memory_exceeded():
        return True
    return deadline is not None and time.monotonic() >= deadline


def filled_absorption_steps(
    eq1: dict[str, Any],
    term: Term,
    pool: list[Term],
    *,
    max_size: int,
    max_depth: int,
    max_fills: int = ABSORPTION_MAX_FILLS,
    deadline: float | None = None,
    fill_pool: list[Term] | None = None,
) -> list[tuple[Term, str, str]]:
    if not pool:
        return []

    steps: list[tuple[Term, str, str]] = []
    seen_terms: set[Term] = set()
    sides = (eq1["lhs"], eq1["rhs"])
    default_term = pool[0]

    for path in subterm_paths(term):
        if deadline_expired(deadline):
            return steps
        subterm = term_at_path(term, path)
        for source_idx in (0, 1):
            if deadline_expired(deadline):
                return steps
            subst: dict[str, Term] = {}
            if not match_term(sides[source_idx], subterm, subst):
                continue

            replacement_pattern = sides[1 - source_idx]
            replacement_vars = term_vars(replacement_pattern)
            needed = [var for var in eq1["variables"] if var not in subst and var in replacement_vars]
            if len(needed) > 3:
                continue

            fill_count = 0
            # Multi-variable fills explode combinatorially; concentrate them on
            # the prioritized fill_pool when the caller provides one.
            fills_source = fill_pool if (fill_pool is not None and len(needed) > 1) else pool
            fill_iter = product(fills_source, repeat=len(needed)) if needed else ((),)
            for fills in fill_iter:
                if deadline_expired(deadline):
                    return steps
                fill_count += 1
                if fill_count > max_fills:
                    break

                subst_full = dict(subst)
                for var, value in zip(needed, fills):
                    subst_full[var] = value
                for var in eq1["variables"]:
                    if var not in subst_full:
                        subst_full[var] = default_term

                replacement = instantiate_term(replacement_pattern, subst_full)
                new_term = replace_subterm(term, path, replacement)
                if new_term == term or new_term in seen_terms:
                    continue
                if term_size(new_term) > max_size or term_depth(new_term) > max_depth:
                    continue

                call = call_expression(eq1["variables"], subst_full)
                proof = call if source_idx == 0 else f"({call}).symm"
                if path:
                    context = context_to_lean(term, path, "t")
                    proof = f"congrArg (fun t => {context}) ({proof})"
                seen_terms.add(new_term)
                steps.append((new_term, proof, f"absorb:{source_idx}:{len(path)}:{len(needed)}"))

    steps.sort(key=lambda item: (term_size(item[0]), term_depth(item[0]), item[2], term_to_lean(item[0])))
    return steps


def chain_trans(prefix: str | None, proof: str) -> str:
    if prefix is None:
        return proof
    return f"({prefix}).trans ({proof})"


def combine_meeting_proofs(left_proof: str | None, right_proof: str | None) -> str:
    if left_proof is None and right_proof is None:
        return "rfl"
    if left_proof is None:
        return f"({right_proof}).symm"
    if right_proof is None:
        return left_proof
    return f"({left_proof}).trans ({right_proof}).symm"


def absorption_context_bridge_route(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    route_name: str = "true:absorption_context_bridge",
    pool_limit: int = ABSORPTION_CONTEXT_BRIDGE_POOL_LIMIT,
    seed_limit: int = ABSORPTION_CONTEXT_BRIDGE_SEED_LIMIT,
    max_fills: int = ABSORPTION_CONTEXT_BRIDGE_MAX_FILLS,
    term_slack: int = ABSORPTION_CONTEXT_BRIDGE_TERM_SLACK,
    depth_slack: int = ABSORPTION_CONTEXT_BRIDGE_DEPTH_SLACK,
    time_budget: float | None = None,
    max_goal_vars: int = 2,
) -> tuple[str, str] | None:
    if not absorption_hypothesis(eq1) or len(eq2["variables"]) > max_goal_vars:
        return None
    if time_budget is None:
        time_budget = ABSORPTION_CONTEXT_BRIDGE_TIME_BUDGET
    pool = absorption_context_bridge_pool(eq1, eq2, pool_limit=pool_limit, seed_limit=seed_limit)
    if not pool:
        return None
    deadline = local_deadline(time_budget)
    max_size = max(
        term_size(eq1["lhs"]),
        term_size(eq1["rhs"]),
        term_size(eq2["lhs"]),
        term_size(eq2["rhs"]),
    ) + term_slack
    max_depth = max(
        term_depth(eq1["lhs"]),
        term_depth(eq1["rhs"]),
        term_depth(eq2["lhs"]),
        term_depth(eq2["rhs"]),
    ) + depth_slack
    left_steps = filled_absorption_steps(
        eq1,
        eq2["lhs"],
        pool,
        max_size=max_size,
        max_depth=max_depth,
        max_fills=max_fills,
        deadline=deadline,
    )
    if deadline_expired(deadline):
        return None
    right_steps = filled_absorption_steps(
        eq1,
        eq2["rhs"],
        pool,
        max_size=max_size,
        max_depth=max_depth,
        max_fills=max_fills,
        deadline=deadline,
    )
    if deadline_expired(deadline):
        return None

    left_seen: dict[Term, str] = {}
    for term, proof, _route in left_steps:
        left_seen.setdefault(term, proof)
    right_seen: dict[Term, str] = {}
    for term, proof, _route in right_steps:
        right_seen.setdefault(term, proof)

    common = sorted(
        set(left_seen).intersection(right_seen),
        key=lambda term: (term_size(term), term_depth(term), term_to_lean(term)),
    )
    if not common:
        return None
    proof_expr = combine_meeting_proofs(left_seen[common[0]], right_seen[common[0]])
    return route_name, substitution_true_certificate(eq2["variables"], proof_expr)


def _closure_proof_expr_impl(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    route_name: str,
    chain_max_depth: int,
    pool_limit: int,
    frontier_limit: int,
    max_fills: int,
    term_slack: int,
    depth_slack: int,
    time_budget: float | None,
    seed_terms: list[Term] | None = None,
) -> tuple[str, str] | None:
    if time_budget:
        time_budget = _eff_time(time_budget)
    frontier_limit = _eff_frontier(frontier_limit)
    max_fills = _eff_fills(max_fills)
    pool_limit = _eff_pool(pool_limit)

    deadline = local_deadline(time_budget)
    pool = absorption_term_pool(eq1, eq2, pool_limit=pool_limit)
    fill_pool: list[Term] | None = None
    if seed_terms:
        allowed_vars = set(eq2["variables"])
        seed_extra: list[Term] = []
        seed_seen: set[Term] = set()
        for seed in seed_terms:
            for term in term_subterms_tuple(seed):
                if term in seed_seen or not term_vars(term).issubset(allowed_vars):
                    continue
                seed_seen.add(term)
                seed_extra.append(term)
        seed_extra.sort(key=lambda term: (term_size(term), term_depth(term), term_to_lean(term)))
        seed_extra = seed_extra[:LLM_SEEDED_CLOSURE_MAX_SEEDS]
        # Order matters: fills iterate the pool front-first, so put variables,
        # then the LLM-proposed terms, ahead of the generic base pool.
        var_terms = [term for term in pool if term[0] == "var"]
        rest = [term for term in pool if term[0] != "var" and term not in seed_seen]
        pool = var_terms + [term for term in seed_extra if term[0] != "var"] + rest
        fill_pool = pool[:LLM_SEEDED_CLOSURE_FILL_POOL_CAP]
    if not pool:
        return None

    size_basis = [
        term_size(eq1["lhs"]),
        term_size(eq1["rhs"]),
        term_size(eq2["lhs"]),
        term_size(eq2["rhs"]),
    ]
    depth_basis = [
        term_depth(eq1["lhs"]),
        term_depth(eq1["rhs"]),
        term_depth(eq2["lhs"]),
        term_depth(eq2["rhs"]),
    ]
    if seed_terms:
        size_basis.extend(term_size(term) for term in seed_terms)
        depth_basis.extend(term_depth(term) for term in seed_terms)
    max_size = max(size_basis) + term_slack
    max_depth = max(depth_basis) + depth_slack

    left_start = eq2["lhs"]
    right_start = eq2["rhs"]
    left_seen: dict[Term, str | None] = {left_start: None}
    right_seen: dict[Term, str | None] = {right_start: None}
    left_frontier = [left_start]
    right_frontier = [right_start]

    def expand_frontier(
        frontier: list[Term],
        seen: dict[Term, str | None],
        other_seen: dict[Term, str | None],
        *,
        from_left: bool,
    ) -> tuple[list[Term], tuple[str, str] | None, bool]:
        next_frontier: list[Term] = []
        for term in frontier:
            if deadline_expired(deadline):
                return next_frontier, None, True
            prefix = seen[term]
            for new_term, proof, _route in filled_absorption_steps(
                eq1,
                term,
                pool,
                max_size=max_size,
                max_depth=max_depth,
                max_fills=max_fills,
                deadline=deadline,
                fill_pool=fill_pool,
            ):
                if deadline_expired(deadline):
                    return next_frontier, None, True
                if new_term in seen:
                    continue
                new_proof = chain_trans(prefix, proof)
                if new_term in other_seen:
                    if from_left:
                        proof_expr = combine_meeting_proofs(new_proof, other_seen[new_term])
                    else:
                        proof_expr = combine_meeting_proofs(other_seen[new_term], new_proof)
                    return next_frontier, (route_name, proof_expr), False
                seen[new_term] = new_proof
                next_frontier.append(new_term)
                if len(seen) >= frontier_limit:
                    break
            if len(seen) >= frontier_limit:
                break
        return next_frontier[:frontier_limit], None, False

    for _depth in range(chain_max_depth):
        if deadline_expired(deadline):
            return None
        left_frontier, result, timed_out = expand_frontier(left_frontier, left_seen, right_seen, from_left=True)
        if timed_out:
            return None
        if result is not None:
            return result

        right_frontier, result, timed_out = expand_frontier(right_frontier, right_seen, left_seen, from_left=False)
        if timed_out:
            return None
        if result is not None:
            return result

        if not left_frontier and not right_frontier:
            break

    return None


def _closure_route_impl(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    route_name: str,
    chain_max_depth: int,
    pool_limit: int,
    frontier_limit: int,
    max_fills: int,
    term_slack: int,
    depth_slack: int,
    time_budget: float | None,
) -> tuple[str, str] | None:
    result = _closure_proof_expr_impl(
        eq1,
        eq2,
        route_name=route_name,
        chain_max_depth=chain_max_depth,
        pool_limit=pool_limit,
        frontier_limit=frontier_limit,
        max_fills=max_fills,
        term_slack=term_slack,
        depth_slack=depth_slack,
        time_budget=time_budget,
    )
    if result is None:
        return None
    route, proof_expr = result
    return route, substitution_true_certificate(eq2["variables"], proof_expr)


def absorption_closure_route(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    route_name: str = "true:absorption_closure",
    chain_max_depth: int = ABSORPTION_CHAIN_MAX_DEPTH,
    pool_limit: int = ABSORPTION_POOL_LIMIT,
    frontier_limit: int = ABSORPTION_FRONTIER_LIMIT,
    max_fills: int = ABSORPTION_MAX_FILLS,
    term_slack: int = ABSORPTION_TERM_SLACK,
    time_budget: float | None = ABSORPTION_TIME_BUDGET,
) -> tuple[str, str] | None:
    if not absorption_hypothesis(eq1):
        return None
    return _closure_route_impl(
        eq1,
        eq2,
        route_name=route_name,
        chain_max_depth=chain_max_depth,
        pool_limit=pool_limit,
        frontier_limit=frontier_limit,
        max_fills=max_fills,
        term_slack=term_slack,
        depth_slack=2,
        time_budget=time_budget,
    )


def deep_absorption_closure_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    return absorption_closure_route(
        eq1,
        eq2,
        route_name="true:absorption_closure:deep",
        chain_max_depth=ABSORPTION_DEEP_CHAIN_MAX_DEPTH,
        pool_limit=ABSORPTION_DEEP_POOL_LIMIT,
        frontier_limit=ABSORPTION_DEEP_FRONTIER_LIMIT,
        max_fills=ABSORPTION_DEEP_MAX_FILLS,
        term_slack=ABSORPTION_DEEP_TERM_SLACK,
        time_budget=ABSORPTION_DEEP_TIME_BUDGET,
    )


def equational_closure_route(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    route_name: str = "true:equational_closure",
    chain_max_depth: int = EQUATIONAL_CLOSURE_CHAIN_MAX_DEPTH,
    pool_limit: int = EQUATIONAL_CLOSURE_POOL_LIMIT,
    frontier_limit: int = EQUATIONAL_CLOSURE_FRONTIER_LIMIT,
    max_fills: int = EQUATIONAL_CLOSURE_MAX_FILLS,
    term_slack: int = EQUATIONAL_CLOSURE_TERM_SLACK,
    depth_slack: int = EQUATIONAL_CLOSURE_DEPTH_SLACK,
    time_budget: float | None = EQUATIONAL_CLOSURE_TIME_BUDGET,
) -> tuple[str, str] | None:
    if eq2["lhs"] == eq2["rhs"]:
        return route_name, substitution_true_certificate(eq2["variables"], "rfl")
    return _closure_route_impl(
        eq1,
        eq2,
        route_name=route_name,
        chain_max_depth=chain_max_depth,
        pool_limit=pool_limit,
        frontier_limit=frontier_limit,
        max_fills=max_fills,
        term_slack=term_slack,
        depth_slack=depth_slack,
        time_budget=time_budget,
    )


# --------------------------------------------------------------------------
# Derived critical-pair rules (Knuth-Bendix-lite).
#
# Critical pairs of the hypothesis with itself package two exact hypothesis
# instantiations into one reusable rewrite rule, each carrying a constructive
# Lean proof expression. The bidirectional closure over {base rule} + derived
# rules reaches derivations the base closure cannot at the same depth.
# --------------------------------------------------------------------------

def _kb_walk(term: Term, subst: dict[str, Term]) -> Term:
    while term[0] == "var" and term[1] in subst:
        term = subst[term[1]]
    return term


def _kb_occurs(name: str, term: Term, subst: dict[str, Term]) -> bool:
    term = _kb_walk(term, subst)
    if term[0] == "var":
        return term[1] == name
    return _kb_occurs(name, term[1], subst) or _kb_occurs(name, term[2], subst)


def _kb_unify(a: Term, b: Term, subst: dict[str, Term]) -> dict[str, Term] | None:
    a = _kb_walk(a, subst)
    b = _kb_walk(b, subst)
    if a == b:
        return subst
    if a[0] == "var":
        if _kb_occurs(a[1], b, subst):
            return None
        out = dict(subst)
        out[a[1]] = b
        return out
    if b[0] == "var":
        if _kb_occurs(b[1], a, subst):
            return None
        out = dict(subst)
        out[b[1]] = a
        return out
    out = _kb_unify(a[1], b[1], subst)
    if out is None:
        return None
    return _kb_unify(a[2], b[2], out)


def _kb_resolve(term: Term, subst: dict[str, Term]) -> Term:
    term = _kb_walk(term, subst)
    if term[0] == "var":
        return term
    return ("op", _kb_resolve(term[1], subst), _kb_resolve(term[2], subst))


def _kb_rename(term: Term, suffix: str) -> Term:
    if term[0] == "var":
        return ("var", term[1] + suffix)
    return ("op", _kb_rename(term[1], suffix), _kb_rename(term[2], suffix))


def _kb_nonvar_paths(term: Term, prefix: tuple[int, ...] = ()) -> list[tuple[int, ...]]:
    if term[0] != "op":
        return []
    out = [prefix]
    out.extend(_kb_nonvar_paths(term[1], prefix + (0,)))
    out.extend(_kb_nonvar_paths(term[2], prefix + (1,)))
    return out


class DerivedRule:
    __slots__ = ("lhs", "rhs", "vars", "proof_only_vars", "builder", "label")

    def __init__(self, lhs: Term, rhs: Term, builder: Any, label: str,
                 extra_vars: set[str] | None = None):
        self.lhs = lhs
        self.rhs = rhs
        pattern_vars = term_vars(lhs) | term_vars(rhs)
        # Vars only in the proof templates: any value is sound (the hypothesis
        # instance proves the pattern equation for every value), so they take a
        # default fill and never join the fill product.
        self.proof_only_vars = sorted((extra_vars or set()) - pattern_vars)
        self.vars = sorted(pattern_vars)
        self.builder = builder
        self.label = label


def _derived_base_rules(eq1: dict[str, Any], hyp_name: str = "h") -> list[DerivedRule]:
    ev = list(eq1["variables"])

    def fwd(subst: dict[str, Term]) -> str:
        return call_expression(ev, subst, hyp_name)

    def bwd(subst: dict[str, Term]) -> str:
        return f"({call_expression(ev, subst, hyp_name)}).symm"

    return [
        DerivedRule(eq1["lhs"], eq1["rhs"], fwd, "base_fwd"),
        DerivedRule(eq1["rhs"], eq1["lhs"], bwd, "base_bwd"),
    ]


def _canonicalize_derived_rule(lhs: Term, rhs: Term) -> tuple[Term, Term, dict[str, str]]:
    mapping: dict[str, str] = {}

    def canon(term: Term) -> Term:
        if term[0] == "var":
            if term[1] not in mapping:
                mapping[term[1]] = f"v{len(mapping)}"
            return ("var", mapping[term[1]])
        return ("op", canon(term[1]), canon(term[2]))

    return canon(lhs), canon(rhs), mapping


_DERIVED_RULES_CACHE: dict[tuple[Term, Term], list[DerivedRule]] = {}


def critical_pair_rules(
    eq1: dict[str, Any],
    *,
    max_rule_size: int = DERIVED_CP_MAX_RULE_SIZE,
    max_rules: int = DERIVED_CP_MAX_RULES,
    hyp_name: str = "h",
) -> list[DerivedRule]:
    cache_key = (eq1["lhs"], eq1["rhs"], hyp_name)
    cached = _DERIVED_RULES_CACHE.get(cache_key)
    if cached is not None:
        return cached
    ev = list(eq1["variables"])
    L1 = _kb_rename(eq1["lhs"], "@1")
    R1 = _kb_rename(eq1["rhs"], "@1")
    L2 = _kb_rename(eq1["lhs"], "@2")
    R2 = _kb_rename(eq1["rhs"], "@2")

    rules: list[DerivedRule] = []
    seen: set[tuple[Term, Term]] = set()

    for s1, t1, s1_is_L in ((L1, R1, True), (R1, L1, False)):
        for s2, t2, s2_is_L in ((L2, R2, True), (R2, L2, False)):
            for p in _kb_nonvar_paths(s2):
                sub = term_at_path(s2, p)
                sigma = _kb_unify(s1, sub, {})
                if sigma is None:
                    continue
                new_lhs = _kb_resolve(t2, sigma)
                inner_repl = _kb_resolve(t1, sigma)
                expanded = _kb_resolve(s2, sigma)
                new_rhs = replace_subterm(expanded, p, inner_repl)
                if new_lhs == new_rhs:
                    continue
                if max(term_size(new_lhs), term_size(new_rhs)) > max_rule_size:
                    continue
                canon_l, canon_r, mapping = _canonicalize_derived_rule(new_lhs, new_rhs)
                if (canon_l, canon_r) in seen:
                    continue
                seen.add((canon_l, canon_r))

                def remap(term: Term) -> Term:
                    # Extend the mapping for vars that vanished from the rule
                    # patterns but survive in the instantiation templates.
                    if term[0] == "var":
                        if term[1] not in mapping:
                            mapping[term[1]] = f"v{len(mapping)}"
                        return ("var", mapping[term[1]])
                    return ("op", remap(term[1]), remap(term[2]))

                tau2 = {v: remap(_kb_resolve(("var", v + "@2"), sigma)) for v in ev}
                tau1 = {v: remap(_kb_resolve(("var", v + "@1"), sigma)) for v in ev}
                expanded_pat = remap(expanded)

                def make_builder(tau1=tau1, tau2=tau2, expanded_pat=expanded_pat,
                                 p=p, s1_is_L=s1_is_L, s2_is_L=s2_is_L, ev=ev,
                                 hyp_name=hyp_name):
                    def build(subst: dict[str, Term]) -> str:
                        c2 = {v: instantiate_term(t, subst) for v, t in tau2.items()}
                        c1 = {v: instantiate_term(t, subst) for v, t in tau1.items()}
                        whole = instantiate_term(expanded_pat, subst)
                        call2 = call_expression(ev, c2, hyp_name)
                        step1 = f"({call2}).symm" if s2_is_L else call2
                        call1 = call_expression(ev, c1, hyp_name)
                        inner = call1 if s1_is_L else f"({call1}).symm"
                        if p:
                            ctx = context_to_lean(whole, p, "t")
                            step2 = f"congrArg (fun t => {ctx}) ({inner})"
                        else:
                            step2 = inner
                        return f"({step1}).trans ({step2})"
                    return build

                label = f"cp:{'L' if s1_is_L else 'R'}{'L' if s2_is_L else 'R'}:{'.'.join(map(str, p)) or 'root'}"
                all_vars: set[str] = set()
                for t in list(tau1.values()) + list(tau2.values()):
                    all_vars |= term_vars(t)
                fwd_rule = DerivedRule(canon_l, canon_r, make_builder(), label, extra_vars=all_vars)
                rules.append(fwd_rule)

                def make_rev(fwd_rule=fwd_rule):
                    def build(subst: dict[str, Term]) -> str:
                        return f"({fwd_rule.builder(subst)}).symm"
                    return build

                rules.append(DerivedRule(canon_r, canon_l, make_rev(), label + ":rev", extra_vars=all_vars))

    rules.sort(key=lambda r: (term_size(r.lhs) + term_size(r.rhs), r.label))
    rules = rules[:max_rules]
    _DERIVED_RULES_CACHE[cache_key] = rules
    if len(_DERIVED_RULES_CACHE) > 64:
        _DERIVED_RULES_CACHE.clear()
    return rules


def derived_rule_steps(
    rules: list[DerivedRule],
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
    for path in subterm_paths(term):
        if deadline_expired(deadline):
            break
        sub = term_at_path(term, path)
        for rule in rules:
            subst: dict[str, Term] = {}
            if not match_term(rule.lhs, sub, subst):
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
                replacement = instantiate_term(rule.rhs, full)
                new_term = replace_subterm(term, path, replacement)
                if new_term == term or new_term in seen:
                    continue
                if term_size(new_term) > max_size or term_depth(new_term) > max_depth:
                    continue
                proof = rule.builder(full)
                if path:
                    ctx = context_to_lean(term, path, "t")
                    proof = f"congrArg (fun t => {ctx}) ({proof})"
                seen.add(new_term)
                steps.append((new_term, proof))
    steps.sort(key=lambda item: (term_size(item[0]), term_depth(item[0])))
    return steps


def derived_cp_closure_proof_expr(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    chain_max_depth: int = DERIVED_CP_CHAIN_MAX_DEPTH,
    pool_limit: int = DERIVED_CP_POOL_LIMIT,
    fill_pool_cap: int = DERIVED_CP_FILL_POOL_CAP,
    frontier_limit: int = DERIVED_CP_FRONTIER_LIMIT,
    max_fills: int = DERIVED_CP_MAX_FILLS,
    term_slack: int = DERIVED_CP_TERM_SLACK,
    depth_slack: int = DERIVED_CP_DEPTH_SLACK,
    time_budget: float = DERIVED_CP_TIME_BUDGET,
    max_rules: int = DERIVED_CP_MAX_RULES,
    extra_rules: list[DerivedRule] | None = None,
) -> str | None:
    time_budget = _eff_time(time_budget)
    frontier_limit = _eff_frontier(frontier_limit)
    max_fills = _eff_fills(max_fills)
    pool_limit = _eff_pool(pool_limit)
    chain_max_depth = _eff_depth(chain_max_depth)

    deadline = local_deadline(time_budget)
    rules = (_derived_base_rules(eq1) + list(extra_rules or [])
             + critical_pair_rules(eq1, max_rules=max_rules))
    pool = absorption_term_pool(eq1, eq2, pool_limit=pool_limit)
    if not pool:
        return None
    fill_pool = pool[:fill_pool_cap]

    max_size = max(term_size(eq1["lhs"]), term_size(eq1["rhs"]),
                   term_size(eq2["lhs"]), term_size(eq2["rhs"])) + term_slack
    max_depth_t = max(term_depth(eq1["lhs"]), term_depth(eq1["rhs"]),
                      term_depth(eq2["lhs"]), term_depth(eq2["rhs"])) + depth_slack

    left_seen: dict[Term, str | None] = {eq2["lhs"]: None}
    right_seen: dict[Term, str | None] = {eq2["rhs"]: None}
    left_frontier = [eq2["lhs"]]
    right_frontier = [eq2["rhs"]]

    def expand(frontier: list[Term], seen: dict[Term, str | None],
               other: dict[Term, str | None], from_left: bool):
        nxt: list[Term] = []
        for term in frontier:
            if deadline_expired(deadline):
                return nxt, None, True
            prefix = seen[term]
            for new_term, proof in derived_rule_steps(
                rules, term, pool, fill_pool,
                max_size=max_size, max_depth=max_depth_t,
                max_fills=max_fills, deadline=deadline,
            ):
                if new_term in seen:
                    continue
                new_proof = chain_trans(prefix, proof)
                if new_term in other:
                    if from_left:
                        return nxt, combine_meeting_proofs(new_proof, other[new_term]), False
                    return nxt, combine_meeting_proofs(other[new_term], new_proof), False
                seen[new_term] = new_proof
                nxt.append(new_term)
                if len(seen) >= frontier_limit:
                    break
            if len(seen) >= frontier_limit:
                break
        return nxt[:frontier_limit], None, False

    for _ in range(chain_max_depth):
        if deadline_expired(deadline):
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


def derived_cp_closure_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    proof_expr = derived_cp_closure_proof_expr(eq1, eq2)
    if proof_expr is None:
        return None
    return "true:derived_cp_closure", substitution_true_certificate(eq2["variables"], proof_expr)


PROJECTION_LEMMA_TEXT = {"left": "a ◇ b = a", "right": "a ◇ b = b"}

# Small laws worth trying as proof targets in their own right. A lemma earns a
# place here only by winning rows: it has to be derivable from real hypotheses
# *and* strong enough to close real goals. Order is cheapest-and-strongest
# first, since the first one that works wins.
LEMMA_LIBRARY_TEXT = (
    ("trivial", "a = b"),
    ("idempotent", "a ◇ a = a"),
    ("left_row_constant", "a ◇ b = a ◇ c"),
    ("right_col_constant", "a ◇ b = c ◇ b"),
    ("product_constant", "a ◇ b = c ◇ d"),
    ("commutative", "a ◇ b = b ◇ a"),
)

LEMMA_APPLY_CHAIN_MAX_DEPTH = 3

# Budget per lemma search, by how much a hit is worth paying for. The two
# projection lemmas keep the full budget: only two candidates, a high hit rate,
# and cutting them to the library budget measurably lost 5 rows. The six-entry
# library and LLM proposals are speculative and numerous, so they get less —
# a lemma that will land usually lands almost immediately. Scaled by the effort
# tier inside `derived_cp_closure_proof_expr`.
LEMMA_LIBRARY_CLOSURE_TIME_BUDGET = 1.5
LLM_LEMMA_CLOSURE_TIME_BUDGET = 4.0

# Enumerated small-law candidates extending the curated library. ETP mining on
# the 2026-07-22 playground misses showed the winning pivots are simply *small
# universal laws* (x = (x ◇ y) ◇ z cracked a row the curated six could not);
# the family below generates every law with lhs `a` or `a ◇ b` and rhs of at
# most three ops over four variables, deduped by shape. Total route spend is
# capped separately so a deep tier cannot burn the clock on the long tail.
LEMMA_ENUM_MAX_RHS_OPS = 3
LEMMA_ENUM_VARS = ("a", "b", "c", "d")
LEMMA_ENUM_MAX_CANDIDATES = 600
LEMMA_BOOTSTRAP_TOTAL_BUDGET = 6.0


@lru_cache(maxsize=1)
def enumerated_lemma_library() -> tuple[tuple[str, str], ...]:
    def build_terms(max_ops: int) -> list[Term]:
        by_ops: list[list[Term]] = [[("var", v) for v in LEMMA_ENUM_VARS]]
        for ops in range(1, max_ops + 1):
            level: list[Term] = []
            for left_ops in range(ops):
                right_ops = ops - 1 - left_ops
                for left in by_ops[left_ops]:
                    for right in by_ops[right_ops]:
                        level.append(("op", left, right))
            by_ops.append(level)
        return [term for level in by_ops for term in level]

    rhs_terms = build_terms(LEMMA_ENUM_MAX_RHS_OPS)
    lhs_terms: tuple[Term, ...] = (
        ("var", "a"),
        ("op", ("var", "a"), ("var", "b")),
    )
    seen: set[tuple[Term, Term]] = set()
    laws: list[tuple[int, str, str]] = []
    for lhs in lhs_terms:
        for rhs in rhs_terms:
            if lhs == rhs:
                continue
            text = f"{term_to_lean(lhs)} = {term_to_lean(rhs)}"
            try:
                law = parse_equation(text)
            except ValueError:
                continue
            key = canonical_law_key(law)
            if key in seen:
                continue
            seen.add(key)
            size = term_size(lhs) + term_size(rhs)
            laws.append((size, f"enum{len(laws)}", text))
    laws.sort(key=lambda item: (item[0], item[2]))
    return tuple((name, text) for _, name, text in laws[:LEMMA_ENUM_MAX_CANDIDATES])


@lru_cache(maxsize=1)
def full_lemma_library() -> tuple[tuple[str, str], ...]:
    curated_shapes = set()
    curated: list[tuple[str, str]] = []
    for name, text in LEMMA_LIBRARY_TEXT:
        curated.append((name, text))
        curated_shapes.add(canonical_law_key(parse_equation(text)))
    extra = [
        (name, text)
        for name, text in enumerated_lemma_library()
        if canonical_law_key(parse_equation(text)) not in curated_shapes
    ]
    return tuple(curated + extra)


LEMMA_FILTER_FIN3_SAMPLES = 200
LEMMA_FILTER_SEED = 20260722


@lru_cache(maxsize=8)
def _lemma_filter_models(lhs: Term, rhs: Term, variables: tuple[str, ...]) -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Small magmas satisfying eq1: every Fin2, plus a fixed Fin3 sample."""
    eq1 = {"lhs": lhs, "rhs": rhs, "variables": list(variables)}
    models: list[tuple[tuple[int, ...], ...]] = []
    for encoding in product(range(2), repeat=4):
        table = [list(encoding[:2]), list(encoding[2:])]
        if equation_holds(eq1, table):
            models.append(tuple(tuple(row) for row in table))
    rng = random.Random(LEMMA_FILTER_SEED)
    for _ in range(LEMMA_FILTER_FIN3_SAMPLES):
        table = [[rng.randrange(3) for _ in range(3)] for _ in range(3)]
        if equation_holds(eq1, table):
            models.append(tuple(tuple(row) for row in table))
    return tuple(models)


def lemma_survives_models(eq1: dict[str, Any], lemma: dict[str, Any]) -> bool:
    """False as soon as one eq1-model refutes the lemma, so it cannot follow.

    Measured 2026-07-22: 6 of 13 lemmas the LLM proposed were refutable this
    way, and none of the survivors became derivable with 22x the search budget.
    Filtering first therefore costs milliseconds and saves the whole closure
    budget on the cases that could never have worked.
    """
    models = _lemma_filter_models(
        eq1["lhs"], eq1["rhs"], tuple(eq1["variables"]))
    return all(equation_holds(lemma, [list(row) for row in table]) for table in models)


def lemma_closure_proof(
    eq1: dict[str, Any],
    lemma: dict[str, Any],
    *,
    time_budget: float = DERIVED_CP_TIME_BUDGET,
) -> str | None:
    if not lemma_survives_models(eq1, lemma):
        return None
    return derived_cp_closure_proof_expr(eq1, lemma, time_budget=time_budget)


@lru_cache(maxsize=2048)
def lemma_goal(text: str) -> dict[str, Any]:
    return parse_equation(text)


def lemma_certificate(
    lemma: dict[str, Any],
    lemma_proof: str,
    eq2_vars: list[str],
    proof_expr: str,
) -> str:
    """A certificate that proves a named lemma, then the goal from it.

    Both halves stay inside the offline kernel's grammar, so
    `oracles.check_true_lemma_certificate` can verify each independently.
    """
    binders = " ".join(lemma["variables"])
    intro_vars = " ".join(eq2_vars)
    intro_line = f"  intro {intro_vars}\n" if intro_vars else ""
    statement = f"{term_to_lean(lemma['lhs'])} = {term_to_lean(lemma['rhs'])}"
    return (
        "import JudgeProblem\n\n"
        "def submission : Goal := by\n"
        "  intro G _ h\n"
        f"  have hlem : ∀ {binders} : G, {statement} := by\n"
        f"    intro {binders}\n"
        f"    exact {lemma_proof}\n"
        f"{intro_line}"
        f"  exact {proof_expr}\n"
    )


def lemma_applies_to_goal(lemma: dict[str, Any], eq2: dict[str, Any]) -> str | None:
    """Prove eq2 from the lemma alone. Cheap: the lemma is a tiny equation."""
    simple = simple_true_proof_expr(lemma, eq2, hypothesis_name="hlem")
    if simple is not None:
        return simple[1]
    chain = find_rewrite_chain(
        lemma, eq2, max_depth=LEMMA_APPLY_CHAIN_MAX_DEPTH, hypothesis_name="hlem")
    if chain is not None:
        return chain[1]
    return None


def projection_bootstrap_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    """Prove eq2 by deriving a projection law as a standalone lemma first.

    A projection law closes any goal whose two sides project to the same
    variable, and `a ◇ b = a` is a far smaller target for the critical-pair
    closure than the real goal: on rows where that engine cannot reach the goal
    at any budget it still lands the lemma in milliseconds. Applying the law to
    the goal is a free syntactic check, so it is done first and the closure runs
    only when it could actually finish the proof.
    """
    for side in ("left", "right"):
        proof_expr = projection_from_lemma_goal_proof(eq2, side, hypothesis_name="hlem")
        if proof_expr is None:
            continue
        lemma = lemma_goal(PROJECTION_LEMMA_TEXT[side])
        lemma_proof = lemma_closure_proof(eq1, lemma)
        if lemma_proof is None:
            continue
        return (
            f"true:projection_bootstrap:{side}",
            lemma_certificate(lemma, lemma_proof, eq2["variables"], proof_expr),
        )
    return None


def lemma_bootstrap_route(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    candidates: tuple[tuple[str, str], ...] | None = None,
) -> tuple[str, str] | None:
    """Prove eq2 via a small intermediate lemma instead of head-on.

    Proof search cost scales with the size of the goal, so a small law that
    happens to imply the goal can be reachable when the goal itself is not.
    The default candidate set is the curated library plus the enumerated
    small-law family; `candidates` stays a parameter so LLM-proposed lemmas
    can use exactly the same verified path.

    Ordering matters: the cheap direction (goal from lemma) runs first and
    rejects most candidates outright, so the expensive direction (lemma from
    eq1) is only ever paid for when it would finish the proof. The route-level
    deadline bounds the closure attempts across the whole candidate list.
    """
    if candidates is None:
        candidates = full_lemma_library()
    route_deadline = local_deadline(_eff_time(LEMMA_BOOTSTRAP_TOTAL_BUDGET))
    for name, text in candidates:
        if deadline_expired(route_deadline):
            return None
        try:
            lemma = lemma_goal(text)
        except ValueError:
            continue
        proof_expr = lemma_applies_to_goal(lemma, eq2)
        if proof_expr is None:
            continue
        lemma_proof = lemma_closure_proof(
            eq1, lemma, time_budget=LEMMA_LIBRARY_CLOSURE_TIME_BUDGET)
        if lemma_proof is None:
            continue
        return (
            f"true:lemma_bootstrap:{name}",
            lemma_certificate(lemma, lemma_proof, eq2["variables"], proof_expr),
        )
    return None


# Multi-hop lemma chaining. ETP mining (2026-07-22) showed the playground
# misses are `implicit_proof_true` rows: the ETP itself only reaches them
# through intermediate laws, so a single closure hop from eq1 cannot. The
# chain route first harvests small laws that ARE reachable from eq1, then
# reruns the closure on the goal-applying pivot with the harvested laws as
# additional rewrite rules — the deterministic analogue of the ETP's
# transitivity derivation, with every hop kernel-checkable.
LEMMA_CHAIN_MAX_HELPERS = 4
LEMMA_CHAIN_HARVEST_BUDGET = 0.4
LEMMA_CHAIN_TARGET_BUDGET = 2.5
LEMMA_CHAIN_TOTAL_BUDGET = 10.0


LEMMA_CHAIN_CP_HELPERS = 3
LEMMA_CHAIN_CP_RULES_EACH = 24
_CP_HELPER_LETTERS = "abcdefgh"


def cp_rule_helpers(
    eq1: dict[str, Any], limit: int
) -> list[tuple[dict[str, Any], str]]:
    """Standalone lemmas taken straight from eq1's critical-pair rules.

    Every derived rule already carries a proof builder, so these helpers cost
    no search at all — they are the one-rewrite-away laws (the ETP's explicit
    single-step implications) that the small-law library cannot express.
    """
    out: list[tuple[dict[str, Any], str]] = []
    seen: set[tuple[Term, Term]] = set()
    for rule in critical_pair_rules(eq1):
        if len(out) >= limit:
            break
        if rule.label.endswith(":rev"):
            continue
        rule_vars = list(rule.vars)
        all_vars = rule_vars + [v for v in rule.proof_only_vars if v not in rule.vars]
        if not rule_vars or len(rule_vars) > len(_CP_HELPER_LETTERS):
            continue
        rename = {v: _CP_HELPER_LETTERS[i] for i, v in enumerate(rule_vars)}
        subst: dict[str, Term] = {v: ("var", rename[v]) for v in rule_vars}
        fallback = rename[rule_vars[0]] if rule_vars else "a"
        for v in all_vars:
            if v not in subst:
                subst[v] = ("var", fallback)
        lhs = instantiate_term(rule.lhs, subst)
        rhs = instantiate_term(rule.rhs, subst)
        if lhs == rhs:
            continue
        lemma = {
            "lhs": lhs,
            "rhs": rhs,
            "variables": [rename[v] for v in rule_vars],
            "text": f"{term_to_lean(lhs)} = {term_to_lean(rhs)}",
        }
        key = canonical_law_key(lemma)
        if key in seen:
            continue
        seen.add(key)
        out.append((lemma, rule.builder(subst)))
    return out


def _helper_lemma_rules(name: str, lemma: dict[str, Any]) -> list[DerivedRule]:
    binders = list(lemma["variables"])

    def fwd(subst: dict[str, Term], binders=binders, name=name) -> str:
        return call_expression(binders, subst, name)

    def bwd(subst: dict[str, Term], binders=binders, name=name) -> str:
        return f"({call_expression(binders, subst, name)}).symm"

    return [
        DerivedRule(lemma["lhs"], lemma["rhs"], fwd, f"{name}:fwd"),
        DerivedRule(lemma["rhs"], lemma["lhs"], bwd, f"{name}:bwd"),
    ]


def _lemma_chain_goal_certificate(
    blocks: list[tuple[str, dict[str, Any], str]],
    eq2_vars: list[str],
    goal_expr: str,
) -> str:
    lines = ["import JudgeProblem", "", "def submission : Goal := by", "  intro G _ h"]
    for name, lemma, proof in blocks:
        binders = " ".join(lemma["variables"])
        statement = f"{term_to_lean(lemma['lhs'])} = {term_to_lean(lemma['rhs'])}"
        lines.append(f"  have {name} : ∀ {binders} : G, {statement} := by")
        lines.append(f"    intro {binders}")
        lines.append(f"    exact {proof}")
    if eq2_vars:
        lines.append(f"  intro {' '.join(eq2_vars)}")
    lines.append(f"  exact {goal_expr}")
    return "\n".join(lines) + "\n"


def lemma_chain_certificate(
    helpers: list[tuple[str, dict[str, Any], str]],
    final_lemma: dict[str, Any],
    final_proof: str,
    eq2_vars: list[str],
    goal_expr: str,
) -> str:
    return _lemma_chain_goal_certificate(
        helpers + [("hlem", final_lemma, final_proof)], eq2_vars, goal_expr)


def lemma_chain_bootstrap_route(
    eq1: dict[str, Any], eq2: dict[str, Any]
) -> tuple[str, str] | None:
    route_budget = _eff_time(LEMMA_CHAIN_TOTAL_BUDGET)
    route_deadline = local_deadline(route_budget)
    # The harvest may not eat the whole route budget: proving with the
    # harvested rules is the half that actually finishes rows.
    harvest_deadline = local_deadline(0.5 * route_budget)

    targets: list[tuple[str, dict[str, Any], str]] = []
    for name, text in full_lemma_library():
        if deadline_expired(route_deadline):
            return None
        try:
            lemma = lemma_goal(text)
        except ValueError:
            continue
        proof_expr = lemma_applies_to_goal(lemma, eq2)
        if proof_expr is None:
            continue
        if not lemma_survives_models(eq1, lemma):
            continue
        targets.append((name, lemma, proof_expr))
    target_keys = {canonical_law_key(lemma) for _, lemma, _ in targets}

    helpers: list[tuple[str, dict[str, Any], str]] = []
    helper_keys: set[Any] = set()
    extra_rules: list[DerivedRule] = []

    # Free helpers first: eq1's own critical-pair laws come with ready-made
    # proofs, and taking critical pairs OF those helpers gives the closure a
    # second derivation level it cannot reach in one hop.
    for lemma, proof in cp_rule_helpers(eq1, LEMMA_CHAIN_CP_HELPERS):
        key = canonical_law_key(lemma)
        if key in target_keys or key in helper_keys:
            continue
        helper_keys.add(key)
        name = f"hlem{len(helpers)}"
        helpers.append((name, lemma, proof))
        extra_rules.extend(_helper_lemma_rules(name, lemma))
        extra_rules.extend(critical_pair_rules(
            lemma, hyp_name=name, max_rules=LEMMA_CHAIN_CP_RULES_EACH))

    # Two harvest rounds: laws unreachable from eq1 alone often fall once the
    # first round's laws join the rule set (the ETP reaches these rows only
    # through chained intermediates, so single-round harvesting mirrors the
    # single-hop failure). The CP helpers above have their own slots — they
    # must not starve the searched harvest.
    harvested = 0
    for harvest_round in range(2):
        if harvest_round == 1 and not helpers:
            break
        for _, text in full_lemma_library():
            if harvested >= LEMMA_CHAIN_MAX_HELPERS or deadline_expired(harvest_deadline):
                break
            try:
                lemma = lemma_goal(text)
            except ValueError:
                continue
            key = canonical_law_key(lemma)
            # Targets already failed the single-hop route with a bigger
            # budget, so they are neither worth re-proving here nor useful
            # as helpers.
            if key in target_keys or key in helper_keys:
                continue
            if not lemma_survives_models(eq1, lemma):
                continue
            proof = derived_cp_closure_proof_expr(
                eq1, lemma, time_budget=LEMMA_CHAIN_HARVEST_BUDGET,
                extra_rules=extra_rules)
            if proof is None:
                continue
            helper_keys.add(key)
            name = f"hlem{len(helpers)}"
            helpers.append((name, lemma, proof))
            harvested += 1
            extra_rules.extend(_helper_lemma_rules(name, lemma))
        if harvested >= LEMMA_CHAIN_MAX_HELPERS or deadline_expired(harvest_deadline):
            break
    if not helpers:
        return None

    for name, lemma, goal_expr in targets:
        if deadline_expired(route_deadline):
            return None
        proof = derived_cp_closure_proof_expr(
            eq1, lemma,
            time_budget=LEMMA_CHAIN_TARGET_BUDGET, extra_rules=extra_rules)
        if proof is None:
            continue
        return (
            f"true:lemma_chain:{name}",
            lemma_chain_certificate(
                helpers, lemma, proof, eq2["variables"], goal_expr),
        )

    # No library pivot reached — aim the strengthened closure at the goal
    # itself. The helper rules often make the goal reachable even when no
    # small pivot law exists (the ETP path may run through laws bigger than
    # the enumerated family).
    if deadline_expired(route_deadline):
        return None
    direct = derived_cp_closure_proof_expr(
        eq1, eq2, time_budget=LEMMA_CHAIN_TARGET_BUDGET, extra_rules=extra_rules)
    if direct is not None:
        return (
            "true:lemma_chain:direct_goal",
            _lemma_chain_goal_certificate(helpers, eq2["variables"], direct),
        )
    return None


# ---------------------------------------------------------------------------
# Ground equality saturation with proof extraction ("egg with receipts").
#
# The 2026-07-23 frontier study proved the critical-pair closure cannot
# traverse single ETP explicit edges even when handed the exact intermediate
# lemma (oracle-pivot experiment), while the ETP's own MagmaEgg proofs reach
# them by instantiating eq1 at composite ground terms over the goal's
# variables — a move CP unification never makes. This engine is that
# mechanism: a ground e-graph over goal-variable terms, congruence closure,
# eq1 applied by e-matching with pool-drawn instantiations, and a proof
# forest that renders the discovered equality into the same
# h/.symm/.trans/congrArg grammar the offline kernel checks.
#
# Soundness: the renderer REPLAYS every extracted step syntactically on the
# concrete term before emitting anything — a bug anywhere in the e-graph or
# explanation code fails closed (route returns None); it cannot emit a wrong
# proof. Validated 2026-07-23: 21-23 of the 67 then-unreachable TRUE rows
# extract and pass the offline kernel; 9/9 shippable-size certificates were
# accepted by the real local Lean judge; 0/25 false positives on ETP-FALSE
# negative controls (see stage2/results/2026-07-23-*.md).

EGG_TIME_BUDGET = 10.0
EGG_ROUNDS = 30
EGG_POOL_MAX = 36
EGG_EXPAND_CAP = 900
EGG_MAX_ENODES = 60_000
# The production judge rejects code over JUDGE_MAX_CODE_LENGTH = 50_000 UTF-8
# bytes as malformed (vendor judge/verify.py). Measured 2026-07-23:
# 59,820-byte cert bounced, 48,526-byte cert accepted. Since 2026-07-29
# MAX_LEAN_CODE_BYTES enforces the same bound module-wide, so this route's cap
# is no longer the only one that is correct.
EGG_MAX_PROOF_BYTES = 46_000
EGG_MAX_CERT_BYTES = MAX_LEAN_CODE_BYTES

_EGG_BINDER_CANDIDATES = ("t", "q", "p", "s", "r", "m", "n", "k")


class _EggProvenanceError(Exception):
    pass


def _egg_term_size(t: Term) -> int:
    if t[0] == "var":
        return 1
    return _egg_term_size(t[1]) + _egg_term_size(t[2]) + 1


def _egg_substitute(term: Term, subst: dict[str, Term]) -> Term:
    if term[0] == "var":
        return subst[term[1]]
    return ("op", _egg_substitute(term[1], subst), _egg_substitute(term[2], subst))


def _egg_subterms(t: Term, acc: list[Term]) -> list[Term]:
    acc.append(t)
    if t[0] == "op":
        _egg_subterms(t[1], acc)
        _egg_subterms(t[2], acc)
    return acc


def _egg_pattern_vars(t: Term, acc: set[str] | None = None) -> set[str]:
    if acc is None:
        acc = set()
    if t[0] == "var":
        acc.add(t[1])
    else:
        _egg_pattern_vars(t[1], acc)
        _egg_pattern_vars(t[2], acc)
    return acc


def _egg_subterm_at(t: Term, pos: tuple) -> Term:
    for step in pos:
        t = t[1] if step == "L" else t[2]
    return t


def _egg_replace_at(t: Term, pos: tuple, new: Term) -> Term:
    if not pos:
        return new
    if pos[0] == "L":
        return ("op", _egg_replace_at(t[1], pos[1:], new), t[2])
    return ("op", t[1], _egg_replace_at(t[2], pos[1:], new))


def _egg_upper_patterns(eq1: dict[str, Any]) -> tuple[Term, Term, list[str]]:
    """eq1 with vars renamed to uppercase so they never collide with the
    goal's lowercase variables."""
    def walk(t: Term) -> Term:
        if t[0] == "var":
            return ("var", t[1].upper())
        return ("op", walk(t[1]), walk(t[2]))
    return walk(eq1["lhs"]), walk(eq1["rhs"]), [v.upper() for v in eq1["variables"]]


class _EggProver:
    """Term-registered e-graph with a proof forest.

    Forest edges (one per class merge, plus redundant alternatives):
      rule edge (a, b): a = eq1.lhs[σ], b = eq1.rhs[σ] — a root h-instance;
      congr edge (a, b): same top op, children pairwise merged earlier.
    """

    def __init__(self) -> None:
        self.parent: list[int] = []
        self.size_rep: list[int] = []
        self.enodes: dict[tuple, int] = {}
        self.witness: dict[tuple, Term] = {}
        self.term_class: dict[Term, int] = {}
        self.class_repr: dict[int, Term] = {}
        self.adj: dict[Term, list[tuple[Term, tuple, bool]]] = {}

    def find(self, a: int) -> int:
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def canon(self, node: tuple) -> tuple:
        if node[0] == "op":
            return ("op", self.find(node[1]), self.find(node[2]))
        return node

    def _register(self, t: Term, cid: int) -> None:
        if t not in self.term_class:
            self.term_class[t] = cid
        root = self.find(cid)
        best = self.class_repr.get(root)
        if best is None or _egg_term_size(t) < _egg_term_size(best):
            self.class_repr[root] = t

    def _add_edge(self, a: Term, b: Term, reason: tuple) -> None:
        self.adj.setdefault(a, []).append((b, reason, False))
        self.adj.setdefault(b, []).append((a, reason, True))

    def add_term(self, t: Term) -> int:
        # A registered term's class is authoritative: re-deriving it bottom-up
        # between rebuilds would miss the stale hashcons key and spawn a
        # duplicate class (found the hard way against the v2 engine).
        known = self.term_class.get(t)
        if known is not None:
            return self.find(known)
        if t[0] == "var":
            key: tuple = t
            sz = 1
        else:
            a = self.add_term(t[1])
            b = self.add_term(t[2])
            key = ("op", self.find(a), self.find(b))
            sz = self.size_rep[self.find(a)] + self.size_rep[self.find(b)] + 1
        existing = self.enodes.get(key)
        if existing is not None:
            cid = self.find(existing)
            if sz < self.size_rep[cid]:
                self.size_rep[cid] = sz
            w = self.witness.get(key)
            if w is not None and w != t:
                self._add_edge(t, w, ("congr",))
            self._register(t, cid)
            return cid
        cid = len(self.parent)
        self.parent.append(cid)
        self.size_rep.append(sz)
        self.enodes[key] = cid
        self.witness[key] = t
        self._register(t, cid)
        return cid

    def merge_terms(self, a_term: Term, b_term: Term, reason: tuple) -> bool:
        a = self.find(self.term_class[a_term])
        b = self.find(self.term_class[b_term])
        if a_term != b_term:
            # keep redundant justifications: they are alternative paths and
            # the BFS picks the shortest — without them explanations wander
            # the whole merge history
            self._add_edge(a_term, b_term, reason)
        if a == b:
            return False
        self.parent[a] = b
        self.size_rep[b] = min(self.size_rep[b], self.size_rep[a])
        ra, rb = self.class_repr.get(a), self.class_repr.get(b)
        if ra is not None and (rb is None or _egg_term_size(ra) < _egg_term_size(rb)):
            self.class_repr[b] = ra
        return True

    def rebuild(self) -> None:
        changed = True
        while changed:
            changed = False
            fresh: dict[tuple, int] = {}
            fresh_wit: dict[tuple, Term] = {}
            for node, cid in self.enodes.items():
                node2 = self.canon(node)
                cid = self.find(cid)
                wit = self.witness.get(node)
                other = fresh.get(node2)
                if other is None:
                    fresh[node2] = cid
                    if wit is not None:
                        fresh_wit[node2] = wit
                elif self.find(other) != cid:
                    ow = fresh_wit.get(node2)
                    if wit is not None and ow is not None:
                        self.merge_terms(ow, wit, ("congr",))
                    else:
                        # unexplained merge: any explanation crossing it
                        # fails closed later
                        self.parent[self.find(other)] = cid
                    changed = True
            self.enodes = fresh
            self.witness = fresh_wit

    def class_of(self, t: Term) -> int:
        return self.find(self.term_class[t])

    def _tree_path(self, s: Term, t: Term) -> list[tuple[Term, Term, tuple, bool]]:
        if s == t:
            return []
        prev: dict[Term, tuple[Term, tuple, bool]] = {s: (s, (), False)}
        queue = [s]
        while queue:
            nxt: list[Term] = []
            for u in queue:
                for v, reason, flipped in self.adj.get(u, ()):
                    if v in prev:
                        continue
                    prev[v] = (u, reason, flipped)
                    if v == t:
                        path: list[tuple[Term, Term, tuple, bool]] = []
                        cur = t
                        while cur != s:
                            p, r, f = prev[cur]
                            path.append((p, cur, r, f))
                            cur = p
                        path.reverse()
                        return path
                    nxt.append(v)
            queue = nxt
        raise _EggProvenanceError("terms not connected in proof forest")

    def explain(self, s: Term, t: Term, *, depth: int = 0,
                budget: list[int] | None = None) -> list[tuple]:
        if depth > 300:
            raise _EggProvenanceError("explanation recursion too deep")
        if budget is None:
            budget = [200000]
        steps: list[tuple] = []
        cur = s
        for a, b, reason, flipped in self._tree_path(s, t):
            if a != cur:
                raise _EggProvenanceError("path does not chain")
            budget[0] -= 1
            if budget[0] < 0:
                raise _EggProvenanceError("explanation too long")
            if reason and reason[0] == "rule":
                _, subst_items = reason
                # edge (x, y): x = eq1.lhs[σ], y = eq1.rhs[σ]; walking
                # backwards (flipped) is rhs -> lhs, i.e. .symm
                steps.append(((), dict(subst_items), flipped))
                cur = b
            elif reason and reason[0] == "congr":
                if a[0] != "op" or b[0] != "op":
                    raise _EggProvenanceError("congr edge on non-op terms")
                for sub in self.explain(a[1], b[1], depth=depth + 1, budget=budget):
                    steps.append((("L",) + sub[0], sub[1], sub[2]))
                for sub in self.explain(a[2], b[2], depth=depth + 1, budget=budget):
                    steps.append((("R",) + sub[0], sub[1], sub[2]))
                cur = b
            else:
                raise _EggProvenanceError(f"unknown reason {reason!r}")
        if cur != t:
            raise _EggProvenanceError("explanation does not reach target")
        return steps


def _egg_match_pattern(pattern: Term, term: Term,
                       subst: dict[str, Term]) -> dict[str, Term] | None:
    if pattern[0] == "var":
        bound = subst.get(pattern[1])
        if bound is None:
            s2 = dict(subst)
            s2[pattern[1]] = term
            return s2
        return subst if bound == term else None
    if term[0] != "op":
        return None
    s1 = _egg_match_pattern(pattern[1], term[1], subst)
    if s1 is None:
        return None
    return _egg_match_pattern(pattern[2], term[2], s1)


def _egg_diff_pos(a: Term, b: Term) -> tuple | None:
    if a == b:
        return None
    if a[0] == "op" and b[0] == "op":
        left = a[1] != b[1]
        right = a[2] != b[2]
        if left and not right:
            sub = _egg_diff_pos(a[1], b[1])
            return ("L",) + sub if sub is not None else ("L",)
        if right and not left:
            sub = _egg_diff_pos(a[2], b[2])
            return ("R",) + sub if sub is not None else ("R",)
    return ()


def _egg_one_step_between(s: Term, t: Term, lhs_p: Term, rhs_p: Term):
    if s == t:
        return None
    pos = _egg_diff_pos(s, t)
    if pos is None:
        return None
    sub_s = _egg_subterm_at(s, pos)
    sub_t = _egg_subterm_at(t, pos)
    for symm, (frm, to) in ((False, (lhs_p, rhs_p)), (True, (rhs_p, lhs_p))):
        subst = _egg_match_pattern(frm, sub_s, {})
        if subst is None:
            continue
        subst2 = _egg_match_pattern(to, sub_t, dict(subst))
        if subst2 is not None and _egg_substitute(frm, subst2) == sub_s:
            return (pos, subst2, symm)
    return None


def _egg_bridge_steps(start: Term, steps: list, lhs_p: Term, rhs_p: Term):
    """Greedy shortcutting: jump to the farthest later state reachable in one
    eq1 rewrite. Every emitted step is a checked instance; the renderer
    replays everything again anyway."""
    states: list[Term] = [start]
    cur = start
    for pos, subst, symm in steps:
        to_t = _egg_substitute(lhs_p if symm else rhs_p, subst)
        cur = _egg_replace_at(cur, pos, to_t)
        states.append(cur)
    out: list = []
    i = 0
    while i < len(states) - 1:
        jumped = False
        for j in range(len(states) - 1, i, -1):
            if j == i + 1:
                break
            step = _egg_one_step_between(states[i], states[j], lhs_p, rhs_p)
            if step is not None:
                out.append(step)
                i = j
                jumped = True
                break
        if not jumped:
            if len(steps) != len(states) - 1:
                return None
            out.append(steps[i])
            i += 1
    return out


def _egg_shorten_steps(start: Term, steps: list, lhs_p: Term, rhs_p: Term):
    """Replay the chain and cut every cycle in the term-state sequence; also
    validates every incoming step."""
    kept: list = []
    states: list[Term] = [start]
    index: dict[Term, int] = {start: 0}
    cur = start
    for pos, subst, symm in steps:
        from_t = _egg_substitute(rhs_p if symm else lhs_p, subst)
        try:
            if _egg_subterm_at(cur, pos) != from_t:
                return None
        except (IndexError, TypeError):
            return None
        to_t = _egg_substitute(lhs_p if symm else rhs_p, subst)
        nxt = _egg_replace_at(cur, pos, to_t)
        seen = index.get(nxt)
        if seen is not None:
            for t in states[seen + 1:]:
                index.pop(t, None)
            del kept[seen:]
            del states[seen + 1:]
        else:
            kept.append((pos, subst, symm))
            states.append(nxt)
            index[nxt] = len(states) - 1
        cur = nxt
    return kept


def _egg_balanced_trans(parts: list[str]) -> str:
    if len(parts) == 1:
        return parts[0]
    mid = len(parts) // 2
    return f"({_egg_balanced_trans(parts[:mid])}).trans ({_egg_balanced_trans(parts[mid:])})"


def _egg_render_steps(start: Term, target: Term, steps: list,
                      lhs_p: Term, rhs_p: Term, eq1_vars: list[str],
                      goal_vars: list[str]) -> str | None:
    """Render flat steps into one proof expression, replaying each step:
    the subterm at the recorded position must equal the instantiated eq1
    side, or the whole extraction is discarded."""
    binder = next((b for b in _EGG_BINDER_CANDIDATES if b not in goal_vars), None)
    if binder is None:
        return None
    cur = start
    parts: list[str] = []
    total = 0
    for pos, subst, symm in steps:
        from_t = _egg_substitute(rhs_p if symm else lhs_p, subst)
        to_t = _egg_substitute(lhs_p if symm else rhs_p, subst)
        try:
            if _egg_subterm_at(cur, pos) != from_t:
                return None
        except (IndexError, TypeError):
            return None
        args = " ".join(term_to_lean(subst[v]) for v in eq1_vars)
        inner = f"(h {args})" if args else "(h)"
        if symm:
            inner = f"{inner}.symm"
        if pos:
            ctx = _egg_replace_at(cur, pos, ("var", binder))
            step_proof = f"congrArg (fun {binder} => {term_to_lean(ctx)}) ({inner})"
        else:
            step_proof = inner
        cur = _egg_replace_at(cur, pos, to_t)
        parts.append(step_proof)
        total += len(step_proof.encode("utf-8")) + 10
        if total > EGG_MAX_PROOF_BYTES:
            return None
    if cur != target:
        return None
    if not parts:
        return "rfl"
    return _egg_balanced_trans(parts)


def _egg_ematch(egg: _EggProver, pattern: Term, cid: int, subst: dict,
                by_class: dict[int, list[tuple]]):
    cid = egg.find(cid)
    if pattern[0] == "var":
        v = pattern[1]
        bound = subst.get(v)
        if bound is not None:
            if egg.find(bound) == cid:
                yield subst
            return
        s2 = dict(subst)
        s2[v] = cid
        yield s2
        return
    for node in by_class.get(cid, ()):
        if node[0] != "op":
            continue
        for s1 in _egg_ematch(egg, pattern[1], node[1], subst, by_class):
            yield from _egg_ematch(egg, pattern[2], node[2], s1, by_class)


def egg_saturate_prove(eq1: dict[str, Any], eq2: dict[str, Any], *,
                       time_budget: float) -> str | None:
    """Saturate a ground e-graph from the goal's terms under eq1; if the goal
    sides merge, extract, shorten, and render a replayed proof expression."""
    lhs_p, rhs_p, eq1_vars = _egg_upper_patterns(eq1)
    goal_vars = list(eq2["variables"])
    L, R = eq2["lhs"], eq2["rhs"]

    egg = _EggProver()
    pool: list[int] = []
    for t in _egg_subterms(L, []) + _egg_subterms(R, []):
        cid = egg.add_term(t)
        if cid not in pool:
            pool.append(cid)

    orientations = []
    for symm, (a, b) in ((False, (lhs_p, rhs_p)), (True, (rhs_p, lhs_p))):
        free = sorted(_egg_pattern_vars(b) - _egg_pattern_vars(a))
        orientations.append((a, b, free, symm))

    deadline = local_deadline(time_budget)
    done: set = set()

    proved = egg.class_of(L) == egg.class_of(R)
    for rnd in range(EGG_ROUNDS):
        if proved or deadline_expired(deadline) or len(egg.enodes) > EGG_MAX_ENODES:
            break
        expand_targets = min(EGG_POOL_MAX, 10 + 6 * rnd)
        free_pool = min(18, 8 + 2 * rnd)

        cur_pool = sorted({egg.find(c) for c in pool},
                          key=lambda c: egg.size_rep[c])
        pool = cur_pool[:EGG_POOL_MAX]
        prods = []
        for p in pool[:expand_targets]:
            for q in pool[:expand_targets]:
                prods.append(egg.add_term(
                    ("op", egg.class_repr[egg.find(p)],
                     egg.class_repr[egg.find(q)])))
        for c in prods:
            c = egg.find(c)
            if c not in pool and len(pool) < EGG_POOL_MAX:
                pool.append(c)

        by_class: dict[int, list[tuple]] = {}
        for node, cid in egg.enodes.items():
            by_class.setdefault(egg.find(cid), []).append(egg.canon(node))

        apps = []
        for oi, (a, b, free, symm) in enumerate(orientations):
            classes = pool[:expand_targets] if a[0] == "var" else list(by_class)
            for cid in classes:
                if deadline_expired(deadline):
                    break
                for subst in _egg_ematch(egg, a, cid, {}, by_class):
                    key = (oi, egg.find(cid),
                           tuple(sorted((v, egg.find(c)) for v, c in subst.items())))
                    if not free:
                        if key in done:
                            continue
                        apps.append((0, key, a, b, subst, symm))
                    else:
                        for combo in product(pool[:free_pool], repeat=len(free)):
                            key2 = key + (tuple(egg.find(c) for c in combo),)
                            if key2 in done:
                                continue
                            s2 = dict(subst)
                            s2.update(zip(free, combo))
                            cost = sum(egg.size_rep[egg.find(c)]
                                       for c in s2.values())
                            apps.append((cost, key2, a, b, s2, symm))
        apps.sort(key=lambda x: x[0])

        merged_any = False
        capped = False
        applied_now = 0
        for cost, key, lhs_pat, rhs_pat, subst_cls, symm in apps:
            if applied_now > EGG_EXPAND_CAP and cost > 0:
                capped = True
                break
            if deadline_expired(deadline) or len(egg.enodes) > EGG_MAX_ENODES:
                capped = True
                break
            if key in done:
                continue
            done.add(key)
            applied_now += 1
            subst_terms = {v: egg.class_repr[egg.find(c)]
                           for v, c in subst_cls.items()}
            l_term = _egg_substitute(lhs_pat, subst_terms)
            r_term = _egg_substitute(rhs_pat, subst_terms)
            egg.add_term(l_term)
            egg.add_term(r_term)
            edge = (r_term, l_term) if symm else (l_term, r_term)
            subst_items = tuple(sorted(subst_terms.items()))
            if egg.merge_terms(edge[0], edge[1], ("rule", subst_items)):
                merged_any = True
            if egg.class_of(L) == egg.class_of(R):
                proved = True
                break
        egg.rebuild()
        if egg.class_of(L) == egg.class_of(R):
            proved = True
        if proved or (not merged_any and not capped):
            break

    if egg.class_of(L) != egg.class_of(R):
        return None
    try:
        steps = egg.explain(L, R)
    except (_EggProvenanceError, RecursionError):
        return None
    shortened = _egg_shorten_steps(L, steps, lhs_p, rhs_p)
    if shortened is None:
        return None
    # shorten+bridge to fixpoint: bridging creates new states, which open
    # new cycle cuts and new shortcuts
    for _ in range(4):
        before = len(shortened)
        bridged = _egg_bridge_steps(L, shortened, lhs_p, rhs_p)
        if bridged is None:
            break
        cut = _egg_shorten_steps(L, bridged, lhs_p, rhs_p)
        if cut is None:
            break
        shortened = cut
        if len(shortened) >= before:
            break
    return _egg_render_steps(L, R, shortened, lhs_p, rhs_p, eq1_vars, goal_vars)


def egg_closure_route(eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[str, str] | None:
    proof_expr = egg_saturate_prove(
        eq1, eq2, time_budget=_eff_time(EGG_TIME_BUDGET))
    if proof_expr is None:
        return None
    code = substitution_true_certificate(eq2["variables"], proof_expr)
    if len(code.encode("utf-8")) > EGG_MAX_CERT_BYTES:
        return None
    return "true:egg_closure", code


# ---------------------------------------------------------------------------
# Egg-proved lemma bootstrap.
#
# `lemma_bootstrap_route` picks a small law that implies the goal and proves it
# from eq1 with the *critical-pair closure*. That closure is exactly the engine
# the 2026-07-23 oracle-pivot experiment showed cannot traverse a single ETP
# explicit edge even when handed the right intermediate law — candidate
# generation was never the bottleneck, the closure mechanism was. `egg_closure`
# fixed the mechanism, but only for the real goal.
#
# This route is the missing composition: **egg as the lemma prover**. Two
# independent facts made it worth building:
#
#  - ETP pivot mining (2026-07-29) shows many hard TRUE misses factor through a
#    *tiny* law — `hard2_0073` and `hard2_0099` both go via `Eq2: x = y`, i.e.
#    eq1 collapses the magma outright.
#  - Egg proves that collapse where the CP closure cannot: measured
#    `hard2_0099` -> `a = b` in 13.4 s at `standard` effort, on a row every
#    existing engine skips.
#
# Certificates use the same `lemma_certificate` shape as `lemma_bootstrap`, so
# they are fully kernel-checkable (`check_true_lemma_certificate` runs the kernel
# twice — lemma from eq1, goal from the stated lemma). No new oracle surface.
#
# Ordering is deliberate: the free syntactic gate (`lemma_applies_to_goal`) runs
# first and rejects nearly every candidate, so egg — the expensive half — is only
# ever paid for on a lemma that would actually finish the proof.
# ---------------------------------------------------------------------------

EGG_BOOTSTRAP_TOTAL_BUDGET = 24.0
EGG_BOOTSTRAP_LEMMA_BUDGET = 8.0
EGG_BOOTSTRAP_MAX_ATTEMPTS = 6

# The collapse law gets its own route and its own budget because it is by far the
# most common pivot on the frontier. ETP mining over every unsolved official row
# (2026-07-29): **14 of the 31 unsolved TRUE rows have `eq1 => (x = y)`** — eq1
# forces a one-element magma, so the goal is irrelevant and the whole problem is
# "prove eq1 collapses". `singleton_route` catches only the syntactic case, and
# `lemma_bootstrap`'s CP closure cannot derive it. Egg can: 10 of those 14, in
# 1.9-34.3 s, every proof kernel-verified.
#
# The budget is deliberately larger than `EGG_BOOTSTRAP_LEMMA_BUDGET`: measured
# successes span 1.9 s to 34.3 s, so an 8 s cap would drop most of them.
EGG_COLLAPSE_BUDGET = 40.0


def egg_collapse_route(
    eq1: dict[str, Any], eq2: dict[str, Any]
) -> tuple[str, str] | None:
    """Prove eq1 forces a one-element magma, via equality saturation on `a = b`.

    Certificate is the kernel-checkable `lemma` shape: `check_true_lemma_certificate`
    replays the collapse proof against eq1 and the goal against the stated law, so
    neither half is taken on trust.
    """
    collapse = lemma_goal("a = b")
    goal_expr = lemma_applies_to_goal(collapse, eq2)
    if goal_expr is None:
        return None
    # A nontrivial finite model of eq1 refutes collapse outright — milliseconds,
    # and it rules out the whole route before egg spends anything.
    if not lemma_survives_models(eq1, collapse):
        return None
    proof = egg_saturate_prove(
        eq1, collapse, time_budget=_eff_time(EGG_COLLAPSE_BUDGET))
    if proof is None:
        return None
    code = lemma_certificate(collapse, proof, eq2["variables"], goal_expr)
    if len(code.encode("utf-8")) > MAX_LEAN_CODE_BYTES:
        return None
    return "true:egg_collapse", code


# Which laws actually pay, measured rather than guessed. Two real-LLM sweeps over
# the open TRUE frontier (2026-07-29, 51 rows, gpt-oss-120b naming pivot lemmas)
# produced 9 solved rows, and **every single winning law was one of these four** —
# collapse plus the two projections plus product-constant. The 601-entry library
# contributed nothing else.
#
# So they get the collapse-sized budget and go first. The library scan still runs
# after, on the remaining budget, because it costs nothing when the free gates
# reject (and 2026-07-21 established that "looks unused" is not a deletion
# licence). The earlier flat 8 s cap over the library was the binding constraint:
# these proofs need 13-20 s, so the route was starved on rows it could win.
EGG_PRIORITY_LEMMAS = (
    ("left_projection", "a ◇ b = a"),
    ("right_projection", "a ◇ b = b"),
    ("product_constant", "a ◇ b = c ◇ d"),
)


def egg_priority_bootstrap_route(
    eq1: dict[str, Any], eq2: dict[str, Any]
) -> tuple[str, str] | None:
    """`egg_bootstrap` restricted to the handful of laws that measurably win,
    with a real budget each."""
    route_deadline = local_deadline(_eff_time(EGG_COLLAPSE_BUDGET * 2))
    for name, text in EGG_PRIORITY_LEMMAS:
        if deadline_expired(route_deadline):
            return None
        try:
            lemma = lemma_goal(text)
        except ValueError:
            continue
        proof_expr = lemma_applies_to_goal(lemma, eq2)
        if proof_expr is None:
            continue
        if not lemma_survives_models(eq1, lemma):
            continue
        proof = egg_saturate_prove(
            eq1, lemma, time_budget=_eff_time(EGG_COLLAPSE_BUDGET))
        if proof is None:
            continue
        code = lemma_certificate(lemma, proof, eq2["variables"], proof_expr)
        if len(code.encode("utf-8")) > MAX_LEAN_CODE_BYTES:
            continue
        return f"true:egg_bootstrap:{name}", code
    return None


def egg_bootstrap_route(
    eq1: dict[str, Any], eq2: dict[str, Any]
) -> tuple[str, str] | None:
    route_deadline = local_deadline(_eff_time(EGG_BOOTSTRAP_TOTAL_BUDGET))
    attempts = 0
    for name, text in full_lemma_library():
        if attempts >= EGG_BOOTSTRAP_MAX_ATTEMPTS:
            return None
        if deadline_expired(route_deadline):
            return None
        try:
            lemma = lemma_goal(text)
        except ValueError:
            continue
        # Free gate: does this law even close the goal?
        proof_expr = lemma_applies_to_goal(lemma, eq2)
        if proof_expr is None:
            continue
        # Free gate: is the law refutable in a model of eq1? Then eq1 cannot
        # prove it and egg would burn its budget confirming that.
        if not lemma_survives_models(eq1, lemma):
            continue
        attempts += 1
        lemma_proof = egg_saturate_prove(
            eq1, lemma, time_budget=_eff_time(EGG_BOOTSTRAP_LEMMA_BUDGET))
        if lemma_proof is None:
            continue
        code = lemma_certificate(lemma, lemma_proof, eq2["variables"], proof_expr)
        if len(code.encode("utf-8")) > MAX_LEAN_CODE_BYTES:
            continue
        return f"true:egg_bootstrap:{name}", code
    return None


def projection_cue(eq1: dict[str, Any], eq2: dict[str, Any]) -> bool:
    eq1_left, eq1_right = boundary_vars(eq1["lhs"])
    eq2_left, eq2_right = boundary_vars(eq2["rhs"])
    return eq1_left != eq2_left or eq1_right != eq2_right


def problem_priority(problem: dict[str, Any], eq1: dict[str, Any], eq2: dict[str, Any]) -> tuple[int, int, str]:
    if is_reflexive_problem(problem):
        return (0, len(eq2["text"]), "true:reflexive")
    if singleton_route(eq1):
        return (1, len(eq2["text"]), "true:singleton")
    if deep_repeat_singleton_source(eq1):
        return (1, len(eq2["text"]), "true:deep_repeat_singleton")
    if reverse_deep_repeat_singleton_source(eq1):
        return (1, len(eq2["text"]), "true:reverse_deep_repeat_singleton")
    if sandwich_repeat_singleton_source(eq1):
        return (1, len(eq2["text"]), "true:sandwich_repeat_singleton")
    if outer_sandwich_singleton_source(eq1):
        return (1, len(eq2["text"]), "true:outer_sandwich_singleton")
    if forked_square_singleton_source(eq1):
        return (1, len(eq2["text"]), "true:forked_square_singleton")
    if crossed_pair_singleton_source(eq1):
        return (1, len(eq2["text"]), "true:crossed_pair_singleton")
    if nested_square_singleton_source(eq1):
        return (1, len(eq2["text"]), "true:nested_square_singleton")
    if tail_square_singleton_source(eq1):
        return (1, len(eq2["text"]), "true:tail_square_singleton")
    if paired_tail_singleton_source(eq1):
        return (1, len(eq2["text"]), "true:paired_tail_singleton")
    if wrapped_tail_singleton_source(eq1):
        return (1, len(eq2["text"]), "true:wrapped_tail_singleton")
    if middle_self_collapse_source(eq1):
        return (1, len(eq2["text"]), "true:middle_self_collapse")
    if front_double_self_collapse_source(eq1):
        return (1, len(eq2["text"]), "true:front_double_self_collapse")
    if alternating_front_self_collapse_source(eq1):
        return (1, len(eq2["text"]), "true:alternating_front_self_collapse")
    if mirrored_alternating_front_self_collapse_source(eq1):
        return (1, len(eq2["text"]), "true:mirrored_alternating_front_self_collapse")
    if sandwich_left_projection_source(eq1) and projection_proof_expr_from_law(eq2, "left", hypothesis_name="hleft"):
        return (2, len(eq2["text"]), "true:sandwich_left_projection")
    if nested_left_projection_source(eq1) and projection_from_lemma_goal_proof(eq2, "left", hypothesis_name="hleft"):
        return (2, len(eq2["text"]), "true:nested_left_projection")
    if (right_nested_tail_left_projection_source(eq1) or bracket_tail_left_projection_source(eq1) or pair_square_left_projection_source(eq1)) and projection_from_lemma_goal_proof(eq2, "left", hypothesis_name="hleft"):
        return (2, len(eq2["text"]), "true:left_projection_collapse")
    if left_row_constancy_source(eq1) and left_row_constancy_term_proof(eq2["lhs"], eq2["rhs"]):
        return (2, len(eq2["text"]), "true:left_row_constancy")
    if product_constancy_source(eq1) and eq2["lhs"][0] == "op" and eq2["rhs"][0] == "op":
        return (2, len(eq2["text"]), "true:product_constancy")
    if repeated_prefix_product_constancy_source(eq1) and eq2["lhs"][0] == "op" and eq2["rhs"][0] == "op":
        return (2, len(eq2["text"]), "true:repeated_prefix_product_constancy")
    if double_tail_square_product_source(eq1) and square_product_basis_goal(eq2):
        return (2, len(eq2["text"]), "true:double_tail_square_product")
    if square_twist_comm_source(eq1) and commutative_term_key(eq2["lhs"]) == commutative_term_key(eq2["rhs"]):
        return (2, len(eq2["text"]), "true:square_twist_comm")
    if square_to_right_product_source(eq1) and square_to_right_product_goal(eq2):
        return (2, len(eq2["text"]), "true:square_to_right_product")
    if (tail_square_right_projection_source(eq1) or nested_tail_right_projection_source(eq1) or sandwich_tail_right_projection_source(eq1) or left_pair_tail_right_projection_source(eq1)) and projection_from_lemma_goal_proof(eq2, "right", hypothesis_name="hright"):
        return (2, len(eq2["text"]), "true:right_projection_collapse")
    if (*equation_shape_key(eq1), *equation_shape_key(eq2)) in narrow_grind_true_shape_keys():
        return (2, len(eq2["text"]), "true:narrow_grind")
    if direct_substitution_route(eq1, eq2):
        return (2, len(eq2["text"]), "true:rewrite")
    if bridge_route(eq1, eq2):
        return (3, len(eq2["text"]), "true:bridge")
    if projection_cue(eq1, eq2):
        return (4, len(eq2["text"]), "false:projection_cue")
    if absorption_hypothesis(eq1):
        return (5, len(eq1["text"]) + len(eq2["text"]), "true:absorption")
    return (6, len(eq1["text"]) + len(eq2["text"]), "false:finite_search")


def find_counterexample(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    max_n: int = ENUMERATION_MAX_N,
    time_budget: float | None = None,
    allow_dual: bool = True,
) -> tuple[int, list[list[int]], str] | None:
    deadline = local_deadline(time_budget)

    for name, table in WITNESS_TABLES:
        if deadline is not None and time.monotonic() >= deadline:
            return None
        if witness_check(eq1, eq2, table):
            return len(table), table, f"false:witness:{name}"

    family_max = max(max_n, STRUCTURED_MAX_N)
    for route, table in structured_family_tables(max_n=family_max):
        if deadline is not None and time.monotonic() >= deadline:
            return None
        if witness_check(eq1, eq2, table):
            return len(table), table, route

    for route, table in affine_family_tables(max_n=max(max_n, max(AFFINE_LINEAR_SIZES))):
        if deadline is not None and time.monotonic() >= deadline:
            return None
        if witness_check(eq1, eq2, table):
            return len(table), table, route

    for route, table in quadratic_family_tables(max_n=family_max):
        if deadline is not None and time.monotonic() >= deadline:
            return None
        if witness_check(eq1, eq2, table):
            return len(table), table, route

    for n in range(2, max_n + 1):
        for table in enumerate_tables(n):
            if deadline is not None and time.monotonic() >= deadline:
                return None
            if witness_check(eq1, eq2, table):
                return n, table, f"false:enum_fin{n}"
    if allow_dual:
        remaining_budget = None
        if deadline is not None:
            remaining_budget = max(0.0, deadline - time.monotonic())
            if remaining_budget <= 0:
                return None
        dual = find_counterexample(
            dual_equation(eq1),
            dual_equation(eq2),
            max_n=max_n,
            time_budget=remaining_budget,
            allow_dual=False,
        )
        if dual is not None:
            n, table, route = dual
            return n, transpose_table(table), f"false:dual:{route}"
    return None


def _lm_eval(term: Term, env: dict[str, int], table: list[list[int]]) -> int:
    if term[0] == "var":
        return env[term[1]]
    return table[_lm_eval(term[1], env, table)][_lm_eval(term[2], env, table)]


def _lm_envs(equation: dict[str, Any], n: int) -> list[dict[str, int]]:
    variables = list(equation["variables"])
    return [dict(zip(variables, values))
            for values in product(range(n), repeat=len(variables))]


def _lm_cells(term: Term, env: dict[str, int], table: list[list[int]],
              out: set[tuple[int, int]]) -> int:
    if term[0] == "var":
        return env[term[1]]
    a = _lm_cells(term[1], env, table, out)
    b = _lm_cells(term[2], env, table, out)
    out.add((a, b))
    return table[a][b]


# ---------------------------------------------------------------------------
# Constraint-propagation countermodel search (Mace4-style).
#
# The canned portfolio (named tables, structured/affine/quadratic families,
# `Fin 2..3` enumeration) and the randomized `local_model_counterexample` repair
# search share one blind spot: laws of the form `x = F(x, y-bar)` with `x`
# occurring once on the right. Those force *quasigroups*, so a random table
# essentially never satisfies them and the smallest countermodel usually lives at
# order 8-9, out of enumeration range.
#
# Measured cost of that gap (playground, 2026-07-29): six `hard2` rows with
# ground-truth label FALSE were answered `true` by the Solo grind fallback, at
# 363-847 s each. A TRUE verdict on a FALSE row can never be accepted.
#
# This search treats the n^2 Cayley cells as unknowns and every ground instance
# of eq1 as a constraint. Two things make it work where the others do not:
#
#  1. **Unit propagation.** If one side of an instance evaluates and the other is
#     blocked exactly at its outermost product, that cell is forced. For
#     `x = F(x, y-bar)` this cascades hard.
#  2. **Order schedule, not smallest-first.** On `hard2_0009`, order 7 exhausted a
#     120 s budget and found nothing while order 8 succeeded in 0.03 s / 40 nodes.
#     Difficulty tracks how well the order fits the algebra, not its size.
#
# Results: 4 of those 6 rows solved in ~0.05 s each, all four judge-accepted as
# 426-byte `Fin 8` certificates. Every table still passes through
# `table_is_counterexample` before it can be emitted, so the search cannot
# produce an unsound witness even if it has a bug.
# ---------------------------------------------------------------------------

# Did the constraint search finish every order it was asked for, or did it run out
# of clock / nodes? Only the first case is evidence: "no countermodel exists at
# orders 8,9,10,12,16" is a real statement, while "the search was cut off" says
# nothing at all.
#
# This matters because the signal it replaces was worthless. `run_solo` used
# `hypothesis_models_seen() > 0` to decide the row was probably TRUE and submit a
# speculative grind certificate. On the six FALSE playground rows that misfired on,
# models_seen was 1050, 1272, 1349, 1352, 7698 and 2 — all comfortably above zero,
# all genuinely FALSE, all guaranteed misses that each burned 363-847 s.
_CONSTRAINT_EXHAUSTED = False


def reset_constraint_evidence() -> None:
    global _CONSTRAINT_EXHAUSTED
    _CONSTRAINT_EXHAUSTED = False


def constraint_search_exhausted() -> bool:
    return _CONSTRAINT_EXHAUSTED


# HARD CEILING ON WITNESS ORDER: 10.
#
# The judge builds the magma with `MemoFinOp.finOpTable`, whose parser is
# `extractDigits`: it walks the table string character by character and keeps each
# *digit* as one value (vendor/stage2-official/judge/JudgeFinOp/MemoFinOp.lean).
# A cell holding `10` therefore becomes two cells, `1` and `0`, and the whole
# table shifts. Orders 2..10 use only single-digit entries and are safe; order 11+
# is silently corrupted.
#
# Confirmed the hard way (2026-07-29): a genuine `Fin 13` witness for `hard2_0051`
# — the linear model `x ◇ y = 7x + 7y (mod 13)`, verified by hand and by both
# offline oracles — came back `LEAN_REJECTED` with `decide` reporting the
# conjunction *false*, because Lean was reading a different table than we sent.
# Nothing in the offline harness could see this, since every local check reads the
# Python table rather than the rendered string.
MAX_WITNESS_ORDER = 10

CONSTRAINT_ORDERS = (8, 9, 6, 4, 10)
CONSTRAINT_TIME_BUDGET = 3.0
CONSTRAINT_MAX_NODES = 60000
# Wide tier, reached only when nothing else claimed the row. 5 and 7 are the
# expensive orders for this family (they fit the algebra badly, so the search
# explores instead of propagating), which is exactly why they belong here and not
# in the cheap schedule.
CONSTRAINT_WIDE_ORDERS = (8, 9, 10, 6, 5, 7, 4)
# Budget is per *order*, not for the whole schedule. With one shared deadline a
# 25 s wide tier never reached order 5 at all, and the dev sweep needed 125 s there
# for `hard1_0025`, 94 s at order 6 for `hard2_0125` and 21 s at order 8 for
# `hard2_0092` — three rows with genuine witnesses that the solver could not claim.
# Reached only by rows nothing else solved, where the alternative is a speculative
# `true` guess, so spending real time here is the better trade.
CONSTRAINT_WIDE_PER_ORDER_BUDGET = 45.0
_CELL_UNKNOWN = -1


def _cp_eval(term: Term, env: dict[str, int], table: list[int], n: int):
    """Partial evaluation. Returns (value, ready_cell, root_cell).

    `root_cell` is set only when this term's own outermost lookup is the missing
    one (both children known) — the only position where propagating the other
    side's value is valid. `ready_cell` is any unknown cell whose operands are
    known, i.e. a legal branch point.
    """
    if term[0] == "var":
        return env[term[1]], None, None
    lv, lr, _ = _cp_eval(term[1], env, table, n)
    rv, rr, _ = _cp_eval(term[2], env, table, n)
    if lv is None or rv is None:
        return None, (lr if lr is not None else rr), None
    idx = lv * n + rv
    val = table[idx]
    if val == _CELL_UNKNOWN:
        return None, idx, idx
    return val, None, None


def _cp_instances(eq: dict[str, Any], n: int) -> list[tuple[dict[str, int], Term, Term]]:
    variables = list(eq["variables"])
    lhs, rhs = eq["lhs"], eq["rhs"]
    return [(dict(zip(variables, values)), lhs, rhs)
            for values in product(range(n), repeat=len(variables))]


def _cp_propagate(table: list[int], n: int, instances) -> bool:
    """Unit-propagate to a fixpoint. False on conflict."""
    changed = True
    while changed:
        changed = False
        for env, lhs, rhs in instances:
            lv, _lr, lroot = _cp_eval(lhs, env, table, n)
            rv, _rr, rroot = _cp_eval(rhs, env, table, n)
            if lv is not None and rv is not None:
                if lv != rv:
                    return False
                continue
            if lv is not None and rroot is not None:
                table[rroot] = lv
                changed = True
            elif rv is not None and lroot is not None:
                table[lroot] = rv
                changed = True
    return True


def _cp_search(eq1: dict[str, Any], eq2: dict[str, Any], n: int,
               deadline: float | None, budget: list[int]) -> list[list[int]] | None:
    instances = _cp_instances(eq1, n)
    eq2_vars = list(eq2["variables"])
    eq2_lhs, eq2_rhs = eq2["lhs"], eq2["rhs"]

    def branch(table: list[int]) -> list[list[int]] | None:
        budget[0] -= 1
        if budget[0] <= 0:
            return None
        if deadline is not None and time.monotonic() >= deadline:
            return None
        work = table[:]
        if not _cp_propagate(work, n, instances):
            return None
        lv, _lr, _lroot = _cp_eval(eq2_lhs, tenv, work, n)
        rv, _rr, _rroot = _cp_eval(eq2_rhs, tenv, work, n)
        if lv is not None and rv is not None and lv == rv:
            return None
        blocking: dict[int, int] = {}
        for env, lhs, rhs in instances:
            for term in (lhs, rhs):
                _v, ready, _root = _cp_eval(term, env, work, n)
                if ready is not None:
                    blocking[ready] = blocking.get(ready, 0) + 1
        cell = -1
        if blocking:
            cell = max(blocking, key=lambda k: blocking[k])
        else:
            for term in (eq2_lhs, eq2_rhs):
                _v, ready, _root = _cp_eval(term, tenv, work, n)
                if ready is not None:
                    cell = ready
                    break
        if cell < 0:
            if lv is None or rv is None or lv == rv:
                return None
            filled = [0 if v == _CELL_UNKNOWN else v for v in work]
            return [filled[r * n:(r + 1) * n] for r in range(n)]
        for value in range(n):
            trial = work[:]
            trial[cell] = value
            got = branch(trial)
            if got is not None:
                return got
        return None

    # Commit to one violating assignment of eq2 at a time: much stronger pruning
    # than finding any model and testing eq2 afterwards.
    for target in product(range(n), repeat=len(eq2_vars)):
        if budget[0] <= 0:
            return None
        if deadline is not None and time.monotonic() >= deadline:
            return None
        tenv = dict(zip(eq2_vars, target))
        found = branch([_CELL_UNKNOWN] * (n * n))
        if found is not None:
            return found
    return None


def constraint_countermodel(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    orders: tuple[int, ...] = CONSTRAINT_ORDERS,
    time_budget: float = CONSTRAINT_TIME_BUDGET,
    per_order: bool = False,
) -> tuple[int, list[list[int]], str] | None:
    """Constraint-propagation search for a finite magma separating eq1 from eq2.

    `per_order=False` shares one deadline across the whole schedule (cheap tier:
    the successes there land in milliseconds). `per_order=True` gives each order
    its own slice, which is what the wide tier needs — the orders that pay off
    late in the schedule need tens of seconds each, and a shared deadline never
    reaches them.
    """
    global _CONSTRAINT_EXHAUSTED
    if len(eq1["variables"]) > 4 or len(eq2["variables"]) > 4:
        return None  # n^k instance blow-up; the cheap portfolio owns these
    shared_deadline = None if per_order else local_deadline(_eff_time(time_budget))
    complete = True
    for n in orders:
        deadline = (local_deadline(_eff_time(time_budget)) if per_order
                    else shared_deadline)
        if deadline is not None and time.monotonic() >= deadline:
            complete = False
            break
        if memory_exceeded() and not try_reclaim_memory():
            complete = False
            break
        budget = [CONSTRAINT_MAX_NODES]
        table = _cp_search(eq1, eq2, n, deadline, budget)
        if budget[0] <= 0:
            complete = False  # node cap hit: this order was not settled
        if table is None:
            continue
        note_hypothesis_model()
        # The search is never trusted: only a table that genuinely satisfies eq1
        # and genuinely refutes eq2 can leave this function.
        if table_is_counterexample(eq1, eq2, table):
            return n, table, f"false:constraint_fin{n}"
    if complete:
        _CONSTRAINT_EXHAUSTED = True
    return None


def local_model_counterexample(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    *,
    sizes: tuple[int, ...] = LOCAL_MODEL_SIZES,
    time_budget: float = LOCAL_MODEL_TIME_BUDGET,
    max_flips: int = LOCAL_MODEL_MAX_FLIPS,
    noise: float = LOCAL_MODEL_NOISE,
    seed: int = 0,
) -> tuple[int, list[list[int]], str] | None:
    """Randomized repair search for a finite magma separating eq1 from eq2.

    Last resort after the named tables, structured/affine/quadratic families,
    bounded enumeration, and duals have all missed. Every candidate is
    re-checked by `table_is_counterexample`, so this can only ever return a
    genuine witness.
    """
    deadline = local_deadline(_eff_time(time_budget))
    rng = random.Random(seed)
    lhs1, rhs1 = eq1["lhs"], eq1["rhs"]
    lhs2, rhs2 = eq2["lhs"], eq2["rhs"]
    if _EFFORT != "fast":
        # Frequent restarts beat long walks on these laws (sweep evidence),
        # and the extra size only pays once there is clock to spend.
        sizes = sizes + (6,)
        max_flips = 800

    for n in sizes:
        envs1 = _lm_envs(eq1, n)
        envs2 = _lm_envs(eq2, n)

        def bad_envs(table: list[list[int]]) -> list[dict[str, int]]:
            return [env for env in envs1
                    if _lm_eval(lhs1, env, table) != _lm_eval(rhs1, env, table)]

        def breaks_goal(table: list[list[int]]) -> bool:
            return any(_lm_eval(lhs2, env, table) != _lm_eval(rhs2, env, table)
                       for env in envs2)

        while time.monotonic() < deadline:
            table = [[rng.randrange(n) for _ in range(n)] for _ in range(n)]
            for _ in range(max_flips):
                if time.monotonic() >= deadline:
                    break
                bad = bad_envs(table)
                if not bad:
                    # A table with no bad env is a model of the hypothesis, so
                    # it counts toward the evidence the fallback policy reads.
                    note_hypothesis_model()
                    if breaks_goal(table) and table_is_counterexample(eq1, eq2, table):
                        return n, table, f"false:local_model{n}"
                    row, col = rng.randrange(n), rng.randrange(n)
                    table[row][col] = rng.randrange(n)
                    continue
                env = bad[rng.randrange(len(bad))]
                cells: set[tuple[int, int]] = set()
                _lm_cells(lhs1, env, table, cells)
                _lm_cells(rhs1, env, table, cells)
                if not cells:
                    break
                row, col = sorted(cells)[rng.randrange(len(cells))]
                if rng.random() < noise:
                    table[row][col] = rng.randrange(n)
                    continue
                best, best_score = table[row][col], len(bad) + 1
                for value in range(n):
                    previous, table[row][col] = table[row][col], value
                    score = len(bad_envs(table))
                    if score < best_score:
                        best, best_score = value, score
                    table[row][col] = previous
                table[row][col] = best
    return None



def _engine_gate() -> bool:
    """True -> stop launching deterministic engines now. A memory trip gets
    one reclaim attempt first, so the cheap routes after a ballooning engine
    still run; a passed hard deadline is final."""
    if _HARD_DEADLINE is not None and time.monotonic() >= _HARD_DEADLINE:
        return True
    if memory_exceeded() and not try_reclaim_memory():
        return True
    return False


# ---------------------------------------------------------------------------
# TRUE route table.
#
# Order is load-bearing: cheap syntactic recognisers first, search engines last,
# so a row that a millisecond pattern match can close never pays for the
# closures. This used to be ~380 lines of copy-pasted
# `x = fn(eq1, eq2); if x is not None: route, code = x; return {...}` blocks,
# which is how two defects hid in plain sight (2026-07-29): a duplicated
# `sandwich_left_projection_route` call whose second copy was unreachable, and a
# missing `_engine_gate()` before `narrow_grind`. Adding a route is now one line.
#
# Every entry has the same signature: (eq1, eq2) -> (route_label, lean_code) or
# None. The handful of routes with a different return shape get a thin adapter
# below rather than a special case in the dispatcher.
# ---------------------------------------------------------------------------

RouteResult = tuple[str, str]


def _direct_substitution_entry(
    eq1: dict[str, Any], eq2: dict[str, Any]
) -> RouteResult | None:
    direct = direct_substitution_route(eq1, eq2)
    if direct is None:
        return None
    mode, subst = direct
    call_expr = call_expression(eq1["variables"], subst)
    if mode == "symm":
        call_expr = f"({call_expr}).symm"
    route = "true:rewrite" if mode == "direct" else "true:rewrite:symm"
    return route, substitution_true_certificate(eq2["variables"], call_expr)


def _bridge_result(
    finder: Any, eq1: dict[str, Any], eq2: dict[str, Any]
) -> RouteResult | None:
    """Shared rendering for `bridge_route` / `completed_bridge_route`.

    Both return (name, left_subst, right_subst) and the last two characters of
    the name say which side of eq1 each leg starts from.
    """
    found = finder(eq1, eq2)
    if found is None:
        return None
    bridge_name, left_subst, right_subst = found
    left_call = call_expression(eq1["variables"], left_subst)
    right_call = call_expression(eq1["variables"], right_subst)
    left_source = int(bridge_name[-2])
    right_source = int(bridge_name[-1])
    left_to_mid = left_call if left_source == 0 else f"({left_call}).symm"
    mid_to_right = f"({right_call}).symm" if right_source == 0 else right_call
    return bridge_name, substitution_true_certificate(
        eq2["variables"], f"({left_to_mid}).trans ({mid_to_right})")


def _bridge_entry(eq1: dict[str, Any], eq2: dict[str, Any]) -> RouteResult | None:
    return _bridge_result(bridge_route, eq1, eq2)


def _completed_bridge_entry(
    eq1: dict[str, Any], eq2: dict[str, Any]
) -> RouteResult | None:
    return _bridge_result(completed_bridge_route, eq1, eq2)


def _rewrite_chain_entry(
    eq1: dict[str, Any], eq2: dict[str, Any]
) -> RouteResult | None:
    chain = find_rewrite_chain(eq1, eq2)
    if chain is None:
        return None
    routes, proof_expr = chain
    return ("true:rewrite_chain:" + ",".join(routes),
            substitution_true_certificate(eq2["variables"], proof_expr))


TRUE_ROUTES: tuple[Any, ...] = (
    # Derived-basis collapse recognisers.
    deep_repeat_singleton_route,
    reverse_deep_repeat_singleton_route,
    sandwich_repeat_singleton_route,
    outer_sandwich_singleton_route,
    forked_square_singleton_route,
    crossed_pair_singleton_route,
    repeated_prefix_product_constancy_route,
    double_tail_square_product_route,
    # Structural singleton / self-collapse families.
    nested_square_singleton_route,
    tail_square_singleton_route,
    paired_tail_singleton_route,
    wrapped_tail_singleton_route,
    middle_self_collapse_route,
    front_double_self_collapse_route,
    alternating_front_self_collapse_route,
    mirrored_alternating_front_self_collapse_route,
    square_twist_comm_route,
    # Projection-boundary families.
    sandwich_left_projection_route,
    nested_left_projection_route,
    specialized_left_projection_route,
    derived_left_projection_route,
    derived_right_projection_route,
    square_to_right_product_route,
    right_projection_collapse_route,
    # Absorption / constancy families.
    right_self_absorption_route,
    repeated_right_square_route,
    self_tail_triple_route,
    nested_left_absorption_route,
    # NOTE: `sandwich_left_projection_route` used to appear a second time here.
    # It is deterministic in (eq1, eq2), so the earlier call above already
    # decided it and the second copy could never fire. Removed 2026-07-29.
    left_row_constancy_route,
    product_constancy_route,
    # Substitution / bridging.
    _direct_substitution_entry,
    _bridge_entry,
    _completed_bridge_entry,
    projection_true_route,
    _rewrite_chain_entry,
    # Named collapse plus the wider absorption recognisers.
    c9_e1072_collapse_route,
    self_square_absorption_route,
    repeat_tail_absorption_route,
    universal_identity_route,
    absorption_context_bridge_route,
    absorption_closure_route,
)


def solve_problem(
    problem: dict[str, Any],
    *,
    false_time_budget: float | None = None,
) -> dict[str, Any] | None:
    reset_hypothesis_model_count()
    reset_constraint_evidence()
    try:
        eq1 = parse_equation(str(problem["equation1"]))
        eq2 = parse_equation(str(problem["equation2"]))
    except (KeyError, ValueError):
        return None

    def true_record(route: str, code: str) -> dict[str, Any]:
        return {
            "answer": make_true_answer(problem, code),
            "route": route,
            "priority": problem_priority(problem, eq1, eq2),
        }

    def false_record(n: int, table: list[list[int]], route: str) -> dict[str, Any]:
        return {
            "answer": make_false_answer(problem, n, table),
            "route": route,
            "priority": problem_priority(problem, eq1, eq2),
        }

    # Two pre-checks that do not take (eq1, eq2): reflexive reads the problem's
    # equation ids, and the singleton recogniser looks only at eq1.
    if is_reflexive_problem(problem):
        return true_record("true:reflexive", reflexive_true_certificate())

    singleton = singleton_route(eq1)
    if singleton is not None:
        singleton_var, singleton_on_lhs = singleton
        return true_record("true:singleton", singleton_true_certificate(
            eq1["variables"], eq2["variables"], singleton_var, singleton_on_lhs))

    for route_fn in TRUE_ROUTES:
        found = route_fn(eq1, eq2)
        if found is not None:
            route, code = found
            return true_record(route, code)

    if _engine_gate():
        return None
    counterexample = find_counterexample(eq1, eq2, time_budget=false_time_budget)
    if counterexample is not None:
        n, table, route = counterexample
        return false_record(n, table, route)

    # Constraint-propagation witness search, cheap tier. Placed here rather than
    # with the other last-resort search because when it succeeds it succeeds in
    # milliseconds (4 of 6 known-FALSE misses in ~0.05 s), and a FALSE row that
    # falls through to the general TRUE engines pays for all of them first.
    if _engine_gate():
        return None
    constrained = constraint_countermodel(eq1, eq2)
    if constrained is not None:
        n, table, route = constrained
        return false_record(n, table, route)

    # General TRUE engines. Each is expensive, so `_engine_gate()` is checked
    # before every one: it enforces the global hard deadline and the memory
    # guard modelling the 2048 MB sandbox (deep-tier closures were measured at
    # 5-17 GB RSS and were being OOM-killed in the playground).
    #
    # `equational_closure` runs first unless eq1 is an absorption hypothesis, in
    # which case `deep_absorption_closure` gets the first attempt. That single
    # conditional is why this block is a sequence rather than a flat table.
    closure_first = not absorption_hypothesis(eq1)
    engines: list[Any] = []
    if closure_first:
        engines.append(equational_closure_route)
    engines.append(deep_absorption_closure_route)
    if not closure_first:
        engines.append(equational_closure_route)
    engines.extend((
        derived_cp_closure_route,
        projection_bootstrap_route,
        lemma_bootstrap_route,
        lemma_chain_bootstrap_route,
        # Ground equality saturation with kernel-checkable extraction — the only
        # engine that reaches the ETP's MagmaEgg-style proofs. Placed after every
        # other TRUE engine as a pure addition (2026-07-23).
        egg_closure_route,
        # Egg pointed at a small lemma instead of the real goal. Strictly more
        # reachable than `egg_closure` (the target is smaller), so these go after
        # it: if egg can close the goal directly, that is the shorter certificate.
        # Collapse first — it is the most common pivot on the frontier by a wide
        # margin, and it subsumes every other lemma when it fires.
        egg_collapse_route,
        egg_priority_bootstrap_route,
        egg_bootstrap_route,
        # Demoted 2026-07-22: the playground judge rejected a narrow_grind cert
        # the local judge accepts (evaluation_normal_0048), and the proof kernel
        # cannot check the grind shape at all. Kernel-verifiable engines above
        # get first claim; grind is a last-ditch attempt on known-TRUE shapes.
        # It previously ran with NO preceding gate — the only engine to do so —
        # so it fired even after a memory trip or a passed deadline (fixed
        # 2026-07-29 by folding it into this loop).
        narrow_grind_true_route,
    ))

    for engine in engines:
        if _engine_gate():
            return None
        found = engine(eq1, eq2)
        if found is not None:
            route, code = found
            return true_record(route, code)

    # Last resort: the row is unresolved either way, so a randomized model
    # search costs nothing that was already being won. Runs after the TRUE
    # routes so solved implications never pay for it.
    if _engine_gate():
        return None
    late = local_model_counterexample(eq1, eq2)
    if late is not None:
        n, table, route = late
        return false_record(n, table, route)

    # Widest witness tier, reached only on a row nothing else claimed. Orders
    # beyond the cheap schedule and a much larger budget: the alternative for
    # this row is a speculative `true` guess, and a found witness is a certainty
    # where that guess is a ~7% lottery that also burns the judge's Lean timeout.
    if _engine_gate():
        return None
    wide = constraint_countermodel(
        eq1, eq2, orders=CONSTRAINT_WIDE_ORDERS,
        time_budget=CONSTRAINT_WIDE_PER_ORDER_BUDGET, per_order=True)
    if wide is not None:
        n, table, route = wide
        return false_record(n, table, route)
    return None


def load_json_line(stream: Any) -> dict[str, Any] | None:
    line = stream.readline()
    if not line:
        return None
    return json.loads(line)


def send_proxy_call(message: dict[str, Any]) -> dict[str, Any] | None:
    print(json.dumps(message, separators=(",", ":")), flush=True)
    return load_json_line(sys.stdin)


def judge_via_solo_proxy(answer: dict[str, Any]) -> dict[str, Any] | None:
    request = judge_answer_payload(answer)
    if request is None:
        log_stderr({"route": "output:skip_malformed_judge_answer"})
        return None
    request["call"] = "judge"
    return send_proxy_call(request)


def fallback_true_certificate() -> str:
    return reflexive_true_certificate()


def extract_json_object(text: str) -> dict[str, Any] | None:
    text = re.sub(r"<think>[\s\S]*?</think>", "", text or "").strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        obj = json.loads(match.group())
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def sanitize_lean_code(code: str, *, verdict: str) -> bool:
    if not isinstance(code, str) or not code.strip():
        return False
    if len(code.encode("utf-8")) > MAX_LEAN_CODE_BYTES:
        return False
    if verdict == "false" and len(code.encode("utf-8")) > MAX_FALSE_CERT_BYTES:
        return False
    if BANNED_LEAN_RE.search(code):
        return False
    has_submission = bool(re.search(r"\b(?:def|theorem)\s+submission\b", code))
    if not has_submission:
        return False
    # NOTE: we no longer require the literal ``intro G _ h`` shape. The proof is
    # always locally judge-verified before submission, so the judge — not this
    # pre-filter — is the correctness gate. Requiring a fixed intro pattern only
    # rejected valid proofs that intro the instance/hypothesis differently.
    saw_judge_problem = False
    for raw_line in code.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("--"):
            continue
        if line.startswith("import "):
            modules = line.split()[1:]
            if not modules:
                return False
            for module in modules:
                if module not in ALLOWED_IMPORTS:
                    return False
                if module == "JudgeProblem":
                    saw_judge_problem = True
    return saw_judge_problem


def normalize_table(value: Any) -> list[list[int]] | None:
    if not isinstance(value, list) or not value:
        return None
    n = len(value)
    if n < 1 or n > LLM_MAX_TABLE_N:
        return None
    table: list[list[int]] = []
    for row in value:
        if not isinstance(row, list) or len(row) != n:
            return None
        out_row: list[int] = []
        for cell in row:
            if type(cell) is not int or cell < 0 or cell >= n:
                return None
            out_row.append(cell)
        table.append(out_row)
    return table


def parse_llm_chain_terms(chain: Any, variables: set[str]) -> list[Term] | None:
    if not isinstance(chain, list) or len(chain) < 2:
        return None
    terms: list[Term] = []
    for item in chain:
        if not isinstance(item, str):
            return None
        try:
            terms.append(parse_term(item, variables))
        except ValueError:
            return None
    return terms


def chain_certificate_from_terms(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    chain_terms: list[Term],
) -> str | None:
    if chain_terms[0] != eq2["lhs"] or chain_terms[-1] != eq2["rhs"]:
        return None
    proofs: list[str] = []
    for src, dst in zip(chain_terms, chain_terms[1:]):
        step = proof_between_terms(eq1, src, dst)
        if step is None:
            return None
        proofs.append(step[0])
    if not proofs:
        return None
    expr = proofs[0]
    for proof in proofs[1:]:
        expr = f"({expr}).trans ({proof})"
    return substitution_true_certificate(eq2["variables"], expr)


def guided_chain_certificate_from_terms(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    chain_terms: list[Term],
) -> str | None:
    if chain_terms[0] != eq2["lhs"] or chain_terms[-1] != eq2["rhs"]:
        return None
    proofs: list[str] = []
    for src, dst in zip(chain_terms, chain_terms[1:]):
        # The model supplies coarse waypoints; bridging them is the solver's
        # job, so this per-edge search scales with the budget like the other
        # engines. At the old fixed 1.0 s it gave up on edges it could close.
        step = proof_between_terms_guided(
            eq1,
            eq2["variables"],
            src,
            dst,
            max_depth=_eff_depth(LLM_GUIDED_CHAIN_MAX_DEPTH),
            closure_time_budget=_eff_time(LLM_GUIDED_CHAIN_CLOSURE_TIME_BUDGET),
        )
        if step is None:
            return None
        proofs.append(step[0])
    if not proofs:
        return None
    expr = proofs[0]
    for proof in proofs[1:]:
        expr = f"({expr}).trans ({proof})"
    return substitution_true_certificate(eq2["variables"], expr)


def parse_llm_key_terms(raw: Any, variables: set[str]) -> list[Term]:
    terms: list[Term] = []
    if not isinstance(raw, list):
        return terms
    for item in raw:
        if not isinstance(item, str):
            continue
        try:
            terms.append(parse_term(item, variables))
        except ValueError:
            continue
    return terms


def _seeded_closure_expr(
    eq1: dict[str, Any],
    goal_eq: dict[str, Any],
    seed_terms: list[Term],
    *,
    time_budget: float,
) -> str | None:
    result = _closure_proof_expr_impl(
        eq1,
        goal_eq,
        route_name="llm:true:seeded_closure",
        chain_max_depth=LLM_SEEDED_CLOSURE_CHAIN_MAX_DEPTH,
        pool_limit=LLM_SEEDED_CLOSURE_POOL_LIMIT,
        frontier_limit=LLM_SEEDED_CLOSURE_FRONTIER_LIMIT,
        max_fills=LLM_SEEDED_CLOSURE_MAX_FILLS,
        term_slack=LLM_SEEDED_CLOSURE_TERM_SLACK,
        depth_slack=LLM_SEEDED_CLOSURE_DEPTH_SLACK,
        time_budget=time_budget,
        seed_terms=seed_terms,
    )
    if result is None:
        return None
    return result[1]


def seeded_closure_certificate_from_terms(
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    seed_terms: list[Term],
) -> str | None:
    if not seed_terms:
        return None
    total_deadline = local_deadline(LLM_SEEDED_CLOSURE_TOTAL_BUDGET)

    proof_expr = _seeded_closure_expr(
        eq1, eq2, seed_terms, time_budget=LLM_SEEDED_CLOSURE_TIME_BUDGET
    )
    if proof_expr is not None:
        return substitution_true_certificate(eq2["variables"], proof_expr)

    # Waypoint split: if a proposed term sits on the derivation path, prove
    # goal-lhs = waypoint and waypoint = goal-rhs separately, then glue.
    endpoints = (eq2["lhs"], eq2["rhs"])
    waypoints: list[Term] = []
    waypoint_seen: set[Term] = set(endpoints)
    for term in seed_terms:
        if term in waypoint_seen:
            continue
        waypoint_seen.add(term)
        waypoints.append(term)
    for waypoint in waypoints[:LLM_SEEDED_CLOSURE_MAX_WAYPOINTS]:
        remaining = total_deadline - time.monotonic()
        if remaining < 2.0 * LLM_SEEDED_CLOSURE_WAYPOINT_BUDGET:
            break
        left_eq = {"lhs": eq2["lhs"], "rhs": waypoint, "variables": eq2["variables"]}
        left_expr = _seeded_closure_expr(
            eq1, left_eq, seed_terms, time_budget=LLM_SEEDED_CLOSURE_WAYPOINT_BUDGET
        )
        if left_expr is None:
            continue
        right_eq = {"lhs": waypoint, "rhs": eq2["rhs"], "variables": eq2["variables"]}
        right_expr = _seeded_closure_expr(
            eq1, right_eq, seed_terms, time_budget=LLM_SEEDED_CLOSURE_WAYPOINT_BUDGET
        )
        if right_expr is None:
            continue
        glued = f"({left_expr}).trans ({right_expr})"
        return substitution_true_certificate(eq2["variables"], glued)
    return None


LLM_MAX_LEMMAS = 6
LLM_LEMMA_MAX_TERM_SIZE = 13


LLM_LEMMA_BINDER_PREFIX = re.compile(r"^\s*(?:∀|forall\b)[^,]*,\s*")


def usable_llm_lemma(text: str) -> dict[str, Any] | None:
    """Parse a model-proposed lemma, or None if it cannot be used safely.

    Binders are emitted verbatim into `∀ ... : G,` and `intro ...`, so they must
    be single lowercase letters and must not shadow the hypothesis `h` — the
    lemma's own proof refers to it. Size is bounded because the lemma becomes a
    proof-search target.

    A leading explicit quantifier is stripped first: the model writes
    `∀ a b, a ◇ b = b ◇ b` often enough to be worth accepting, and the lemma is
    universally quantified over its own variables either way.
    """
    if not isinstance(text, str):
        return None
    text = LLM_LEMMA_BINDER_PREFIX.sub("", text).strip().rstrip(".")
    try:
        lemma = parse_equation(text)
    except (ValueError, TypeError):
        return None
    variables = list(lemma["variables"])
    if not 1 <= len(variables) <= 4:
        return None
    if any(len(name) != 1 or not name.isalpha() or not name.islower() for name in variables):
        return None
    if "h" in variables:
        return None
    if max(term_size(lemma["lhs"]), term_size(lemma["rhs"])) > LLM_LEMMA_MAX_TERM_SIZE:
        return None
    return lemma


def llm_lemma_candidate(
    problem: dict[str, Any],
    eq1: dict[str, Any],
    eq2: dict[str, Any],
    obj: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    """Turn a model-proposed lemma into a fully verified certificate.

    The model contributes only the *idea* of which law to aim at; the solver
    proves the lemma from eq1 and the goal from the lemma, and the offline
    kernel re-checks both halves. Three sessions of evidence say this is the
    right split: the model proposes plausible structure but botches exact
    instantiation, which is precisely the part it no longer has to do.
    """
    raw = obj.get("lemma")
    extra = obj.get("lemmas")
    proposals: list[Any] = []
    if isinstance(raw, str):
        proposals.append(raw)
    if isinstance(extra, list):
        proposals.extend(extra)
    elif isinstance(extra, str):
        proposals.append(extra)
    if not proposals:
        return None, None

    reason = "lemma_unparsable"
    seen: set[str] = set()
    for proposal in proposals:
        if not isinstance(proposal, str) or proposal in seen:
            continue
        seen.add(proposal)
        if len(seen) > LLM_MAX_LEMMAS:
            break
        lemma = usable_llm_lemma(proposal)
        if lemma is None:
            continue
        proof_expr = lemma_applies_to_goal(lemma, eq2)
        if proof_expr is None:
            reason = "lemma_does_not_imply_goal"
            continue
        lemma_proof = lemma_closure_proof(
            eq1, lemma, time_budget=LLM_LEMMA_CLOSURE_TIME_BUDGET)
        if lemma_proof is None:
            reason = "lemma_not_derivable_from_hypothesis"
            continue
        return {
            "answer": make_true_answer(
                problem,
                lemma_certificate(lemma, lemma_proof, eq2["variables"], proof_expr),
            ),
            "route": "llm:true:lemma",
        }, None
    return None, reason


def candidate_from_llm_text_with_reason(
    problem: dict[str, Any],
    text: str,
    *,
    allow_raw_true: bool = True,
) -> tuple[dict[str, Any] | None, str]:
    obj = extract_json_object(text)
    if obj is None:
        return None, "no_json_object"
    if isinstance(obj.get("answer"), dict):
        obj = obj["answer"]
    verdict = str(obj.get("verdict", "")).lower()
    if verdict not in {"true", "false"}:
        return None, "missing_or_invalid_verdict"
    try:
        eq1 = parse_equation(str(problem["equation1"]))
        eq2 = parse_equation(str(problem["equation2"]))
    except (KeyError, ValueError):
        return None, "problem_parse_failed"

    if verdict == "false":
        raw_table = obj.get("counterexample_table", obj.get("table"))
        if raw_table is None:
            return None, "false_verdict_without_table"
        table = normalize_table(raw_table)
        if table is None:
            return None, "false_table_invalid_shape"
        if not table_is_counterexample(eq1, eq2, table):
            return None, "false_table_not_counterexample"
        return {
            "answer": make_false_answer(problem, len(table), table),
            "route": "llm:false:table",
        }, "ok"

    lemma_candidate, lemma_reject = llm_lemma_candidate(problem, eq1, eq2, obj)
    if lemma_candidate is not None:
        return lemma_candidate, "ok"

    chain = obj.get("chain")
    if chain is None and isinstance(obj.get("steps"), list):
        steps = obj["steps"]
        if steps and all(isinstance(step, dict) for step in steps):
            chain = [steps[0].get("from")]
            chain.extend(step.get("to") for step in steps)
    variables = set(eq2["variables"])
    seed_terms: list[Term] = []
    peak_raw = obj.get("peak_term")
    if isinstance(peak_raw, str):
        try:
            # Peak first: the waypoint split tries seeds in order.
            seed_terms.append(parse_term(peak_raw, variables))
        except ValueError:
            pass
    seed_terms.extend(parse_llm_key_terms(obj.get("key_terms"), variables))
    chain_reject_reason = "no_chain_supplied"
    if chain is not None:
        chain_terms = None
        if isinstance(chain, list) and any(
            isinstance(item, str) and not set(re.findall(r"\b([a-z])\b", item)).issubset(variables)
            for item in chain
        ):
            chain_reject_reason = "rewrite_chain_uses_non_goal_variables"
        else:
            chain_terms = parse_llm_chain_terms(chain, variables)
        if chain_terms is None and chain_reject_reason != "rewrite_chain_uses_non_goal_variables":
            chain_reject_reason = "rewrite_chain_parse_failed"
        elif chain_terms is not None:
            # Peak/key terms first: the waypoint split tries seeds in order.
            seed_terms = seed_terms + chain_terms
            code = chain_certificate_from_terms(eq1, eq2, chain_terms)
            if code is not None:
                return {
                    "answer": make_true_answer(problem, code),
                    "route": "llm:true:rewrite_chain",
                }, "ok"
            code = guided_chain_certificate_from_terms(eq1, eq2, chain_terms)
            if code is not None:
                return {
                    "answer": make_true_answer(problem, code),
                    "route": "llm:true:guided_chain",
                }, "ok"
            chain_reject_reason = "guided_chain_unproved_or_bad_endpoints"
    if seed_terms:
        code = seeded_closure_certificate_from_terms(eq1, eq2, seed_terms)
        if code is not None:
            return {
                "answer": make_true_answer(problem, code),
                "route": "llm:true:seeded_closure",
            }, "ok"
        chain_reject_reason += "; seeded bidirectional closure around your terms also failed"

    if lemma_reject is not None:
        chain_reject_reason = f"{lemma_reject}; {chain_reject_reason}"

    if isinstance(obj.get("proof"), str) or isinstance(obj.get("proof_body"), str):
        return None, "proof_body_unsupported"

    if not allow_raw_true:
        if isinstance(obj.get("code", obj.get("lean")), str):
            return None, "raw_true_disabled"
        return None, chain_reject_reason

    code = obj.get("code", obj.get("lean"))
    if isinstance(code, str) and sanitize_lean_code(code, verdict="true"):
        return {
            "answer": make_true_answer(problem, code),
            "route": "llm:true:raw_code",
        }, "ok"
    if isinstance(code, str):
        return None, "raw_code_sanitizer_rejected"
    return None, chain_reject_reason


def candidate_from_llm_text(
    problem: dict[str, Any],
    text: str,
    *,
    allow_raw_true: bool = True,
) -> dict[str, Any] | None:
    candidate, _reason = candidate_from_llm_text_with_reason(problem, text, allow_raw_true=allow_raw_true)
    return candidate


def terms_preview(terms: list[Term] | tuple[Term, ...], *, limit: int = 10) -> str:
    rendered: list[str] = []
    seen: set[str] = set()
    for term in terms:
        text = term_to_lean(term)
        if text in seen:
            continue
        seen.add(text)
        rendered.append(text)
        if len(rendered) >= limit:
            break
    if not rendered:
        return "(none)"
    return ", ".join(rendered)


def llm_middle_term_hints(eq1: dict[str, Any], eq2: dict[str, Any], *, limit: int = 18) -> list[Term]:
    allowed_vars = set(eq2["variables"])
    seen: set[Term] = set()
    hints: list[Term] = []

    def add(term: Term) -> None:
        if term in seen or not term_vars(term).issubset(allowed_vars):
            return
        seen.add(term)
        hints.append(term)

    for term in (eq2["lhs"], eq2["rhs"]):
        add(term)
    for term in term_subterms_tuple(eq2["lhs"]) + term_subterms_tuple(eq2["rhs"]):
        add(term)
    for term in term_subterms_tuple(eq1["lhs"]) + term_subterms_tuple(eq1["rhs"]):
        add(term)
    for seed in (eq2["lhs"], eq2["rhs"]):
        for new_term, _proof, _route in rewrite_steps_from_term(eq1, seed):
            add(new_term)

    hints.sort(key=lambda term: (0 if term in (eq2["lhs"], eq2["rhs"]) else 1, term_size(term), term_depth(term), term_to_lean(term)))
    return hints[:limit]


def solver_analysis(problem: dict[str, Any]) -> str:
    try:
        eq1 = parse_equation(str(problem["equation1"]))
        eq2 = parse_equation(str(problem["equation2"]))
    except (KeyError, ValueError):
        return "Could not parse one of the equations; return a TRUE full Lean file only if certain."
    hypothesis_subterms = list(term_subterms_tuple(eq1["lhs"]) + term_subterms_tuple(eq1["rhs"]))
    goal_subterms = list(term_subterms_tuple(eq2["lhs"]) + term_subterms_tuple(eq2["rhs"]))
    middle_hints = llm_middle_term_hints(eq1, eq2)
    deterministic_status: list[str] = []
    deterministic_status.append("singleton: yes" if singleton_route(eq1) else "singleton: no")
    deterministic_status.append("direct substitution: yes" if direct_substitution_route(eq1, eq2) else "direct substitution: no")
    deterministic_status.append("two-instance bridge: yes" if bridge_route(eq1, eq2) else "two-instance bridge: no")
    deterministic_status.append(
        "completed bridge/constancy: yes"
        if completed_bridge_route(eq1, eq2, max_trials=300)
        else "completed bridge/constancy: no"
    )
    deterministic_status.append("projection law: yes" if projection_law_route(eq1) else "projection law: no")
    deterministic_status.append("absorption-like hypothesis: yes" if absorption_hypothesis(eq1) else "absorption-like hypothesis: no")
    cues: list[str] = [
        f"hypothesis variables: {' '.join(eq1['variables']) or '(none)'}",
        f"goal variables: {' '.join(eq2['variables']) or '(none)'}",
        f"goal lhs: {eq2['lhs_text']}",
        f"goal rhs: {eq2['rhs_text']}",
        f"hypothesis subterms: {terms_preview(hypothesis_subterms, limit=12)}",
        f"goal subterms: {terms_preview(goal_subterms, limit=12)}",
        f"candidate chain middle terms: {terms_preview(middle_hints, limit=18)}",
        "deterministic route cues: " + "; ".join(deterministic_status),
    ]
    if absorption_hypothesis(eq1):
        cues.append("This is a good TRUE candidate for absorption/collapse/congruence chaining.")
    elif projection_cue(eq1, eq2):
        cues.append("Boundary/projection cues are risky; use TRUE only if the chain is explicit and solver-provable.")
    cues.append("Admissible term syntax: variables x y z w u v; binary products as a ◇ b; parentheses are allowed.")
    cues.append("A TRUE chain must start exactly with the goal lhs and end exactly with the goal rhs.")
    cues.append("Each adjacent TRUE chain step must be one explicit hypothesis rewrite, short rewrite chain, or bounded solver-owned closure/congruence step.")
    cues.append('Use {"proof_kind":"guided_chain"} when an adjacent chain edge needs more than one direct rewrite.')
    cues.append("If the chain needs a derived fact, include a lemmas array explaining it, but keep the chain terms concrete.")
    cues.append("Prefer the guided_chain: give intermediate terms and let the solver build the Lean proof; a raw Lean file is only a fallback.")
    cues.append("This row escaped deterministic finite-countermodel search, which is thorough but NOT exhaustive, so it is very likely TRUE — build a proof. Claim FALSE only with a concrete Cayley table you have actually verified; the solver re-checks it.")
    return "\n".join(cues)


def llm_problem_priority(priority: tuple[int, int, str], problem: dict[str, Any]) -> tuple[int, int, int, str]:
    try:
        eq1 = parse_equation(str(problem["equation1"]))
        eq2 = parse_equation(str(problem["equation2"]))
    except (KeyError, ValueError):
        return (9, priority[0], priority[1], str(problem.get("id", "")))

    score = 4
    if absorption_hypothesis(eq1):
        score -= 3
    if eq1["lhs"][0] == "var" or eq1["rhs"][0] == "var":
        score -= 1
    if eq2["lhs"][0] == "var" or eq2["rhs"][0] == "var":
        score -= 1
    if term_vars(eq2["lhs"]) == term_vars(eq2["rhs"]):
        score -= 1
    if projection_cue(eq1, eq2) and not absorption_hypothesis(eq1):
        score += 2
    if not term_vars(eq2["lhs"]).issubset(set(eq1["variables"])) or not term_vars(eq2["rhs"]).issubset(set(eq1["variables"])):
        score += 1
    score = max(0, score)
    size = term_size(eq1["lhs"]) + term_size(eq1["rhs"]) + term_size(eq2["lhs"]) + term_size(eq2["rhs"])
    return (score, priority[0], size, str(problem.get("id", "")))


def render_marathon_prompt(problem: dict[str, Any], analysis: str) -> str:
    replacements = {
        "problem.id": str(problem.get("id", "")),
        "problem.eq1_id": str(problem.get("eq1_id", "")),
        "problem.eq2_id": str(problem.get("eq2_id", "")),
        "problem.equation1": str(problem.get("equation1", "")),
        "problem.equation2": str(problem.get("equation2", "")),
        "solver.analysis": analysis,
        "history.attempts": "",
    }
    prompt = PROMPT
    for key, value in replacements.items():
        prompt = prompt.replace("{" + key + "}", value)
    return re.sub(r"\{(?:problem|solver|history)\.[a-zA-Z_]+\}", "", prompt)


def log_stderr(record: dict[str, Any]) -> None:
    print(json.dumps(record, separators=(",", ":")), file=sys.stderr, flush=True)


def log_route_count_chunks(route_counts: dict[str, int], *, max_chars: int = 850) -> None:
    chunk: dict[str, int] = {}
    for route, count in sorted(route_counts.items()):
        trial = dict(chunk)
        trial[route] = count
        record = {"route": "route_counts", "routes": trial}
        if chunk and len(json.dumps(record, separators=(",", ":"))) > max_chars:
            log_stderr({"route": "route_counts", "routes": chunk})
            chunk = {route: count}
        else:
            chunk = trial
    if chunk:
        log_stderr({"route": "route_counts", "routes": chunk})


def text_preview(text: str, limit: int = 160) -> str:
    compact = re.sub(r"\s+", " ", text or "").strip()
    if len(compact) <= limit:
        return compact
    return compact[:limit]


def marathon_llm_attempt(
    call_llm: Any,
    problem: dict[str, Any],
    config: dict[str, Any],
    deadline: float,
) -> dict[str, Any]:
    pid = str(problem.get("id"))
    started = time.monotonic()
    max_seconds = min(float(config.get("http_timeout_seconds", LLM_HTTP_TIMEOUT_SECONDS)), max(1.0, deadline - started - 5.0))
    result: dict[str, Any] = {"id": pid}
    try:
        analysis = solver_analysis(problem)
        prompt = render_marathon_prompt(problem, analysis)
        response = call_llm(prompt, config=config, max_seconds=max_seconds)
    except Exception as exc:  # noqa: BLE001
        result["error"] = str(exc)
        result["elapsed_seconds"] = round(time.monotonic() - started, 3)
        return result

    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    for key in ("tokens_used_call", "tokens_used_total", "budget_remaining"):
        if key in response:
            result[key] = response.get(key)
    if "error" in response:
        result["error"] = str(response.get("error", ""))
        return result

    response_text = str(response.get("response", ""))
    candidate, reject_reason = candidate_from_llm_text_with_reason(
        problem,
        response_text,
        allow_raw_true=marathon_allow_raw_true(),
    )
    if candidate is None:
        result["reject_reason"] = reject_reason
        result["response_chars"] = len(response_text)
        result["response_preview"] = text_preview(response_text)
        return result
    result["candidate"] = candidate
    result["route"] = str(candidate.get("route", "llm:unknown"))
    return result


def solo_llm_rounds() -> int:
    raw = os.environ.get("MAGMA_SOLO_LLM_ROUNDS")
    if raw is None:
        return LLM_MAX_ROUNDS
    try:
        return max(0, int(raw))
    except ValueError:
        return LLM_MAX_ROUNDS


def marathon_allow_raw_true() -> bool:
    raw = os.environ.get("MAGMA_MARATHON_ALLOW_RAW_TRUE", "")
    return raw.strip().lower() in {"1", "true", "yes", "debug"}


def run_solo() -> int:
    payload = load_json_line(sys.stdin)
    if not payload:
        return 0

    problem = payload.get("problem", payload)
    if not isinstance(problem, dict):
        return 0

    # Real per-problem budget: the proxy's start message wins, the env knob
    # is the local-testing fallback. The proxy started the clock at spawn,
    # so all deadlines anchor at _PROCESS_START.
    budget_info = payload.get("budget")
    budget_seconds = 0.0
    if isinstance(budget_info, dict):
        try:
            budget_seconds = float(budget_info.get("timeout_seconds") or 0.0)
        except (TypeError, ValueError):
            budget_seconds = 0.0
    if budget_seconds <= 0.0:
        budget_seconds = float(os.environ.get("JUDGE_SOLO_BUDGET_SECONDS", "3600"))

    # Solo affords one problem per subprocess (reference 3600 s), so the
    # deterministic engines should run at their widest setting.
    set_effort(effort_for_seconds(budget_seconds))

    # The proxy refuses calls issued with <= 1 s left and kills the process
    # at the deadline, so reserve room for the final fallback judge call.
    # Clamp the reserve so a tiny local-testing budget stays usable.
    reserve = min(SOLO_FALLBACK_RESERVE_SECONDS, 0.2 * budget_seconds)
    full_deadline = _PROCESS_START + budget_seconds - reserve
    det_deadline = min(
        full_deadline,
        _PROCESS_START + SOLO_DETERMINISTIC_SHARE * budget_seconds,
    )

    attempted: set[tuple[str, str]] = set()
    arm_memory_guard()
    set_hard_deadline(det_deadline)
    try:
        solved = solve_problem(problem)
    except Exception as exc:  # noqa: BLE001 - a crash must never eat the run
        log_stderr({"route": "solve:crash", "error": f"{type(exc).__name__}: {exc}"})
        solved = None
    if solved is not None:
        answer = dict(solved["answer"])
        attempted.add((str(answer.get("verdict")), str(answer.get("code"))))
        response = judge_via_solo_proxy(answer)
        if response:
            print(
                json.dumps(
                    {
                        "judge_status": response.get("status"),
                        "route": solved["route"],
                    }
                ),
                file=sys.stderr,
            )
            if response.get("status") == "accepted":
                return 0

    analysis = solver_analysis(problem)
    if solved is None:
        print(
            json.dumps(
                {
                    "route": "skip:deterministic",
                    "reason": "No deterministic certificate available; escalating through proxy LLM.",
                }
            ),
            file=sys.stderr,
        )
        # Insurance: bank one judged verdict now, so that even a wall-clock
        # kill mid-LLM-round leaves the run with a real judge status instead
        # of a harness ERROR. Cheap (the reflexive cert fails Lean fast), and
        # a later accepted certificate still wins because the proxy keeps the
        # first accepted answer.
        insurance = make_true_answer(problem, fallback_true_certificate())
        insurance_key = (str(insurance.get("verdict")), str(insurance.get("code")))
        attempted.add(insurance_key)
        insurance_response = judge_via_solo_proxy(insurance)
        if insurance_response:
            print(
                json.dumps(
                    {
                        "judge_status": insurance_response.get("status"),
                        "route": "fallback:insurance_reflexive",
                    }
                ),
                file=sys.stderr,
            )
            if insurance_response.get("status") == "accepted":
                return 0

    # The LLM phase may use the whole remaining clock (minus the reserve);
    # engines invoked while parsing chain candidates stay clamped to it.
    set_hard_deadline(full_deadline)

    feedback = ""
    for round_idx in range(solo_llm_rounds()):
        if time.monotonic() >= full_deadline - SOLO_LLM_ROUND_MIN_SECONDS:
            print(
                json.dumps({"route": "llm:stop_deadline", "round": round_idx}),
                file=sys.stderr,
            )
            break
        llm_response = send_proxy_call(
            {
                "call": "llm",
                "context": {
                    "round": str(round_idx),
                    "analysis": analysis,
                    "feedback": feedback,
                },
            }
        )
        if not llm_response or "error" in llm_response:
            print(
                json.dumps(
                    {
                        "route": "llm:skip",
                        "round": round_idx,
                        "error": (llm_response or {}).get("error", "no response"),
                    }
                ),
                file=sys.stderr,
            )
            break
        response_text = str(llm_response.get("response", ""))
        candidate, reject_reason = candidate_from_llm_text_with_reason(problem, response_text)
        if candidate is None:
            # Feed the parse-level rejection back to the next round. The proxy's
            # {history.attempts} only carries judge results (candidates that
            # reached the judge); parse rejects never do, so without this the
            # model gets no signal about malformed / non-goal-variable / unproved
            # chain outputs.
            feedback = (
                f"Previous answer rejected before judging: {reject_reason}. "
                "Return one valid JSON object using ONLY the goal's variables; "
                "prefer proof_kind guided_chain with small single-rewrite steps "
                "whose first term is the goal LHS and last term is the goal RHS."
            )
            print(
                json.dumps(
                    {
                        "route": "llm:reject",
                        "round": round_idx,
                        "reason": reject_reason,
                        "response_chars": len(response_text),
                        "response_preview": text_preview(response_text),
                    }
                ),
                file=sys.stderr,
            )
            continue
        feedback = ""
        answer = dict(candidate["answer"])
        key = (str(answer.get("verdict")), str(answer.get("code")))
        if key in attempted:
            print(json.dumps({"route": "llm:duplicate", "round": round_idx}), file=sys.stderr)
            continue
        attempted.add(key)
        judge_response = judge_via_solo_proxy(answer)
        if judge_response:
            print(
                json.dumps(
                    {
                        "judge_status": judge_response.get("status"),
                        "route": candidate["route"],
                        "round": round_idx,
                    }
                ),
                file=sys.stderr,
            )
            if judge_response.get("status") == "accepted":
                return 0
    # Final fallback: one speculative grind attempt beats the never-passing
    # reflexive cert (historical grind acceptance on unresolved TRUE rows is
    # small but nonzero). The judge's Lean timeout is clamped by the proxy to
    # the remaining wall clock.
    #
    # But it is only a guess about a row we think is TRUE, and it is worth
    # making only where TRUE is still open. If the FALSE search never found a
    # single model of the hypothesis, it refuted nothing and proved nothing --
    # a `verdict: "true"` there is a coin flip we have no reason to take, and
    # on a genuinely FALSE row it is a guaranteed miss that also burns the
    # judge's full Lean timeout. Measured 2026-07-23: seven `Eq168` playground
    # rows returned `TRUE INCORRECT` this way in 400-630 s each.
    if hypothesis_models_seen() == 0:
        print(
            json.dumps(
                {
                    "route": "fallback:skip_no_model_evidence",
                    "reason": (
                        "FALSE search inspected 0 models of the hypothesis; "
                        "a speculative TRUE verdict has no evidence behind it."
                    ),
                }
            ),
            file=sys.stderr,
        )
        return 0
    # `models_seen > 0` on its own is a much weaker signal than it looks. On the
    # six FALSE playground rows this fallback misfired on (2026-07-29) it read
    # 1050-7698 and every row was genuinely FALSE, so the guess could never be
    # accepted and each one burned 363-847 s. Record what the constraint search
    # actually established so the log distinguishes "searched orders 8-16 and
    # found nothing" from "ran out of clock", instead of implying evidence that
    # was never there.
    log_stderr({
        "route": "fallback:evidence",
        "models_seen": hypothesis_models_seen(),
        "constraint_search_exhausted": constraint_search_exhausted(),
    })
    fallback_route = "fallback:unsolved_grind"
    try:
        fallback_code = grind_true_certificate(
            parse_equation(str(problem["equation2"]))["variables"]
        )
    except (KeyError, ValueError):
        fallback_route = "fallback:unsolved_exact_h"
        fallback_code = fallback_true_certificate()
    fallback = make_true_answer(problem, fallback_code)
    fallback_key = (str(fallback.get("verdict")), str(fallback.get("code")))
    if fallback_key in attempted:
        return 0
    judge_response = judge_via_solo_proxy(fallback)
    if judge_response:
        print(
            json.dumps(
                {
                    "judge_status": judge_response.get("status"),
                    "route": fallback_route,
                }
            ),
            file=sys.stderr,
        )
    return 0


def iter_manifest(path: str) -> list[dict[str, Any]]:
    problems: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as manifest_file:
        for line in manifest_file:
            stripped = line.strip()
            if stripped:
                problems.append(json.loads(stripped))
    return problems


def append_answer(path: str, answer: dict[str, Any]) -> bool:
    payload = marathon_answer_payload(answer)
    if payload is None:
        log_stderr({"route": "output:skip_malformed_marathon_answer"})
        return False
    with open(path, "a", encoding="utf-8") as output_file:
        output_file.write(json.dumps(payload, separators=(",", ":")))
        output_file.write("\n")
        output_file.flush()
    return True


def marathon_reference_seconds() -> float:
    raw = os.environ.get("MAGMA_MARATHON_REF_SECONDS_PER_PROBLEM")
    if raw:
        try:
            value = float(raw)
            if value > 0:
                return value
        except ValueError:
            pass
    return MARATHON_REF_SECONDS_DEFAULT


def marathon_per_problem_budget(total_budget: float, problem_count: int, ref_seconds: float) -> float:
    """Wall-clock the FALSE portfolio may spend on one problem.

    Previously hard-capped at 4 s, which threw away most of the Marathon
    clock: at N=100 with the reference 180000 s budget this returned 4 s while
    ~1800 s per problem was available. The cap now scales with the real budget
    and only the share reserved for the cheap portfolio is taken here; the
    TRUE engines scale separately via the effort tier.
    """
    if problem_count <= 0:
        return 0.25
    share = total_budget / max(1, problem_count)
    compression = total_budget / max(1.0, ref_seconds * problem_count)
    floor = max(0.2, min(4.0, 0.5 + 5.0 * compression))
    return max(floor, min(60.0, 0.05 * share))


def load_marathon_llm() -> tuple[Any | None, Any | None, Any | None]:
    lib_dir = os.environ.get("JUDGE_MARATHON_LIB_DIR")
    if not lib_dir:
        return None, None, None
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
    try:
        marathon_llm = importlib.import_module("marathon_llm")
    except Exception:  # noqa: BLE001
        return None, None, None
    return marathon_llm.call_llm, marathon_llm.tokens_used, marathon_llm.budget_remaining


def run_marathon() -> int:
    manifest_path = os.environ.get("JUDGE_MARATHON_MANIFEST")
    output_path = os.environ.get("JUDGE_MARATHON_OUTPUT")
    if not manifest_path or not output_path:
        print("Missing Marathon manifest/output environment variables.", file=sys.stderr)
        return 2

    problems = iter_manifest(manifest_path)
    budget_seconds = float(os.environ.get("JUDGE_MARATHON_BUDGET_SECONDS", "3600"))
    budget_tokens = int(os.environ.get("JUDGE_MARATHON_BUDGET_TOKENS", "0"))
    deadline = time.monotonic() + budget_seconds
    # Global bound for every engine-local deadline: no single search loop may
    # cross the whole-run deadline, whatever its own budget says.
    arm_memory_guard()
    set_hard_deadline(deadline - 20.0)
    ref_seconds = marathon_reference_seconds()
    per_problem_budget = marathon_per_problem_budget(budget_seconds, len(problems), ref_seconds)
    # Reserve roughly half the clock for the deterministic pass; the LLM lane
    # and the output grace period get the rest.
    set_effort(effort_for_seconds(0.5 * budget_seconds / max(1, len(problems))))
    # Hard stop for the deterministic pass. The engines scale with the budget
    # now, so without this a hard manifest could spend the entire run in
    # closure search and never reach the LLM lane.
    deterministic_deadline = time.monotonic() + MARATHON_DETERMINISTIC_SHARE * budget_seconds

    prioritized: list[tuple[tuple[int, int, str], dict[str, Any]]] = []
    for problem in problems:
        try:
            eq1 = parse_equation(str(problem["equation1"]))
            eq2 = parse_equation(str(problem["equation2"]))
            priority = problem_priority(problem, eq1, eq2)
        except (KeyError, ValueError):
            priority = (9, 0, "skip:parse_error")
        prioritized.append((priority, problem))
    prioritized.sort(key=lambda item: item[0])

    route_counts: dict[str, int] = {}
    solved = 0
    deterministic_submitted = 0
    solved_ids: set[str] = set()
    for priority, problem in prioritized:
        if time.monotonic() + 5.0 >= min(deterministic_deadline, deadline):
            break
        clear_term_caches()
        answer_record = solve_problem(problem, false_time_budget=per_problem_budget)
        if answer_record is None:
            continue
        if not append_answer(output_path, answer_record["answer"]):
            continue
        route = str(answer_record["route"])
        route_counts[route] = route_counts.get(route, 0) + 1
        solved += 1
        deterministic_submitted += 1
        solved_ids.add(str(problem.get("id")))

    llm_calls = 0
    call_llm, tokens_used, budget_remaining = load_marathon_llm()
    unresolved_count = len(prioritized) - len(solved_ids)
    if unresolved_count > 0 and call_llm is None:
        print(
            json.dumps(
                {
                    "route": "llm:disabled",
                    "reason": "missing_marathon_proxy_library",
                    "unresolved": unresolved_count,
                    "budget_tokens": budget_tokens,
                }
            ),
            file=sys.stderr,
        )
    if unresolved_count > 0 and budget_tokens == 0:
        print(
            json.dumps(
                {
                    "route": "llm:disabled",
                    "reason": "zero_token_budget",
                    "unresolved": unresolved_count,
                    "budget_tokens": budget_tokens,
                }
            ),
            file=sys.stderr,
        )
    if call_llm is not None and budget_tokens != 0:
        unresolved = [
            (llm_problem_priority(priority, problem), problem)
            for priority, problem in prioritized
            if str(problem.get("id")) not in solved_ids
        ]
        unresolved.sort(key=lambda item: item[0])
        index = 0
        stop_llm = False
        with ThreadPoolExecutor(max_workers=MARATHON_LLM_BATCH_SIZE) as executor:
            while index < len(unresolved) and llm_calls < MARATHON_LLM_MAX_CALLS and not stop_llm:
                if time.monotonic() + 20.0 >= deadline:
                    break
                used = tokens_used() if tokens_used is not None else None
                if budget_tokens > 0 and used is not None and used >= budget_tokens:
                    log_stderr(
                        {
                            "route": "llm:disabled",
                            "reason": "token_budget_spent",
                            "tokens_used": used,
                            "budget_tokens": budget_tokens,
                        }
                    )
                    break
                remaining = budget_remaining() if budget_remaining is not None else None
                min_headroom = int(LLM_CONFIG["max_output_tokens"])
                if budget_tokens > 0 and remaining is not None and remaining >= 0 and remaining < min_headroom:
                    log_stderr(
                        {
                            "route": "llm:disabled",
                            "reason": "insufficient_remaining_token_headroom",
                            "budget_remaining": remaining,
                            "required_headroom": min_headroom,
                            "budget_tokens": budget_tokens,
                        }
                    )
                    break

                batch: list[dict[str, Any]] = []
                remaining_call_slots = MARATHON_LLM_MAX_CALLS - llm_calls
                while index < len(unresolved) and len(batch) < min(MARATHON_LLM_BATCH_SIZE, remaining_call_slots):
                    _priority, problem = unresolved[index]
                    index += 1
                    pid = str(problem.get("id"))
                    if pid not in solved_ids:
                        batch.append(problem)
                if not batch:
                    continue

                llm_calls += len(batch)
                log_stderr(
                    {
                        "route": "llm:batch_start",
                        "size": len(batch),
                        "ids": [str(problem.get("id")) for problem in batch],
                        "llm_calls": llm_calls,
                        "max_output_tokens": LLM_CONFIG["max_output_tokens"],
                        "reasoning_effort": LLM_CONFIG.get("reasoning_effort"),
                        "http_timeout_seconds": LLM_CONFIG.get("http_timeout_seconds"),
                        "allow_raw_true": marathon_allow_raw_true(),
                        "budget_remaining": remaining,
                    }
                )
                futures = {
                    executor.submit(marathon_llm_attempt, call_llm, problem, LLM_CONFIG, deadline): problem
                    for problem in batch
                }
                for future in as_completed(futures):
                    problem = futures[future]
                    pid = str(problem.get("id"))
                    try:
                        result = future.result()
                    except Exception as exc:  # noqa: BLE001
                        log_stderr({"route": "llm:error", "id": pid, "error": str(exc)})
                        continue
                    if "error" in result:
                        error = str(result.get("error", ""))
                        log_stderr(
                            {
                                "route": "llm:error",
                                "id": pid,
                                "error": error,
                                "elapsed_seconds": result.get("elapsed_seconds"),
                                "budget_remaining": result.get("budget_remaining"),
                            }
                        )
                        if "exhausted" in error or "budget" in error:
                            stop_llm = True
                        continue
                    if "candidate" not in result:
                        log_stderr(
                            {
                                "route": "llm:reject",
                                "id": pid,
                                "reason": result.get("reject_reason", "unknown"),
                                "elapsed_seconds": result.get("elapsed_seconds"),
                                "tokens_used_call": result.get("tokens_used_call"),
                                "budget_remaining": result.get("budget_remaining"),
                                "response_chars": result.get("response_chars"),
                                "response_preview": result.get("response_preview"),
                            }
                        )
                        continue

                    candidate = result["candidate"]
                    if not append_answer(output_path, candidate["answer"]):
                        continue
                    route = str(candidate["route"])
                    route_counts[route] = route_counts.get(route, 0) + 1
                    solved += 1
                    solved_ids.add(pid)
                    log_stderr(
                        {
                            "route": "llm:accepted_candidate",
                            "id": pid,
                            "candidate_route": route,
                            "elapsed_seconds": result.get("elapsed_seconds"),
                            "tokens_used_call": result.get("tokens_used_call"),
                            "budget_remaining": result.get("budget_remaining"),
                        }
                    )

    log_route_count_chunks(route_counts)
    log_stderr(
        {
            "submitted_deterministic": deterministic_submitted,
            "submitted_total": solved,
            "llm_calls": llm_calls,
            "budget_seconds": budget_seconds,
            "budget_tokens": budget_tokens,
            "reference_seconds_per_problem": ref_seconds,
            "per_problem_false_budget": round(per_problem_budget, 3),
            "route_kind_count": len(route_counts),
            "route_count_total": sum(route_counts.values()),
        }
    )
    return 0


def is_marathon_mode() -> bool:
    return bool(os.environ.get("JUDGE_MARATHON_MANIFEST") and os.environ.get("JUDGE_MARATHON_OUTPUT"))


def main() -> int:
    if is_marathon_mode():
        return run_marathon()
    return run_solo()


if __name__ == "__main__":
    raise SystemExit(main())
