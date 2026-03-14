"""
run_experiments.py — Orchestrator for ablation studies.

Runs the full distill→eval pipeline across configurations:
  - Prompt variants (default, textbook, concise, summary)
  - Rationale augmentation (on/off)
  - n_shots sweep
  - Self-consistency ablation
  - Model transfer (distill with model A, eval with model B)
"""

import json
import itertools
import logging
from pathlib import Path
from datetime import datetime

from config import ExperimentConfig, RESULTS_DIR, CHEATSHEETS_DIR
from distill import run_pipeline
from run_eval import run_evaluation

logger = logging.getLogger(__name__)


# ── Experiment Definitions ────────────────────────────────────────

ABLATION_CONFIGS = {
    # Prompt variant sweep
    "prompt_variants": [
        {"name": "variant_default", "variant": "default"},
        {"name": "variant_textbook", "variant": "textbook"},
        {"name": "variant_concise", "variant": "concise"},
        {"name": "variant_summary", "variant": "summary"},
    ],

    # Shot count sweep
    "n_shots_sweep": [
        {"name": "shots_50", "n_shots": 50},
        {"name": "shots_100", "n_shots": 100},
        {"name": "shots_150", "n_shots": 150},
        {"name": "shots_200", "n_shots": 200},
    ],

    # Rationale augmentation ablation
    "rationale_ablation": [
        {"name": "with_rationale", "use_rationale_augmentation": True},
        {"name": "no_rationale", "use_rationale_augmentation": False},
    ],

    # Model transfer
    "model_transfer": [
        {"name": "gpt41_to_mini", "distill_model": "gpt-4.1", "eval_model": "gpt-4o-mini"},
        {"name": "gpt41_to_gemini", "distill_model": "gpt-4.1", "eval_model": "gemini-2.0-flash"},
        {"name": "gemini_to_mini", "distill_model": "gemini-2.0-flash", "eval_model": "gpt-4o-mini"},
    ],

    # Self-consistency
    "self_consistency": [
        {"name": "no_sc", "use_self_consistency": False},
        {"name": "sc_3", "use_self_consistency": True, "sc_samples": 3},
        {"name": "sc_5", "use_self_consistency": True, "sc_samples": 5},
    ],
}


def run_ablation(
    ablation_name: str,
    training_data: str,
    eval_data: str,
    base_config: dict = None,
):
    """Run a single ablation study."""
    if ablation_name not in ABLATION_CONFIGS:
        raise ValueError(f"Unknown ablation: {ablation_name}. Available: {list(ABLATION_CONFIGS.keys())}")

    configs = ABLATION_CONFIGS[ablation_name]
    results = []

    for cfg_override in configs:
        name = cfg_override.pop("name")
        variant = cfg_override.pop("variant", "default")

        # Build config
        params = dict(base_config or {})
        params.update(cfg_override)
        params["name"] = f"{ablation_name}_{name}"
        config = ExperimentConfig(**params)

        logger.info(f"\n{'='*60}")
        logger.info(f"Running: {config.name}")
        logger.info(f"{'='*60}")

        # Distill
        cs_path = str(CHEATSHEETS_DIR / f"{config.name}.txt")
        run_pipeline(
            training_data=training_data,
            config=config,
            prompt_variant=variant,
            output_path=cs_path,
        )

        # Evaluate
        result = run_evaluation(
            cheatsheet_path=cs_path,
            eval_data_path=eval_data,
            config=config,
        )
        result["experiment_name"] = config.name
        results.append(result)

    # Save ablation summary
    summary = {
        "ablation": ablation_name,
        "timestamp": datetime.now().isoformat(),
        "results": [
            {
                "name": r["experiment_name"],
                "accuracy": r["accuracy"],
                "log_loss": r["log_loss"],
                "cost": r["total_cost"],
                "cheatsheet_bytes": r["cheatsheet_bytes"],
            }
            for r in results
        ],
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = RESULTS_DIR / f"ablation_{ablation_name}.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"\nAblation summary saved to {summary_path}")

    # Print comparison table
    print(f"\n{'='*70}")
    print(f"ABLATION: {ablation_name}")
    print(f"{'Name':<30} {'Acc':>8} {'LogLoss':>10} {'Cost':>10} {'Bytes':>8}")
    print(f"{'-'*70}")
    for r in summary["results"]:
        print(f"{r['name']:<30} {r['accuracy']:>8.3f} {r['log_loss']:>10.4f} ${r['cost']:>9.4f} {r['cheatsheet_bytes']:>8}")
    print(f"{'='*70}")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run experiment ablations")
    parser.add_argument("--ablation", required=True,
                        choices=list(ABLATION_CONFIGS.keys()) + ["all"],
                        help="Which ablation to run")
    parser.add_argument("--train-data", required=True, help="Training JSONL")
    parser.add_argument("--eval-data", required=True, help="Eval JSONL")
    parser.add_argument("--distill-model", default="gpt-4.1")
    parser.add_argument("--eval-model", default="gpt-4o-mini")
    parser.add_argument("--n-shots", type=int, default=150)
    parser.add_argument("--n-eval", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    base = {
        "distill_model": args.distill_model,
        "eval_model": args.eval_model,
        "n_shots": args.n_shots,
        "n_eval": args.n_eval,
        "seed": args.seed,
    }

    ablations = list(ABLATION_CONFIGS.keys()) if args.ablation == "all" else [args.ablation]
    for abl in ablations:
        run_ablation(abl, args.train_data, args.eval_data, base)


if __name__ == "__main__":
    main()
