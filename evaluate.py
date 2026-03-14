"""
evaluate.py — Local evaluation for TAO Challenge Stage 1.

Test a cheatsheet by checking correctness against known implications.
Uses the raw implications CSV and equations.txt as ground truth.
"""

import csv
import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Optional


def load_equations(filepath: str = 'equations.txt') -> list:
    """Load equations. Line number (1-indexed) = equation index."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


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


def load_implication_matrix(filepath: str = 'export_raw_implications_14_3_2026.csv') -> dict:
    """Load the raw implications CSV into a dict: (eq1_idx, eq2_idx) -> bool."""
    print(f"Loading implications from {filepath}...")
    matrix = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 3:
                try:
                    eq1 = int(row[0])
                    eq2 = int(row[1])
                    val = int(row[2])
                    matrix[(eq1, eq2)] = val > 0
                except ValueError:
                    continue
    print(f"Loaded {len(matrix)} implications")
    return matrix


def load_training_data(filepath: str) -> list:
    """Load JSONL training data."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def sample_problems(matrix: dict, n: int = 100, seed: int = 42) -> list:
    """Sample balanced (50/50 TRUE/FALSE) problems from the implication matrix."""
    true_pairs = [(k, True) for k, v in matrix.items() if v]
    false_pairs = [(k, False) for k, v in matrix.items() if not v]

    rng = random.Random(seed)
    rng.shuffle(true_pairs)
    rng.shuffle(false_pairs)

    half = n // 2
    problems = true_pairs[:half] + false_pairs[:half]
    rng.shuffle(problems)
    return problems


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
    """Compute balanced log-loss (the competition metric)."""
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
    parser = argparse.ArgumentParser(description='Evaluate cheatsheet for TAO Challenge')
    parser.add_argument('--cheatsheet', default='cheatsheet.txt', help='Path to cheatsheet file')
    parser.add_argument('--equations', default='equations.txt', help='Path to equations file')
    parser.add_argument('--mode', choices=['heuristic', 'prompt'], default='heuristic',
                        help='Evaluation mode: heuristic (no LLM) or prompt (print prompts)')
    parser.add_argument('--data', default=None, help='Path to JSONL training data')
    parser.add_argument('--matrix', default='export_raw_implications_14_3_2026.csv',
                        help='Path to raw implications CSV')
    parser.add_argument('--n', type=int, default=100, help='Number of problems to evaluate')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    args = parser.parse_args()

    equations = load_equations(args.equations)
    cheatsheet = load_cheatsheet(args.cheatsheet)

    # Load problems
    if args.data:
        problems_data = load_training_data(args.data)
        problems = []
        for p in problems_data:
            eq1_idx = p.get('equation1_index', p.get('eq1'))
            eq2_idx = p.get('equation2_index', p.get('eq2'))
            label = p.get('implies', p.get('label'))
            if eq1_idx and eq2_idx and label is not None:
                problems.append(((eq1_idx, eq2_idx), bool(label)))
    else:
        if not os.path.exists(args.matrix):
            print(f"Matrix file {args.matrix} not found. Using random equations.")
            problems = []
        else:
            matrix = load_implication_matrix(args.matrix)
            problems = sample_problems(matrix, n=args.n, seed=args.seed)

    if not problems:
        print("No problems loaded.")
        return

    print(f"\nEvaluating on {len(problems)} problems...\n")

    predictions = []
    labels = []
    correct = 0

    for i, ((eq1_idx, eq2_idx), label) in enumerate(problems):
        if args.mode == 'heuristic':
            prob = evaluate_with_heuristic(eq1_idx, eq2_idx, equations)
            pred = prob > 0.5
            predictions.append(prob)
            labels.append(label)
            if pred == label:
                correct += 1
            if (i + 1) % 20 == 0 or i == len(problems) - 1:
                acc = correct / (i + 1)
                ll = compute_log_loss(predictions, labels)
                print(f"  [{i + 1}/{len(problems)}] Accuracy: {acc:.3f}, Log-loss: {ll:.4f}")
        elif args.mode == 'prompt':
            eq1_str = equations[eq1_idx - 1]
            eq2_str = equations[eq2_idx - 1]
            prompt = build_prompt(eq1_str, eq2_str, cheatsheet)
            print(f"--- Problem {i + 1} (Eq{eq1_idx} -> Eq{eq2_idx}, label={label}) ---")
            print(prompt[:500])
            print("...")
            print()

    if predictions:
        acc = correct / len(predictions)
        ll = compute_log_loss(predictions, labels)
        true_count = sum(1 for l in labels if l)
        false_count = len(labels) - true_count
        print(f"\n{'=' * 50}")
        print(f"Final Results ({len(predictions)} problems)")
        print(f"  TRUE/FALSE split: {true_count}/{false_count}")
        print(f"  Accuracy: {acc:.4f}")
        print(f"  Log-loss: {ll:.4f}")
        print(f"{'=' * 50}")


if __name__ == '__main__':
    main()
