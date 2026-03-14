"""
run_eval.py — LLM-based evaluation harness for cheatsheet quality.

Tests a cheatsheet by prompting an LLM on equational implication problems
and scoring against ground truth. Supports:
  - Cheatsheet + format examples (Honda et al. eq. 2)
  - Self-consistency decoding
  - Cost tracking & log-loss scoring
"""

import json
import math
import random
import re
import argparse
import logging
from pathlib import Path
from typing import Optional

from config import ExperimentConfig, DEFAULT_CONFIG, RESULTS_DIR, DATA_DIR
from llm_client import LLMClient

logger = logging.getLogger(__name__)


# ── Evaluation prompts ────────────────────────────────────────────

EVAL_SYSTEM_PROMPT = """\
You are an expert in abstract algebra, specifically equational theories over magmas.
A magma (M, ◇) is a set M with a binary operation ◇ (no axioms assumed).
You must determine whether one equational law implies another over all magmas."""


def build_eval_prompt(
    eq1: str,
    eq2: str,
    cheatsheet: str,
    format_examples: list = None,
) -> str:
    """Build the evaluation prompt with cheatsheet and optional format examples.

    Implements Honda et al. equation (2):
      y* = argmax P(y | S, D̂₂, x_test)
    where S = cheatsheet, D̂₂ = format examples, x_test = the problem.
    """
    parts = []

    # Cheatsheet
    parts.append("REFERENCE CHEAT SHEET:")
    parts.append("---")
    parts.append(cheatsheet)
    parts.append("---")
    parts.append("")

    # Format examples (D̂₂)
    if format_examples:
        parts.append("WORKED EXAMPLES:")
        for i, ex in enumerate(format_examples):
            parts.append(f"\nExample {i+1}:")
            parts.append(f"Equation 1: {ex['eq1']}")
            parts.append(f"Equation 2: {ex['eq2']}")
            if ex.get("rationale"):
                parts.append(f"Reasoning: {ex['rationale']}")
            parts.append(f"VERDICT: {ex['label']}")
        parts.append("")

    # Test problem
    parts.append("NOW SOLVE THIS PROBLEM:")
    parts.append(f"Equation 1: {eq1}")
    parts.append(f"Equation 2: {eq2}")
    parts.append("")
    parts.append("Think step by step. Then give your final answer as VERDICT: TRUE or VERDICT: FALSE")

    return "\n".join(parts)


def parse_verdict(text: str) -> Optional[bool]:
    """Extract TRUE/FALSE verdict from LLM response."""
    # Look for explicit VERDICT
    match = re.search(r'VERDICT:\s*(TRUE|FALSE)', text, re.IGNORECASE)
    if match:
        return match.group(1).upper() == "TRUE"
    # Fallback: last occurrence of TRUE/FALSE
    matches = re.findall(r'\b(TRUE|FALSE)\b', text, re.IGNORECASE)
    if matches:
        return matches[-1].upper() == "TRUE"
    return None


def verdict_to_prob(verdict: Optional[bool], confidence: float = 0.95) -> float:
    """Convert boolean verdict to probability."""
    if verdict is None:
        return 0.5
    return confidence if verdict else (1.0 - confidence)


def compute_log_loss(predictions: list, labels: list) -> float:
    """Compute balanced binary log-loss."""
    eps = 1e-7
    total = 0.0
    n = len(predictions)
    if n == 0:
        return float('inf')
    for pred, label in zip(predictions, labels):
        p = max(eps, min(1.0 - eps, pred))
        if label:
            total -= math.log(p)
        else:
            total -= math.log(1.0 - p)
    return total / n


def load_equations(filepath: str = "equations.txt") -> list:
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def load_eval_problems(filepath: str, equations: list) -> list:
    """Load evaluation problems from JSONL."""
    problems = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            eq1_idx = int(rec.get('equation1_index', rec.get('eq1', 0)))
            eq2_idx = int(rec.get('equation2_index', rec.get('eq2', 0)))
            label = rec.get('implies', rec.get('label'))
            if eq1_idx and eq2_idx and label is not None:
                problems.append({
                    "eq1": equations[eq1_idx - 1],
                    "eq2": equations[eq2_idx - 1],
                    "eq1_idx": eq1_idx,
                    "eq2_idx": eq2_idx,
                    "label": bool(label),
                })
    return problems


def select_format_examples(
    problems: list,
    n: int = 2,
    seed: int = 42,
) -> list:
    """Select balanced format examples (D̂₂ in the paper)."""
    true_ex = [p for p in problems if p["label"]]
    false_ex = [p for p in problems if not p["label"]]
    rng = random.Random(seed)

    examples = []
    if true_ex:
        ex = rng.choice(true_ex)
        examples.append({"eq1": ex["eq1"], "eq2": ex["eq2"], "label": "TRUE"})
    if false_ex:
        ex = rng.choice(false_ex)
        examples.append({"eq1": ex["eq1"], "eq2": ex["eq2"], "label": "FALSE"})

    return examples[:n]


def evaluate_single(
    eq1: str,
    eq2: str,
    cheatsheet: str,
    client: LLMClient,
    format_examples: list = None,
    use_self_consistency: bool = False,
    sc_samples: int = 5,
) -> tuple:
    """Evaluate a single problem. Returns (predicted_prob, verdict_bool, response_text)."""
    prompt = build_eval_prompt(eq1, eq2, cheatsheet, format_examples)

    if not use_self_consistency:
        resp = client.call(prompt, system=EVAL_SYSTEM_PROMPT)
        verdict = parse_verdict(resp.text)
        prob = verdict_to_prob(verdict)
        return prob, verdict, resp.text

    # Self-consistency: sample multiple times, take majority
    verdicts = []
    for _ in range(sc_samples):
        resp = client.call(prompt, system=EVAL_SYSTEM_PROMPT, temperature=0.7)
        v = parse_verdict(resp.text)
        if v is not None:
            verdicts.append(v)

    if not verdicts:
        return 0.5, None, "(no valid verdicts)"

    true_count = sum(verdicts)
    prob = true_count / len(verdicts)
    verdict = prob > 0.5
    return prob, verdict, f"SC({len(verdicts)}): {true_count} TRUE, {len(verdicts)-true_count} FALSE"


def run_evaluation(
    cheatsheet_path: str,
    eval_data_path: str,
    config: ExperimentConfig,
) -> dict:
    """Run full evaluation and return results dict."""
    # Load
    equations = load_equations()
    with open(cheatsheet_path, 'r', encoding='utf-8') as f:
        cheatsheet = f.read()

    cs_bytes = len(cheatsheet.encode('utf-8'))
    logger.info(f"Cheatsheet: {cs_bytes} bytes ({cs_bytes*100/10240:.1f}% of limit)")

    problems = load_eval_problems(eval_data_path, equations)
    logger.info(f"Loaded {len(problems)} eval problems")

    if config.n_eval > 0 and len(problems) > config.n_eval:
        rng = random.Random(config.seed)
        problems = rng.sample(problems, config.n_eval)
        logger.info(f"Sampled {len(problems)} for evaluation")

    # Format examples
    format_ex = select_format_examples(problems, n=config.n_format_examples, seed=config.seed)
    # Remove format examples from eval set
    fmt_pairs = {(e["eq1"], e["eq2"]) for e in format_ex}
    eval_problems = [p for p in problems if (p["eq1"], p["eq2"]) not in fmt_pairs]

    # Evaluate
    client = LLMClient(config.eval_model)
    predictions = []
    labels = []
    correct = 0
    results_detail = []

    for i, prob in enumerate(eval_problems):
        pred_prob, verdict, raw = evaluate_single(
            prob["eq1"], prob["eq2"], cheatsheet, client,
            format_examples=format_ex,
            use_self_consistency=config.use_self_consistency,
            sc_samples=config.sc_samples,
        )
        predictions.append(pred_prob)
        labels.append(prob["label"])
        pred_bool = pred_prob > 0.5
        if pred_bool == prob["label"]:
            correct += 1

        results_detail.append({
            "eq1_idx": prob["eq1_idx"],
            "eq2_idx": prob["eq2_idx"],
            "label": prob["label"],
            "predicted_prob": pred_prob,
            "predicted": pred_bool,
            "correct": pred_bool == prob["label"],
        })

        if (i + 1) % 10 == 0 or i == len(eval_problems) - 1:
            acc = correct / (i + 1)
            ll = compute_log_loss(predictions, labels)
            logger.info(
                f"  [{i+1}/{len(eval_problems)}] Acc={acc:.3f} LogLoss={ll:.4f} Cost=${client.total_cost:.4f}"
            )

    # Final metrics
    acc = correct / len(eval_problems) if eval_problems else 0
    ll = compute_log_loss(predictions, labels)
    true_labels = [l for l in labels if l]
    false_labels = [l for l in labels if not l]
    true_correct = sum(1 for r in results_detail if r["label"] and r["correct"])
    false_correct = sum(1 for r in results_detail if not r["label"] and r["correct"])

    results = {
        "accuracy": acc,
        "log_loss": ll,
        "n_eval": len(eval_problems),
        "n_correct": correct,
        "true_accuracy": true_correct / len(true_labels) if true_labels else 0,
        "false_accuracy": false_correct / len(false_labels) if false_labels else 0,
        "total_cost": client.total_cost,
        "total_calls": client.total_calls,
        "config": config.__dict__,
        "cheatsheet_bytes": cs_bytes,
        "details": results_detail,
    }

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"eval_{config.name}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"Results saved to {out_path}")
    logger.info(f"FINAL — Accuracy: {acc:.3f}, LogLoss: {ll:.4f}, Cost: ${client.total_cost:.4f}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate a cheatsheet with LLM")
    parser.add_argument("--cheatsheet", required=True, help="Path to cheatsheet file")
    parser.add_argument("--data", required=True, help="JSONL eval data file")
    parser.add_argument("--eval-model", default="gpt-4o-mini", help="Model for evaluation")
    parser.add_argument("--n-eval", type=int, default=100, help="Number of problems")
    parser.add_argument("--n-format", type=int, default=2, help="Number of format examples")
    parser.add_argument("--self-consistency", action="store_true", help="Use self-consistency")
    parser.add_argument("--sc-samples", type=int, default=5, help="Self-consistency samples")
    parser.add_argument("--name", default="default", help="Experiment name")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    config = ExperimentConfig(
        name=args.name,
        eval_model=args.eval_model,
        n_eval=args.n_eval,
        n_format_examples=args.n_format,
        use_self_consistency=args.self_consistency,
        sc_samples=args.sc_samples,
        seed=args.seed,
    )

    run_evaluation(
        cheatsheet_path=args.cheatsheet,
        eval_data_path=args.data,
        config=config,
    )


if __name__ == "__main__":
    main()
