#!/usr/bin/env python3
"""Dev-loop harness for TRUE-proof generation with gpt-oss-120b via OpenRouter.

For each TRUE-frontier problem (a TRUE implication the deterministic solver
currently skips) this runs a **self-verifying repair loop**:

    round r:
      prompt  = fill(solver.PROMPT, problem, analysis, history-so-far)
      text    = gpt-oss-120b(prompt)                 # OpenRouter, pinned provider
      cand    = solver.candidate_from_llm_text_with_reason(problem, text)
      if cand: status = local Lean judge(cand)        # verify_answer
               if accepted -> WIN, stop
      feed the judge error (or the parse-reject reason) into round r+1

It writes a structured failure ledger (JSONL, one line per problem with
per-round detail) plus a summary, so we can learn from failures and drive
solver improvements. This is a DEV-TIME tool; it is not part of the shipped
single-file solver and it talks to OpenRouter directly (the shipped solver
only ever reaches the organizer proxy).

Secret-safe: never prints the API key. Prefers the fresh repo-local ``.env``
key over any stale key already present in the process environment.
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
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
OFFICIAL = REPO / "vendor" / "stage2-official"
SOLVER_DIR = REPO / "stage2" / "solver"
EXPERIMENTS = REPO / "stage2" / "experiments"

# --- API key: prefer the fresh repo .env over any stale process-env key ------
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
    # Make the fresh key win everywhere (this process + any child it spawns).
    os.environ["OPENROUTER_API_KEY"] = API_KEY
    os.environ["OPENAI_API_KEY"] = API_KEY

# --- imports that must come after sys.path is wired --------------------------
sys.path.insert(0, str(OFFICIAL))
sys.path.insert(0, str(SOLVER_DIR))
from judge.verify import verify_answer  # noqa: E402
import solver as S  # noqa: E402

# Mirrors pipeline/proxy.py DEFAULT_PROOF_POLICY so local verification matches
# production. Kept inline to avoid importing the proxy (which pulls in openai).
DEFAULT_PROOF_POLICY = {
    "allowed_axioms": ["propext", "Quot.sound", "Classical.choice"],
    "allowed_declarations": ["letFun"],
    "allowed_declaration_prefixes": [
        "And.", "Bool.", "Classical.", "Decidable.", "Eq.",
        "EquationLHS", "EquationRHS", "Goal", "Exists.", "False.",
        "Fin.", "Fintype.", "Function.", "HEq.", "Iff.", "Init.", "Int.", "Lean.",
        "List.", "Magma.", "Mathlib.", "MemoFinOp.", "Nat.", "Nonempty.", "Not.",
        "NthRewrites.", "OfNat.", "Option.", "Or.", "Prod.", "PUnit.",
        "RewriteCombinations.", "RewriteGoal.", "RewriteHypothesis.",
        "RewriteHypothesisAndGoal.", "SimpleRewrites.",
        "Std.", "Subgraph.", "Subtype.", "Sum.",
        "Trans.", "True.", "Unit.",
        "JudgeDecide.", "JudgeFinOp.", "JudgeMagma.",
        "inst", "of_decide_", "submission.",
        "congrArg", "congr_arg", "eq_self", "of_eq_true", "id",
        "eq_comm", "eq_mp", "eq_mpr", "rfl", "absurd",
    ],
}

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def to_judge_problem(problem: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": problem["id"],
        "eq1_id": problem["eq1_id"],
        "eq2_id": problem["eq2_id"],
        "equation1": problem["equation1"],
        "equation2": problem["equation2"],
        "proof_policy": problem.get("proof_policy") or DEFAULT_PROOF_POLICY,
    }


# --- prompt filling (mirrors pipeline/proxy._fill_prompt_template) -----------
def format_history(judge_log: list[dict]) -> str:
    if not judge_log:
        return "(no previous attempts)"
    parts = []
    for i, entry in enumerate(judge_log, 1):
        req = entry.get("request", {})
        resp = entry.get("response", {})
        verdict = req.get("verdict", "?")
        status = resp.get("status", "unknown")
        part = f"Attempt {i}: verdict={verdict}, judge={status}"
        err = resp.get("stderr") or resp.get("message") or ""
        if err:
            if len(err) > 600:
                err = err[:600] + "\n... (truncated)"
            part += f"\n  Error: {err}"
        parts.append(part)
    return "\n".join(parts)


def fill_prompt(template: str, problem: dict, solver_context: dict, judge_log: list[dict]) -> str:
    import re as _re

    eq1_name = f"Equation{problem.get('eq1_id', '')}"
    eq2_name = f"Equation{problem.get('eq2_id', '')}"
    problem_vars = {
        "problem.id": problem.get("id", ""),
        "problem.eq1_id": str(problem.get("eq1_id", "")),
        "problem.eq2_id": str(problem.get("eq2_id", "")),
        "problem.eq1_name": eq1_name,
        "problem.eq2_name": eq2_name,
        "problem.equation1": problem.get("equation1", ""),
        "problem.equation2": problem.get("equation2", ""),
        "problem.equation1_id": eq1_name,
        "problem.equation2_id": eq2_name,
    }
    history_vars = {
        "history.attempts": format_history(judge_log),
        "history.round": str(len(judge_log)),
    }
    if judge_log:
        last = judge_log[-1].get("response", {})
        history_vars["history.last_error"] = last.get("stderr") or last.get("message") or ""
        history_vars["history.last_status"] = last.get("status", "")
    else:
        history_vars["history.last_error"] = ""
        history_vars["history.last_status"] = ""
    solver_vars = {f"solver.{k}": str(v) for k, v in solver_context.items()}
    all_vars = {**problem_vars, **history_vars, **solver_vars}
    result = template
    for key, value in all_vars.items():
        result = result.replace("{" + key + "}", value)
    return _re.sub(r"\{(problem|solver|history)\.[a-zA-Z_]+\}", "", result)


# --- OpenRouter call ---------------------------------------------------------
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
        # Production parity: pin DeepInfra/bf16 exactly like pipeline/config.json.
        extra_body["provider"] = {"order": ["DeepInfra"], "allow_fallbacks": False,
                                  "quantizations": ["bf16"]}
    # else: let OpenRouter load-balance across gpt-oss-120b providers (dev speed).
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
            text = content or reasoning
            usage = resp.usage
            return {
                "text": text,
                "content_chars": len(content),
                "reasoning_chars": len(reasoning),
                "finish": choice.finish_reason,
                "truncated": choice.finish_reason == "length",
                "total_tokens": getattr(usage, "total_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "seconds": round(dt, 1),
            }
        except (openai.APITimeoutError, openai.APIConnectionError, openai.RateLimitError,
                openai.InternalServerError) as e:
            last_err = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(min(2 ** attempt, 8))
        except Exception as e:  # noqa: BLE001
            return {"error": f"{type(e).__name__}: {str(e)[:200]}"}
    return {"error": last_err or "llm call failed after retries"}


# --- one problem: the repair loop -------------------------------------------
def run_one(problem: dict[str, Any], template: str, args) -> dict[str, Any]:
    pid = str(problem.get("id"))
    jp = to_judge_problem(problem)
    analysis = S.solver_analysis(problem)
    judge_log: list[dict] = []
    rounds_out: list[dict] = []
    solver_feedback = ""  # parse-reject feedback carried between rounds
    accepted = False
    accepted_route = None
    started = time.monotonic()

    for r in range(args.rounds):
        ctx = {"round": str(r), "analysis": analysis, "feedback": solver_feedback}
        prompt = fill_prompt(template, problem, ctx, judge_log)
        llm = call_llm(prompt, args)
        rec: dict[str, Any] = {"round": r}
        if "error" in llm:
            rec["llm_error"] = llm["error"]
            rounds_out.append(rec)
            break
        rec.update({
            "finish": llm["finish"], "truncated": llm["truncated"],
            "total_tokens": llm["total_tokens"], "completion_tokens": llm["completion_tokens"],
            "llm_seconds": llm["seconds"], "content_chars": llm["content_chars"],
            "reasoning_chars": llm["reasoning_chars"],
        })
        text = llm["text"]
        candidate, reason = S.candidate_from_llm_text_with_reason(problem, text, allow_raw_true=args.allow_raw_true)
        rec["parse_reason"] = reason
        if candidate is None:
            rec["outcome"] = "parse_reject"
            rec["text_preview"] = S.text_preview(text, 600)
            solver_feedback = f"Your previous JSON was rejected before the judge (reason: {reason}). Fix the format and return one valid JSON object."
            rounds_out.append(rec)
            continue
        rec["route"] = candidate["route"]
        payload = S.judge_answer_payload(candidate["answer"])
        if payload is None:
            rec["outcome"] = "payload_invalid"
            rounds_out.append(rec)
            continue
        raw = json.dumps(payload)
        v = verify_answer(jp, raw)
        status = v.get("status")
        rec["judge_status"] = status
        rec["verdict"] = payload["verdict"]
        rec["code_bytes"] = len(payload["code"].encode("utf-8"))
        rec["code_preview"] = payload["code"][:2000]
        judge_log.append({"request": payload, "response": v})
        if status == "accepted":
            rec["outcome"] = "accepted"
            accepted = True
            accepted_route = candidate["route"]
            rounds_out.append(rec)
            break
        rec["outcome"] = status
        rec["error_code"] = v.get("error_code")
        rec["lean_error"] = (v.get("stderr") or v.get("message") or "")[:800]
        solver_feedback = ""  # judge history already carries the Lean error
        rounds_out.append(rec)

    return {
        "id": pid,
        "eq1_id": problem.get("eq1_id"),
        "eq2_id": problem.get("eq2_id"),
        "equation1": problem.get("equation1"),
        "equation2": problem.get("equation2"),
        "truth": problem.get("answer"),
        "difficulty": problem.get("difficulty"),
        "accepted": accepted,
        "accepted_route": accepted_route,
        "rounds_used": len(rounds_out),
        "seconds": round(time.monotonic() - started, 1),
        "rounds": rounds_out,
    }


# --- problem loading / frontier selection ------------------------------------
def load_rows(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("["):
        return list(json.loads(text))
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def is_true(problem: dict) -> bool | None:
    ans = problem.get("answer")
    if isinstance(ans, bool):
        return ans
    return None


def select_frontier(rows: list[dict], args) -> tuple[list[dict], dict[str, int]]:
    stats = {"total": 0, "true": 0, "true_and_skip": 0, "det_solved": 0, "unknown_truth": 0}
    frontier = []
    target = getattr(args, "target", 0) or 0
    for p in rows:
        stats["total"] += 1
        if stats["total"] % 200 == 0:
            print(f"  ...scanned {stats['total']} rows, frontier so far={len(frontier)}", flush=True)
        if target and len(frontier) >= target:
            break
        t = is_true(p)
        if args.only_true:
            if t is None:
                stats["unknown_truth"] += 1
                continue
            if not t:
                continue
        stats["true"] += 1
        if args.require_skip:
            try:
                # false_time_budget=0: TRUE-answer rows have no counterexample,
                # so skip the (wasted) FALSE search and only test TRUE routes.
                det = S.solve_problem(p, false_time_budget=0.0)
            except Exception:  # noqa: BLE001
                det = None
            if det is not None:
                stats["det_solved"] += 1
                continue
        stats["true_and_skip"] += 1
        frontier.append(p)
    return frontier, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--problems", nargs="*", default=[], help="problem set file(s); optional if --frontier-file given")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--limit", type=int, default=0, help="cap total frontier problems (0=all)")
    ap.add_argument("--limit-per-file", type=int, default=0)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--model", default="openai/gpt-oss-120b")
    ap.add_argument("--reasoning", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--http-timeout", type=float, default=300.0)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--prompt-file", default=None, help="override solver.PROMPT with this file")
    ap.add_argument("--allow-fallbacks", action="store_true", default=False,
                    help="dev speed: let OpenRouter load-balance providers (not prod-pinned)")
    ap.add_argument("--allow-raw-true", dest="allow_raw_true", action="store_true", default=True)
    ap.add_argument("--no-raw-true", dest="allow_raw_true", action="store_false")
    ap.add_argument("--only-true", dest="only_true", action="store_true", default=True)
    ap.add_argument("--all-verdicts", dest="only_true", action="store_false")
    ap.add_argument("--require-skip", dest="require_skip", action="store_true", default=True)
    ap.add_argument("--no-skip-filter", dest="require_skip", action="store_false")
    ap.add_argument("--select-only", action="store_true", help="report+save frontier, no LLM")
    ap.add_argument("--target", type=int, default=0, help="early-stop selection after N frontier found")
    ap.add_argument("--frontier-file", default=None, help="run a pre-selected frontier jsonl directly")
    args = ap.parse_args()

    if not API_KEY:
        print("ERROR: no OpenRouter API key found (.env or env).", file=sys.stderr)
        return 2
    if not args.frontier_file and not args.problems:
        print("ERROR: give --problems and/or --frontier-file.", file=sys.stderr)
        return 2

    template = S.PROMPT
    prompt_label = "solver.PROMPT"
    if args.prompt_file:
        template = Path(args.prompt_file).read_text(encoding="utf-8")
        prompt_label = args.prompt_file

    out_dir = Path(args.out_dir) if args.out_dir else (
        REPO / "tmp_stage2_smoke" / f"{date.today().isoformat()}-true-loop"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = out_dir / "ledger.jsonl"
    summary_path = out_dir / "summary.json"

    if args.frontier_file:
        frontier = load_rows(Path(args.frontier_file))
        sel_stats = {"preselected": len(frontier)}
    else:
        rows: list[dict] = []
        for pf in args.problems:
            file_rows = load_rows(Path(pf))
            if args.limit_per_file:
                file_rows = file_rows[: args.limit_per_file]
            rows.extend(file_rows)
        frontier, sel_stats = select_frontier(rows, args)
    if args.limit and len(frontier) > args.limit:
        frontier = frontier[: args.limit]

    frontier_path = out_dir / "frontier.jsonl"
    with frontier_path.open("w", encoding="utf-8") as fh:
        for p in frontier:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"selection: {sel_stats} -> {len(frontier)} frontier; saved {frontier_path}")
    if args.select_only:
        return 0

    print(f"prompt={prompt_label} model={args.model} reasoning={args.reasoning} "
          f"rounds={args.rounds} workers={args.workers} max_tokens={args.max_tokens}")
    print(f"selection: {sel_stats} -> running {len(frontier)} frontier problems")
    print(f"out_dir: {out_dir}")

    lock = threading.Lock()
    results: list[dict] = []
    done = {"n": 0, "acc": 0}
    t_start = time.monotonic()

    def work(p):
        try:
            res = run_one(p, template, args)
        except Exception as e:  # noqa: BLE001 — never let one row kill the batch
            res = {"id": str(p.get("id")), "eq1_id": p.get("eq1_id"), "eq2_id": p.get("eq2_id"),
                   "equation1": p.get("equation1"), "equation2": p.get("equation2"),
                   "truth": p.get("answer"), "accepted": False, "accepted_route": None,
                   "rounds_used": 0, "seconds": 0.0, "rounds": [],
                   "fatal_error": f"{type(e).__name__}: {str(e)[:200]}"}
        with lock:
            results.append(res)
            done["n"] += 1
            if res["accepted"]:
                done["acc"] += 1
            with ledger_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(res, ensure_ascii=False) + "\n")
            n = done["n"]
            if n % 10 == 0 or n == len(frontier):
                rate = done["acc"] / n
                el = time.monotonic() - t_start
                print(f"  [{n}/{len(frontier)}] accepted={done['acc']} ({rate:.0%})  {el:.0f}s", flush=True)
        return res

    # fresh ledger
    if ledger_path.exists():
        ledger_path.unlink()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, frontier))

    # summary
    accepted = [r for r in results if r["accepted"]]
    by_route: dict[str, int] = {}
    for r in accepted:
        by_route[r["accepted_route"]] = by_route.get(r["accepted_route"], 0) + 1
    reject_reasons: dict[str, int] = {}
    judge_statuses: dict[str, int] = {}
    error_codes: dict[str, int] = {}
    llm_errors = 0
    truncations = 0
    for r in results:
        for rd in r["rounds"]:
            if rd.get("llm_error"):
                llm_errors += 1
            if rd.get("truncated"):
                truncations += 1
            if rd.get("outcome") == "parse_reject":
                reject_reasons[rd["parse_reason"]] = reject_reasons.get(rd["parse_reason"], 0) + 1
            js = rd.get("judge_status")
            if js:
                judge_statuses[js] = judge_statuses.get(js, 0) + 1
            ec = rd.get("error_code")
            if ec:
                error_codes[ec] = error_codes.get(ec, 0) + 1
    summary = {
        "date": date.today().isoformat(),
        "prompt": prompt_label,
        "model": args.model,
        "reasoning": args.reasoning,
        "rounds": args.rounds,
        "max_tokens": args.max_tokens,
        "selection": sel_stats,
        "frontier": len(frontier),
        "accepted": len(accepted),
        "accept_rate": round(len(accepted) / max(1, len(frontier)), 4),
        "accepted_by_route": by_route,
        "parse_reject_reasons": dict(sorted(reject_reasons.items(), key=lambda kv: -kv[1])),
        "judge_statuses": dict(sorted(judge_statuses.items(), key=lambda kv: -kv[1])),
        "judge_error_codes": dict(sorted(error_codes.items(), key=lambda kv: -kv[1])),
        "llm_errors": llm_errors,
        "truncations": truncations,
        "wall_seconds": round(time.monotonic() - t_start, 1),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
