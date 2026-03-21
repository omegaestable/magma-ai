#!/usr/bin/env python3
"""
SAIR Equational Theories — Stage 1 Simulation Lab

Evaluation harness that mirrors the official SAIR playground and competition
pipeline.  Supports both Ollama (local) and OpenRouter (cloud) inference.

Matches the official format:
  - Official HF problem subsets: normal, hard, hard1, hard2
  - Complete-prompt mode (cheatsheet IS the full prompt template)
  - 3 repeats per problem (configurable)
  - Strict F1 scoring (unparsed TRUE→FN, unparsed FALSE→FP)
  - 10 KB cheatsheet cap

Usage:
    # Quick smoke test (5 problems, OpenRouter)
    python sim_lab.py --quick --openrouter

    # Run official hard2 subset via OpenRouter
    python sim_lab.py --subset hard2 --openrouter

    # Run with a cheatsheet
    python sim_lab.py --subset normal --n 100 --cheatsheet cheatsheets/v10_proof_required.txt --openrouter

    # Ollama (local, offline)
    python sim_lab.py --subset hard2

    # Compare two cheatsheets
    python sim_lab.py --compare cs1.txt cs2.txt --subset hard2 --n 50 --openrouter

    # 3 repeats per problem (matches official benchmark)
    python sim_lab.py --subset hard2 --repeats 3 --openrouter
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

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct"
DEFAULT_MODEL_OLLAMA = "llama3.3:70b"
DEFAULT_NUM_PREDICT = 1024
DEFAULT_REQUEST_TIMEOUT_S = 600          # 10 min — matches competition cap
DEFAULT_REPEATS = 1
CHEATSHEET_MAX_BYTES = 10_240            # 10 KB (official cap)

# OpenRouter (same provider the SAIR benchmark uses)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Official HuggingFace dataset info
HF_DATASET = "SAIRfoundation/equational-theories-selected-problems"
HF_SUBSETS = ("normal", "hard", "hard1", "hard2")
HF_CACHE_DIR = Path(__file__).parent / "data" / "hf_cache"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

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
    verdict: Optional[bool]          # None = unparsed
    raw_response: str
    elapsed_s: float
    parsed_ok: bool
    usage: Optional[dict[str, int]] = None


@dataclass
class RunStats:
    """Aggregate metrics matching the official SAIR benchmark leaderboard."""
    total: int = 0                   # total runs (problems × repeats)
    correct: int = 0
    incorrect: int = 0
    unparsed: int = 0
    true_total: int = 0              # runs where ground truth = TRUE
    true_correct: int = 0
    false_total: int = 0             # runs where ground truth = FALSE
    false_correct: int = 0
    elapsed_total: float = 0.0
    results: list = field(default_factory=list)

    # Strict confusion matrix (official scoring)
    # Unparsed TRUE → FN, Unparsed FALSE → FP
    tp: int = 0   # predicted TRUE,  answer TRUE
    fp: int = 0   # predicted TRUE,  answer FALSE  (+ unparsed FALSE)
    fn: int = 0   # predicted FALSE, answer TRUE    (+ unparsed TRUE)
    tn: int = 0   # predicted FALSE, answer FALSE
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0

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
        """Strict F1 — matches official SAIR leaderboard calculation."""
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def parse_success_rate(self) -> float:
        return (self.total - self.unparsed) / self.total if self.total else 0.0

    @property
    def avg_time(self) -> float:
        return self.elapsed_total / self.total if self.total else 0.0

    @property
    def quality_score(self) -> float:
        """Fraction of parsed responses with properly filled PROOF/CE fields."""
        parsed = [r for r in self.results if r.verdict is not None]
        if not parsed:
            return 0.0
        good = sum(1 for r in parsed if parse_proof_quality(r.raw_response, r.verdict))
        return good / len(parsed)


# ---------------------------------------------------------------------------
# Problem loading — official HF datasets + local JSONL
# ---------------------------------------------------------------------------

def download_hf_subset(subset: str) -> Path:
    """Download an official HF problem subset JSONL if not cached."""
    if subset not in HF_SUBSETS:
        raise ValueError(f"Unknown subset '{subset}'. Choose from: {HF_SUBSETS}")
    cache_path = HF_CACHE_DIR / f"{subset}.jsonl"
    if cache_path.exists():
        return cache_path
    url = (
        f"https://huggingface.co/datasets/{HF_DATASET}"
        f"/resolve/main/data/{subset}.jsonl"
    )
    print(f"Downloading {subset} dataset from HuggingFace …")
    HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    cache_path.write_bytes(r.content)
    print(f"  Cached → {cache_path}  ({len(r.content):,} bytes)")
    return cache_path


def load_problems(
    path: Optional[str] = None,
    subset: Optional[str] = None,
    n: Optional[int] = None,
    shuffle: bool = False,
    answer_filter: str = "all",
) -> list[Problem]:
    """Load problems from a local JSONL file or an official HF subset."""
    if subset:
        resolved = download_hf_subset(subset)
    elif path:
        resolved = Path(path)
    else:
        raise ValueError("Provide --data <file> or --subset <name>")

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
                equation1=obj["equation1"],
                equation2=obj["equation2"],
                answer=bool(obj["answer"]),
            ))

    if answer_filter == "true":
        problems = [p for p in problems if p.answer]
    elif answer_filter == "false":
        problems = [p for p in problems if not p.answer]

    if shuffle:
        import random
        random.shuffle(problems)

    if n is not None:
        problems = problems[:n]

    return problems


# ---------------------------------------------------------------------------
# Prompt rendering — complete-prompt mode (matches competition submission)
# ---------------------------------------------------------------------------

def load_cheatsheet(path: Optional[str]) -> str:
    """Load and validate cheatsheet size (10 KB official cap)."""
    if not path:
        return ""
    p = Path(path)
    raw = p.read_bytes()
    size = len(raw)
    if size > CHEATSHEET_MAX_BYTES:
        print(f"WARNING: Cheatsheet is {size:,} bytes — exceeds 10 KB limit ({CHEATSHEET_MAX_BYTES:,} bytes)!")
        print(f"  Overage: {size - CHEATSHEET_MAX_BYTES:,} bytes")
    else:
        print(f"Cheatsheet: {size:,} / {CHEATSHEET_MAX_BYTES:,} bytes ({100*size/CHEATSHEET_MAX_BYTES:.1f}%)")
    return raw.decode("utf-8")


def render_prompt(problem: Problem, cheatsheet: str) -> str:
    """Render the full prompt from the cheatsheet template alone."""
    if not cheatsheet:
        raise ValueError("A cheatsheet prompt is required.")
    return jinja2.Template(cheatsheet).render(
        equation1=problem.equation1,
        equation2=problem.equation2,
    )


# ---------------------------------------------------------------------------
# Verdict parsing
# ---------------------------------------------------------------------------

_VERDICT_RE = re.compile(r"VERDICT\s*:\s*(TRUE|FALSE)", re.IGNORECASE)
_PROOF_RE = re.compile(r"PROOF\s*:(.*?)(?=COUNTEREXAMPLE\s*:|$)", re.IGNORECASE | re.DOTALL)
_CE_RE = re.compile(r"COUNTEREXAMPLE\s*:(.*?)$", re.IGNORECASE | re.DOTALL)


def parse_verdict(response: str) -> Optional[bool]:
    """Extract TRUE/FALSE verdict from model response."""
    m = _VERDICT_RE.search(response)
    if m:
        return m.group(1).upper() == "TRUE"
    return None


def parse_proof_quality(response: str, verdict: Optional[bool]) -> bool:
    """Check if PROOF/COUNTEREXAMPLE field is properly filled for the verdict."""
    if verdict is None:
        return False
    if verdict:  # TRUE → PROOF must be non-empty
        m = _PROOF_RE.search(response)
        return bool(m and m.group(1).strip())
    else:  # FALSE → COUNTEREXAMPLE must be non-empty
        m = _CE_RE.search(response)
        return bool(m and m.group(1).strip())


# ---------------------------------------------------------------------------
# Ollama inference
# ---------------------------------------------------------------------------

def check_ollama() -> bool:
    """Check if Ollama is running."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


def list_models() -> list[str]:
    """List available Ollama models."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        r.raise_for_status()
        data = r.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def query_ollama(
    prompt: str,
    model: str,
    temperature: float = 0.0,
    num_predict: int = DEFAULT_NUM_PREDICT,
    timeout_s: int = DEFAULT_REQUEST_TIMEOUT_S,
) -> tuple[str, float, Optional[dict[str, int]]]:
    """Send a prompt to Ollama and return (response_text, elapsed_seconds)."""
    t0 = time.time()
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=timeout_s,
    )
    r.raise_for_status()
    elapsed = time.time() - t0
    return r.json().get("response", ""), elapsed, None


# ---------------------------------------------------------------------------
# OpenRouter inference (cloud — same provider as SAIR benchmark)
# ---------------------------------------------------------------------------

def query_openrouter(
    prompt: str,
    model: str,
    api_key: str,
    temperature: float = 0.0,
    max_tokens: int = DEFAULT_NUM_PREDICT,
    timeout_s: int = DEFAULT_REQUEST_TIMEOUT_S,
) -> tuple[str, float, Optional[dict[str, int]]]:
    """Send a prompt to OpenRouter and return (response_text, elapsed_seconds, usage)."""
    t0 = time.time()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    r = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=timeout_s,
    )
    r.raise_for_status()
    data = r.json()
    elapsed = time.time() - t0
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage")
    normalized_usage = None
    if usage:
        normalized_usage = {
            "prompt_tokens": int(usage.get("prompt_tokens") or usage.get("input_tokens") or usage.get("promptTokens") or 0),
            "completion_tokens": int(usage.get("completion_tokens") or usage.get("output_tokens") or usage.get("completionTokens") or 0),
            "reasoning_tokens": int(usage.get("reasoning_tokens") or usage.get("reasoningTokens") or 0),
        }
    return text, elapsed, normalized_usage


# ---------------------------------------------------------------------------
# Evaluation engine
# ---------------------------------------------------------------------------

# Module-level backend state (set from CLI)
_backend = "ollama"       # "ollama" or "openrouter"
_api_key = ""             # OpenRouter API key when using cloud


def evaluate_problem(
    problem: Problem,
    cheatsheet: str,
    model: str,
    repeat_id: int = 1,
    temperature: float = 0.0,
    num_predict: int = DEFAULT_NUM_PREDICT,
    request_timeout_s: int = DEFAULT_REQUEST_TIMEOUT_S,
) -> Result:
    """Evaluate a single problem (one repeat)."""
    prompt = render_prompt(problem, cheatsheet)
    try:
        if _backend == "openrouter":
            response, elapsed, usage = query_openrouter(
                prompt, model, _api_key,
                temperature=temperature,
                max_tokens=num_predict,
                timeout_s=request_timeout_s,
            )
        else:
            response, elapsed, usage = query_ollama(
                prompt, model, temperature,
                num_predict=num_predict,
                timeout_s=request_timeout_s,
            )
    except Exception as e:
        return Result(
            problem=problem,
            repeat_id=repeat_id,
            verdict=None,
            raw_response=f"ERROR: {e}",
            elapsed_s=0.0,
            parsed_ok=False,
            usage=None,
        )

    verdict = parse_verdict(response)
    return Result(
        problem=problem,
        repeat_id=repeat_id,
        verdict=verdict,
        raw_response=response,
        elapsed_s=elapsed,
        parsed_ok=verdict is not None,
        usage=usage,
    )


def _update_stats(stats: RunStats, result: Result) -> str:
    """Update stats with one result and return mark character."""
    problem = result.problem
    stats.total += 1
    stats.elapsed_total += result.elapsed_s
    stats.results.append(result)
    if result.usage:
        stats.prompt_tokens += int(result.usage.get("prompt_tokens", 0) or 0)
        stats.completion_tokens += int(result.usage.get("completion_tokens", 0) or 0)
        stats.reasoning_tokens += int(result.usage.get("reasoning_tokens", 0) or 0)

    if problem.answer:
        stats.true_total += 1
    else:
        stats.false_total += 1

    if result.verdict is None:
        stats.unparsed += 1
        # Strict scoring: unparsed TRUE → FN, unparsed FALSE → FP
        if problem.answer:
            stats.fn += 1
        else:
            stats.fp += 1
        return "?"

    is_correct = result.verdict == problem.answer
    if is_correct:
        stats.correct += 1
        if problem.answer:
            stats.true_correct += 1
        else:
            stats.false_correct += 1
    else:
        stats.incorrect += 1

    # Confusion matrix
    if result.verdict and problem.answer:
        stats.tp += 1
    elif result.verdict and not problem.answer:
        stats.fp += 1
    elif not result.verdict and problem.answer:
        stats.fn += 1
    else:
        stats.tn += 1

    return "✓" if is_correct else "✗"


def run_evaluation(
    problems: list[Problem],
    cheatsheet: str,
    model: str,
    temperature: float = 0.0,
    num_predict: int = DEFAULT_NUM_PREDICT,
    request_timeout_s: int = DEFAULT_REQUEST_TIMEOUT_S,
    repeats: int = DEFAULT_REPEATS,
    verbose: bool = True,
) -> RunStats:
    """Run evaluation over a list of problems (with repeats)."""
    stats = RunStats()
    total_runs = len(problems) * repeats
    run_idx = 0

    for i, problem in enumerate(problems):
        for rep in range(1, repeats + 1):
            run_idx += 1
            result = evaluate_problem(
                problem, cheatsheet, model,
                repeat_id=rep,
                temperature=temperature,
                num_predict=num_predict,
                request_timeout_s=request_timeout_s,
            )
            mark = _update_stats(stats, result)

            if verbose:
                gt = "T" if problem.answer else "F"
                pred = "T" if result.verdict is True else ("F" if result.verdict is False else "?")
                rep_label = f"r{rep}" if repeats > 1 else ""
                print(
                    f"  [{run_idx:4d}/{total_runs}] {problem.id:15s} {rep_label:3s} "
                    f"gt={gt} pred={pred} {mark}  "
                    f"{result.elapsed_s:5.1f}s  "
                    f"acc={stats.accuracy:.1%}  f1={stats.f1:.1%}"
                )

    return stats


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(stats: RunStats, label: str = ""):
    """Print a formatted evaluation report matching SAIR benchmark metrics."""
    header = f"═══ Results{': ' + label if label else ''} ═══"
    print(f"\n{'═' * len(header)}")
    print(header)
    print(f"{'═' * len(header)}")
    print(f"  Total runs:       {stats.total}")
    print(f"  Correct:          {stats.correct}")
    print(f"  Incorrect:        {stats.incorrect}")
    print(f"  Unparsed:         {stats.unparsed}")
    print(f"  ─────────────────────────────────")
    print(f"  Accuracy:         {stats.accuracy:.1%}")
    print(f"  F1 (strict):      {stats.f1:.1%}")
    print(f"  Precision (TRUE): {stats.precision:.1%}")
    print(f"  Recall (TRUE):    {stats.recall:.1%}")
    print(f"  Parse rate:       {stats.parse_success_rate:.1%}")
    print(f"  ─────────────────────────────────")
    print(f"  TRUE accuracy:    {stats.true_accuracy:.1%}  ({stats.true_correct}/{stats.true_total})")
    print(f"  FALSE accuracy:   {stats.false_accuracy:.1%}  ({stats.false_correct}/{stats.false_total})")
    print(f"  TP/FP/FN/TN:      {stats.tp}/{stats.fp}/{stats.fn}/{stats.tn}")
    print(f"  ─────────────────────────────────")
    print(f"  Quality score:    {stats.quality_score:.1%}")
    print(f"  Avg time/run:     {stats.avg_time:.1f}s")
    print(f"  Total time:       {stats.elapsed_total:.1f}s")
    print()


def save_results(stats: RunStats, output_path: str, model: str,
                 cheatsheet_path: Optional[str], subset: Optional[str] = None,
                 repeats: int = 1):
    """Save detailed results to JSON (mirrors SAIR benchmark schema)."""
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
            "parse_success_rate": round(stats.parse_success_rate, 4),
            "true_accuracy": round(stats.true_accuracy, 4),
            "false_accuracy": round(stats.false_accuracy, 4),
            "tp": stats.tp,
            "fp": stats.fp,
            "fn": stats.fn,
            "tn": stats.tn,
            "quality_score": round(stats.quality_score, 4),
            "avg_time_s": round(stats.avg_time, 2),
            "total_time_s": round(stats.elapsed_total, 2),
            "prompt_tokens": stats.prompt_tokens,
            "completion_tokens": stats.completion_tokens,
            "reasoning_tokens": stats.reasoning_tokens,
            "total_tokens": stats.prompt_tokens + stats.completion_tokens + stats.reasoning_tokens,
        },
        "results": [
            {
                "id": r.problem.id,
                "repeat_id": r.repeat_id,
                "equation1": r.problem.equation1,
                "equation2": r.problem.equation2,
                "ground_truth": r.problem.answer,
                "predicted": r.verdict,
                "correct": r.verdict == r.problem.answer if r.verdict is not None else False,
                "parsed_ok": r.parsed_ok,
                "elapsed_s": round(r.elapsed_s, 2),
                "raw_response": r.raw_response,
                "usage": r.usage,
            }
            for r in stats.results
        ],
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {output_path}")


# ---------------------------------------------------------------------------
# Comparison mode
# ---------------------------------------------------------------------------

def run_comparison(
    cheatsheet_paths: list[str],
    problems: list[Problem],
    model: str,
    temperature: float = 0.0,
    num_predict: int = DEFAULT_NUM_PREDICT,
    request_timeout_s: int = DEFAULT_REQUEST_TIMEOUT_S,
    repeats: int = DEFAULT_REPEATS,
    verbose: bool = True,
):
    """Run evaluation with multiple cheatsheets and compare."""
    total_runs = len(problems) * repeats
    print(f"\n{'═' * 60}")
    print(f"  COMPARISON MODE — {len(cheatsheet_paths)} cheatsheets × {len(problems)} problems × {repeats} repeats")
    print(f"  Model: {model}")
    print(f"{'═' * 60}\n")

    all_stats = []
    for cs_path in cheatsheet_paths:
        label = Path(cs_path).stem
        print(f"\n▶ Evaluating: {cs_path}")
        cheatsheet = load_cheatsheet(cs_path)
        stats = run_evaluation(
            problems, cheatsheet, model,
            temperature, num_predict=num_predict,
            request_timeout_s=request_timeout_s,
            repeats=repeats, verbose=verbose,
        )
        print_report(stats, label)
        all_stats.append((label, stats))

    # Comparison table
    print(f"\n{'═' * 80}")
    print(f"  COMPARISON SUMMARY")
    print(f"{'═' * 80}")
    print(f"  {'Cheatsheet':<25s} {'Acc':>7s} {'F1':>7s} {'T_acc':>7s} {'F_acc':>7s} {'Parse':>7s} {'Unp':>5s}")
    print(f"  {'─' * 25} {'─' * 7} {'─' * 7} {'─' * 7} {'─' * 7} {'─' * 7} {'─' * 5}")
    for label, s in all_stats:
        print(
            f"  {label:<25s} "
            f"{s.accuracy:>6.1%} "
            f"{s.f1:>6.1%} "
            f"{s.true_accuracy:>6.1%} "
            f"{s.false_accuracy:>6.1%} "
            f"{s.parse_success_rate:>6.1%} "
            f"{s.unparsed:>5d}"
        )
    print()


# ---------------------------------------------------------------------------
# Error analysis
# ---------------------------------------------------------------------------

def print_error_analysis(stats: RunStats, top_n: int = 10):
    """Print error analysis focusing on misclassified problems."""
    errors = [r for r in stats.results if r.verdict is not None and r.verdict != r.problem.answer]
    unparsed = [r for r in stats.results if r.verdict is None]

    false_negatives = [r for r in errors if r.problem.answer and not r.verdict]
    false_positives = [r for r in errors if not r.problem.answer and r.verdict]

    print(f"\n{'═' * 60}")
    print(f"  ERROR ANALYSIS")
    print(f"{'═' * 60}")
    print(f"  Total errors: {len(errors)}")
    print(f"  False negatives (missed TRUE):  {len(false_negatives)}")
    print(f"  False positives (wrong TRUE):   {len(false_positives)}")
    print(f"  Unparsed:                       {len(unparsed)}")

    if false_negatives:
        print(f"\n  ── Top {min(top_n, len(false_negatives))} FALSE NEGATIVES (should be TRUE) ──")
        for r in false_negatives[:top_n]:
            print(f"    {r.problem.id}: {r.problem.equation1}  →  {r.problem.equation2}")

    if false_positives:
        print(f"\n  ── Top {min(top_n, len(false_positives))} FALSE POSITIVES (should be FALSE) ──")
        for r in false_positives[:top_n]:
            print(f"    {r.problem.id}: {r.problem.equation1}  →  {r.problem.equation2}")

    if unparsed:
        print(f"\n  ── Unparsed responses ──")
        for r in unparsed[:top_n]:
            snippet = r.raw_response[:120].replace("\n", " ")
            print(f"    {r.problem.id}: {snippet}...")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SAIR Equational Theories — Stage 1 Simulation Lab",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sim_lab.py --quick --openrouter                       # 5-problem smoke test (cloud)
  python sim_lab.py --subset normal --n 100 --openrouter       # 100 normal problems (cloud)
  python sim_lab.py --subset hard2 --cheatsheet cs/v10.txt --openrouter  # with cheatsheet
  python sim_lab.py --subset hard2 --repeats 3 --openrouter    # 3 repeats per problem
  python sim_lab.py --data data/benchmark/control_hard20_seed17.jsonl   # local file (Ollama)
  python sim_lab.py --compare cs1.txt cs2.txt --subset hard2 --n 50 --openrouter
  python sim_lab.py --list-models                              # show available Ollama models
  python sim_lab.py --list-subsets                             # show official HF subsets
        """,
    )

    parser.add_argument("--subset", choices=list(HF_SUBSETS), default=None,
                        help="Official HF problem subset (downloads automatically)")
    parser.add_argument("--data", default=None,
                        help="Path to local JSONL benchmark file")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Ollama model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--cheatsheet", default=None,
                        help="Path to cheatsheet text file (complete prompt content)")
    parser.add_argument("--n", type=int, default=None,
                        help="Number of problems to evaluate (default: all)")
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS,
                        help=f"Repeats per problem (default: {DEFAULT_REPEATS}, official benchmark uses 3)")
    parser.add_argument("--answer-filter", choices=["all", "true", "false"], default="all",
                        help="Filter benchmark items by ground-truth label before shuffle/n")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="Sampling temperature (default: 0.0)")
    parser.add_argument("--num-predict", type=int, default=DEFAULT_NUM_PREDICT,
                        help=f"Max generated tokens per response (default: {DEFAULT_NUM_PREDICT})")
    parser.add_argument("--request-timeout", type=int, default=DEFAULT_REQUEST_TIMEOUT_S,
                        help=f"HTTP timeout (seconds) per request (default: {DEFAULT_REQUEST_TIMEOUT_S})")
    parser.add_argument("--output", default=None,
                        help="Save results JSON to this path")
    parser.add_argument("--quick", action="store_true",
                        help="Quick smoke test: 5 problems from hard2")
    parser.add_argument("--fast", action="store_true",
                        help="Fast mode: set n=20 (if unset), num_predict=512, timeout=120")
    parser.add_argument("--compare", nargs="+", metavar="CHEATSHEET",
                        help="Compare multiple cheatsheets")
    parser.add_argument("--errors", action="store_true",
                        help="Print detailed error analysis")
    parser.add_argument("--shuffle", action="store_true",
                        help="Shuffle problems before selecting")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress per-problem output")
    parser.add_argument("--list-models", action="store_true",
                        help="List available Ollama models and exit")
    parser.add_argument("--list-subsets", action="store_true",
                        help="List official HF problem subsets and exit")
    parser.add_argument("--openrouter", action="store_true",
                        help="Use OpenRouter API instead of Ollama (requires --api-key or OPENROUTER_API_KEY env)")
    parser.add_argument("--api-key", default=None,
                        help="OpenRouter API key (or set OPENROUTER_API_KEY env var)")
    parser.add_argument("--template", default=None,
                        help="Deprecated and ignored. Prompts now come entirely from the cheatsheet file.")
    parser.add_argument("--ollama-url", default=None,
                        help="Ollama API URL (default: http://localhost:11434)")

    args = parser.parse_args()

    if args.ollama_url:
        global OLLAMA_URL
        OLLAMA_URL = args.ollama_url

    # List subsets mode
    if args.list_subsets:
        print("Official HF problem subsets:")
        print("  normal  — 1000 problems (500 TRUE, 500 FALSE) programmatic selection")
        print("  hard    — 200 problems (74 TRUE, 126 FALSE) human+AI co-curated")
        print("  hard1   — 69 problems (24 TRUE, 45 FALSE) deduped hard subset")
        print("  hard2   — 200 problems (100 TRUE, 100 FALSE) human+AI co-curated")
        print(f"\nDataset: https://huggingface.co/datasets/{HF_DATASET}")
        sys.exit(0)

    # List models mode
    if args.list_models:
        if not check_ollama():
            print("ERROR: Ollama is not running. Start it with: ollama serve")
            sys.exit(1)
        models = list_models()
        print(f"Available Ollama models ({len(models)}):")
        for m in models:
            print(f"  • {m}")
        sys.exit(0)

    # Resolve backend
    global _backend, _api_key
    if args.openrouter:
        _backend = "openrouter"
        _api_key = args.api_key or OPENROUTER_API_KEY
        if not _api_key:
            print("ERROR: OpenRouter requires an API key.")
            print("  Pass --api-key <key> or set OPENROUTER_API_KEY env var.")
            sys.exit(1)
        # Default model for OpenRouter
        if args.model == DEFAULT_MODEL_OLLAMA:
            args.model = DEFAULT_MODEL
        print(f"Backend: OpenRouter (model: {args.model})")
    else:
        _backend = "ollama"
        # Default model for Ollama
        if args.model == DEFAULT_MODEL:
            args.model = DEFAULT_MODEL_OLLAMA
        # Check Ollama
        if not check_ollama():
            print("ERROR: Ollama is not running at", OLLAMA_URL)
            print("Start Ollama with: ollama serve")
            print("Or use --openrouter for cloud inference.")
            sys.exit(1)
        # Check model availability
        available = list_models()
        if available and args.model not in available:
            print(f"WARNING: Model '{args.model}' not found locally.")
            print(f"Available models: {', '.join(available)}")
            print(f"Pull it with: ollama pull {args.model}")
            resp = input("Continue anyway (Ollama will try to pull)? [y/N] ")
            if resp.lower() != "y":
                sys.exit(1)

    # Quick mode — uses hard2 by default
    if args.quick:
        args.n = args.n or 5
        if not args.subset and not args.data:
            args.subset = "hard2"

    # Fast mode
    if args.fast:
        args.n = args.n or 20
        args.num_predict = min(args.num_predict, 512)
        args.request_timeout = min(args.request_timeout, 120)

    # Default subset if nothing specified
    if not args.subset and not args.data:
        args.subset = "hard2"

    # Load data
    if args.data and not Path(args.data).exists():
        print(f"ERROR: Data file not found: {args.data}")
        sys.exit(1)
    if not args.cheatsheet:
        print("ERROR: A cheatsheet prompt is required.")
        print("  Pass --cheatsheet <path> so the simulator has a full prompt template.")
        sys.exit(1)
    if args.template:
        print("WARNING: --template is deprecated and ignored; using only the cheatsheet prompt.")

    problems = load_problems(
        path=args.data,
        subset=args.subset,
        n=args.n,
        shuffle=args.shuffle,
        answer_filter=args.answer_filter,
    )

    true_count = sum(1 for p in problems if p.answer)
    false_count = len(problems) - true_count
    source = args.subset or args.data
    total_runs = len(problems) * args.repeats
    print(f"\n{'═' * 60}")
    print(f"  SAIR Equational Theories — Stage 1 Simulation Lab")
    print(f"{'═' * 60}")
    print(f"  Backend:     {'OpenRouter' if _backend == 'openrouter' else 'Ollama'}")
    print(f"  Model:       {args.model}")
    print(f"  Source:      {source}")
    if args.answer_filter != "all":
        print(f"  Label set:   {args.answer_filter.upper()} only")
    print(f"  Problems:    {len(problems)} (TRUE: {true_count}, FALSE: {false_count})")
    print(f"  Repeats:     {args.repeats}")
    print(f"  Total runs:  {total_runs}")
    print(f"  Temperature: {args.temperature}")
    print(f"  Num predict: {args.num_predict}")
    print(f"  Timeout:     {args.request_timeout}s")
    if args.cheatsheet:
        print(f"  Cheatsheet:  {args.cheatsheet}")
    print(f"{'═' * 60}\n")

    # Comparison mode
    if args.compare:
        run_comparison(
            args.compare, problems, args.model,
            args.temperature, args.num_predict, args.request_timeout,
            args.repeats, not args.quiet,
        )
        return

    # Single evaluation
    cheatsheet = load_cheatsheet(args.cheatsheet)
    stats = run_evaluation(
        problems, cheatsheet, args.model,
        args.temperature, args.num_predict, args.request_timeout,
        args.repeats, not args.quiet,
    )
    print_report(stats, Path(args.cheatsheet).stem if args.cheatsheet else args.model)

    if args.errors:
        print_error_analysis(stats)

    # Auto-generate output path if not specified
    if args.output:
        output_path = args.output
    else:
        ts = time.strftime("%Y%m%d_%H%M%S")
        cs_label = Path(args.cheatsheet).stem if args.cheatsheet else "no_cheatsheet"
        sub_label = args.subset or Path(args.data).stem if args.data else "local"
        output_path = f"results/sim_{args.model.replace(':', '_').replace('/', '_')}_{sub_label}_{cs_label}_{ts}.json"

    save_results(stats, output_path, args.model, args.cheatsheet,
                 subset=args.subset, repeats=args.repeats)


if __name__ == "__main__":
    main()
