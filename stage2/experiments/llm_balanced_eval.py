#!/usr/bin/env python3
"""Balanced real-LLM evaluation: 50 TRUE + 50 FALSE from normal/hard1/hard2.

Runs the *shipped* pipeline end to end against the real model:

    solver.PROMPT -> gpt-oss-120b (OpenRouter, pinned provider)
                  -> solver.candidate_from_llm_text_with_reason
                  -> offline oracles (proof kernel + finite-model)
                  -> ground-truth label

The judge is cloud-only, so correctness is established with the offline
oracles from stage2/tests: a TRUE certificate must *prove* eq2 from eq1 under
the proof kernel, and must survive model-checking against finite models of
eq1. A FALSE certificate's witness table is re-verified directly.

Outcome classes (worst first):
  WRONG_VERDICT_SUBMITTED  the pipeline would submit the wrong verdict  <- fatal
  UNSOUND_CERT             certificate would fail the Lean judge        <- fatal
  correct                  right verdict, oracle-verified
  no_candidate             LLM output rejected before submission        <- safe
  llm_error                transport failure

Dev-time only; the shipped solver never talks to OpenRouter directly.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import threading
import time
from collections import Counter
from concurrent.futures import (ProcessPoolExecutor, ThreadPoolExecutor,
                                as_completed)
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "experiments"))
sys.path.insert(0, str(REPO / "stage2" / "solver"))
sys.path.insert(0, str(REPO / "stage2" / "tests"))

import local_runner_env  # noqa: E402


def _resolve_key() -> str:
    vals = local_runner_env.repo_env_values()
    return (vals.get("OPENROUTER_API_KEY") or vals.get("OPENAI_API_KEY")
            or os.environ.get("OPENROUTER_API_KEY", "")
            or os.environ.get("OPENAI_API_KEY", ""))


API_KEY = _resolve_key()
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

import oracles  # noqa: E402
import solver as S  # noqa: E402

SETS = ("normal", "hard1", "hard2")
_thread_local = threading.local()


def load_rows() -> list[dict]:
    out = []
    for name in SETS:
        path = REPO / "data" / "stage2_official_problems" / f"{name}.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                row["_set"] = name
                out.append(row)
    return out


def load_rows_from_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    rows = ([json.loads(line) for line in text.splitlines() if line.strip()]
            if path.suffix == ".jsonl" else json.loads(text))
    for row in rows:
        row["_set"] = path.stem
    return rows


def sample_balanced(rows: list[dict], per_class: int, seed: int,
                    unresolved_only: bool, workers: int) -> list[dict]:
    rng = random.Random(seed)
    pools = {True: [], False: []}
    for row in rows:
        if isinstance(row.get("answer"), bool):
            pools[row["answer"]].append(row)
    for pool in pools.values():
        rng.shuffle(pool)

    # Probe a candidate slab in parallel; solve_problem is CPU-bound so this
    # needs processes. Sequential probing was several minutes on its own.
    slab = per_class * (6 if unresolved_only else 2)
    candidates = [r for label in (True, False) for r in pools[label][:slab]]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        det = dict(pool.map(_det_probe, candidates, chunksize=4))
    for row in candidates:
        row["_deterministic"] = det.get(str(row.get("id")))

    picked: list[dict] = []
    for label in (True, False):
        pool_rows = [r for r in pools[label][:slab] if "_deterministic" in r]
        chosen = [r for r in pool_rows if r["_deterministic"] is None] \
            if unresolved_only else list(pool_rows)
        if len(chosen) < per_class:
            # Top up so the requested class balance is preserved.
            chosen += [r for r in pool_rows if r not in chosen]
        picked.extend(chosen[:per_class])
    return picked


def _client(timeout: float):
    cli = getattr(_thread_local, "client", None)
    if cli is None:
        from openai import OpenAI
        cli = OpenAI(api_key=API_KEY, base_url=OPENROUTER_BASE_URL, timeout=timeout)
        _thread_local.client = cli
    return cli


def fill_prompt(template: str, problem: dict, analysis: str, feedback: str) -> str:
    import re as _re

    values = {
        "problem.id": str(problem.get("id", "")),
        "problem.eq1_id": str(problem.get("eq1_id", "")),
        "problem.eq2_id": str(problem.get("eq2_id", "")),
        "problem.equation1": str(problem.get("equation1", "")),
        "problem.equation2": str(problem.get("equation2", "")),
        "solver.analysis": analysis,
        "solver.feedback": feedback,
        "history.attempts": "",
    }
    out = template
    for key, value in values.items():
        out = out.replace("{" + key + "}", value)
    return _re.sub(r"\{(problem|solver|history)\.[a-zA-Z_]+\}", "", out)


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
            choice = resp.choices[0]
            msg = choice.message
            content = getattr(msg, "content", None) or ""
            reasoning = (getattr(msg, "reasoning", None)
                         or getattr(msg, "reasoning_content", None) or "")
            return {
                "text": content or reasoning,
                "content_chars": len(content),
                "reasoning_chars": len(reasoning),
                "truncated": choice.finish_reason == "length",
                "completion_tokens": getattr(resp.usage, "completion_tokens", None),
                "seconds": round(time.monotonic() - t0, 1),
            }
        except (openai.APITimeoutError, openai.APIConnectionError,
                openai.RateLimitError, openai.InternalServerError) as e:
            last_err = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(min(2 ** attempt, 8))
        except Exception as e:  # noqa: BLE001
            return {"error": f"{type(e).__name__}: {str(e)[:200]}"}
    return {"error": last_err or "llm call failed after retries"}


def verify_candidate(problem: dict, candidate: dict) -> tuple[str, str]:
    """Return (status, detail) for a produced candidate."""
    answer = candidate["answer"]
    verdict = answer["verdict"]
    code = answer["code"]
    label = "true" if problem["answer"] else "false"
    if verdict != label:
        return "WRONG_VERDICT_SUBMITTED", f"said {verdict}, truth {label}"

    eq1 = S.parse_equation(str(problem["equation1"]))
    eq2 = S.parse_equation(str(problem["equation2"]))
    try:
        if verdict == "false":
            oracles.check_false_certificate(code, eq1, eq2)
            return "correct", "false_table_verified"
        shape = oracles.classify_true_certificate(code)
        if shape == "exact_expr":
            oracles.check_true_exact_certificate(code, eq1, eq2)
            detail = "proof_kernel_verified"
        elif shape == "singleton":
            oracles.check_true_singleton_certificate(code, eq1)
            detail = "collapse_kernel_verified"
        else:
            detail = f"kernel_skipped:{shape}"
        extras = [t for _n, t in S.WITNESS_TABLES]
        extras.extend(t for _r, t in S.structured_family_tables())
        oracles.model_check_true(
            eq2, oracles.model_battery(eq1, extras, fin3_samples=200, seed=17))
        return "correct", detail
    except oracles.OracleError as exc:
        return "UNSOUND_CERT", str(exc)[:200]


def fetch_one(job) -> dict:
    """Phase 1: network only. Threads are fine here (I/O releases the GIL)."""
    problem, args = job
    row: dict = {
        "id": str(problem.get("id")), "set": problem.get("_set"),
        "label": "true" if problem["answer"] else "false",
        "deterministic_route": problem.get("_deterministic"),
        "eq1": problem.get("equation1"), "eq2": problem.get("equation2"),
    }
    analysis = S.solver_analysis(problem)
    prompt = fill_prompt(S.PROMPT, problem, analysis, "")
    result = call_llm(prompt, args)
    if "error" in result:
        row.update(status="llm_error", detail=result["error"])
        return row
    row.update(seconds=result["seconds"], truncated=result["truncated"],
               completion_tokens=result["completion_tokens"],
               content_chars=result["content_chars"],
               reasoning_chars=result["reasoning_chars"],
               _text=result["text"])
    return row


def judge_one(job) -> dict:
    """Phase 2: CPU-bound parse + verify. Must be processes, not threads.

    Running this inside the network thread pool was the throughput bug: the
    closure search holds the GIL, so 8 'parallel' workers ran serially.
    """
    row, problem, allow_raw_true, effort = job
    if row.get("status") == "llm_error":
        return row
    S.set_effort(effort)
    text = row.pop("_text", "")

    candidate, reason = S.candidate_from_llm_text_with_reason(
        problem, text, allow_raw_true=allow_raw_true)
    row["reject_reason"] = reason
    if candidate is None:
        row["status"] = "no_candidate"
        row["detail"] = reason
        obj = S.extract_json_object(text) or {}
        row["claimed_verdict"] = str(obj.get("verdict", "")).lower() or None
        row["response_preview"] = S.text_preview(text, 200)
        return row

    row["route"] = candidate["route"]
    status, detail = verify_candidate(problem, candidate)
    row["status"] = status
    row["detail"] = detail
    if status != "correct":
        row["response_preview"] = S.text_preview(text, 400)
    return row


def _det_probe(problem: dict) -> tuple[str, str | None]:
    record = S.solve_problem(problem, false_time_budget=1.0)
    return str(problem.get("id")), None if record is None else str(record["route"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260721)
    ap.add_argument("--model", default="openai/gpt-oss-120b")
    ap.add_argument("--reasoning", default="medium")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=6144)
    ap.add_argument("--http-timeout", type=float, default=180.0)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--allow-fallbacks", action="store_true")
    ap.add_argument("--allow-raw-true", action="store_true",
                    help="Solo-style: accept raw Lean from the model")
    ap.add_argument("--unresolved-only", action="store_true",
                    help="prefer rows the deterministic solver skips")
    ap.add_argument("--file", type=Path, default=None,
                    help="load problems from an arbitrary jsonl/json instead "
                         "of the named official sets (e.g. a frontier of "
                         "unsolved rows from audit_corpus.py)")
    ap.add_argument("--all-in-file", action="store_true",
                    help="use every row in --file directly, skipping the "
                         "balanced-sample re-probe (rows are assumed "
                         "already-unresolved, e.g. straight from an "
                         "audit_corpus.py 'skip' list)")
    ap.add_argument("--effort", choices=("fast", "standard", "deep"),
                    default="fast",
                    help="engine effort while bridging LLM chains; Solo runs "
                         "at 'deep' in production, so use that for parity")
    ap.add_argument("--out", type=Path,
                    default=REPO / "stage2" / "results" / "llm-balanced-eval.json")
    args = ap.parse_args()

    if not API_KEY:
        print("No OpenRouter key found (.env or environment).", file=sys.stderr)
        return 2

    print(f"model={args.model} reasoning={args.reasoning} "
          f"raw_true={args.allow_raw_true} unresolved_only={args.unresolved_only} "
          f"effort={args.effort}")
    S.set_effort(args.effort)
    cpu = max(1, min(16, (os.cpu_count() or 2) - 2))
    t_start = time.monotonic()
    if args.file and args.all_in_file:
        sample = load_rows_from_file(args.file)
        for row in sample:
            row["_deterministic"] = None
    else:
        rows = load_rows_from_file(args.file) if args.file else load_rows()
        sample = sample_balanced(rows, args.per_class, args.seed,
                                 args.unresolved_only, cpu)
    det_solved = sum(1 for p in sample if p.get("_deterministic"))
    print(f"sampled {len(sample)} problems "
          f"({sum(1 for p in sample if p['answer'])} TRUE / "
          f"{sum(1 for p in sample if not p['answer'])} FALSE); "
          f"{det_solved} already solved deterministically "
          f"[{time.monotonic()-t_start:.0f}s]\n", flush=True)

    # Phase 1 - network, threads.
    fetched: list[dict] = []
    by_id = {str(p.get("id")): p for p in sample}
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(fetch_one, (p, args)) for p in sample]
        for i, fut in enumerate(as_completed(futures), 1):
            fetched.append(fut.result())
            if i % 10 == 0 or i == len(sample):
                print(f"  fetched {i}/{len(sample)} "
                      f"[{time.monotonic()-t0:.0f}s]", flush=True)
    print(f"  all responses in {time.monotonic()-t0:.0f}s", flush=True)

    # Phase 2 - CPU, processes.
    t1 = time.monotonic()
    jobs = [(r, by_id[r["id"]], args.allow_raw_true, args.effort) for r in fetched]
    with ProcessPoolExecutor(max_workers=cpu) as pool:
        results = list(pool.map(judge_one, jobs, chunksize=1))
    print(f"  verified {len(results)} in {time.monotonic()-t1:.0f}s "
          f"(total {time.monotonic()-t_start:.0f}s)", flush=True)

    by_status = Counter(r["status"] for r in results)
    print("\n=== outcomes ===")
    for status, count in by_status.most_common():
        print(f"  {status:26s} {count}")

    fatal = [r for r in results
             if r["status"] in ("WRONG_VERDICT_SUBMITTED", "UNSOUND_CERT")]
    print(f"\nFATAL (would be judge-incorrect): {len(fatal)}")
    for r in fatal[:20]:
        print(f"  {r['id']:16s} {r['label']:5s} {r.get('route','-'):28s} {r['detail']}")

    print("\n=== rejects by reason (safe, but lost coverage) ===")
    for reason, count in Counter(
            r["detail"] for r in results if r["status"] == "no_candidate").most_common():
        print(f"  {count:4d}  {reason}")

    # Did the model silently get the verdict wrong where we refused to submit?
    claimed_wrong = [r for r in results if r["status"] == "no_candidate"
                     and r.get("claimed_verdict")
                     and r["claimed_verdict"] != r["label"]]
    print(f"\nverdict errors caught before submission: {len(claimed_wrong)}")

    print("\n=== by label ===")
    for label in ("true", "false"):
        sub = [r for r in results if r["label"] == label]
        ok = sum(1 for r in sub if r["status"] == "correct")
        print(f"  {label:5s} n={len(sub):3d} correct={ok:3d} "
              f"({100*ok/max(len(sub),1):.0f}%)")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
