#!/usr/bin/env python3
"""
Diagnostic script: compare wrapped vs complete prompt modes and strict vs lenient parsers.

Runs a small set of problems in 4 configurations to identify which matches the
official SAIR playground results:

  1. complete + lenient  (legacy sim_lab behavior)
  2. complete + strict   (legacy prompt, strict parser)
  3. wrapped  + lenient  (official template, lenient parser)
  4. wrapped  + strict   (full official parity candidate)

Usage:
  python diagnose_parity.py --cheatsheet cheatsheets/v24j.txt --n 10 --openrouter
  python diagnose_parity.py --cheatsheet cheatsheets/v24j.txt --data data/benchmark/normal_balanced10_true5_false5_seed0.jsonl --openrouter
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import sim_lab


def run_config(problems, cheatsheet, model, api_key, prompt_mode, parser_mode,
               temperature, num_predict, timeout, repeats, label):
    """Run evaluation with specific prompt_mode and parser_mode."""
    # Set module-level state
    sim_lab._api_key = api_key
    sim_lab._prompt_mode = prompt_mode
    sim_lab._parser_mode = parser_mode
    sim_lab._strict_output_contract = False

    print(f"\n{'═' * 70}")
    print(f"  CONFIG: {label}")
    print(f"  prompt_mode={prompt_mode}  parser={parser_mode}")
    print(f"{'═' * 70}")

    stats = sim_lab.run_evaluation(
        problems, cheatsheet, model,
        temperature=temperature,
        num_predict=num_predict,
        request_timeout_s=timeout,
        repeats=repeats,
        verbose=True,
    )
    sim_lab.print_report(stats, label)
    return stats


def main():
    parser = argparse.ArgumentParser(description="Diagnose sim_lab vs playground parity")
    parser.add_argument("--cheatsheet", required=True, help="Cheatsheet to test")
    parser.add_argument("--subset", choices=list(sim_lab.HF_SUBSETS), default=None)
    parser.add_argument("--data", default=None, help="Path to local JSONL benchmark file")
    parser.add_argument("--n", type=int, default=10, help="Problems to test (default: 10)")
    parser.add_argument("--repeats", type=int, default=1, help="Repeats per problem (default: 1)")
    parser.add_argument("--model", default=sim_lab.DEFAULT_MODEL)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--openrouter", action="store_true")
    parser.add_argument("--output", default=None, help="Save diagnostic JSON to this path")
    parser.add_argument("--configs", nargs="+",
                        choices=["complete-lenient", "complete-strict", "wrapped-lenient", "wrapped-strict"],
                        default=["complete-lenient", "wrapped-strict"],
                        help="Configurations to test (default: the two extremes)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("ERROR: Set OPENROUTER_API_KEY or pass --api-key")
        sys.exit(1)

    # Load problems
    if not args.subset and not args.data:
        args.subset = "normal"
    problems = sim_lab.load_problems(
        path=args.data, subset=args.subset, n=args.n, shuffle=True,
    )
    cheatsheet = sim_lab.load_cheatsheet(args.cheatsheet)

    # Pre-download template
    sim_lab.download_eval_template()

    # Show what the wrapped prompt looks like for the first problem
    if problems:
        p0 = problems[0]
        print(f"\n{'═' * 70}")
        print(f"  PROMPT PREVIEW (problem: {p0.id})")
        print(f"{'═' * 70}")

        prompt_complete = sim_lab.render_prompt(p0, cheatsheet, "complete")
        prompt_wrapped = sim_lab.render_prompt(p0, cheatsheet, "wrapped")

        print(f"\n  --- COMPLETE MODE (first 500 chars) ---")
        print(f"  {prompt_complete[:500]}")
        print(f"  ... ({len(prompt_complete)} chars total)")

        print(f"\n  --- WRAPPED MODE (first 500 chars) ---")
        print(f"  {prompt_wrapped[:500]}")
        print(f"  ... ({len(prompt_wrapped)} chars total)")

        print(f"\n  --- WRAPPED MODE (last 500 chars) ---")
        print(f"  {prompt_wrapped[-500:]}")
        print()

    # Define configurations
    config_defs = {
        "complete-lenient": ("complete", "lenient"),
        "complete-strict":  ("complete", "strict"),
        "wrapped-lenient":  ("wrapped", "lenient"),
        "wrapped-strict":   ("wrapped", "strict"),
    }

    all_results = {}
    for config_name in args.configs:
        prompt_mode, parser_mode = config_defs[config_name]
        stats = run_config(
            problems, cheatsheet, args.model, api_key,
            prompt_mode, parser_mode,
            temperature=None,  # provider default, matching playground
            num_predict=None,  # provider default, matching playground
            timeout=sim_lab.DEFAULT_REQUEST_TIMEOUT_S,
            repeats=args.repeats,
            label=config_name,
        )
        all_results[config_name] = {
            "accuracy": round(stats.accuracy, 4),
            "f1": round(stats.f1, 4),
            "parse_rate": round(stats.parse_success_rate, 4),
            "unparsed": stats.unparsed,
            "true_accuracy": round(stats.true_accuracy, 4),
            "false_accuracy": round(stats.false_accuracy, 4),
            "tp": stats.tp, "fp": stats.fp, "fn": stats.fn, "tn": stats.tn,
        }

    # Summary comparison
    print(f"\n{'═' * 80}")
    print(f"  DIAGNOSTIC COMPARISON SUMMARY")
    print(f"{'═' * 80}")
    print(f"  {'Config':<25s} {'Acc':>7s} {'F1':>7s} {'Parse':>7s} {'Unp':>5s} {'T_acc':>7s} {'F_acc':>7s}")
    print(f"  {'─' * 25} {'─' * 7} {'─' * 7} {'─' * 7} {'─' * 5} {'─' * 7} {'─' * 7}")
    for name, r in all_results.items():
        print(
            f"  {name:<25s} "
            f"{r['accuracy']:>6.1%} "
            f"{r['f1']:>6.1%} "
            f"{r['parse_rate']:>6.1%} "
            f"{r['unparsed']:>5d} "
            f"{r['true_accuracy']:>6.1%} "
            f"{r['false_accuracy']:>6.1%}"
        )
    print()

    # Interpretation
    if len(all_results) >= 2:
        configs = list(all_results.keys())
        print("  INTERPRETATION:")
        for name, r in all_results.items():
            if r["parse_rate"] < 0.8:
                print(f"  ⚠ {name}: LOW PARSE RATE ({r['parse_rate']:.0%}) — parser rejects many responses")
            if r["accuracy"] < 0.6:
                print(f"  ⚠ {name}: LOW ACCURACY ({r['accuracy']:.0%}) — likely matches playground experience")
        print()

    # Save
    output_path = args.output or f"results/diagnostic_{Path(args.cheatsheet).stem}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    diagnostic = {
        "cheatsheet": args.cheatsheet,
        "model": args.model,
        "n_problems": len(problems),
        "repeats": args.repeats,
        "problem_ids": [p.id for p in problems],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "configs": all_results,
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(diagnostic, f, indent=2)
    print(f"Diagnostic saved to {output_path}")


if __name__ == "__main__":
    main()
