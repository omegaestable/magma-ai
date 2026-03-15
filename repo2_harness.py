"""Repo 2.0 one-command E2E harness.

This orchestrator makes the naive Stage 1 workflow reproducible end-to-end:
1) benchmark bootstrap
2) research-model bootstrap (auto dataset creation in train.py)
3) baseline cheatsheet evaluation
4) optional candidate distillation and evaluation
5) acceptance gating + report emission

Submission validity is preserved by evaluating with cheatsheet-only prompts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
CHEATSHEET_PATH = ROOT / "cheatsheet.txt"


@dataclass
class GateConfig:
    min_overall_acc: float = 0.60
    min_true_acc: float = 0.45
    min_hard_acc: float = 0.35
    min_dual_consistency: float = 0.90


def run_cmd(args: list[str], label: str) -> None:
    print(f"\n[repo2] {label}")
    print("[repo2] cmd:", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def load_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_bucket_accuracy(payload: dict[str, Any], bucket: str) -> float:
    info = payload.get("bucket_accuracy", {}).get(bucket)
    if not info:
        return 0.0
    return float(info.get("accuracy", 0.0))


def gate_eval(payload: dict[str, Any], gates: GateConfig) -> dict[str, Any]:
    overall = float(payload.get("accuracy", 0.0))
    true_acc = float(payload.get("true_accuracy", 0.0))
    hard_acc = safe_bucket_accuracy(payload, "hard")
    dual_consistency = float(payload.get("dual_swap", {}).get("prediction_consistency", 0.0))

    checks = {
        "overall_accuracy": {"value": overall, "min": gates.min_overall_acc, "pass": overall >= gates.min_overall_acc},
        "true_accuracy": {"value": true_acc, "min": gates.min_true_acc, "pass": true_acc >= gates.min_true_acc},
        "hard_bucket_accuracy": {"value": hard_acc, "min": gates.min_hard_acc, "pass": hard_acc >= gates.min_hard_acc},
        "dual_swap_consistency": {
            "value": dual_consistency,
            "min": gates.min_dual_consistency,
            "pass": dual_consistency >= gates.min_dual_consistency,
        },
    }
    return {
        "pass": all(v["pass"] for v in checks.values()),
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Repo 2.0 one-command naive E2E runner")
    parser.add_argument("--name", default="repo2", help="Run name prefix")
    parser.add_argument("--eval-model", default="ollama-qwen2.5-3b", help="Model alias from config.py")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--local-n", type=int, default=200)
    parser.add_argument("--no-leak-n", type=int, default=200)
    parser.add_argument("--holdout-count", type=int, default=100)
    parser.add_argument("--hardest-n", type=int, default=500)
    parser.add_argument("--run-distill", action="store_true", help="Also run distillation ablation + candidate evaluation")
    parser.add_argument("--n-shots", type=int, default=150)
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument("--min-overall-acc", type=float, default=0.60)
    parser.add_argument("--min-true-acc", type=float, default=0.45)
    parser.add_argument("--min-hard-acc", type=float, default=0.35)
    parser.add_argument("--min-dual-consistency", type=float, default=0.90)
    args = parser.parse_args()

    py = sys.executable
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Build fresh benchmark slices.
    run_cmd(
        [
            py,
            "download_data.py",
            "--generate-local",
            "--n",
            str(args.local_n),
            "--seed",
            str(args.seed),
        ],
        "Generating local benchmark",
    )
    run_cmd(
        [
            py,
            "download_data.py",
            "--generate-no-leak",
            "--n",
            str(args.no_leak_n),
            "--holdout-count",
            str(args.holdout_count),
            "--seed",
            str(args.seed),
        ],
        "Generating no-leak benchmark",
    )
    run_cmd(
        [
            py,
            "download_data.py",
            "--generate-hardest",
            "--hardest-n",
            str(args.hardest_n),
            "--seed",
            str(args.seed),
        ],
        "Generating hardest benchmark",
    )

    # 2) Train with dataset auto-bootstrap when missing.
    run_cmd(
        [
            py,
            "train.py",
            "--dataset",
            "default",
            "--bootstrap-samples",
            str(args.bootstrap_samples),
            "--model-type",
            "xgboost",
            "--cv",
            "5",
            "--hardest-k",
            "500",
            "--name",
            f"{args.name}_ml",
        ],
        "Training research model (auto-bootstrap enabled)",
    )

    # 3) Baseline cheatsheet eval (submission-valid path).
    baseline_eval_name = f"{args.name}_baseline_no_leak"
    run_cmd(
        [
            py,
            "run_eval.py",
            "--cheatsheet",
            str(CHEATSHEET_PATH),
            "--data",
            "data/no_leak_benchmark.jsonl",
            "--eval-model",
            args.eval_model,
            "--dual-swap-check",
            "--name",
            baseline_eval_name,
        ],
        "Evaluating baseline cheatsheet on no-leak benchmark",
    )

    baseline_path = RESULTS_DIR / f"eval_{baseline_eval_name}.json"
    baseline_payload = load_json(baseline_path)

    gates = GateConfig(
        min_overall_acc=args.min_overall_acc,
        min_true_acc=args.min_true_acc,
        min_hard_acc=args.min_hard_acc,
        min_dual_consistency=args.min_dual_consistency,
    )
    baseline_gate = gate_eval(baseline_payload, gates)

    run_summary: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "name": args.name,
        "model": args.eval_model,
        "baseline": {
            "result_path": str(baseline_path),
            "accuracy": baseline_payload.get("accuracy"),
            "true_accuracy": baseline_payload.get("true_accuracy"),
            "false_accuracy": baseline_payload.get("false_accuracy"),
            "hard_bucket_accuracy": safe_bucket_accuracy(baseline_payload, "hard"),
            "dual_swap_consistency": baseline_payload.get("dual_swap", {}).get("prediction_consistency"),
            "gate": baseline_gate,
        },
    }

    if args.run_distill:
        candidate_name = f"{args.name}_candidate"
        candidate_path = ROOT / "cheatsheets" / f"cheatsheet_{candidate_name}_default.txt"

        run_cmd(
            [
                py,
                "distill.py",
                "--data",
                "data/local_benchmark.jsonl",
                "--config-name",
                candidate_name,
                "--n-shots",
                str(args.n_shots),
                "--distill-model",
                args.eval_model,
            ],
            "Distilling candidate cheatsheet",
        )

        candidate_eval_name = f"{args.name}_candidate_no_leak"
        run_cmd(
            [
                py,
                "run_eval.py",
                "--cheatsheet",
                str(candidate_path),
                "--data",
                "data/no_leak_benchmark.jsonl",
                "--eval-model",
                args.eval_model,
                "--dual-swap-check",
                "--name",
                candidate_eval_name,
            ],
            "Evaluating candidate cheatsheet on no-leak benchmark",
        )

        candidate_eval_path = RESULTS_DIR / f"eval_{candidate_eval_name}.json"
        candidate_payload = load_json(candidate_eval_path)
        candidate_gate = gate_eval(candidate_payload, gates)

        run_summary["candidate"] = {
            "cheatsheet_path": str(candidate_path),
            "result_path": str(candidate_eval_path),
            "accuracy": candidate_payload.get("accuracy"),
            "true_accuracy": candidate_payload.get("true_accuracy"),
            "false_accuracy": candidate_payload.get("false_accuracy"),
            "hard_bucket_accuracy": safe_bucket_accuracy(candidate_payload, "hard"),
            "dual_swap_consistency": candidate_payload.get("dual_swap", {}).get("prediction_consistency"),
            "gate": candidate_gate,
        }

    out_json = RESULTS_DIR / f"repo2_summary_{args.name}.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(run_summary, f, indent=2)

    print("\n[repo2] Summary written:", out_json)
    print("[repo2] Baseline gate pass:", run_summary["baseline"]["gate"]["pass"])
    if "candidate" in run_summary:
        print("[repo2] Candidate gate pass:", run_summary["candidate"]["gate"]["pass"])


if __name__ == "__main__":
    main()
