#!/usr/bin/env python3
"""
SAIR Equational Theories — Stage 1 Simulation Lab

Local evaluation harness that mirrors the official competition pipeline.
Uses Ollama for inference so everything runs offline with no API keys.

Usage:
    # Quick smoke test (5 problems, default model)
    python sim_lab.py --quick

    # Full hard benchmark
    python sim_lab.py --data data/benchmark/hard.jsonl --model qwen2.5:3b

    # With cheatsheet
    python sim_lab.py --data data/benchmark/hard.jsonl --cheatsheet cheatsheets/v1.txt

    # Normal benchmark, subset
    python sim_lab.py --data data/benchmark/normal.jsonl --n 100 --model llama3.2:3b

    # Compare two cheatsheets
    python sim_lab.py --compare cheatsheets/v1.txt cheatsheets/v2.txt --data data/benchmark/hard.jsonl --n 50
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
DEFAULT_MODEL = "qwen2.5:3b"
PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompts" / "evaluation.jinja2"
CHEATSHEET_MAX_BYTES = 10_240  # 10 KB


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
    verdict: Optional[bool]          # None = unparsed
    raw_response: str
    elapsed_s: float
    parsed_ok: bool


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
    predicted_true: int = 0
    predicted_true_correct: int = 0
    elapsed_total: float = 0.0
    results: list = field(default_factory=list)

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
        return self.predicted_true_correct / self.predicted_true if self.predicted_true else 0.0

    @property
    def recall(self) -> float:
        return self.true_correct / self.true_total if self.true_total else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def avg_time(self) -> float:
        return self.elapsed_total / self.total if self.total else 0.0


# ---------------------------------------------------------------------------
# Problem loading
# ---------------------------------------------------------------------------

def load_problems(path: str, n: Optional[int] = None, shuffle: bool = False) -> list[Problem]:
    """Load problems from a JSONL file."""
    problems = []
    with open(path, "r", encoding="utf-8") as f:
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

    if shuffle:
        import random
        random.shuffle(problems)

    if n is not None:
        problems = problems[:n]

    return problems


# ---------------------------------------------------------------------------
# Prompt rendering
# ---------------------------------------------------------------------------

def load_template(path: Optional[str] = None) -> jinja2.Template:
    """Load the Jinja2 evaluation prompt template."""
    p = Path(path) if path else PROMPT_TEMPLATE_PATH
    with open(p, "r", encoding="utf-8") as f:
        return jinja2.Template(f.read())


def load_cheatsheet(path: Optional[str]) -> str:
    """Load and validate cheatsheet size."""
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


def render_prompt(template: jinja2.Template, problem: Problem, cheatsheet: str = "") -> str:
    """Render the evaluation prompt for a single problem."""
    return template.render(
        equation1=problem.equation1,
        equation2=problem.equation2,
        cheatsheet=cheatsheet if cheatsheet else None,
    )


# ---------------------------------------------------------------------------
# Verdict parsing
# ---------------------------------------------------------------------------

_VERDICT_RE = re.compile(r"VERDICT\s*:\s*(TRUE|FALSE)", re.IGNORECASE)


def parse_verdict(response: str) -> Optional[bool]:
    """Extract TRUE/FALSE verdict from model response."""
    m = _VERDICT_RE.search(response)
    if m:
        return m.group(1).upper() == "TRUE"
    return None


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
    timeout: int = 600,
) -> tuple[str, float]:
    """Send a prompt to Ollama and return (response_text, elapsed_seconds)."""
    t0 = time.time()
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 2048,
        },
    }
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=timeout,
    )
    r.raise_for_status()
    elapsed = time.time() - t0
    return r.json().get("response", ""), elapsed


# ---------------------------------------------------------------------------
# Evaluation engine
# ---------------------------------------------------------------------------

def evaluate_problem(
    problem: Problem,
    template: jinja2.Template,
    cheatsheet: str,
    model: str,
    temperature: float = 0.0,
) -> Result:
    """Evaluate a single problem."""
    prompt = render_prompt(template, problem, cheatsheet)
    try:
        response, elapsed = query_ollama(prompt, model, temperature)
    except Exception as e:
        return Result(
            problem=problem,
            verdict=None,
            raw_response=f"ERROR: {e}",
            elapsed_s=0.0,
            parsed_ok=False,
        )

    verdict = parse_verdict(response)
    return Result(
        problem=problem,
        verdict=verdict,
        raw_response=response,
        elapsed_s=elapsed,
        parsed_ok=verdict is not None,
    )


def run_evaluation(
    problems: list[Problem],
    template: jinja2.Template,
    cheatsheet: str,
    model: str,
    temperature: float = 0.0,
    verbose: bool = True,
) -> RunStats:
    """Run evaluation over a list of problems."""
    stats = RunStats()

    for i, problem in enumerate(problems):
        result = evaluate_problem(problem, template, cheatsheet, model, temperature)
        stats.total += 1
        stats.elapsed_total += result.elapsed_s
        stats.results.append(result)

        # Ground truth tracking
        if problem.answer:
            stats.true_total += 1
        else:
            stats.false_total += 1

        # Verdict tracking
        if result.verdict is None:
            stats.unparsed += 1
            mark = "?"
        else:
            if result.verdict:
                stats.predicted_true += 1
            is_correct = result.verdict == problem.answer
            if is_correct:
                stats.correct += 1
                if problem.answer:
                    stats.true_correct += 1
                    if result.verdict:
                        stats.predicted_true_correct += 1
                else:
                    stats.false_correct += 1
                mark = "✓"
            else:
                stats.incorrect += 1
                if result.verdict and not problem.answer:
                    pass  # false positive — predicted TRUE but answer FALSE
                elif not result.verdict and problem.answer:
                    pass  # false negative — predicted FALSE but answer TRUE
                mark = "✗"

        if verbose:
            gt = "T" if problem.answer else "F"
            pred = "T" if result.verdict is True else ("F" if result.verdict is False else "?")
            print(
                f"  [{i+1:4d}/{len(problems)}] {problem.id:15s}  "
                f"gt={gt} pred={pred} {mark}  "
                f"{result.elapsed_s:5.1f}s  "
                f"acc={stats.accuracy:.1%}  f1={stats.f1:.1%}"
            )

    return stats


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(stats: RunStats, label: str = ""):
    """Print a formatted evaluation report."""
    header = f"═══ Results{': ' + label if label else ''} ═══"
    print(f"\n{'═' * len(header)}")
    print(header)
    print(f"{'═' * len(header)}")
    print(f"  Total:            {stats.total}")
    print(f"  Correct:          {stats.correct}")
    print(f"  Incorrect:        {stats.incorrect}")
    print(f"  Unparsed:         {stats.unparsed}")
    print(f"  ─────────────────────────────────")
    print(f"  Accuracy:         {stats.accuracy:.1%}")
    print(f"  F1 (TRUE class):  {stats.f1:.1%}")
    print(f"  TRUE accuracy:    {stats.true_accuracy:.1%}  ({stats.true_correct}/{stats.true_total})")
    print(f"  FALSE accuracy:   {stats.false_accuracy:.1%}  ({stats.false_correct}/{stats.false_total})")
    print(f"  Precision (TRUE): {stats.precision:.1%}")
    print(f"  Recall (TRUE):    {stats.recall:.1%}")
    print(f"  ─────────────────────────────────")
    print(f"  Avg time/problem: {stats.avg_time:.1f}s")
    print(f"  Total time:       {stats.elapsed_total:.1f}s")
    print()


def save_results(stats: RunStats, output_path: str, model: str, cheatsheet_path: Optional[str]):
    """Save detailed results to JSON."""
    data = {
        "model": model,
        "cheatsheet": cheatsheet_path or "(none)",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total": stats.total,
            "correct": stats.correct,
            "incorrect": stats.incorrect,
            "unparsed": stats.unparsed,
            "accuracy": round(stats.accuracy, 4),
            "f1": round(stats.f1, 4),
            "true_accuracy": round(stats.true_accuracy, 4),
            "false_accuracy": round(stats.false_accuracy, 4),
            "precision": round(stats.precision, 4),
            "recall": round(stats.recall, 4),
            "avg_time_s": round(stats.avg_time, 2),
        },
        "results": [
            {
                "id": r.problem.id,
                "equation1": r.problem.equation1,
                "equation2": r.problem.equation2,
                "ground_truth": r.problem.answer,
                "predicted": r.verdict,
                "correct": r.verdict == r.problem.answer if r.verdict is not None else False,
                "parsed_ok": r.parsed_ok,
                "elapsed_s": round(r.elapsed_s, 2),
                "raw_response": r.raw_response,
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
    template: jinja2.Template,
    model: str,
    temperature: float = 0.0,
    verbose: bool = True,
):
    """Run evaluation with multiple cheatsheets and compare."""
    print(f"\n{'═' * 60}")
    print(f"  COMPARISON MODE — {len(cheatsheet_paths)} cheatsheets × {len(problems)} problems")
    print(f"  Model: {model}")
    print(f"{'═' * 60}\n")

    all_stats = []
    for cs_path in cheatsheet_paths:
        label = Path(cs_path).stem
        print(f"\n▶ Evaluating: {cs_path}")
        cheatsheet = load_cheatsheet(cs_path)
        stats = run_evaluation(problems, template, cheatsheet, model, temperature, verbose)
        print_report(stats, label)
        all_stats.append((label, stats))

    # Comparison table
    print(f"\n{'═' * 70}")
    print(f"  COMPARISON SUMMARY")
    print(f"{'═' * 70}")
    print(f"  {'Cheatsheet':<25s} {'Acc':>7s} {'F1':>7s} {'T_acc':>7s} {'F_acc':>7s} {'Unp':>5s}")
    print(f"  {'─' * 25} {'─' * 7} {'─' * 7} {'─' * 7} {'─' * 7} {'─' * 5}")
    for label, s in all_stats:
        print(
            f"  {label:<25s} "
            f"{s.accuracy:>6.1%} "
            f"{s.f1:>6.1%} "
            f"{s.true_accuracy:>6.1%} "
            f"{s.false_accuracy:>6.1%} "
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
  python sim_lab.py --quick                              # 5-problem smoke test
  python sim_lab.py --data data/benchmark/hard.jsonl     # full hard benchmark
  python sim_lab.py --cheatsheet cheatsheets/v1.txt      # test a cheatsheet
  python sim_lab.py --compare cs1.txt cs2.txt --n 50     # compare cheatsheets
  python sim_lab.py --list-models                        # show available Ollama models
        """,
    )

    parser.add_argument("--data", default="data/benchmark/hard.jsonl",
                        help="Path to JSONL benchmark file")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Ollama model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--cheatsheet", default=None,
                        help="Path to cheatsheet text file")
    parser.add_argument("--n", type=int, default=None,
                        help="Number of problems to evaluate (default: all)")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="Sampling temperature (default: 0.0)")
    parser.add_argument("--output", default=None,
                        help="Save results JSON to this path")
    parser.add_argument("--quick", action="store_true",
                        help="Quick smoke test: 5 problems")
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
    parser.add_argument("--template", default=None,
                        help="Custom prompt template path")
    parser.add_argument("--ollama-url", default=None,
                        help="Ollama API URL (default: http://localhost:11434)")

    args = parser.parse_args()

    if args.ollama_url:
        global OLLAMA_URL
        OLLAMA_URL = args.ollama_url

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

    # Check Ollama
    if not check_ollama():
        print("ERROR: Ollama is not running at", OLLAMA_URL)
        print("Start Ollama with: ollama serve")
        print("Or set OLLAMA_URL env var to point to your Ollama instance.")
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

    # Quick mode
    if args.quick:
        args.n = args.n or 5

    # Load data
    if not Path(args.data).exists():
        print(f"ERROR: Data file not found: {args.data}")
        sys.exit(1)

    problems = load_problems(args.data, args.n, args.shuffle)
    template = load_template(args.template)

    true_count = sum(1 for p in problems if p.answer)
    false_count = len(problems) - true_count
    print(f"\n{'═' * 60}")
    print(f"  SAIR Equational Theories — Stage 1 Simulation Lab")
    print(f"{'═' * 60}")
    print(f"  Model:      {args.model}")
    print(f"  Data:       {args.data}")
    print(f"  Problems:   {len(problems)} (TRUE: {true_count}, FALSE: {false_count})")
    print(f"  Temperature: {args.temperature}")
    if args.cheatsheet:
        print(f"  Cheatsheet: {args.cheatsheet}")
    print(f"{'═' * 60}\n")

    # Comparison mode
    if args.compare:
        run_comparison(
            args.compare, problems, template, args.model,
            args.temperature, not args.quiet,
        )
        return

    # Single evaluation
    cheatsheet = load_cheatsheet(args.cheatsheet)
    stats = run_evaluation(
        problems, template, cheatsheet, args.model,
        args.temperature, not args.quiet,
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
        output_path = f"results/sim_{args.model.replace(':', '_')}_{cs_label}_{ts}.json"

    save_results(stats, output_path, args.model, args.cheatsheet)


if __name__ == "__main__":
    main()
