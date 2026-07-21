#!/usr/bin/env python3
"""Dev-loop harness for FALSE counterexample tables with gpt-oss-120b via OpenRouter.

For each FALSE-frontier problem (a FALSE-labeled row the deterministic solver
skips) this runs a self-verifying repair loop:

    round r:
      prompt = FALSE_PROMPT filled with the problem + feedback so far
      text   = gpt-oss-120b(prompt)
      table  = parse "counterexample_table" from the reply
      check  = solver.table_is_counterexample(eq1, eq2, table)   # pure Python
      if check -> WIN (optionally confirm with the local Lean judge)
      else feed the exact failing constraint back into round r+1

The table check is exact and local, so a WIN here is a certain FALSE certificate
(the shipped decideFin! certificate is deterministic given a correct table).
Dev-only tool; mirrors dev_true_loop.py conventions. Secret-safe.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import sys
import threading
import time
from datetime import date
from itertools import product
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
OFFICIAL = REPO / "vendor" / "stage2-official"
SOLVER_DIR = REPO / "stage2" / "solver"
EXPERIMENTS = REPO / "stage2" / "experiments"

sys.path.insert(0, str(EXPERIMENTS))
import local_runner_env  # noqa: E402


def _resolve_key() -> str:
    repo_vals = local_runner_env.repo_env_values()
    return (
        repo_vals.get("OPENROUTER_API_KEY")
        or repo_vals.get("OPENAI_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY", "")
        or os.environ.get("OPENAI_API_KEY", "")
    )


API_KEY = _resolve_key()
if API_KEY:
    os.environ["OPENROUTER_API_KEY"] = API_KEY
    os.environ["OPENAI_API_KEY"] = API_KEY

sys.path.insert(0, str(OFFICIAL))
sys.path.insert(0, str(SOLVER_DIR))
import solver as S  # noqa: E402

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

FALSE_PROMPT = """You disprove implications between magma laws. A magma is a set with one
binary operation `a ◇ b` given by an n x n table: entry table[i][j] = i ◇ j,
values 0..n-1 (0-indexed).

This implication is FALSE. Find a finite magma satisfying Equation1 (for ALL
variable assignments) while violating Equation2 (for AT LEAST ONE assignment).

Problem {problem.id}: refute Equation{problem.eq1_id} implies Equation{problem.eq2_id}.
Equation1 (must HOLD everywhere):  {problem.equation1}
Equation2 (must FAIL somewhere):   {problem.equation2}

A deterministic search already tried and FAILED with: a library of known small
tables, structured families (left/right projections, constants), affine maps
x ◇ y = (a*x + b*y + c) mod n for n in {{2,3,4,5,7,8,9}}, quadratic maps mod
{{2,3,5,7}}, dual (transposed) forms of all of these, and brute force over ALL
tables of size n <= 3. So: n = 2 or 3 will NOT work, and plain affine maps mod n
will likely NOT work. Try n between 4 and {solver.max_n}. Promising ideas:
  - affine maps with a TWIST: mostly linear but change a few entries, then
    re-check Equation1 by hand on the changed rows/columns;
  - block constructions: two sub-magmas glued so Equation1 survives but a
    cross-block product breaks Equation2;
  - idempotent tables (i ◇ i = i) when Equation1 allows, with asymmetric
    off-diagonal entries breaking Equation2;
  - tables built from a function f: i ◇ j = f(i) or f(j) variants.

Work strategy: choose a candidate structure, VERIFY Equation1 on ALL assignments
(be systematic: if Equation1 has 3 variables and n = 4 that is 64 checks — use the
structure to argue most cases, hand-check the rest), then find one assignment
violating Equation2.

{solver.feedback}

Output exactly ONE JSON object (first char {{, last char }}), no markdown, no prose:
{{"verdict":"false","n":<size>,"counterexample_table":[[...],...]}}
"""


def fill_prompt(problem: dict, feedback: str, max_n: int) -> str:
    out = FALSE_PROMPT
    for key, value in {
        "{problem.id}": str(problem.get("id", "")),
        "{problem.eq1_id}": str(problem.get("eq1_id", "")),
        "{problem.eq2_id}": str(problem.get("eq2_id", "")),
        "{problem.equation1}": str(problem.get("equation1", "")),
        "{problem.equation2}": str(problem.get("equation2", "")),
        "{solver.max_n}": str(max_n),
        "{solver.feedback}": feedback,
    }.items():
        out = out.replace(key, value)
    return out.replace("{{", "{").replace("}}", "}")


_thread_local = threading.local()


def _client(timeout: float):
    cli = getattr(_thread_local, "client", None)
    if cli is None:
        from openai import OpenAI
        cli = OpenAI(api_key=API_KEY, base_url=OPENROUTER_BASE_URL, timeout=timeout)
        _thread_local.client = cli
    return cli


def call_llm(prompt: str, args) -> dict[str, Any]:
    import openai

    extra_body: dict = {"reasoning": {"effort": args.reasoning}}
    if not args.allow_fallbacks:
        extra_body["provider"] = {"order": ["DeepInfra"], "allow_fallbacks": False,
                                  "quantizations": ["bf16"]}
    last_err = ""
    for attempt in range(args.retries + 1):
        try:
            t0 = time.monotonic()
            resp = _client(args.http_timeout).chat.completions.create(
                model=args.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                seed=args.seed,
                extra_body=extra_body,
            )
            dt = time.monotonic() - t0
            choice = resp.choices[0]
            msg = choice.message
            content = getattr(msg, "content", None) or ""
            reasoning = getattr(msg, "reasoning", None) or getattr(msg, "reasoning_content", None) or ""
            usage = resp.usage
            return {
                "text": content or reasoning,
                "finish": choice.finish_reason,
                "truncated": choice.finish_reason == "length",
                "total_tokens": getattr(usage, "total_tokens", None),
                "seconds": round(dt, 1),
            }
        except (openai.APITimeoutError, openai.APIConnectionError, openai.RateLimitError,
                openai.InternalServerError) as e:
            last_err = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(min(2 ** attempt, 8))
        except Exception as e:  # noqa: BLE001
            return {"error": f"{type(e).__name__}: {str(e)[:200]}"}
    return {"error": last_err or "llm call failed after retries"}


def eval_term(term, env, table):
    if term[0] == "var":
        return env[term[1]]
    return table[eval_term(term[1], env, table)][eval_term(term[2], env, table)]


def explain_table_failure(eq1: dict, eq2: dict, table: list[list[int]]) -> str:
    """Exact, assignment-level feedback for the repair round."""
    n = len(table)
    for assignment in product(range(n), repeat=len(eq1["variables"])):
        env = dict(zip(eq1["variables"], assignment))
        lhs = eval_term(eq1["lhs"], env, table)
        rhs = eval_term(eq1["rhs"], env, table)
        if lhs != rhs:
            binding = ", ".join(f"{v}={env[v]}" for v in eq1["variables"])
            return (f"Your table FAILS Equation1 at {binding}: "
                    f"LHS evaluates to {lhs} but RHS evaluates to {rhs}. "
                    f"Equation1 must hold for ALL assignments. Fix the table or try another structure.")
    return ("Your table satisfies Equation1 but ALSO satisfies Equation2 everywhere, "
            "so it is not a counterexample. Keep Equation1 intact and break Equation2.")


def parse_table_reply(text: str) -> tuple[list[list[int]] | None, str]:
    obj = S.extract_json_object(text)
    if obj is None:
        return None, "no_json_object"
    if isinstance(obj.get("answer"), dict):
        obj = obj["answer"]
    raw = obj.get("counterexample_table", obj.get("table"))
    if raw is None:
        return None, "no_table_field"
    table = S.normalize_table(raw)
    if table is None:
        return None, "table_invalid_shape"
    return table, "ok"


def run_one(problem: dict[str, Any], args) -> dict[str, Any]:
    pid = str(problem.get("id"))
    eq1 = S.parse_equation(str(problem["equation1"]))
    eq2 = S.parse_equation(str(problem["equation2"]))
    feedback = ""
    rounds_out: list[dict] = []
    accepted = False
    win_table = None
    started = time.monotonic()

    for r in range(args.rounds):
        prompt = fill_prompt(problem, feedback, args.max_table_n)
        llm = call_llm(prompt, args)
        rec: dict[str, Any] = {"round": r}
        if "error" in llm:
            rec["llm_error"] = llm["error"]
            rounds_out.append(rec)
            break
        rec.update({"finish": llm["finish"], "truncated": llm["truncated"],
                    "total_tokens": llm["total_tokens"], "llm_seconds": llm["seconds"]})
        table, reason = parse_table_reply(llm["text"])
        rec["parse_reason"] = reason
        if table is None:
            rec["outcome"] = "parse_reject"
            rec["text_preview"] = S.text_preview(llm["text"], 400)
            feedback = ("PREVIOUS ATTEMPT: your reply was rejected before checking "
                        f"(reason: {reason}). Return one valid JSON object with a full n x n table.")
            rounds_out.append(rec)
            continue
        rec["n"] = len(table)
        if S.table_is_counterexample(eq1, eq2, table):
            rec["outcome"] = "table_verified"
            accepted = True
            win_table = table
            rounds_out.append(rec)
            break
        why = explain_table_failure(eq1, eq2, table)
        rec["outcome"] = "table_wrong"
        rec["why"] = why
        feedback = ("PREVIOUS ATTEMPT (n=%d) was wrong. %s\nYour previous table: %s"
                    % (len(table), why, json.dumps(table)))
        rounds_out.append(rec)

    return {
        "id": pid,
        "eq1_id": problem.get("eq1_id"),
        "eq2_id": problem.get("eq2_id"),
        "equation1": problem.get("equation1"),
        "equation2": problem.get("equation2"),
        "set": problem.get("_set"),
        "accepted": accepted,
        "table": win_table,
        "rounds_used": len(rounds_out),
        "seconds": round(time.monotonic() - started, 1),
        "rounds": rounds_out,
    }


def load_rows(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("["):
        return list(json.loads(text))
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frontier-file", required=True)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--model", default="openai/gpt-oss-120b")
    ap.add_argument("--reasoning", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--http-timeout", type=float, default=300.0)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--max-table-n", type=int, default=S.LLM_MAX_TABLE_N)
    ap.add_argument("--allow-fallbacks", action="store_true", default=False)
    args = ap.parse_args()

    if not API_KEY:
        print("ERROR: no OpenRouter API key found (.env or env).", file=sys.stderr)
        return 2

    frontier = load_rows(Path(args.frontier_file))
    if args.limit and len(frontier) > args.limit:
        frontier = frontier[: args.limit]

    out_dir = Path(args.out_dir) if args.out_dir else (
        REPO / "tmp_stage2_smoke" / f"{date.today().isoformat()}-false-loop"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = out_dir / "ledger.jsonl"
    if ledger_path.exists():
        ledger_path.unlink()

    print(f"model={args.model} reasoning={args.reasoning} rounds={args.rounds} "
          f"workers={args.workers} rows={len(frontier)}")
    print(f"out_dir: {out_dir}")

    lock = threading.Lock()
    results: list[dict] = []
    done = {"n": 0, "acc": 0}
    t_start = time.monotonic()

    def work(p):
        try:
            res = run_one(p, args)
        except Exception as e:  # noqa: BLE001
            res = {"id": str(p.get("id")), "accepted": False, "rounds": [],
                   "fatal_error": f"{type(e).__name__}: {str(e)[:200]}"}
        with lock:
            results.append(res)
            done["n"] += 1
            if res.get("accepted"):
                done["acc"] += 1
            with ledger_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(res, ensure_ascii=False) + "\n")
            n = done["n"]
            if n % 5 == 0 or n == len(frontier):
                print(f"  [{n}/{len(frontier)}] verified={done['acc']} "
                      f"({done['acc']/max(1,n):.0%})  {time.monotonic()-t_start:.0f}s", flush=True)
        return res

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, frontier))

    accepted = [r for r in results if r.get("accepted")]
    outcome_counts: dict[str, int] = {}
    for r in results:
        for rd in r.get("rounds", []):
            oc = rd.get("outcome", "llm_error" if rd.get("llm_error") else "?")
            outcome_counts[oc] = outcome_counts.get(oc, 0) + 1
    summary = {
        "date": date.today().isoformat(),
        "model": args.model,
        "reasoning": args.reasoning,
        "rounds": args.rounds,
        "frontier": len(frontier),
        "verified_tables": len(accepted),
        "verify_rate": round(len(accepted) / max(1, len(frontier)), 4),
        "verified_ids": [r["id"] for r in accepted],
        "table_sizes": sorted({len(r["table"]) for r in accepted}) if accepted else [],
        "round_outcomes": dict(sorted(outcome_counts.items(), key=lambda kv: -kv[1])),
        "wall_seconds": round(time.monotonic() - t_start, 1),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
