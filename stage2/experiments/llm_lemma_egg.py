"""LLM names the pivot law; egg derives it; the kernel checks it.

This is the composition the 2026-07-23 handoff flagged as the next lever and the
2026-07-29 ETP mining justified:

- The LLM is measurably good at *which law is relevant* and measurably bad at Lean
  bookkeeping. Of 16 parsed proposals in the 2026-07-22 balanced eval, 14 passed
  the "does this imply the goal" gate — but the dominant failure became
  `lemma_not_derivable_from_hypothesis` (13 cases), because the CP closure could
  not prove the laws it named.
- Egg removes that wall. Measured this session: egg proves the collapse law
  `a = b` from eq1 on 10 of the 14 official rows whose ETP pivot is `x = y`,
  where the CP closure proves none of them.

So the model supplies only a *target*; nothing it says is trusted. Every proposal
passes three gates before it can become a certificate:

1. `lemma_applies_to_goal` — does the law actually close the goal? (free, syntactic)
2. `lemma_survives_models`  — is it refuted by a finite model of eq1? (free)
3. `egg_saturate_prove`     — can it be derived from eq1? (the expensive half)

and then the emitted certificate is re-checked by the independent proof kernel.

Two-phase by construction: threads for the network, processes for verification.
Mixing them in one `ThreadPoolExecutor` costs ~10x because verification is
CPU-bound and the GIL serialises it (standing rail).

    python stage2/experiments/llm_lemma_egg.py --ids hard2_0073,normal_0582
    python stage2/experiments/llm_lemma_egg.py --unsolved --sets hard1,hard2 --workers 8
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "tests"))

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

MODEL = os.environ.get("SAIR_STAGE2_MODEL", "openai/gpt-oss-120b")

SETS = {
    "normal": REPO_ROOT / "data/stage2_official_problems/normal.jsonl",
    "hard1": REPO_ROOT / "data/stage2_official_problems/hard1.jsonl",
    "hard2": REPO_ROOT / "data/stage2_official_problems/hard2.jsonl",
    "hard3": REPO_ROOT / "data/stage2_official_problems/hard3.jsonl",
    "evaluation_normal": REPO_ROOT / "data/hf_cache/evaluation_normal.jsonl",
    "evaluation_hard": REPO_ROOT / "data/hf_cache/evaluation_hard.jsonl",
    "evaluation_extra_hard": REPO_ROOT / "data/hf_cache/evaluation_extra_hard.jsonl",
    "evaluation_order5": REPO_ROOT / "data/hf_cache/evaluation_order5.jsonl",
}

PROMPT = """You are given two equational laws for a magma (one binary operation
`◇`, no associativity, no commutativity — never assume either).

HYPOTHESIS (holds for all variables):
  {eq1}

GOAL (must be derived):
  {eq2}

Your job is NOT to write a proof. Your job is to name **intermediate laws**: small
equations that follow from the HYPOTHESIS and from which the GOAL follows. A
smaller law is a much easier proof target, so prefer the smallest laws that could
work.

Laws worth considering, in rough order of usefulness:
  a = b                  (the magma collapses to one element — very common here)
  a ◇ b = a              (left projection)
  a ◇ b = b              (right projection)
  a ◇ a = a              (idempotent)
  a ◇ b = a ◇ c          (left row constant)
  a ◇ b = c ◇ b          (right column constant)
  a ◇ b = c ◇ d          (product constant)
  a ◇ b = b ◇ a          (commutative)
  ...or any other short equation you can justify.

Write laws with variables a, b, c, d only, fully parenthesised, using ◇.

Output exactly ONE JSON object, first character {{, last character }}, no prose and
no markdown:

{{"lemmas": ["a = b", "a ◇ b = a"]}}

List at most 5, best first."""


def load_rows(name: str) -> list[dict]:
    return [json.loads(line) for line in
            SETS[name].read_text(encoding="utf-8").splitlines() if line.strip()]


def load_all() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for name in SETS:
        if SETS[name].exists():
            for row in load_rows(name):
                out.setdefault(str(row["id"]), row)
    return out


def load_env() -> None:
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()


def ask_llm(row: dict, *, max_tokens: int, retries: int = 2) -> dict:
    """Network phase: one call per row, threads only. Never verifies anything."""
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"],
                    base_url=os.environ.get("OPENAI_BASE_URL",
                                            "https://openrouter.ai/api/v1"))
    prompt = PROMPT.format(eq1=row["equation1"], eq2=row["equation2"])
    last_err = ""
    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            text = resp.choices[0].message.content or ""
            usage = resp.usage
            return {"id": str(row["id"]), "text": text,
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens}
        except Exception as exc:  # noqa: BLE001 - transport, not math
            last_err = f"{type(exc).__name__}: {exc}"
            time.sleep(1.5 * (attempt + 1))
    return {"id": str(row["id"]), "text": "", "error": last_err,
            "prompt_tokens": 0, "completion_tokens": 0}


def parse_lemmas(text: str) -> list[str]:
    text = re.sub(r"<think>[\s\S]*?</think>", "", text or "").strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    obj = None
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                obj = json.loads(match.group())
            except json.JSONDecodeError:
                obj = None
    if not isinstance(obj, dict):
        return []
    raw = obj.get("lemmas") or obj.get("lemma") or []
    if isinstance(raw, str):
        raw = [raw]
    return [s for s in raw if isinstance(s, str)][:5]


def verify_proposal(payload: tuple[dict, list[str]], *, egg_budget: float,
                    effort: str) -> dict:
    """CPU phase: separate process. Gates, then egg, then the kernel."""
    import oracles
    import solver as S

    row, lemma_texts = payload
    rid = str(row["id"])
    S.set_effort(effort)
    S.clear_term_caches()
    out = {"id": rid, "label": row.get("answer"), "proposals": len(lemma_texts),
           "solved": False, "rejects": []}
    try:
        eq1 = S.parse_equation(str(row["equation1"]))
        eq2 = S.parse_equation(str(row["equation2"]))
    except (KeyError, ValueError) as exc:
        out["rejects"].append(f"parse:{exc}")
        return out

    for text in lemma_texts:
        try:
            lemma = S.lemma_goal(text)
        except ValueError:
            out["rejects"].append(f"unparseable:{text}")
            continue
        goal_expr = S.lemma_applies_to_goal(lemma, eq2)
        if goal_expr is None:
            out["rejects"].append(f"does_not_close_goal:{text}")
            continue
        if not S.lemma_survives_models(eq1, lemma):
            out["rejects"].append(f"refuted_by_eq1_model:{text}")
            continue
        proof = S.egg_saturate_prove(eq1, lemma, time_budget=egg_budget)
        if proof is None:
            out["rejects"].append(f"egg_cannot_derive:{text}")
            continue
        code = S.lemma_certificate(lemma, proof, eq2["variables"], goal_expr)
        try:
            oracles.check_true_lemma_certificate(code, eq1, eq2)
        except oracles.OracleError as exc:
            out["rejects"].append(f"KERNEL_REJECT:{text}:{exc}")
            continue
        out.update(solved=True, lemma=text, code=code,
                   code_bytes=len(code.encode("utf-8")))
        return out
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--sets", default="")
    ap.add_argument("--unsolved", action="store_true",
                    help="restrict to rows the solver currently skips")
    ap.add_argument("--true-only", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8, help="network concurrency")
    ap.add_argument("--verify-workers", type=int, default=8)
    ap.add_argument("--egg-budget", type=float, default=25.0)
    ap.add_argument("--effort", default="standard")
    ap.add_argument("--max-tokens", type=int, default=16384)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    load_env()
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("no OPENROUTER_API_KEY (checked process env and repo .env)")
        return 2

    catalog = load_all()
    rows: list[dict] = []
    if args.ids:
        rows = [catalog[i] for i in args.ids.split(",") if i.strip() in catalog]
    elif args.sets:
        for name in args.sets.split(","):
            rows.extend(load_rows(name.strip()))
    else:
        print("pass --ids or --sets")
        return 2

    if args.true_only:
        rows = [r for r in rows if r.get("answer") is True]
    if args.unsolved:
        import solver as S
        keep = []
        for r in rows:
            S.set_effort("fast")
            S.clear_term_caches()
            if S.solve_problem(r, false_time_budget=2.0) is None:
                keep.append(r)
        rows = keep
        print(f"{len(rows)} unsolved row(s) after filtering", flush=True)
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("nothing to do")
        return 0

    print(f"phase 1: {len(rows)} LLM calls on {MODEL} "
          f"({args.workers} threads)", flush=True)
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        answers = list(pool.map(
            partial(ask_llm, max_tokens=args.max_tokens), rows))
    prompt_tokens = sum(a.get("prompt_tokens", 0) for a in answers)
    completion_tokens = sum(a.get("completion_tokens", 0) for a in answers)
    errors = [a for a in answers if a.get("error")]
    print(f"  {time.monotonic() - started:.0f}s, "
          f"{prompt_tokens} prompt + {completion_tokens} completion tokens, "
          f"{len(errors)} transport errors", flush=True)
    for a in errors[:3]:
        print(f"  ! {a['id']}: {a['error'][:120]}")

    by_id = {str(r["id"]): r for r in rows}
    payloads = []
    empty = 0
    for a in answers:
        lemmas = parse_lemmas(a["text"])
        if not lemmas:
            empty += 1
            continue
        payloads.append((by_id[a["id"]], lemmas))
    print(f"  {len(payloads)} rows with parseable lemma lists, "
          f"{empty} unparseable/empty", flush=True)

    print(f"\nphase 2: verification in {args.verify_workers} processes "
          f"(egg budget {args.egg_budget}s, effort {args.effort})", flush=True)
    started = time.monotonic()
    results = []
    with ProcessPoolExecutor(max_workers=args.verify_workers) as pool:
        for res in pool.map(partial(verify_proposal, egg_budget=args.egg_budget,
                                    effort=args.effort), payloads, chunksize=1):
            results.append(res)
            if res["solved"]:
                print(f"  SOLVED {res['id']:<26} via {res['lemma']!r} "
                      f"({res['code_bytes']}B)", flush=True)
    print(f"  {time.monotonic() - started:.0f}s", flush=True)

    solved = [r for r in results if r["solved"]]
    kernel_rejects = [r for r in results
                      if any(x.startswith("KERNEL_REJECT") for x in r["rejects"])]
    print(f"\nsolved {len(solved)}/{len(results)} verified rows")
    print(f"kernel rejects (should be 0): {len(kernel_rejects)}")
    reasons: dict[str, int] = {}
    for r in results:
        for x in r["rejects"]:
            reasons[x.split(":")[0]] = reasons.get(x.split(":")[0], 0) + 1
    print("reject reasons:", dict(sorted(reasons.items(),
                                        key=lambda kv: -kv[1])))
    print(f"tokens: {prompt_tokens} prompt + {completion_tokens} completion")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
