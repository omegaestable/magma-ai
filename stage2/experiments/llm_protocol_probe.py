#!/usr/bin/env python3
"""Compare alternative LLM protocols on hard frontier rows, with real calls.

Phase 1 (threads): render one prompt per (row, protocol), call OpenRouter.
Phase 2 (processes): parse + verify with the solver's own primitives and the
offline oracles.  Nothing here edits the solver; every verdict is
kernel-checked, so a hallucinated law or table costs nothing but the call.

Protocols
  D  baseline    the shipped solver.PROMPT (control)
  A  derivation  a numbered ladder of universally quantified laws; each is
                 re-proved by multi-rule equality saturation over
                 {eq1} + the laws already proved (egg_ladder's rung mechanism
                 with LLM-supplied rungs)
  A2 derivation+ same, but each step carries its justification fields
  B  terms       terms only; fed to the shipped seeded bidirectional closure
  C  false-first ask for a Cayley table, with the TRUE-bias removed
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
sys.path.insert(0, str(REPO / "stage2" / "tests"))
sys.path.insert(0, str(REPO / "stage2" / "experiments"))

import oracles  # noqa: E402
import solver as S  # noqa: E402
from llm_balanced_eval import API_KEY, _client, fill_prompt  # noqa: E402


HEAD = """You reason about magmas. A magma is a type G with one binary operation
written `a DIAMOND b`. It is NOT associative and NOT commutative: never
reassociate `a DIAMOND (b DIAMOND c)` into `(a DIAMOND b) DIAMOND c`, and never
reorder `a DIAMOND b` into `b DIAMOND a`, unless the hypothesis proves it.

Problem {problem.id}: prove Equation{problem.eq1_id} implies Equation{problem.eq2_id}.
Hypothesis (Equation1):  {problem.equation1}
Goal       (Equation2):  {problem.equation2}

{solver.analysis}
"""

BODY_A = """
The deterministic solver has already run, from the hypothesis alone: equality
saturation, ordered Knuth-Bendix completion, and an exhaustive search for a
finite magma of size <= 7 that satisfies the hypothesis and breaks the goal.
It found no countermodel and no proof. In this family the hypothesis usually
forces the magma to have exactly ONE element, after which every goal holds.
What the solver cannot find is the INTERMEDIATE LAWS. That is the whole job.

################  ANSWER FORMAT: a derivation ladder  ################
Return exactly one JSON object:

{"verdict":"true","derivation":["<law 1>","<law 2>","<law 3>","..."]}

Each law is a universally quantified equation over FRESH variables a, b, c, d
-- one equation per string, for example "a DIAMOND a = a" or
"(a DIAMOND b) DIAMOND a = b". The list is a proof outline read top to bottom:
law k must follow from the hypothesis TOGETHER WITH laws 1..k-1 by a short
argument (a substitution or two, then rewriting).

THE SOLVER PROVES EACH LAW FOR YOU, independently, by equality saturation over
{hypothesis} together with every earlier law it has already proved, and it
tries the goal again after each one. You never write Lean and you never do
term bookkeeping by hand -- that is the #1 source of mistakes.

RULES THAT MAKE THIS WORK
* Small steps. A law the solver cannot prove in a few seconds is DROPPED and
  the rest of your ladder still runs, so ten small laws beat three clever ones.
* Order matters: only earlier laws are available to a later one.
* Aim at the collapse "a = b" (every element equal) whenever you can -- it
  closes ANY goal. Useful rungs on the way: "a DIAMOND a = a",
  "a DIAMOND b = a", "a DIAMOND b = b", "a DIAMOND b = a DIAMOND c",
  "a DIAMOND b = c DIAMOND b", "(a DIAMOND a) DIAMOND a = a",
  "a DIAMOND (b DIAMOND c) = a DIAMOND b".
* To invent a rung: substitute concrete terms for the hypothesis's variables
  so that the result matches (an instance of) the other side of the
  hypothesis, or of an earlier law; the equation left over is your rung.
* The last law may be the goal itself, written in the goal's own variables.
* Wrong laws are harmless -- they are simply unprovable and get dropped -- so
  guess boldly and give 6 to 12 of them.
* If you honestly believe the implication is FALSE, answer instead with
  {"verdict":"false","table":[[...],[...]]}: the full n x n Cayley table over
  {0,...,n-1}, rows indexed by the left argument. The solver re-checks every
  table exhaustively, so a wrong table is discarded harmlessly and a correct
  one wins the problem outright.

Output exactly ONE JSON object (first char {, last char }). No markdown, no
prose, no reasoning trace.
"""

BODY_A2 = """
The deterministic solver has already run, from the hypothesis alone: equality
saturation, ordered Knuth-Bendix completion, and an exhaustive search for a
finite magma of size <= 7 that satisfies the hypothesis and breaks the goal.
It found no countermodel and no proof. In this family the hypothesis usually
forces the magma to have exactly ONE element, after which every goal holds.
What the solver cannot find is the INTERMEDIATE LAWS. That is the whole job.

################  ANSWER FORMAT: a justified derivation  ################
Return exactly one JSON object:

{"verdict":"true","derivation":[
  {"law":"<equation>","from":["hypothesis"],"subst":"<what you substituted>"},
  {"law":"<equation>","from":["hypothesis","law 1"],"subst":"<...>"},
  "..."]}

Each "law" is a universally quantified equation over FRESH variables a, b, c, d
-- for example "a DIAMOND a = a" or "(a DIAMOND b) DIAMOND a = b". "from" names
which earlier facts you used and "subst" records the substitution you applied
to them; both are your own bookkeeping -- writing them down is what keeps the
law correct. THE SOLVER RE-PROVES EVERY LAW ITSELF by equality saturation over
{hypothesis} plus the laws it has already proved, and retries the goal after
each one, so you never write Lean and never do term bookkeeping.

RULES THAT MAKE THIS WORK
* Small steps: a law the solver cannot prove in a few seconds is dropped and
  the rest of your ladder still runs. Ten small laws beat three clever ones.
* Order matters: only earlier laws are available to a later one.
* Aim at the collapse "a = b" (every element equal) -- it closes ANY goal.
  Useful rungs: "a DIAMOND a = a", "a DIAMOND b = a", "a DIAMOND b = b",
  "a DIAMOND b = a DIAMOND c", "a DIAMOND b = c DIAMOND b",
  "(a DIAMOND a) DIAMOND a = a", "a DIAMOND (b DIAMOND c) = a DIAMOND b".
* The last law may be the goal itself, in the goal's own variables.
* Wrong laws are harmless -- unprovable ones are dropped -- so give 6 to 12.
* If you honestly believe the implication is FALSE, answer instead with
  {"verdict":"false","table":[[...],[...]]}: the full n x n Cayley table over
  {0,...,n-1}, rows indexed by the left argument. The solver re-checks it
  exhaustively, so a wrong table is discarded harmlessly.

Output exactly ONE JSON object (first char {, last char }). No markdown, no
prose, no reasoning trace.
"""

BODY_B = """
The deterministic solver runs a bidirectional equational search between the
goal's two sides and an equality-saturation engine from the hypothesis. Both
run out of room because the intermediate terms get large. What they need from
you is not a proof: it is the SET OF TERMS the proof passes through.

################  ANSWER FORMAT: terms only  ################
Return exactly one JSON object:

{"verdict":"true","key_terms":["<term>","<term>","..."],"peak_term":"<term>"}

* Every term uses ONLY the goal's variables, fully parenthesised, e.g.
  "(x DIAMOND (y DIAMOND x)) DIAMOND z".
* Give 8 to 16 key_terms: useful instantiations of the hypothesis's left or
  right side, absorbing shapes, and halfway terms between the goal's sides.
* "peak_term" is the single largest middle term -- many of these proofs expand
  both sides of the goal to one big common term and meet there. Naming it lets
  the solver search goal-lhs -> peak and peak -> goal-rhs separately, which is
  far easier than the whole jump.
* You do not have to be right about every term. The solver seeds its search
  with all of them and proves whatever it can, so extra terms cost nothing and
  one good term can finish the row.

Output exactly ONE JSON object (first char {, last char }). No markdown, no
prose, no reasoning trace.
"""

BODY_C = """
The deterministic solver could not prove this implication and could not refute
it with the finite magmas it knows how to search: named tables, affine and
quadratic families over small rings, every magma of order <= 3, and a
randomised repair search at orders 4 to 6. Its search is NOT exhaustive and it
is biased towards small orders, so a countermodel of order 5, 6, 7, 8 or 9 is
exactly what it misses.

Your job is to REFUTE the implication if you can.

################  ANSWER FORMAT: a Cayley table  ################
{"verdict":"false","table":[[...],[...],"..."]}

The full n x n table of `a DIAMOND b` over the carrier {0,...,n-1}: row i is
the list of i*0, i*1, ..., i*(n-1) under the operation. Choose n between 4 and
9. The table must satisfy the HYPOTHESIS for every assignment of its variables
and must BREAK the goal for at least one assignment. Build it from structure
rather than by guessing: a group operation twisted by a permutation, an affine
form `a DIAMOND b = (f*a + g*b + c) mod n`, a left or right zero adjoined to a
smaller magma, or a quasigroup table are all good starting points.

The solver re-checks the table exhaustively before submitting it, so a wrong
table is discarded harmlessly and a correct one wins the problem outright.
Give your single best table.

If after real effort you are convinced no finite countermodel exists, answer
{"verdict":"true","derivation":["<law 1>","<law 2>","..."]} instead, where each
law is a universally quantified equation over fresh variables a, b, c that
follows from the hypothesis, ending if possible in the collapse "a = b"; the
solver proves each law itself by equality saturation.

Output exactly ONE JSON object (first char {, last char }). No markdown, no
prose, no reasoning trace.
"""


BODY_E = """
This row survived every deterministic engine: equality saturation from the
hypothesis, ordered Knuth-Bendix completion, a bidirectional search between the
goal's two sides, and an exhaustive hunt for a finite magma of size <= 7 that
satisfies the hypothesis and breaks the goal. It also ALREADY TRIED, and failed
to prove, every one of these standard laws, so do not propose them:
  a = b            a DIAMOND a = a        a DIAMOND b = a      a DIAMOND b = b
  a DIAMOND b = b DIAMOND a               a DIAMOND b = a DIAMOND c
  a DIAMOND b = c DIAMOND b               (a DIAMOND a) DIAMOND a = a
What it cannot do is invent a law SPECIFIC TO THIS HYPOTHESIS. That is the job.

################  ANSWER FORMAT  ################
Return exactly one JSON object:

{"verdict":"true","derivation":[
  {"law":"<equation over fresh a,b,c>","from":["hypothesis"],
   "subst":"<the substitution you applied, variable by variable>"},
  {"law":"<equation>","from":["hypothesis","law 1"],"subst":"<...>"} ]}

Write "subst" HONESTLY and in full: it is the arithmetic that keeps the law
correct, and a law you cannot justify is a law that will not verify. Derive a
law like this: instantiate the hypothesis at concrete terms so that one side
becomes an instance of the other side, or of a law you already have; whatever
equation is left over is your new law. Then repeat with the new law in hand.

THE SOLVER RE-PROVES EVERY LAW ITSELF by equality saturation over {hypothesis}
plus the laws it has already proved, and retries the goal after each one. You
never write Lean. A law it cannot prove is dropped and the rest of your ladder
still runs, so 5 to 10 honest, hypothesis-specific laws are what to aim for.
Ordinary consequences are fine -- they do not have to be famous laws.

If instead you can exhibit a finite magma where the hypothesis HOLDS and the
goal FAILS, that wins the row outright and is often much easier:
{"verdict":"false","table":[[...],[...]]} -- the full n x n Cayley table over
{0,...,n-1} for 4 <= n <= 9, row i listing i DIAMOND 0, ..., i DIAMOND (n-1).
The solver re-checks the table exhaustively, so a wrong one is discarded
harmlessly.

Output exactly ONE JSON object (first char {, last char }). No markdown, no
prose, no reasoning trace.
"""


BODY_F = """
YOUR ONLY JOB HERE IS TO REFUTE THIS IMPLICATION. Do not try to prove it.

A refutation is a finite magma: a carrier {0,...,n-1} and an n x n table for
`a DIAMOND b`. It works when BOTH of these hold:
  (1) the HYPOTHESIS is true for every assignment of its variables from the
      carrier -- all n^k assignments, no exceptions;
  (2) the GOAL is false for at least one assignment.
The deterministic solver has already checked every magma of order <= 3, the
named tables, and the affine and quadratic families over small rings, so the
answer you want is a STRUCTURED table of order 4 to 8.

WHAT ACTUALLY WORKS ON THESE LAWS
* Start from a group or a quasigroup on Z_n and twist it: `a DIAMOND b =
  p(a) + q(b) + c mod n`, or `a DIAMOND b = s(a - b) mod n` for a permutation s.
* Hypotheses shaped `x = <term in x,y,z>` force every left- or right-
  multiplication map to be a bijection, so a Latin square (each row and each
  column a permutation of the carrier) is nearly always the right shape.
* A constant table, a table with a repeated row, or anything of order 1 or 2
  will NOT satisfy a hypothesis of that shape. Do not send one.

BEFORE YOU ANSWER, CHECK YOUR TABLE. Pick the hypothesis, walk a few
assignments through your table by hand, and confirm both sides land on the same
element; then find the assignment that breaks the goal and write it down.

################  ANSWER FORMAT  ################
{"verdict":"false","tables":[[[...],[...]],[[...],[...]]],
 "breaks":"<the assignment that falsifies the goal>"}

"tables" is a LIST of 1 to 5 candidate tables, best first; each table is a list
of n rows and row i lists i DIAMOND 0, i DIAMOND 1, ..., i DIAMOND (n-1).
The solver checks every table you send, exhaustively, and keeps the first that
works -- so send your alternatives too. A wrong table costs nothing.

Output exactly ONE JSON object (first char {, last char }). No markdown, no
prose, no reasoning trace.
"""

DIAMOND = "◇"


def _mk(body: str) -> str:
    return (HEAD + body).replace("DIAMOND", DIAMOND)


PROTOCOLS = {"D": None, "A": _mk(BODY_A), "A2": _mk(BODY_A2),
             "B": _mk(BODY_B), "C": _mk(BODY_C), "E": _mk(BODY_E),
             "F": _mk(BODY_F)}


def to_diamond(text: str) -> str:
    return str(text).replace("*", DIAMOND)


TRUE_PUSH = (
    "This row escaped deterministic finite-countermodel search",
    "Boundary/projection cues are risky",
    "This is a good TRUE candidate",
    "A TRUE chain must start",
    "Each adjacent TRUE chain step",
    'Use {"proof_kind"',
    "If the chain needs a derived fact",
    "Prefer the guided_chain",
)


def neutral_analysis(problem: dict) -> str:
    """`solver_analysis` with the verdict-steering cues removed.

    The shipped block ends with "it is very likely TRUE -- build a proof",
    which every protocol inherits through `{solver.analysis}`.  Stripping it
    isolates the protocol from the prior.
    """
    lines = S.solver_analysis(problem).splitlines()
    return "\n".join(line for line in lines
                     if not any(line.startswith(p) for p in TRUE_PUSH))


def build_prompt(protocol: str, problem: dict, analysis_mode: str = "full") -> str:
    shown = dict(problem)
    shown["equation1"] = to_diamond(problem["equation1"])
    shown["equation2"] = to_diamond(problem["equation2"])
    analysis = (neutral_analysis(problem) if analysis_mode == "neutral"
                else S.solver_analysis(problem))
    template = PROTOCOLS[protocol] or S.PROMPT
    return fill_prompt(template, shown, analysis, "")


def call_llm(prompt: str, args) -> dict:
    import openai
    extra_body: dict = {}
    if args.reasoning:
        extra_body["reasoning"] = {"effort": args.reasoning}
    if not args.no_provider_pin:
        extra_body["provider"] = {"order": ["DeepInfra"], "allow_fallbacks": False,
                                  "quantizations": ["bf16"]}
    last = ""
    for attempt in range(args.retries + 1):
        try:
            t0 = time.monotonic()
            resp = _client(args.http_timeout).chat.completions.create(
                model=args.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=args.max_tokens, temperature=0.0, seed=0,
                extra_body=extra_body or None,
            )
            choice = resp.choices[0]
            msg = choice.message
            content = getattr(msg, "content", None) or ""
            reasoning = (getattr(msg, "reasoning", None)
                         or getattr(msg, "reasoning_content", None) or "")
            usage = resp.usage
            return {"text": content or reasoning,
                    "reasoning_chars": len(reasoning),
                    "truncated": choice.finish_reason == "length",
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                    "seconds": round(time.monotonic() - t0, 1)}
        except (openai.APITimeoutError, openai.APIConnectionError,
                openai.RateLimitError, openai.InternalServerError) as e:
            last = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(min(2 ** attempt, 8))
        except Exception as e:  # noqa: BLE001
            return {"error": f"{type(e).__name__}: {str(e)[:200]}"}
    return {"error": last or "failed"}


def fetch_one(job) -> dict:
    problem, protocol, args = job
    row = {"id": str(problem["id"]), "protocol": protocol,
           "tag": problem.get("_tag", "")}
    prompt = build_prompt(protocol, problem, args.analysis_mode)
    row["prompt_chars"] = len(prompt)
    res = call_llm(prompt, args)
    if "error" in res:
        row.update(status="llm_error", detail=res["error"])
        return row
    row.update({k: v for k, v in res.items() if k != "text"})
    row["_text"] = res["text"]
    return row


# ---------------------------------------------------------------- verification

def _candidate_tables(obj):
    out = []
    many = obj.get("tables")
    if isinstance(many, list):
        for item in many:
            if isinstance(item, list):
                out.append(item)
    one = obj.get("counterexample_table", obj.get("table"))
    if one is not None:
        out.append(one)
    return out


def _try_false_table(problem, obj, eq1, eq2):
    raws = _candidate_tables(obj)
    if not raws:
        return None, "no_table"
    why = "table_bad_shape"
    table = None
    for raw in raws:
        cand = S.normalize_table(raw)
        if cand is None:
            continue
        why = "table_not_counterexample"
        if S.table_is_counterexample(eq1, eq2, cand):
            table = cand
            break
    if table is None:
        return None, why
    code = S.make_false_answer(problem, len(table), table,
                               equations=(eq1, eq2))["code"]
    oracles.check_false_certificate(code, eq1, eq2)
    return code, "ok"


def _law_texts(obj):
    raw = obj.get("derivation") or obj.get("laws") or obj.get("lemmas")
    out = []
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return out
    for item in raw:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            for key in ("law", "equation", "lemma", "eq"):
                if isinstance(item.get(key), str):
                    out.append(item[key])
                    break
    return out


COLLAPSE = {"lhs": ("var", "a"), "rhs": ("var", "b"),
            "variables": ["a", "b"], "text": "a = b"}


def replay_derivation(problem, obj, eq1, eq2, step_budget, stats):
    """egg_ladder's rung mechanism, with the LLM supplying the rungs."""
    laws = _law_texts(obj)
    stats["laws_proposed"] = len(laws)
    if not laws:
        return None, "no_derivation"
    rules = [S._egg_rule_from(eq1, "h")]
    blocks: list = []
    seen = {S.canonical_law_key(eq1)}
    verified = 0
    unparsed = 0
    for text in laws[:16]:
        lemma = None
        try:
            lemma = S.usable_llm_lemma(str(text))
        except Exception:  # noqa: BLE001
            lemma = None
        if lemma is None:
            unparsed += 1
            continue
        key = S.canonical_law_key(lemma)
        if key in seen:
            continue
        seen.add(key)
        proof = S.egg_saturate_prove_multi(rules, lemma, time_budget=step_budget)
        if proof is None:
            stats.setdefault("unproved", []).append(str(text))
            continue
        verified += 1
        stats.setdefault("proved", []).append(str(text))
        name = f"hlem{len(blocks)}"
        blocks.append((name, lemma, proof))
        rules.append(S._egg_rule_from(lemma, name))
        stats["laws_verified"] = verified
        stats["laws_unparsed"] = unparsed
        gproof = S.egg_saturate_prove_multi(rules, eq2, time_budget=step_budget)
        if gproof is not None:
            return S._lemma_chain_goal_certificate(
                blocks, eq2["variables"], gproof), "ladder_goal"
        expr = S.lemma_closes_goal(lemma, eq2)
        if expr is not None:
            return S._lemma_chain_goal_certificate(
                blocks, eq2["variables"], expr), "ladder_pivot"
        cproof = S.egg_saturate_prove_multi(rules, COLLAPSE,
                                            time_budget=step_budget)
        if cproof is not None:
            cblocks = blocks + [("hcol", COLLAPSE, cproof)]
            return S._lemma_chain_goal_certificate(
                cblocks, eq2["variables"], "hcol _ _"), "ladder_collapse"
    stats["laws_verified"] = verified
    stats["laws_unparsed"] = unparsed
    return None, "ladder_exhausted"


def verify_one(job) -> dict:
    row, problem, effort, step_budget = job
    if row.get("status") == "llm_error":
        return row
    S.set_effort(effort)
    S.set_hard_deadline(None)
    S.clear_term_caches()
    text = row.pop("_text", "")
    stats: dict = {}
    obj = S.extract_json_object(text)
    if obj is None:
        row.update(status="unsettled", reject="no_json_object")
        return row
    if isinstance(obj.get("answer"), dict):
        obj = obj["answer"]
    row["claimed"] = str(obj.get("verdict", "")).lower() or None
    eq1 = S.parse_equation(str(problem["equation1"]))
    eq2 = S.parse_equation(str(problem["equation2"]))
    t0 = time.monotonic()
    try:
        code, why = _try_false_table(problem, obj, eq1, eq2)
    except oracles.OracleError as exc:
        code, why = None, ("oracle:" + str(exc))[:120]
    if code is not None:
        row.update(status="settled_false", route="llm:false:table",
                   code_bytes=len(code.encode("utf-8")),
                   verify_seconds=round(time.monotonic() - t0, 1),
                   false_reject="ok")
        return row
    row["false_reject"] = why
    code = None
    route = ""
    if row["protocol"] in ("A", "A2", "C", "E"):
        code, route = replay_derivation(problem, obj, eq1, eq2,
                                        step_budget, stats)
    if code is None:
        cand, reason = S.candidate_from_llm_text_with_reason(
            problem, text, allow_raw_true=False)
        if cand is not None:
            code, route = cand["answer"]["code"], cand["route"]
        else:
            stats["shipped_reject"] = reason
    row.update(stats)
    row["verify_seconds"] = round(time.monotonic() - t0, 1)
    if code is None:
        row["status"] = "unsettled"
        row["reject"] = route or stats.get("shipped_reject", "no_candidate")
        return row
    try:
        oracles.check_no_banned_tactics(code, "llm")
        shape = oracles.classify_true_certificate(code)
        if shape == "singleton":
            oracles.check_true_singleton_certificate(code, eq1)
        elif shape == "exact_expr":
            oracles.check_true_exact_certificate(code, eq1, eq2)
        elif shape == "lemma":
            oracles.check_true_lemma_certificate(code, eq1, eq2)
        elif shape == "lemma_chain":
            oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
        else:
            raise oracles.OracleError("unverifiable shape " + str(shape))
        row["status"] = "settled_true"
        row["route"] = route or "llm:true"
        row["code_bytes"] = len(code.encode("utf-8"))
        row["code"] = code
    except oracles.OracleError as exc:
        row["status"] = "unsound_candidate"
        row["detail"] = str(exc)[:200]
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--protocols", default="D,A,B")
    ap.add_argument("--model", default="openai/gpt-oss-120b")
    ap.add_argument("--reasoning", default="low")
    ap.add_argument("--max-tokens", type=int, default=65536)
    ap.add_argument("--http-timeout", type=float, default=600.0)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--verify-workers", type=int, default=4)
    ap.add_argument("--step-budget", type=float, default=3.0)
    ap.add_argument("--effort", default="fast")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-provider-pin", action="store_true")
    ap.add_argument("--analysis-mode", choices=("full", "neutral"),
                    default="full")
    ap.add_argument("--raw-out", type=Path, default=None)
    ap.add_argument("--reuse-raw", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if not API_KEY:
        print("no key", file=sys.stderr)
        return 2
    problems = [json.loads(l) for l in
                args.file.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        problems = problems[: args.limit]
    protocols = [p for p in args.protocols.split(",") if p]
    by_id = {str(p["id"]): p for p in problems}

    if args.reuse_raw:
        fetched = [json.loads(l) for l in
                   args.reuse_raw.read_text(encoding="utf-8").splitlines()
                   if l.strip()]
        fetched = [r for r in fetched
                   if r["protocol"] in protocols and r["id"] in by_id]
    else:
        jobs = [(p, proto, args) for proto in protocols for p in problems]
        print("phase1: %d calls model=%s reasoning=%s max_tokens=%d"
              % (len(jobs), args.model, args.reasoning, args.max_tokens),
              flush=True)
        t0 = time.monotonic()
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            fetched = list(pool.map(fetch_one, jobs))
        print("phase1 done in %.0fs" % (time.monotonic() - t0), flush=True)
        if args.raw_out:
            args.raw_out.parent.mkdir(parents=True, exist_ok=True)
            with args.raw_out.open("w", encoding="utf-8") as fh:
                for r in fetched:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    jobs2 = [(dict(r), by_id[r["id"]], args.effort, args.step_budget)
             for r in fetched]
    t1 = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.verify_workers) as pool:
        done = list(pool.map(verify_one, jobs2, chunksize=1))
    print("phase2 done in %.0fs" % (time.monotonic() - t1), flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for r in done:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    import collections
    for proto in protocols:
        sub = [r for r in done if r["protocol"] == proto]
        if not sub:
            continue
        st = collections.Counter(r.get("status") for r in sub)
        tok = sum(r.get("total_tokens") or 0 for r in sub)
        sec = [r.get("seconds") or 0 for r in sub]
        print("%s: n=%d %s tokens=%d mean_call_s=%.0f"
              % (proto, len(sub), dict(st), tok, sum(sec) / max(1, len(sec))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
