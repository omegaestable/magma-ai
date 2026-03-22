#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import distill
import scoreboard
import sim_lab


ROOT = Path(__file__).resolve().parent
CHEATSHEET_MAX_BYTES = sim_lab.CHEATSHEET_MAX_BYTES


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_path(relative_path: str) -> Path:
    return ROOT / relative_path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def append_jsonl(path: Path, payload: dict) -> None:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def normalize_model_for_filename(model: str) -> str:
    return scoreboard.normalize_model_for_filename(model)


def make_result_output_path(model: str, benchmark_stem: str, cheatsheet_path: Path) -> Path:
    filename = (
        f"sim_{normalize_model_for_filename(model)}_"
        f"{benchmark_stem}_{cheatsheet_path.stem}_{now_stamp()}.json"
    )
    return ROOT / "results" / filename


def build_gate_benchmarks(config: dict) -> list[Path]:
    gate_cfg = config["gates"]
    source_path = resolve_path(gate_cfg["source_subset_path"])
    rows = read_jsonl(source_path)
    true_rows = [row for row in rows if row["answer"] is True]
    false_rows = [row for row in rows if row["answer"] is False]

    items_per_label = int(gate_cfg["items_per_label"])
    benchmark_stems = gate_cfg["benchmark_stems"]
    shuffle_seed = int(gate_cfg["shuffle_seed"])

    rng_true = random.Random(shuffle_seed)
    rng_false = random.Random(shuffle_seed + 1)
    true_rows = true_rows[:]
    false_rows = false_rows[:]
    rng_true.shuffle(true_rows)
    rng_false.shuffle(false_rows)

    required = len(benchmark_stems) * items_per_label
    if len(true_rows) < required or len(false_rows) < required:
        raise ValueError("Not enough TRUE/FALSE rows in source subset to build disjoint gates.")

    written = []
    for index, benchmark_stem in enumerate(benchmark_stems):
        true_chunk = true_rows[index * items_per_label:(index + 1) * items_per_label]
        false_chunk = false_rows[index * items_per_label:(index + 1) * items_per_label]
        gate_rows = true_chunk + false_chunk
        gate_rng = random.Random(index)
        gate_rng.shuffle(gate_rows)
        out_path = ROOT / "data" / "benchmark" / f"{benchmark_stem}.jsonl"
        ensure_parent(out_path)
        with out_path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in gate_rows:
                handle.write(json.dumps(row) + "\n")
        written.append(out_path)
    return written


def run_eval(model: str, benchmark_stem: str, cheatsheet_path: Path) -> Path:
    benchmark_path = ROOT / "data" / "benchmark" / f"{benchmark_stem}.jsonl"
    output_path = make_result_output_path(model, benchmark_stem, cheatsheet_path)
    command = [
        sys.executable,
        "sim_lab.py",
        "--data",
        str(benchmark_path),
        "--cheatsheet",
        str(cheatsheet_path),
        "--openrouter",
        "--model",
        model,
        "--playground-parity",
        "--output",
        str(output_path),
    ]
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    subprocess.run(command, cwd=ROOT, check=True, env=env)
    return output_path


def summarize_result(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    row = scoreboard.parse_result_file(path)
    failures = []
    for result in payload.get("results", []):
        if result.get("correct"):
            continue
        failures.append({
            "id": result.get("id"),
            "ground_truth": result.get("ground_truth"),
            "predicted": result.get("predicted"),
            "equation1": result.get("equation1"),
            "equation2": result.get("equation2"),
        })
    return {
        "result_file": path.name,
        "benchmark": row.benchmark,
        "benchmark_file": row.benchmark_file,
        "accuracy": row.accuracy,
        "f1_score": row.f1_score,
        "true_accuracy": row.true_accuracy,
        "false_accuracy": row.false_accuracy,
        "parse_success_rate": row.parse_success_rate,
        "avg_time_s": row.avg_time_s,
        "estimated_cost_usd": row.estimated_cost_usd,
        "failures": failures,
    }


def build_answer_log_entries(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = []
    for result in payload.get("results", []):
        entries.append({
            "id": result.get("id"),
            "ground_truth": result.get("ground_truth"),
            "predicted": result.get("predicted"),
            "correct": result.get("correct"),
            "parsed_ok": result.get("parsed_ok"),
            "elapsed_s": result.get("elapsed_s"),
            "equation1": result.get("equation1"),
            "equation2": result.get("equation2"),
            "raw_response": result.get("raw_response", ""),
        })
    return entries


def write_answer_review_artifacts(config: dict, benchmark_stem: str, result_path: Path) -> tuple[Path, Path]:
    review_dir = resolve_path(config["artifacts"]["state_dir"]) / "baseline_answers"
    review_dir.mkdir(parents=True, exist_ok=True)
    answer_entries = build_answer_log_entries(result_path)

    json_path = review_dir / f"{benchmark_stem}_{result_path.stem}.json"
    write_json(json_path, {
        "benchmark": benchmark_stem,
        "result_file": str(result_path.relative_to(ROOT)),
        "answers": answer_entries,
    })

    md_path = review_dir / f"{benchmark_stem}_{result_path.stem}.md"
    lines = [
        f"# Baseline Answer Review: {benchmark_stem}",
        "",
        f"- Result file: {result_path.relative_to(ROOT)}",
        f"- Answer log JSON: {json_path.relative_to(ROOT)}",
        "",
    ]
    for item in answer_entries:
        lines.extend([
            f"## {item['id']}",
            "",
            f"- Ground truth: {item['ground_truth']}",
            f"- Predicted: {item['predicted']}",
            f"- Correct: {item['correct']}",
            f"- Parsed: {item['parsed_ok']}",
            f"- Elapsed: {item['elapsed_s']}",
            "",
            "### Equation 1",
            item["equation1"] or "",
            "",
            "### Equation 2",
            item["equation2"] or "",
            "",
            "### Raw Response",
            "```text",
            item["raw_response"] or "",
            "```",
            "",
        ])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def aggregate_gate_metrics(gate_runs: list[dict]) -> dict:
    return {
        "accuracy": mean(run["accuracy"] for run in gate_runs),
        "f1_score": mean(run["f1_score"] for run in gate_runs),
        "true_accuracy": mean(run["true_accuracy"] for run in gate_runs),
        "false_accuracy": mean(run["false_accuracy"] for run in gate_runs),
        "parse_success_rate": mean(run["parse_success_rate"] for run in gate_runs),
        "avg_time_s": mean(run["avg_time_s"] for run in gate_runs),
        "estimated_cost_usd": sum(run["estimated_cost_usd"] for run in gate_runs),
    }


def build_manifest(cheatsheet_path: Path, model: str, gate_runs: list[dict]) -> dict:
    aggregate = aggregate_gate_metrics(gate_runs)
    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "champion_path": str(cheatsheet_path.relative_to(ROOT)),
        "champion_label": cheatsheet_path.stem,
        "champion_bytes": cheatsheet_path.stat().st_size,
        "model": model,
        "gate_runs": gate_runs,
        "aggregate": aggregate,
    }


def render_failure_summary(manifest: dict) -> str:
    lines = [
        f"Champion: {manifest['champion_label']}",
        (
            "Aggregate: "
            f"acc={manifest['aggregate']['accuracy']:.3f}, "
            f"true_acc={manifest['aggregate']['true_accuracy']:.3f}, "
            f"false_acc={manifest['aggregate']['false_accuracy']:.3f}, "
            f"parse={manifest['aggregate']['parse_success_rate']:.3f}"
        ),
        "",
        "Failures:",
    ]
    for gate in manifest["gate_runs"]:
        lines.append(
            f"- {gate['benchmark']}: acc={gate['accuracy']:.3f}, "
            f"true={gate['true_accuracy']:.3f}, false={gate['false_accuracy']:.3f}"
        )
        for failure in gate["failures"][:4]:
            lines.append(
                f"  * {failure['id']} gt={failure['ground_truth']} pred={failure['predicted']}"
            )
            lines.append(f"    E1: {failure['equation1']}")
            lines.append(f"    E2: {failure['equation2']}")
    return "\n".join(lines) + "\n"


def choose_mutation_focus(config: dict, cycle_number: int) -> str:
    focuses = config["search"]["mutation_focuses"]
    return focuses[(cycle_number - 1) % len(focuses)]


def load_manifest(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _class_balance(agg: dict) -> float:
    """Return min(true_accuracy, false_accuracy) — the class-balance objective."""
    return min(agg.get("true_accuracy", 0.0), agg.get("false_accuracy", 0.0))


def compare_candidate(config: dict, champion_manifest: dict, candidate_manifest: dict) -> tuple[bool, list[str], int]:
    rules = config["promotion"]
    promotion_objective = rules.get("promotion_objective", "mean_metric")
    champion_by_benchmark = {run["benchmark"]: run for run in champion_manifest["gate_runs"]}
    candidate_by_benchmark = {run["benchmark"]: run for run in candidate_manifest["gate_runs"]}

    wins = 0
    reasons = []
    for benchmark in config["gates"]["benchmark_stems"]:
        if candidate_by_benchmark[benchmark]["accuracy"] > champion_by_benchmark[benchmark]["accuracy"]:
            wins += 1

    if wins < int(rules["required_seed_wins"]):
        reasons.append(
            f"seed wins {wins} < required {rules['required_seed_wins']}"
        )

    if promotion_objective == "class_balance_first":
        cand_cb = _class_balance(candidate_manifest["aggregate"])
        champ_cb = _class_balance(champion_manifest["aggregate"])
        if cand_cb <= champ_cb:
            reasons.append(
                f"class_balance min(true,false) did not improve ({cand_cb:.3f} <= {champ_cb:.3f})"
            )
    else:
        mean_metric = rules["mean_metric"]
        if candidate_manifest["aggregate"][mean_metric] <= champion_manifest["aggregate"][mean_metric]:
            reasons.append(
                f"mean {mean_metric} did not improve"
            )

    if (
        candidate_manifest["aggregate"]["parse_success_rate"]
        < champion_manifest["aggregate"]["parse_success_rate"] - float(rules["parse_rate_tolerance"])
    ):
        reasons.append("parse rate regressed beyond tolerance")

    if (
        champion_manifest["aggregate"]["true_accuracy"] - candidate_manifest["aggregate"]["true_accuracy"]
        > float(rules["max_true_accuracy_drop"])
    ):
        reasons.append("TRUE accuracy collapsed")

    if (
        champion_manifest["aggregate"]["false_accuracy"] - candidate_manifest["aggregate"]["false_accuracy"]
        > float(rules["max_false_accuracy_drop"])
    ):
        reasons.append("FALSE accuracy collapsed")

    return not reasons, reasons, wins


def write_status(config: dict, manifest: dict | None, latest_entry: dict | None) -> Path:
    status_path = resolve_path(config["artifacts"]["status_path"])
    ensure_parent(status_path)
    lines = ["# VNext Search Status", ""]
    if manifest:
        lines.extend([
            f"- Champion: {manifest['champion_label']}",
            f"- Champion path: {manifest['champion_path']}",
            f"- Champion bytes: {manifest['champion_bytes']}",
            (
                "- Champion aggregate: "
                f"acc={manifest['aggregate']['accuracy']:.3f}, "
                f"true={manifest['aggregate']['true_accuracy']:.3f}, "
                f"false={manifest['aggregate']['false_accuracy']:.3f}, "
                f"parse={manifest['aggregate']['parse_success_rate']:.3f}"
            ),
            "",
        ])
    if latest_entry:
        lines.extend([
            f"- Latest cycle: {latest_entry['cycle_number']}",
            f"- Latest candidate: {latest_entry['candidate_label']}",
            f"- Mutation focus: {latest_entry['mutation_focus']}",
            f"- Promoted: {latest_entry['promoted']}",
            f"- Reasons: {', '.join(latest_entry['reasons']) if latest_entry['reasons'] else 'passed'}",
            (
                "- Candidate aggregate: "
                f"acc={latest_entry['candidate_aggregate']['accuracy']:.3f}, "
                f"true={latest_entry['candidate_aggregate']['true_accuracy']:.3f}, "
                f"false={latest_entry['candidate_aggregate']['false_accuracy']:.3f}, "
                f"parse={latest_entry['candidate_aggregate']['parse_success_rate']:.3f}"
            ),
        ])
    status_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return status_path


def cmd_build_gates(config: dict) -> None:
    written = build_gate_benchmarks(config)
    for path in written:
        print(f"wrote {path.relative_to(ROOT)}")


def ensure_gates_exist(config: dict) -> None:
    missing = [
        stem for stem in config["gates"]["benchmark_stems"]
        if not (ROOT / "data" / "benchmark" / f"{stem}.jsonl").exists()
    ]
    if missing:
        build_gate_benchmarks(config)


def cmd_baseline(config: dict) -> dict:
    ensure_gates_exist(config)
    champion_path = resolve_path(config["champion_path"])
    model = config["model"]
    gate_runs = []
    for benchmark_stem in config["gates"]["benchmark_stems"]:
        result_path = run_eval(model, benchmark_stem, champion_path)
        gate_summary = summarize_result(result_path)
        answer_json_path, answer_md_path = write_answer_review_artifacts(config, benchmark_stem, result_path)
        gate_summary["answer_log_json"] = str(answer_json_path.relative_to(ROOT))
        gate_summary["answer_log_md"] = str(answer_md_path.relative_to(ROOT))
        gate_runs.append(gate_summary)
    manifest = build_manifest(champion_path, model, gate_runs)
    manifest_path = resolve_path(config["artifacts"]["manifest_path"])
    write_json(manifest_path, manifest)
    write_status(config, manifest, None)
    print(f"baseline manifest saved to {manifest_path.relative_to(ROOT)}")
    return manifest


def read_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_adapter(
    config: dict,
    champion_path: Path,
    candidate_path: Path,
    failure_summary_path: Path,
    mutation_focus: str,
    distillation_brief_path: Path | None = None,
) -> None:
    adapter_path = resolve_path(config["copilot"]["adapter_script"])
    if adapter_path.suffix.lower() == ".py":
        command = [
            sys.executable,
            str(adapter_path),
            "--champion-path",
            str(champion_path),
            "--candidate-path",
            str(candidate_path),
            "--failure-summary-path",
            str(failure_summary_path),
            "--mutation-focus",
            mutation_focus,
            "--copilot-command",
            config["copilot"]["command"],
        ]
        if distillation_brief_path and distillation_brief_path.exists():
            command.extend(["--distillation-brief-path", str(distillation_brief_path)])
    else:
        command = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(adapter_path),
            "-ChampionPath",
            str(champion_path),
            "-CandidatePath",
            str(candidate_path),
            "-FailureSummaryPath",
            str(failure_summary_path),
            "-MutationFocus",
            mutation_focus,
            "-CopilotCommand",
            config["copilot"]["command"],
        ]
    copilot_model = config["copilot"].get("model", "")
    if copilot_model:
        if adapter_path.suffix.lower() == ".py":
            command.extend(["--copilot-model", copilot_model])
        else:
            command.extend(["-CopilotModel", copilot_model])
    subprocess.run(command, cwd=ROOT, check=True)


def cmd_cycle(config: dict) -> dict:
    ensure_gates_exist(config)
    manifest_path = resolve_path(config["artifacts"]["manifest_path"])
    ledger_path = resolve_path(config["artifacts"]["ledger_path"])
    context_dir = resolve_path(config["artifacts"]["context_dir"])
    candidate_dir = resolve_path(config["artifacts"]["candidate_dir"])
    context_dir.mkdir(parents=True, exist_ok=True)
    candidate_dir.mkdir(parents=True, exist_ok=True)

    champion_manifest = load_manifest(manifest_path)
    if champion_manifest is None:
        champion_manifest = cmd_baseline(config)

    ledger = read_ledger(ledger_path)
    cycle_number = len(ledger) + 1
    mutation_focus = choose_mutation_focus(config, cycle_number)
    candidate_label = f"candidate_cycle{cycle_number:04d}"
    candidate_path = candidate_dir / f"{candidate_label}.txt"
    failure_summary_path = context_dir / f"failure_summary_cycle{cycle_number:04d}.md"
    failure_summary_path.write_text(render_failure_summary(champion_manifest), encoding="utf-8")

    # Supply the most recent distillation brief to the candidate generation prompt
    distill_dir = resolve_path(config["artifacts"]["state_dir"]) / "distilled_signals"
    latest_brief: Path | None = None
    if distill_dir.exists():
        briefs = sorted(distill_dir.glob("*_distillation_brief.md"))
        if briefs:
            latest_brief = briefs[-1]

    run_adapter(
        config,
        resolve_path(champion_manifest["champion_path"]),
        candidate_path,
        failure_summary_path,
        mutation_focus,
        distillation_brief_path=latest_brief,
    )

    candidate_bytes = candidate_path.stat().st_size
    if candidate_bytes > CHEATSHEET_MAX_BYTES:
        entry = {
            "cycle_number": cycle_number,
            "candidate_label": candidate_label,
            "candidate_path": str(candidate_path.relative_to(ROOT)),
            "candidate_bytes": candidate_bytes,
            "mutation_focus": mutation_focus,
            "promoted": False,
            "wins": 0,
            "reasons": [f"candidate exceeds {CHEATSHEET_MAX_BYTES} bytes"],
            "candidate_aggregate": {
                "accuracy": 0.0,
                "true_accuracy": 0.0,
                "false_accuracy": 0.0,
                "parse_success_rate": 0.0,
                "estimated_cost_usd": 0.0,
            },
        }
        append_jsonl(ledger_path, entry)
        write_status(config, champion_manifest, entry)
        return entry

    gate_runs = []
    for benchmark_stem in config["gates"]["benchmark_stems"]:
        result_path = run_eval(config["model"], benchmark_stem, candidate_path)
        gate_runs.append(summarize_result(result_path))
    candidate_manifest = build_manifest(candidate_path, config["model"], gate_runs)

    # Distillation: annotate failures and write pattern artifacts
    distill_dir = resolve_path(config["artifacts"]["state_dir"]) / "distilled_signals"
    distill_artifacts = distill.run_distillation(
        manifest=candidate_manifest,
        cycle_number=cycle_number,
        out_dir=distill_dir,
    )

    promoted, reasons, wins = compare_candidate(config, champion_manifest, candidate_manifest)
    promoted_path = resolve_path(config["promoted_path"])
    if promoted:
        ensure_parent(promoted_path)
        shutil.copyfile(candidate_path, promoted_path)
        champion_manifest = build_manifest(promoted_path, config["model"], gate_runs)
        write_json(manifest_path, champion_manifest)

    entry = {
        "cycle_number": cycle_number,
        "candidate_label": candidate_label,
        "candidate_path": str(candidate_path.relative_to(ROOT)),
        "candidate_bytes": candidate_bytes,
        "mutation_focus": mutation_focus,
        "promoted": promoted,
        "wins": wins,
        "reasons": reasons,
        "candidate_aggregate": candidate_manifest["aggregate"],
        "candidate_runs": candidate_manifest["gate_runs"],
        "distillation": distill_artifacts,
    }
    append_jsonl(ledger_path, entry)
    write_status(config, champion_manifest, entry)
    if promoted:
        print(f"promoted {candidate_label} -> {promoted_path.relative_to(ROOT)}")
    else:
        print(f"rejected {candidate_label}: {'; '.join(reasons)}")
    return entry


def cmd_loop(config: dict, max_cycles: int | None, max_budget_usd: float | None) -> None:
    if max_cycles is None or max_cycles <= 0:
        max_cycles = int(config["search"]["max_cycles_per_run"])
    if max_budget_usd is None or max_budget_usd <= 0:
        max_budget_usd = float(config["search"]["max_budget_usd"])

    spend = 0.0
    for _ in range(max_cycles):
        entry = cmd_cycle(config)
        spend += float(entry["candidate_aggregate"].get("estimated_cost_usd", 0.0))
        if spend >= max_budget_usd:
            print(f"stopping: spend {spend:.3f} >= budget {max_budget_usd:.3f}")
            break


def cmd_status(config: dict) -> None:
    manifest = load_manifest(resolve_path(config["artifacts"]["manifest_path"]))
    ledger = read_ledger(resolve_path(config["artifacts"]["ledger_path"]))
    latest = ledger[-1] if ledger else None
    status_path = write_status(config, manifest, latest)
    print(status_path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Iterative v_next search controller for balanced20 gates.")
    parser.add_argument("command", choices=("build-gates", "baseline", "cycle", "loop", "status"))
    parser.add_argument("--config", default="vnext_search_config.json")
    parser.add_argument("--max-cycles", type=int, default=0)
    parser.add_argument("--max-budget-usd", type=float, default=0.0)
    args = parser.parse_args()

    config = load_config(resolve_path(args.config))

    if args.command == "build-gates":
        cmd_build_gates(config)
    elif args.command == "baseline":
        cmd_baseline(config)
    elif args.command == "cycle":
        cmd_cycle(config)
    elif args.command == "loop":
        cmd_loop(config, args.max_cycles, args.max_budget_usd)
    elif args.command == "status":
        cmd_status(config)


if __name__ == "__main__":
    main()