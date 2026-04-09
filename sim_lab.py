#!/usr/bin/env python3
"""
sim_lab — SAIR Equational Theories Stage 1 evaluator.

Matches the official platform pipeline exactly:
  - Prompt: evaluation.jinja2 template wrapping the cheatsheet
  - Model: Llama 3.3 70B via OpenRouter
  - Parsing: VERDICT: TRUE / FALSE
  - Scoring: strict F1 (unparsed TRUE → FN, unparsed FALSE → FP)

Usage:
    python sim_lab.py --data file.jsonl --cheatsheet cheatsheets/v24j.txt
    python sim_lab.py --subset normal --n 60 --cheatsheet cheatsheets/v24j.txt
    python sim_lab.py --subset hard3 --cheatsheet cheatsheets/v24j.txt --repeats 3
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import jinja2
import requests

# ── Constants ─────────────────────────────────────────────────────────────

DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct"
DEFAULT_REPEATS = 1
DEFAULT_TIMEOUT_S = 600
CHEATSHEET_MAX_BYTES = 10_240

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HF_DATASET = "SAIRfoundation/equational-theories-selected-problems"
HF_SUBSETS = ("normal", "hard", "hard1", "hard2", "hard3")
HF_CACHE_DIR = Path(__file__).parent / "data" / "hf_cache"

EVAL_TEMPLATE_URL = (
    "https://huggingface.co/datasets/"
    "SAIRfoundation/equational-theories-benchmark"
    "/raw/main/prompts/evaluation.jinja2"
)
EVAL_TEMPLATE_CACHE = HF_CACHE_DIR / "evaluation.jinja2"

_VERDICT_RE = re.compile(
    r"VERDICT\s*[:：]\s*(TRUE|FALSE)(?!\s*OR\b)", re.IGNORECASE
)


# ── Data structures ───────────────────────────────────────────────────────

@dataclass
class Problem:
    id: str
    index: int
    difficulty: str
    equation1: str
    equation2: str
    answer: bool


@dataclass
class Result:
    problem: Problem
    repeat_id: int
    verdict: Optional[bool]
    raw_response: str
    elapsed_s: float
    usage: Optional[dict] = None


@dataclass
class RunStats:
    total: int = 0
    correct: int = 0
    incorrect: int = 0
    unparsed: int = 0
    true_total: int = 0
    true_correct: int = 0
    false_total: int = 0
    false_correct: int = 0
    elapsed_total: float = 0.0
    results: list = field(default_factory=list)
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def true_accuracy(self) -> float:
        return self.true_correct / self.true_total if self.true_total else 0.0

    @property
    def false_accuracy(self) -> float:
        return self.false_correct / self.false_total if self.false_total else 0.0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def parse_rate(self) -> float:
        return (self.total - self.unparsed) / self.total if self.total else 0.0

    @property
    def avg_time(self) -> float:
        return self.elapsed_total / self.total if self.total else 0.0


# ── Data loading ──────────────────────────────────────────────────────────

def _normalize_eq(eq: str) -> str:
    return eq.replace("\u25c7", "*").strip()


def download_hf_subset(subset: str) -> Path:
    if subset not in HF_SUBSETS:
        raise ValueError(f"Unknown subset '{subset}'. Choose from: {HF_SUBSETS}")
    cache_path = HF_CACHE_DIR / f"{subset}.jsonl"
    if cache_path.exists():
        return cache_path
    url = (
        f"https://huggingface.co/datasets/{HF_DATASET}"
        f"/resolve/main/data/{subset}.jsonl"
    )
    print(f"Downloading {subset} from HuggingFace ...")
    HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    cache_path.write_bytes(r.content)
    print(f"  Cached → {cache_path}  ({len(r.content):,} bytes)")
    return cache_path


def download_eval_template() -> str:
    if EVAL_TEMPLATE_CACHE.exists():
        return EVAL_TEMPLATE_CACHE.read_text(encoding="utf-8")
    print("Downloading evaluation template from HuggingFace ...")
    EVAL_TEMPLATE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(EVAL_TEMPLATE_URL, timeout=60)
    r.raise_for_status()
    EVAL_TEMPLATE_CACHE.write_bytes(r.content)
    print(f"  Cached → {EVAL_TEMPLATE_CACHE}")
    return r.content.decode("utf-8")


def load_problems(
    path: Optional[str] = None,
    subset: Optional[str] = None,
    n: Optional[int] = None,
    shuffle: bool = False,
) -> list[Problem]:
    if subset:
        resolved = download_hf_subset(subset)
    elif path:
        resolved = Path(path)
    else:
        raise ValueError("Provide --data or --subset")

    problems = []
    with open(resolved, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            problems.append(Problem(
                id=obj["id"],
                index=obj.get("index", 0),
                difficulty=obj.get("difficulty", "unknown"),
                equation1=_normalize_eq(obj["equation1"]),
                equation2=_normalize_eq(obj["equation2"]),
                answer=bool(obj["answer"]),
            ))

    if shuffle:
        import random
        random.shuffle(problems)

    if n is not None:
        problems = problems[:n]

    return problems


def load_cheatsheet(path: str) -> str:
    p = Path(path)
    raw = p.read_bytes()
    size = len(raw)
    if size > CHEATSHEET_MAX_BYTES:
        print(f"WARNING: cheatsheet {size:,} bytes — exceeds 10 KB cap!")
    else:
        print(f"Cheatsheet: {size:,} / {CHEATSHEET_MAX_BYTES:,} bytes "
              f"({100 * size / CHEATSHEET_MAX_BYTES:.1f}%)")
    return raw.decode("utf-8")


# ── Prompt rendering ──────────────────────────────────────────────────────

def render_prompt(problem: Problem, cheatsheet: str) -> str:
    eq1 = problem.equation1
    eq2 = problem.equation2

    # Render cheatsheet (substitute equation placeholders)
    rendered_cs = cheatsheet
    rendered_cs = rendered_cs.replace("{{ equation1 }}", eq1)
    rendered_cs = rendered_cs.replace("{{equation1}}", eq1)
    rendered_cs = rendered_cs.replace("{{ equation2 }}", eq2)
    rendered_cs = rendered_cs.replace("{{equation2}}", eq2)

    # Render evaluation template (matches official platform)
    template_src = download_eval_template()
    return jinja2.Template(template_src).render(
        equation1=eq1,
        equation2=eq2,
        cheatsheet=rendered_cs,
    )


# ── Verdict parsing ──────────────────────────────────────────────────────

def parse_verdict(response: str) -> Optional[bool]:
    cleaned = response.replace("***", "").replace("**", "").replace("__", "").replace("`", "")
    matches = list(_VERDICT_RE.finditer(cleaned))
    if matches:
        return matches[-1].group(1).upper() == "TRUE"
    return None


# ── OpenRouter API ────────────────────────────────────────────────────────

def query_openrouter(
    prompt: str,
    model: str,
    api_key: str,
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> tuple[str, float, Optional[dict]]:
    t0 = time.time()
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout_s,
    )
    r.raise_for_status()
    data = r.json()
    elapsed = time.time() - t0
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage")
    norm_usage = None
    if usage:
        norm_usage = {
            "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
            "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
        }
    return text, elapsed, norm_usage


# ── Evaluation engine ─────────────────────────────────────────────────────

def evaluate_one(
    problem: Problem,
    cheatsheet: str,
    model: str,
    api_key: str,
    repeat_id: int = 1,
) -> Result:
    prompt = render_prompt(problem, cheatsheet)
    try:
        response, elapsed, usage = query_openrouter(prompt, model, api_key)
    except Exception as e:
        return Result(
            problem=problem,
            repeat_id=repeat_id,
            verdict=None,
            raw_response=f"ERROR: {e}",
            elapsed_s=0.0,
            usage=None,
        )
    verdict = parse_verdict(response)
    return Result(
        problem=problem,
        repeat_id=repeat_id,
        verdict=verdict,
        raw_response=response,
        elapsed_s=elapsed,
        usage=usage,
    )


def _update_stats(stats: RunStats, result: Result) -> str:
    p = result.problem
    stats.total += 1
    stats.elapsed_total += result.elapsed_s
    stats.results.append(result)
    if result.usage:
        stats.prompt_tokens += result.usage.get("prompt_tokens", 0)
        stats.completion_tokens += result.usage.get("completion_tokens", 0)

    if p.answer:
        stats.true_total += 1
    else:
        stats.false_total += 1

    if result.verdict is None:
        stats.unparsed += 1
        if p.answer:
            stats.fn += 1
        else:
            stats.fp += 1
        return "?"

    correct = result.verdict == p.answer
    if correct:
        stats.correct += 1
        if p.answer:
            stats.true_correct += 1
        else:
            stats.false_correct += 1
    else:
        stats.incorrect += 1

    if result.verdict and p.answer:
        stats.tp += 1
    elif result.verdict and not p.answer:
        stats.fp += 1
    elif not result.verdict and p.answer:
        stats.fn += 1
    else:
        stats.tn += 1

    return "✓" if correct else "✗"


def run_evaluation(
    problems: list[Problem],
    cheatsheet: str,
    model: str,
    api_key: str,
    repeats: int = DEFAULT_REPEATS,
    verbose: bool = True,
    checkpoint_path: Optional[str] = None,
) -> RunStats:
    stats = RunStats()
    total_runs = len(problems) * repeats

    # Resume from checkpoint
    done: set[tuple[str, int]] = set()
    if checkpoint_path and Path(checkpoint_path).exists():
        try:
            ckpt = json.loads(Path(checkpoint_path).read_text(encoding="utf-8"))
            for r in ckpt.get("results", []):
                done.add((r["id"], r["repeat_id"]))
            print(f"  Resuming: {len(done)} runs cached")
        except Exception:
            pass

    run_idx = 0
    for problem in problems:
        for rep in range(1, repeats + 1):
            run_idx += 1
            if (problem.id, rep) in done:
                if verbose:
                    print(f"  [{run_idx:4d}/{total_runs}] {problem.id:15s} r{rep}  (cached)")
                continue

            result = evaluate_one(problem, cheatsheet, model, api_key, rep)
            mark = _update_stats(stats, result)

            if verbose:
                gt = "T" if problem.answer else "F"
                pred = "T" if result.verdict is True else ("F" if result.verdict is False else "?")
                print(
                    f"  [{run_idx:4d}/{total_runs}] {problem.id:15s} "
                    f"gt={gt} pred={pred} {mark}  "
                    f"{result.elapsed_s:5.1f}s  "
                    f"acc={stats.accuracy:.1%}  f1={stats.f1:.1%}"
                )

            # Incremental checkpoint
            if checkpoint_path:
                _save_checkpoint(stats, checkpoint_path, model)

    return stats


def _save_checkpoint(stats: RunStats, path: str, model: str):
    data = {
        "model": model,
        "checkpoint": True,
        "results": [_result_to_dict(r) for r in stats.results],
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _result_to_dict(r: Result) -> dict:
    return {
        "id": r.problem.id,
        "repeat_id": r.repeat_id,
        "equation1": r.problem.equation1,
        "equation2": r.problem.equation2,
        "ground_truth": r.problem.answer,
        "predicted": r.verdict,
        "correct": r.verdict == r.problem.answer if r.verdict is not None else False,
        "parsed_ok": r.verdict is not None,
        "elapsed_s": round(r.elapsed_s, 2),
        "raw_response": r.raw_response,
        "usage": r.usage,
    }


# ── Reporting ─────────────────────────────────────────────────────────────

def print_report(stats: RunStats, label: str = ""):
    hdr = f"═══ Results{': ' + label if label else ''} ═══"
    print(f"\n{'═' * len(hdr)}")
    print(hdr)
    print(f"{'═' * len(hdr)}")
    print(f"  Total:        {stats.total}")
    print(f"  Correct:      {stats.correct}")
    print(f"  Incorrect:    {stats.incorrect}")
    print(f"  Unparsed:     {stats.unparsed}")
    print(f"  ─────────────────────────")
    print(f"  Accuracy:     {stats.accuracy:.1%}")
    print(f"  F1 (strict):  {stats.f1:.1%}")
    print(f"  Precision:    {stats.precision:.1%}")
    print(f"  Recall:       {stats.recall:.1%}")
    print(f"  Parse rate:   {stats.parse_rate:.1%}")
    print(f"  ─────────────────────────")
    print(f"  TRUE acc:     {stats.true_accuracy:.1%}  ({stats.true_correct}/{stats.true_total})")
    print(f"  FALSE acc:    {stats.false_accuracy:.1%}  ({stats.false_correct}/{stats.false_total})")
    print(f"  TP/FP/FN/TN:  {stats.tp}/{stats.fp}/{stats.fn}/{stats.tn}")
    print(f"  ─────────────────────────")
    print(f"  Avg time:     {stats.avg_time:.1f}s")
    print(f"  Total time:   {stats.elapsed_total:.1f}s")
    print()


def print_errors(stats: RunStats, top_n: int = 10):
    errors = [r for r in stats.results if r.verdict is not None and r.verdict != r.problem.answer]
    unparsed = [r for r in stats.results if r.verdict is None]
    fn = [r for r in errors if r.problem.answer and not r.verdict]
    fp = [r for r in errors if not r.problem.answer and r.verdict]

    print(f"\n  ERROR ANALYSIS")
    print(f"  Total errors: {len(errors)}  |  FN: {len(fn)}  |  FP: {len(fp)}  |  Unparsed: {len(unparsed)}")

    if fn:
        print(f"\n  False negatives (should be TRUE):")
        for r in fn[:top_n]:
            print(f"    {r.problem.id}: {r.problem.equation1}  →  {r.problem.equation2}")
    if fp:
        print(f"\n  False positives (should be FALSE):")
        for r in fp[:top_n]:
            print(f"    {r.problem.id}: {r.problem.equation1}  →  {r.problem.equation2}")
    if unparsed:
        print(f"\n  Unparsed:")
        for r in unparsed[:top_n]:
            print(f"    {r.problem.id}: {r.raw_response[:100]}...")
    print()


def save_results(stats: RunStats, output_path: str, model: str,
                 cheatsheet_path: Optional[str], subset: Optional[str] = None,
                 repeats: int = 1):
    data = {
        "model": model,
        "cheatsheet": cheatsheet_path or "(none)",
        "subset": subset or "(local)",
        "repeats": repeats,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total": stats.total,
            "correct": stats.correct,
            "incorrect": stats.incorrect,
            "unparsed": stats.unparsed,
            "accuracy": round(stats.accuracy, 4),
            "f1_score": round(stats.f1, 4),
            "precision": round(stats.precision, 4),
            "recall": round(stats.recall, 4),
            "parse_rate": round(stats.parse_rate, 4),
            "true_accuracy": round(stats.true_accuracy, 4),
            "false_accuracy": round(stats.false_accuracy, 4),
            "tp": stats.tp, "fp": stats.fp, "fn": stats.fn, "tn": stats.tn,
            "avg_time_s": round(stats.avg_time, 2),
            "total_time_s": round(stats.elapsed_total, 2),
            "prompt_tokens": stats.prompt_tokens,
            "completion_tokens": stats.completion_tokens,
        },
        "results": [_result_to_dict(r) for r in stats.results],
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved → {output_path}")


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="SAIR Stage 1 Simulation Lab")
    ap.add_argument("--subset", choices=list(HF_SUBSETS))
    ap.add_argument("--data", help="Local JSONL benchmark file")
    ap.add_argument("--cheatsheet", required=True, help="Cheatsheet path")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--n", type=int, help="Limit number of problems")
    ap.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    ap.add_argument("--shuffle", action="store_true")
    ap.add_argument("--output", help="Output JSON path")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--errors", action="store_true", help="Print error analysis")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--api-key", default=None)
    # Retained for CLI compatibility with scripts that pass these
    ap.add_argument("--openrouter", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--prompt-mode", default="wrapped", help=argparse.SUPPRESS)
    ap.add_argument("--parser", default="strict", help=argparse.SUPPRESS)

    args = ap.parse_args()

    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("ERROR: set OPENROUTER_API_KEY or pass --api-key")
        sys.exit(1)

    if not args.subset and not args.data:
        print("ERROR: provide --subset or --data")
        sys.exit(1)
    if args.data and not Path(args.data).exists():
        print(f"ERROR: file not found: {args.data}")
        sys.exit(1)

    # Pre-download evaluation template
    download_eval_template()

    problems = load_problems(
        path=args.data, subset=args.subset,
        n=args.n, shuffle=args.shuffle,
    )

    cheatsheet = load_cheatsheet(args.cheatsheet)

    true_count = sum(1 for p in problems if p.answer)
    false_count = len(problems) - true_count
    source = args.subset or args.data
    total_runs = len(problems) * args.repeats

    print(f"\n{'═' * 50}")
    print(f"  SAIR Stage 1 Simulation Lab")
    print(f"{'═' * 50}")
    print(f"  Model:      {args.model}")
    print(f"  Source:     {source}")
    print(f"  Problems:  {len(problems)} (T:{true_count} F:{false_count})")
    print(f"  Repeats:   {args.repeats}")
    print(f"  Total:     {total_runs} runs")
    print(f"  Cheatsheet: {args.cheatsheet}")
    print(f"{'═' * 50}\n")

    # Checkpoint path
    ckpt = None
    if args.resume:
        ts = time.strftime("%Y%m%d_%H%M%S")
        cs_label = Path(args.cheatsheet).stem
        sub_label = args.subset or Path(args.data).stem
        ckpt = f"results/sim_{sub_label}_{cs_label}_latest.json.checkpoint"

    stats = run_evaluation(
        problems, cheatsheet, args.model, api_key,
        repeats=args.repeats, verbose=not args.quiet,
        checkpoint_path=ckpt,
    )

    print_report(stats, Path(args.cheatsheet).stem)

    if args.errors:
        print_errors(stats)

    # Save results
    if args.output:
        out = args.output
    else:
        ts = time.strftime("%Y%m%d_%H%M%S")
        cs_label = Path(args.cheatsheet).stem
        sub_label = args.subset or Path(args.data).stem
        out = f"results/sim_{sub_label}_{cs_label}_{ts}.json"

    save_results(stats, out, args.model, args.cheatsheet,
                 subset=args.subset, repeats=args.repeats)

    # Clean checkpoint
    if ckpt and Path(ckpt).exists():
        Path(ckpt).unlink()


if __name__ == "__main__":
    main()
