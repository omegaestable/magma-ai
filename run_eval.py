"""LLM-based cheatsheet evaluation harness.

Status:
- Submission-support when the model sees only the cheatsheet and optional
    format examples drawn from a separate labeled file.
- Invalid if evaluation labels are embedded back into the prompt context.

Metrics:
- PRIMARY: Accuracy (% correct TRUE/FALSE classification). This is what the
    Stage 1 competition evaluates.
- SECONDARY: Log-loss (calibration diagnostic only, not submission-scored).
"""

import json
import math
import random
import re
import argparse
import logging
from pathlib import Path
from typing import Optional

from analyze_equations import load_equations
from benchmark_utils import (
    annotate_records,
    benchmark_metadata,
    build_dual_swap_records,
    summarize_bucket_accuracy,
    summarize_bucket_counts,
    summarize_dual_swap_consistency,
    summarize_landmark_accuracy,
    summarize_trivial_share,
    summarize_trivial_free_accuracy,
)
from config import CHEATSHEET_FILE, ExperimentConfig, RESULTS_DIR
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


def load_cheatsheet_text(filepath: str) -> tuple[str, int]:
    """Load cheatsheet text and report its true on-disk byte size."""
    raw = Path(filepath).read_bytes()
    return raw.decode('utf-8'), len(raw)


def load_eval_problems(filepath: str, equations: list) -> list:
    """Load evaluation problems from JSONL."""
    problems = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            eq1_idx = int(rec.get('equation1_index', rec.get('eq1', rec.get('eq1_idx', 0))))
            eq2_idx = int(rec.get('equation2_index', rec.get('eq2', rec.get('eq2_idx', 0))))
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
    n: int = 0,
    seed: int = 42,
) -> list:
    """Select balanced format examples (D̂₂ in the paper)."""
    if n <= 0 or not problems:
        return []

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
    format_data_path: Optional[str] = None,
) -> dict:
    """Run full evaluation and return results dict."""
    # Load
    equations = load_equations()
    cheatsheet, cs_bytes = load_cheatsheet_text(cheatsheet_path)
    logger.info(f"Cheatsheet: {cs_bytes} bytes ({cs_bytes*100/10240:.1f}% of limit)")

    problems = load_eval_problems(eval_data_path, equations)
    logger.info(f"Loaded {len(problems)} eval problems")

    if config.n_eval > 0 and len(problems) > config.n_eval:
        rng = random.Random(config.seed)
        problems = rng.sample(problems, config.n_eval)
        logger.info(f"Sampled {len(problems)} for evaluation")

    format_pool = []
    format_source = 'none'
    if config.n_format_examples > 0 and format_data_path:
        format_pool = load_eval_problems(format_data_path, equations)
        format_source = 'separate_jsonl'
        logger.info(f"Loaded {len(format_pool)} format-example problems from separate data")
    format_ex = select_format_examples(format_pool, n=config.n_format_examples, seed=config.seed)
    eval_problems = problems
    dual_problems = build_dual_swap_records(eval_problems, equations) if config.dual_swap_check else []
    if dual_problems:
        logger.info(f"Prepared {len(dual_problems)} dual-swapped problems for consistency checking")

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
            "eq1": prob["eq1"],
            "eq2": prob["eq2"],
            "label": prob["label"],
            "predicted_prob": pred_prob,
            "predicted": pred_bool,
            "correct": pred_bool == prob["label"],
        })

        if (i + 1) % 10 == 0 or i == len(eval_problems) - 1:
            acc = correct / (i + 1)
            logger.info(
                f"  [{i+1}/{len(eval_problems)}] Accuracy={acc:.3f} Cost=${client.total_cost:.4f}"
            )

    dual_results_detail = []
    if dual_problems:
        logger.info("Running dual-swap consistency evaluation...")
        for i, prob in enumerate(dual_problems):
            pred_prob, verdict, raw = evaluate_single(
                prob["eq1"], prob["eq2"], cheatsheet, client,
                format_examples=format_ex,
                use_self_consistency=config.use_self_consistency,
                sc_samples=config.sc_samples,
            )
            dual_results_detail.append({
                "source_eq1_idx": prob["source_eq1_idx"],
                "source_eq2_idx": prob["source_eq2_idx"],
                "eq1_idx": prob["eq1_idx"],
                "eq2_idx": prob["eq2_idx"],
                "eq1": prob["eq1"],
                "eq2": prob["eq2"],
                "label": prob["label"],
                "predicted_prob": pred_prob,
                "predicted": pred_prob > 0.5,
                "correct": (pred_prob > 0.5) == prob["label"],
            })
            if (i + 1) % 10 == 0 or i == len(dual_problems) - 1:
                logger.info(
                    f"  [dual {i+1}/{len(dual_problems)}] Cost=${client.total_cost:.4f}"
                )

    # Final metrics
    acc = correct / len(eval_problems) if eval_problems else 0
    ll = compute_log_loss(predictions, labels)
    true_labels = [l for l in labels if l]
    false_labels = [l for l in labels if not l]
    true_correct = sum(1 for r in results_detail if r["label"] and r["correct"])
    false_correct = sum(1 for r in results_detail if not r["label"] and r["correct"])
    annotated_details = annotate_records(results_detail, equations)
    bucket_summary = summarize_bucket_accuracy(annotated_details)
    trivial_summary = summarize_trivial_share(annotated_details)
    trivial_free_summary = summarize_trivial_free_accuracy(annotated_details, equations)
    landmark_summary = summarize_landmark_accuracy(annotated_details)
    dual_swap_summary = summarize_dual_swap_consistency(annotated_details, dual_results_detail) if dual_results_detail else None
    metadata = benchmark_metadata(
        artifact_kind='cheatsheet_only',
        label_source='jsonl',
        inference_mode='llm_prompt',
        uses_matrix_at_inference=False,
        format_examples_source=format_source,
        uses_eval_labels_in_prompt=False,
        benchmark_name='jsonl_eval',
    )

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
        "benchmark_metadata": metadata,
        "trivial_count": trivial_summary["trivial_count"],
        "trivial_share": trivial_summary["trivial_share"],
        "nontrivial_count": trivial_summary["nontrivial_count"],
        "nontrivial_share": trivial_summary["nontrivial_share"],
        "trivial_free_accuracy": trivial_free_summary,
        "landmark_accuracy": landmark_summary,
        "dual_swap": dual_swap_summary,
        "bucket_counts": summarize_bucket_counts(annotated_details),
        "bucket_accuracy": bucket_summary,
        "details": annotated_details,
    }
    if dual_results_detail:
        results["dual_swap_details"] = dual_results_detail

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"eval_{config.name}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"Results saved to {out_path}")
    logger.info(f"FINAL — Accuracy: {acc:.3f} ({correct}/{len(eval_problems)})  Cost: ${client.total_cost:.4f}")
    logger.info(f"  Log-loss (calibration diagnostic): {ll:.4f}")
    logger.info(
        f"  Trivial share: {trivial_summary['trivial_share']:.3f} "
        f"({trivial_summary['trivial_count']}/{trivial_summary['total']})"
    )
    logger.info(f"  Benchmark validity: {metadata['submission_valid']} ({metadata['validity_reason']})")
    if trivial_free_summary["accuracy"] is not None:
        logger.info(
            "  Trivial-free accuracy: "
            f"{trivial_free_summary['accuracy']:.3f} on {trivial_free_summary['count']} pairs "
            f"(excluded {trivial_free_summary['excluded_count']})"
        )
    landmark_overall = landmark_summary["overall"]
    if landmark_overall["accuracy"] is not None:
        logger.info(
            f"  Landmark accuracy: {landmark_overall['accuracy']:.3f} on {landmark_overall['count']} pairs"
        )
    if dual_swap_summary and dual_swap_summary["prediction_consistency"] is not None:
        logger.info(
            "  Dual-swap consistency: "
            f"{dual_swap_summary['prediction_consistency']:.3f} over {dual_swap_summary['paired_count']} paired evaluations"
        )
    for bucket, values in bucket_summary.items():
        logger.info(
            f"  Bucket {bucket}: n={values['count']} share={values['share']:.3f} "
            f"acc={values['accuracy']:.3f}"
        )

    return results


def dry_run(cheatsheet_path: str, eval_data_path: str, config: ExperimentConfig):
    """Validate the evaluation pipeline without making any API calls."""
    from config import check_environment

    logger.info("=== DRY RUN: validating pipeline (no API calls) ===")

    # Check cheatsheet
    cheatsheet, cs_bytes = load_cheatsheet_text(cheatsheet_path)
    logger.info(f"Cheatsheet: {cs_bytes} bytes ({cs_bytes*100/10240:.1f}% of 10KB limit)")
    if cs_bytes > 10240:
        logger.warning("Cheatsheet EXCEEDS 10KB limit!")

    # Check eval data
    equations = load_equations()
    problems = load_eval_problems(eval_data_path, equations)
    logger.info(f"Eval data: {len(problems)} problems loaded from {eval_data_path}")
    if problems:
        n_true = sum(1 for p in problems if p['label'])
        n_false = len(problems) - n_true
        logger.info(f"  Label balance: {n_true} TRUE ({n_true*100/len(problems):.1f}%), {n_false} FALSE")
        annotated = annotate_records(problems, equations)
        trivial_summary = summarize_trivial_share(annotated)
        logger.info(
            f"  Trivial share: {trivial_summary['trivial_share']:.3f} "
            f"({trivial_summary['trivial_count']}/{trivial_summary['total']})"
        )
        for bucket, count in summarize_bucket_counts(annotated).items():
            logger.info(f"  Bucket {bucket}: n={count}")

    # Check environment
    env_status = check_environment(config.eval_model)
    for line in env_status:
        logger.info(f"  {line}")

    # Build a sample prompt to show it works
    if problems:
        sample = problems[0]
        prompt = build_eval_prompt(sample['eq1'], sample['eq2'], cheatsheet)
        logger.info(f"Sample prompt length: {len(prompt)} chars")

    logger.info("=== DRY RUN complete. Pipeline is ready for live evaluation. ===")


def main():
    parser = argparse.ArgumentParser(description="Evaluate a cheatsheet with LLM")
    parser.add_argument("--cheatsheet", default=str(CHEATSHEET_FILE), help="Path to cheatsheet file")
    parser.add_argument("--data", required=True, help="JSONL eval data file")
    parser.add_argument("--format-data", default=None,
                        help="Optional separate JSONL file used only for format examples")
    parser.add_argument("--eval-model", default="ollama-qwen2.5-3b", help="Local model for evaluation")
    parser.add_argument("--n-eval", type=int, default=100, help="Number of problems")
    parser.add_argument("--n-format", type=int, default=0,
                        help="Number of format examples (safe default: 0 unless using separate format data)")
    parser.add_argument("--self-consistency", action="store_true", help="Use self-consistency")
    parser.add_argument("--sc-samples", type=int, default=5, help="Self-consistency samples")
    parser.add_argument("--dual-swap-check", action="store_true",
                        help="Also evaluate dual-swapped pairs and report prediction consistency")
    parser.add_argument("--name", default="default", help="Experiment name")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate pipeline (cheatsheet, data, env) without making API calls")
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
        dual_swap_check=args.dual_swap_check,
        seed=args.seed,
    )

    if args.dry_run:
        dry_run(
            cheatsheet_path=args.cheatsheet,
            eval_data_path=args.data,
            config=config,
        )
    else:
        run_evaluation(
            cheatsheet_path=args.cheatsheet,
            eval_data_path=args.data,
            config=config,
            format_data_path=args.format_data,
        )


if __name__ == "__main__":
    main()
