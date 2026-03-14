"""Local benchmark harness and prompt exporter.

Status:
- `prompt` mode is submission-support only when the downstream model sees only the cheatsheet.
- `heuristic` mode is research-only; it does not evaluate the submission artifact.
- Matrix-sampled labels are acceptable as offline supervision, but never as inference-time lookup.
"""

import math
import os
from benchmark_utils import (
    annotate_records,
    benchmark_metadata,
    load_equations,
    load_labeled_pairs_from_jsonl,
    sample_balanced_pairs_from_matrix,
    summarize_bucket_accuracy,
    summarize_bucket_counts,
)

def load_cheatsheet(filepath: str = 'cheatsheet.txt') -> str:
    """Load cheatsheet and check size."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    size = len(text.encode('utf-8'))
    if size > 10240:
        print(f"WARNING: Cheatsheet is {size} bytes (limit: 10240)")
    else:
        print(f"Cheatsheet size: {size}/10240 bytes ({size * 100 / 10240:.1f}%)")
    return text

def build_prompt(eq1_str: str, eq2_str: str, cheatsheet: str) -> str:
    """Build the evaluation prompt matching the competition template."""
    return f"""You are given two equational laws over magmas (a set M equipped with a binary operation ◇).
Your task is to determine whether Equation 1 implies Equation 2 over all magmas.

Equation 1: {eq1_str}
Equation 2: {eq2_str}

Here is a reference cheatsheet to help you:
---
{cheatsheet}
---

Does Equation 1 imply Equation 2?
Respond with a single word: TRUE or FALSE.
Then optionally explain your reasoning."""


def compute_log_loss(predictions: list, labels: list) -> float:
    """Compute log-loss as an optional local calibration metric."""
    eps = 1e-7
    total_loss = 0.0
    n = len(predictions)
    if n == 0:
        return float('inf')
    for pred, label in zip(predictions, labels):
        p = max(eps, min(1.0 - eps, pred))
        if label:
            total_loss -= math.log(p)
        else:
            total_loss -= math.log(1.0 - p)
    return total_loss / n


def evaluate_with_heuristic(eq1_idx: int, eq2_idx: int, equations: list) -> float:
    """Simple heuristic predictor for local testing (no LLM needed).
    Returns predicted probability that eq1 implies eq2."""
    from analyze_equations import (
        parse_equation, get_vars, count_ops, get_depth,
        is_specialization, can_prove_by_rewriting, find_counterexample,
    )

    eq1_str = equations[eq1_idx - 1]
    eq2_str = equations[eq2_idx - 1]

    # Trivial cases
    if eq1_str == eq2_str:
        return 1.0
    if eq1_idx == 1:  # x=x implies nothing
        return 0.0
    if eq2_idx == 1:  # everything implies x=x
        return 1.0
    if eq1_idx == 2 or eq2_idx == 2:  # x=y
        if eq1_idx == 2:
            return 1.0  # x=y implies everything

    try:
        eq1 = parse_equation(eq1_str)
        eq2 = parse_equation(eq2_str)
    except Exception:
        return 0.5

    # Direct specialization check
    if is_specialization(eq1, eq2):
        return 0.95

    # BFS rewriting check
    try:
        if can_prove_by_rewriting(eq1, eq2, max_steps=200):
            return 0.9
    except Exception:
        pass

    # Counterexample search
    try:
        cex = find_counterexample(eq1, eq2, magma_sizes=(2, 3))
        if cex is not None:
            return 0.05
    except Exception:
        pass

    # Structural heuristics
    vars1 = get_vars(eq1[0]) | get_vars(eq1[1])
    vars2 = get_vars(eq2[0]) | get_vars(eq2[1])
    ops1 = count_ops(eq1[0]) + count_ops(eq1[1])
    ops2 = count_ops(eq2[0]) + count_ops(eq2[1])

    # If eq2 uses more distinct variables, less likely
    if len(vars2 - vars1) > 0:
        return 0.15

    # More operations in eq1 -> more constraining -> more likely to imply simpler
    if ops1 > ops2:
        return 0.35
    elif ops1 < ops2:
        return 0.2

    return 0.25


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Evaluate or export a local Stage 1 benchmark')
    parser.add_argument('--cheatsheet', default='cheatsheet.txt', help='Path to cheatsheet file')
    parser.add_argument('--equations', default='equations.txt', help='Path to equations file')
    parser.add_argument('--mode', choices=['heuristic', 'prompt'], default='heuristic',
                        help='Evaluation mode: heuristic research benchmark or prompt export')
    parser.add_argument('--data', default=None, help='Path to JSONL benchmark data')
    parser.add_argument('--matrix', default='export_raw_implications_14_3_2026.csv',
                        help='Path to raw implications CSV for balanced local sampling')
    parser.add_argument('--n', type=int, default=100, help='Number of problems to evaluate')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    args = parser.parse_args()

    equations = load_equations(args.equations)
    cheatsheet = load_cheatsheet(args.cheatsheet)

    label_source = 'jsonl' if args.data else 'matrix_sample'
    if args.data:
        records = load_labeled_pairs_from_jsonl(args.data)
    else:
        if not os.path.exists(args.matrix):
            print(f"Matrix file {args.matrix} not found.")
            records = []
        else:
            print(f"Sampling balanced benchmark pairs from {args.matrix}...")
            records = sample_balanced_pairs_from_matrix(args.matrix, n=args.n, seed=args.seed)

    if not records:
        print("No problems loaded.")
        return

    records = annotate_records(records, equations)
    metadata = benchmark_metadata(
        artifact_kind='cheatsheet_only' if args.mode == 'prompt' else 'heuristic_proxy',
        label_source=label_source,
        inference_mode='prompt_export' if args.mode == 'prompt' else 'heuristic_proxy',
        uses_matrix_at_inference=False,
    )

    print('\nBenchmark metadata:')
    for key, value in metadata.items():
        print(f'  {key}: {value}')
    print('Bucket counts:')
    for bucket, count in summarize_bucket_counts(records).items():
        print(f'  {bucket}: {count}')

    print(f"\nEvaluating on {len(records)} problems...\n")

    predictions = []
    labels = []
    correct = 0
    scored_records = []

    for i, record in enumerate(records):
        eq1_idx = record['eq1_idx']
        eq2_idx = record['eq2_idx']
        label = record['label']
        if args.mode == 'heuristic':
            prob = evaluate_with_heuristic(eq1_idx, eq2_idx, equations)
            pred = prob > 0.5
            predictions.append(prob)
            labels.append(label)
            if pred == label:
                correct += 1
            scored = dict(record)
            scored['predicted_prob'] = prob
            scored['predicted'] = pred
            scored['correct'] = pred == label
            scored_records.append(scored)
            if (i + 1) % 20 == 0 or i == len(records) - 1:
                acc = correct / (i + 1)
                ll = compute_log_loss(predictions, labels)
                print(f"  [{i + 1}/{len(records)}] Accuracy: {acc:.3f}, Log-loss: {ll:.4f}")
        elif args.mode == 'prompt':
            prompt = build_prompt(record['eq1'], record['eq2'], cheatsheet)
            print(f"--- Problem {i + 1} (Eq{eq1_idx} -> Eq{eq2_idx}, label={label}) ---")
            print(prompt[:500])
            print("...")
            print()

    if predictions:
        acc = correct / len(predictions)
        ll = compute_log_loss(predictions, labels)
        true_count = sum(1 for l in labels if l)
        false_count = len(labels) - true_count
        trivial_count = sum(1 for record in scored_records if record['bucket'] == 'trivial')
        bucket_summary = summarize_bucket_accuracy(scored_records)
        print(f"\n{'=' * 50}")
        print(f"Final Results ({len(predictions)} problems)")
        print(f"  TRUE/FALSE split: {true_count}/{false_count}")
        print(f"  Trivial/nontrivial: {trivial_count}/{len(predictions) - trivial_count}")
        print(f"  Accuracy: {acc:.4f}  <- primary Stage 1 metric")
        print(f"  Log-loss: {ll:.4f}  <- optional local calibration metric")
        print("  Bucket accuracy:")
        for bucket, values in bucket_summary.items():
            print(f"    {bucket}: {values['count']} examples, accuracy={values['accuracy']:.3f}")
        print(f"{'=' * 50}")


if __name__ == '__main__':
    main()
