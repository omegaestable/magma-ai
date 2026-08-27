#!/usr/bin/env python3
"""End-to-end real-call test of THIS tree's Marathon LLM lane.

Unlike `llm_protocol_probe.py` (which compares candidate prompt bodies against
each other) this exercises the shipped path: `render_marathon_prompt` with
`PROTOCOL_BODIES[round]`, then `candidate_from_llm_text_with_reason`, then the
offline oracles -- so what it measures is what a Marathon would do, round by
round, with rows that settle dropping out between rounds.

Measured 2026-08-27 on the 37-row hard sample (20 order-5 collapse candidates,
10 order-4 residual, 7 controls), gpt-oss-120b/DeepInfra bf16, reasoning low,
temperature 0, seed 0: round 1 (bare A2 shell) 1/37 at 2.4 laws proposed per
row; round 2 (PROTOCOL_DERIVATION_EXCLUSION) 2/24 at 11.8 laws per row (12
calls lost to provider 429s at 8 workers -- use 4); 3/37 together, and all
three certificates real-judge accepted.

Round r renders PROMPT with PROTOCOL_BODIES[r] through the worktree's own
render_marathon_prompt, calls gpt-oss-120b (DeepInfra bf16 pinned, temp 0,
seed 0, reasoning low) with the same request shape marathon_llm.call_llm
builds, parses with the worktree's candidate_from_llm_text_with_reason, and
verifies every certificate with the offline oracles.
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

import oracles  # noqa: E402
import solver as S  # noqa: E402

DIAMOND = "\u25c7"
MODEL = "openai/gpt-oss-120b"


def api_key() -> str:
    for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip()
    return ""


def to_diamond(text: str) -> str:
    return str(text).replace("*", DIAMOND)


EXCLUSION = """* The solver has ALREADY TRIED, and failed to prove, every one of these
  standard laws on this row, so do not propose them:
    a ◇ a = a       a ◇ b = a       a ◇ b = b       a ◇ b = b ◇ a
    a ◇ b = a ◇ c   a ◇ b = c ◇ b   (a ◇ a) ◇ a = a
    a ◇ (b ◇ c) = a ◇ b
  What it cannot do is invent a law SPECIFIC TO THIS HYPOTHESIS. Derive one
  like this: instantiate the hypothesis at concrete terms so that one side
  becomes an instance of the other side, or of a law you already have;
  whatever equation is left over is your new law. Then repeat with it in hand."""

MENU = """  Useful rungs: "a ◇ a = a", "a ◇ b = a", "a ◇ b = b",
  "a ◇ b = a ◇ c", "a ◇ b = c ◇ b",
  "(a ◇ a) ◇ a = a", "a ◇ (b ◇ c) = a ◇ b"."""

LEGACY = [False]


def build_prompt(problem: dict, body: str, neutral: bool) -> str:
    shown = dict(problem)
    shown["equation1"] = to_diamond(problem["equation1"])
    shown["equation2"] = to_diamond(problem["equation2"])
    analysis = S.solver_analysis(shown)
    if neutral:
        analysis = "\n".join(l for l in analysis.splitlines()
                             if not l.startswith("This row escaped deterministic"))
    prompt = S.render_marathon_prompt(shown, analysis, body)
    if LEGACY[0]:
        assert EXCLUSION in prompt, "exclusion block not found"
        prompt = prompt.replace(EXCLUSION, MENU)
    return prompt


def call(prompt: str, key: str, max_tokens: int, timeout: float) -> dict:
    import openai
    client = openai.OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1",
                           timeout=timeout, max_retries=0)
    t0 = time.monotonic()
    try:
        resp = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens, temperature=0.0, seed=0,
            extra_body={"reasoning": {"effort": "low"},
                        "provider": {"order": ["DeepInfra"],
                                     "allow_fallbacks": False,
                                     "quantizations": ["bf16"]}},
        )
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {str(exc)[:200]}",
                "seconds": round(time.monotonic() - t0, 1)}
    choice = resp.choices[0]
    msg = choice.message
    content = getattr(msg, "content", None) or ""
    reasoning = (getattr(msg, "reasoning", None)
                 or getattr(msg, "reasoning_content", None) or "")
    usage = resp.usage
    return {"text": content or reasoning,
            "truncated": choice.finish_reason == "length",
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
            "seconds": round(time.monotonic() - t0, 1)}


def fetch(job) -> dict:
    problem, body, rnd, key, max_tokens, timeout, neutral, legacy = job
    LEGACY[0] = legacy
    prompt = build_prompt(problem, body, neutral)
    row = {"id": str(problem["id"]), "round": rnd, "tag": problem.get("_tag", ""),
           "prompt_chars": len(prompt)}
    res = call(prompt, key, max_tokens, timeout)
    row.update({k: v for k, v in res.items() if k != "text"})
    row["_text"] = res.get("text", "")
    return row


def verify(job) -> dict:
    row, problem = job
    S.set_effort("fast")
    S.set_hard_deadline(None)
    S.clear_term_caches()
    text = row.pop("_text", "")
    row["raw_text"] = text[:8000]
    if row.get("error"):
        row["status"] = "llm_error"
        return row
    shown = dict(problem)
    shown["equation1"] = to_diamond(problem["equation1"])
    shown["equation2"] = to_diamond(problem["equation2"])
    obj = S.extract_json_object(text)
    row["claimed"] = str((obj or {}).get("verdict", "")).lower() or None
    laws = S.llm_derivation_law_texts(obj or {})
    row["laws_proposed"] = len(laws)
    eq1 = S.parse_equation(str(shown["equation1"]))
    eq2 = S.parse_equation(str(shown["equation2"]))
    t0 = time.monotonic()
    cand, reason = S.candidate_from_llm_text_with_reason(
        shown, text, allow_raw_true=False)
    row["verify_seconds"] = round(time.monotonic() - t0, 1)
    if cand is None:
        row["status"] = "unsettled"
        row["reject"] = reason
        return row
    code = cand["answer"]["code"]
    row["route"] = cand["route"]
    row["code_bytes"] = len(code.encode("utf-8"))
    try:
        if cand["answer"]["verdict"] == "false":
            oracles.check_false_certificate(code, eq1, eq2)
            row["status"] = "settled_false"
        else:
            oracles.check_no_banned_tactics(code, "llm")
            shape = oracles.classify_true_certificate(code)
            if shape == "lemma_chain":
                oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
            elif shape == "lemma":
                oracles.check_true_lemma_certificate(code, eq1, eq2)
            elif shape == "exact_expr":
                oracles.check_true_exact_certificate(code, eq1, eq2)
            elif shape == "singleton":
                oracles.check_true_singleton_certificate(code, eq1)
            else:
                raise oracles.OracleError("unverifiable shape " + str(shape))
            row["status"] = "settled_true"
        row["code"] = code
        row["eq1_id"] = problem.get("eq1_id", "")
        row["eq2_id"] = problem.get("eq2_id", "")
        row["equation1"] = shown["equation1"]
        row["equation2"] = shown["equation2"]
    except oracles.OracleError as exc:
        row["status"] = "unsound_candidate"
        row["detail"] = str(exc)[:200]
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--verify-workers", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=None)
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--legacy-menu", action="store_true")
    args = ap.parse_args()
    LEGACY[0] = args.legacy_menu
    key = api_key()
    if not key:
        print("no key", file=sys.stderr)
        return 2
    max_tokens = args.max_tokens or int(S.LLM_CONFIG["max_output_tokens"])
    problems = [json.loads(l) for l in
                args.file.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        problems = problems[:args.limit]
    by_id = {str(p["id"]): p for p in problems}
    pending = [str(p["id"]) for p in problems]
    settled: dict[str, dict] = {}
    all_rows: list[dict] = []
    for rnd in range(args.rounds):
        if not pending:
            break
        body = S.PROTOCOL_BODIES[rnd % len(S.PROTOCOL_BODIES)]
        jobs = [(by_id[i], body, rnd, key, max_tokens, args.timeout, False,
                 args.legacy_menu) for i in pending]
        print(f"round {rnd}: {len(jobs)} calls, body_chars={len(body)}", flush=True)
        t0 = time.monotonic()
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            fetched = list(pool.map(fetch, jobs))
        print(f"  phase1 {time.monotonic() - t0:.0f}s", flush=True)
        t1 = time.monotonic()
        with ProcessPoolExecutor(max_workers=args.verify_workers) as pool:
            done = list(pool.map(verify, [(dict(r), by_id[r["id"]]) for r in fetched],
                                 chunksize=1))
        print(f"  phase2 {time.monotonic() - t1:.0f}s", flush=True)
        nxt = []
        for row in done:
            all_rows.append(row)
            if row.get("status", "").startswith("settled"):
                settled[row["id"]] = row
            else:
                nxt.append(row["id"])
        toks = sum(r.get("total_tokens") or 0 for r in done)
        secs = [r.get("seconds") or 0 for r in done]
        print("  round %d: settled_now=%d cumulative=%d/%d tokens=%d "
              "mean_tok/call=%.0f mean_s/call=%.1f"
              % (rnd, len(done) - len(nxt), len(settled), len(problems), toks,
                 toks / max(1, len(done)), sum(secs) / max(1, len(secs))), flush=True)
        pending = nxt
    args.out.write_text("\n".join(json.dumps(r, ensure_ascii=False)
                                  for r in all_rows) + "\n", encoding="utf-8")
    import collections
    print("statuses:", dict(collections.Counter(r.get("status") for r in all_rows)))
    print("routes:", dict(collections.Counter(r.get("route") for r in all_rows
                                              if r.get("route"))))
    print("settled ids:", sorted(settled))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
