#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import distill
import scoreboard
import sim_lab

ROOT = Path(__file__).resolve().parent
CHEATSHEET_MAX_BYTES = sim_lab.CHEATSHEET_MAX_BYTES
FIXED_MODEL = "meta-llama/llama-3.3-70b-instruct"
FIXED_WARMUP_BENCHMARK_STEMS = [
    "normal_balanced10_true5_false5_seed0",
    "normal_balanced10_true5_false5_seed1",
]
FIXED_BENCHMARK_STEMS = [
    "normal_balanced20_true10_false10_seed0",
    "normal_balanced20_true10_false10_seed1",
    "normal_balanced20_true10_false10_seed2",
]
REQUIRED_MANIFEST_KEYS = {
    "champion_path",
    "champion_label",
    "champion_bytes",
    "champion_sha256",
    "model",
    "gate_runs",
    "aggregate",
}
REQUIRED_GATE_RUN_KEYS = {
    "benchmark",
    "benchmark_file",
    "accuracy",
    "f1_score",
    "true_accuracy",
    "false_accuracy",
    "parse_success_rate",
    "avg_time_s",
    "estimated_cost_usd",
    "failures",
}
REQUIRED_CYCLE_KEYS = {
    "cycle_number",
    "mode",
    "candidate_label",
    "candidate_path",
    "candidate_bytes",
    "mutation_focus",
    "promoted",
    "wins",
    "reasons",
    "rejection_kind",
    "candidate_aggregate",
    "timestamp",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def ensure_keys(payload: dict, required: set[str], label: str) -> None:
    missing = sorted(required - set(payload.keys()))
    if missing:
        raise ValueError(f"{label} missing required keys: {missing}")


def validate_config(config: dict) -> None:
    ensure_keys(config, {"model", "copilot", "gates", "promotion", "search", "state", "artifacts"}, "config")
    ensure_keys(config["copilot"], {"command", "adapter_script", "model"}, "config.copilot")
    ensure_keys(
        config["gates"],
        {"source_subset_path", "shuffle_seed", "items_per_label", "benchmark_stems", "warmup_items_per_label", "warmup_benchmark_stems"},
        "config.gates",
    )
    ensure_keys(
        config["promotion"],
        {
            "required_seed_wins",
            "per_seed_true_accuracy_floor",
            "per_seed_false_accuracy_floor",
            "warmup_true_accuracy_floor",
            "warmup_false_accuracy_floor",
            "warmup_min_f1_score",
            "warmup_min_parse_success_rate",
        },
        "config.promotion",
    )
    ensure_keys(
        config["search"],
        {
            "shadow_mode",
            "max_cycles_per_run",
            "max_budget_usd",
            "max_oversize_streak",
            "copilot_timeout_s",
            "copilot_max_retries",
            "warmup_pass_streak_required",
        },
        "config.search",
    )
    ensure_keys(config["state"], {"authoritative_champion_path", "promotion_target_path", "state_dir", "legacy_state_dir", "legacy_archive_root"}, "config.state")
    ensure_keys(config["artifacts"], {"candidate_dir"}, "config.artifacts")


def validate_manifest(manifest: dict) -> None:
    ensure_keys(manifest, REQUIRED_MANIFEST_KEYS, "manifest")
    if manifest["model"] != FIXED_MODEL:
        raise ValueError(f"manifest model drift: {manifest['model']} != {FIXED_MODEL}")
    gate_runs = manifest["gate_runs"]
    if not isinstance(gate_runs, list) or len(gate_runs) != len(FIXED_BENCHMARK_STEMS):
        raise ValueError("manifest gate_runs must contain exactly fixed 3-seed runs")
    bench_set = {run.get("benchmark") for run in gate_runs}
    if bench_set != set(FIXED_BENCHMARK_STEMS):
        raise ValueError(f"manifest benchmarks mismatch: {sorted(bench_set)}")
    for run in gate_runs:
        ensure_keys(run, REQUIRED_GATE_RUN_KEYS, f"manifest.gate_run[{run.get('benchmark', '?')}]")


def validate_cycle_entry(entry: dict) -> None:
    ensure_keys(entry, REQUIRED_CYCLE_KEYS, f"cycle[{entry.get('cycle_number', '?')}]")


def validate_champion_file(manifest: dict) -> None:
    champion_path = ROOT / manifest["champion_path"]
    if not champion_path.exists():
        raise FileNotFoundError(f"Champion file missing: {champion_path}")
    size = champion_path.stat().st_size
    if int(manifest["champion_bytes"]) != size:
        raise ValueError(
            f"Champion bytes mismatch for {champion_path}: manifest={manifest['champion_bytes']} disk={size}"
        )
    digest = sha256_file(champion_path)
    if manifest["champion_sha256"] != digest:
        raise ValueError(
            f"Champion hash mismatch for {champion_path}: manifest={manifest['champion_sha256']} disk={digest}"
        )


def ensure_policy_lock(config: dict) -> dict:
    config["model"] = FIXED_MODEL
    gates = config.setdefault("gates", {})
    gates["benchmark_stems"] = FIXED_BENCHMARK_STEMS[:]
    gates["warmup_benchmark_stems"] = FIXED_WARMUP_BENCHMARK_STEMS[:]
    config.setdefault("promotion", {})["required_seed_wins"] = 2
    validate_config(config)
    return config


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_state_paths(config: dict) -> dict:
    base = ROOT / config["state"]["state_dir"]
    return {
        "base": base,
        "current_manifest": base / "champions" / "current.json",
        "history_dir": base / "champions" / "history",
        "cycles": base / "cycles.jsonl",
        "status": base / "status.md",
        "context_dir": base / "context",
        "distill_dir": base / "distilled_signals",
        "candidate_dir": ROOT / config["artifacts"]["candidate_dir"],
        "decision_dir": base / "decisions",
        "replay_dir": base / "replay",
    }


def build_gate_benchmarks(config: dict) -> list[Path]:
    source_path = ROOT / config["gates"]["source_subset_path"]
    rows = read_jsonl(source_path)
    true_rows = [row for row in rows if row["answer"] is True]
    false_rows = [row for row in rows if row["answer"] is False]

    items_per_label = int(config["gates"]["items_per_label"])
    warmup_items_per_label = int(config["gates"]["warmup_items_per_label"])
    shuffle_seed = int(config["gates"]["shuffle_seed"])

    rng_true = random.Random(shuffle_seed)
    rng_false = random.Random(shuffle_seed + 1)
    rng_true.shuffle(true_rows)
    rng_false.shuffle(false_rows)

    warmup_required = len(FIXED_WARMUP_BENCHMARK_STEMS) * warmup_items_per_label
    full_required = len(FIXED_BENCHMARK_STEMS) * items_per_label
    required = warmup_required + full_required
    if len(true_rows) < required or len(false_rows) < required:
        raise ValueError("Not enough TRUE/FALSE rows to build fixed gates.")

    out_paths: list[Path] = []
    for i, stem in enumerate(FIXED_WARMUP_BENCHMARK_STEMS):
        chunk = true_rows[i * warmup_items_per_label:(i + 1) * warmup_items_per_label] + false_rows[
            i * warmup_items_per_label:(i + 1) * warmup_items_per_label
        ]
        random.Random(100 + i).shuffle(chunk)
        out = ROOT / "data" / "benchmark" / f"{stem}.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="\n") as handle:
            for row in chunk:
                handle.write(json.dumps(row) + "\n")
        out_paths.append(out)

    full_offset = warmup_required
    for i, stem in enumerate(FIXED_BENCHMARK_STEMS):
        start = full_offset + (i * items_per_label)
        end = full_offset + ((i + 1) * items_per_label)
        chunk = true_rows[start:end] + false_rows[
            start:end
        ]
        random.Random(i).shuffle(chunk)
        out = ROOT / "data" / "benchmark" / f"{stem}.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="\n") as handle:
            for row in chunk:
                handle.write(json.dumps(row) + "\n")
        out_paths.append(out)
    return out_paths


def ensure_gates(config: dict) -> None:
    missing = [
        stem
        for stem in FIXED_WARMUP_BENCHMARK_STEMS + FIXED_BENCHMARK_STEMS
        if not (ROOT / "data" / "benchmark" / f"{stem}.jsonl").exists()
    ]
    if missing:
        build_gate_benchmarks(config)


def make_output_path(model: str, benchmark_stem: str, cheatsheet_path: Path) -> Path:
    name = (
        f"sim_{scoreboard.normalize_model_for_filename(model)}_"
        f"{benchmark_stem}_{cheatsheet_path.stem}_{now_stamp()}.json"
    )
    return ROOT / "results" / name


def run_eval(model: str, benchmark_stem: str, cheatsheet_path: Path) -> Path:
    out = make_output_path(model, benchmark_stem, cheatsheet_path)
    cmd = [
        sys.executable,
        "sim_lab.py",
        "--data",
        str(ROOT / "data" / "benchmark" / f"{benchmark_stem}.jsonl"),
        "--cheatsheet",
        str(cheatsheet_path),
        "--openrouter",
        "--model",
        model,
        "--playground-parity",
        "--output",
        str(out),
    ]
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    subprocess.run(cmd, cwd=ROOT, check=True, env=env)
    return out


def summarize_result(path: Path) -> dict:
    payload = load_json(path)
    row = scoreboard.parse_result_file(path)
    failures = []
    for result in payload.get("results", []):
        if result.get("correct"):
            continue
        failures.append(
            {
                "id": result.get("id"),
                "ground_truth": result.get("ground_truth"),
                "predicted": result.get("predicted"),
                "equation1": result.get("equation1"),
                "equation2": result.get("equation2"),
            }
        )
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


def aggregate_metrics(gate_runs: list[dict]) -> dict:
    return {
        "accuracy": mean(run["accuracy"] for run in gate_runs),
        "f1_score": mean(run["f1_score"] for run in gate_runs),
        "true_accuracy": mean(run["true_accuracy"] for run in gate_runs),
        "false_accuracy": mean(run["false_accuracy"] for run in gate_runs),
        "parse_success_rate": mean(run["parse_success_rate"] for run in gate_runs),
        "avg_time_s": mean(run["avg_time_s"] for run in gate_runs),
        "estimated_cost_usd": sum(run["estimated_cost_usd"] for run in gate_runs),
    }


def render_failure_summary(manifest: dict) -> str:
    lines = [
        f"Champion: {manifest['champion_label']}",
        (
            "Aggregate: "
            f"acc={manifest['aggregate']['accuracy']:.3f}, "
            f"f1={manifest['aggregate']['f1_score']:.3f}, "
            f"true={manifest['aggregate']['true_accuracy']:.3f}, "
            f"false={manifest['aggregate']['false_accuracy']:.3f}, "
            f"parse={manifest['aggregate']['parse_success_rate']:.3f}"
        ),
        "",
        "Per-seed failures:",
    ]
    for gate in manifest["gate_runs"]:
        lines.append(
            f"- {gate['benchmark']}: acc={gate['accuracy']:.3f}, true={gate['true_accuracy']:.3f}, false={gate['false_accuracy']:.3f}"
        )
        for failure in gate["failures"][:3]:
            lines.append(f"  * {failure['id']} gt={failure['ground_truth']} pred={failure['predicted']}")
    return "\n".join(lines) + "\n"


def load_current_manifest(paths: dict) -> dict | None:
    p = paths["current_manifest"]
    if not p.exists():
        return None
    manifest = load_json(p)
    validate_manifest(manifest)
    validate_champion_file(manifest)
    return manifest


def save_champion_manifest(paths: dict, manifest: dict) -> None:
    validate_manifest(manifest)
    validate_champion_file(manifest)
    history_dir = paths["history_dir"]
    history_dir.mkdir(parents=True, exist_ok=True)
    version_id = f"champion_{now_stamp()}"
    manifest = {**manifest, "version_id": version_id, "updated_at": utc_now()}
    write_json(history_dir / f"{version_id}.json", manifest)
    write_json(paths["current_manifest"], manifest)


def champion_manifest_from_runs(config: dict, champion_path: Path, gate_runs: list[dict]) -> dict:
    return {
        "champion_path": rel(champion_path),
        "champion_label": champion_path.stem,
        "champion_bytes": champion_path.stat().st_size,
        "champion_sha256": sha256_file(champion_path),
        "model": config["model"],
        "gate_runs": gate_runs,
        "aggregate": aggregate_metrics(gate_runs),
    }


def baseline_from_champion(config: dict, paths: dict) -> dict:
    ensure_gates(config)
    champion_path = ROOT / config["state"]["authoritative_champion_path"]
    if not champion_path.exists():
        raise FileNotFoundError(f"Champion baseline file not found: {champion_path}")
    gate_runs = [
        summarize_result(run_eval(config["model"], stem, champion_path)) for stem in FIXED_BENCHMARK_STEMS
    ]
    manifest = champion_manifest_from_runs(config, champion_path, gate_runs)
    save_champion_manifest(paths, manifest)
    return manifest


def evaluate_runs(model: str, benchmark_stems: list[str], cheatsheet_path: Path) -> list[dict]:
    return [summarize_result(run_eval(model, stem, cheatsheet_path)) for stem in benchmark_stems]


def warmup_decide(config: dict, warmup_runs: list[dict]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    true_floor = float(config["promotion"]["warmup_true_accuracy_floor"])
    false_floor = float(config["promotion"]["warmup_false_accuracy_floor"])
    min_f1 = float(config["promotion"]["warmup_min_f1_score"])
    min_parse = float(config["promotion"]["warmup_min_parse_success_rate"])

    for run in warmup_runs:
        seed = run["benchmark"]
        if run["true_accuracy"] < true_floor:
            reasons.append(f"{seed}: warmup true_accuracy {run['true_accuracy']:.3f} < floor {true_floor:.3f}")
        if run["false_accuracy"] < false_floor:
            reasons.append(f"{seed}: warmup false_accuracy {run['false_accuracy']:.3f} < floor {false_floor:.3f}")
        if run["f1_score"] < min_f1:
            reasons.append(f"{seed}: warmup f1_score {run['f1_score']:.3f} < floor {min_f1:.3f}")
        if run["parse_success_rate"] < min_parse:
            reasons.append(f"{seed}: warmup parse_success_rate {run['parse_success_rate']:.3f} < floor {min_parse:.3f}")

    return (not reasons, reasons)


def compute_warmup_streak(cycles: list[dict]) -> int:
    streak = 0
    for entry in reversed(cycles):
        if not entry.get("warmup_passed"):
            break
        streak += 1
    return streak


def select_mutation_focus(paths: dict, cycle_number: int) -> str:
    cycles = read_jsonl(paths["cycles"])
    if not cycles:
        return "repair top structural error pattern from champion failures"
    latest = cycles[-1]
    top_pattern = latest.get("distillation", {}).get("top_pattern")
    if top_pattern:
        return f"repair pattern: {top_pattern}"
    return f"cycle-{cycle_number} balanced-class repair"


def write_decision_artifact(paths: dict, cycle_number: int, payload: dict) -> Path:
    paths["decision_dir"].mkdir(parents=True, exist_ok=True)
    out = paths["decision_dir"] / f"cycle_{cycle_number:04d}_decision.json"
    write_json(out, payload)
    return out


def run_adapter(
    config: dict,
    champion_path: Path,
    candidate_path: Path,
    failure_summary_path: Path,
    mutation_focus: str,
    brief_path: Path | None,
    witness_brief_path: Path | None,
) -> None:
    adapter = ROOT / config["copilot"]["adapter_script"]
    cmd = [
        sys.executable,
        str(adapter),
        "--champion-path",
        str(champion_path),
        "--candidate-path",
        str(candidate_path),
        "--failure-summary-path",
        str(failure_summary_path),
        "--mutation-focus",
        mutation_focus,
        "--copilot-command",
        config["copilot"].get("command", "copilot"),
        "--max-bytes",
        str(CHEATSHEET_MAX_BYTES),
        "--timeout-s",
        str(config["search"].get("copilot_timeout_s", 300)),
        "--max-retries",
        str(config["search"].get("copilot_max_retries", 2)),
    ]
    copilot_model = config["copilot"].get("model", "")
    if copilot_model:
        cmd.extend(["--copilot-model", copilot_model])
    if brief_path and brief_path.exists():
        cmd.extend(["--distillation-brief-path", str(brief_path)])
    if witness_brief_path and witness_brief_path.exists():
        cmd.extend(["--witness-brief-path", str(witness_brief_path)])
    subprocess.run(cmd, cwd=ROOT, check=True)


@dataclass
class Decision:
    promoted: bool
    wins: int
    reasons: list[str]


def strict_decide(config: dict, champion_manifest: dict, candidate_manifest: dict) -> Decision:
    reasons: list[str] = []
    wins = 0
    req_wins = int(config["promotion"]["required_seed_wins"])
    true_floor = float(config["promotion"]["per_seed_true_accuracy_floor"])
    false_floor = float(config["promotion"]["per_seed_false_accuracy_floor"])

    champ_by_seed = {r["benchmark"]: r for r in champion_manifest["gate_runs"]}
    cand_by_seed = {r["benchmark"]: r for r in candidate_manifest["gate_runs"]}

    for seed in FIXED_BENCHMARK_STEMS:
        c = cand_by_seed[seed]
        h = champ_by_seed[seed]
        if c["accuracy"] > h["accuracy"]:
            wins += 1
        if c["true_accuracy"] < true_floor:
            reasons.append(f"{seed}: true_accuracy {c['true_accuracy']:.3f} < floor {true_floor:.3f}")
        if c["false_accuracy"] < false_floor:
            reasons.append(f"{seed}: false_accuracy {c['false_accuracy']:.3f} < floor {false_floor:.3f}")
        if h["f1_score"] > 0 and c["f1_score"] == 0:
            reasons.append(f"{seed}: collapse detected (f1 dropped to 0)")
        if c["parse_success_rate"] < h["parse_success_rate"]:
            reasons.append(f"{seed}: parse rate regressed")

    if wins < req_wins:
        reasons.append(f"seed wins {wins} < required {req_wins}")

    promoted = not reasons
    return Decision(promoted=promoted, wins=wins, reasons=reasons)


def write_status(paths: dict, manifest: dict | None, latest: dict | None) -> None:
    lines = ["# VNext Search V2 Status", ""]
    if manifest:
        lines.extend(
            [
                f"- Champion: {manifest['champion_label']}",
                f"- Champion path: {manifest['champion_path']}",
                f"- Champion bytes: {manifest['champion_bytes']}",
                f"- Champion hash: {manifest['champion_sha256'][:16]}",
                (
                    "- Champion aggregate: "
                    f"acc={manifest['aggregate']['accuracy']:.3f}, "
                    f"f1={manifest['aggregate']['f1_score']:.3f}, "
                    f"true={manifest['aggregate']['true_accuracy']:.3f}, "
                    f"false={manifest['aggregate']['false_accuracy']:.3f}, "
                    f"parse={manifest['aggregate']['parse_success_rate']:.3f}"
                ),
                "",
            ]
        )
    if latest:
        aggregate = latest.get("candidate_aggregate") or latest.get("warmup_aggregate")
        lines.extend(
            [
                f"- Latest cycle: {latest['cycle_number']}",
                f"- Candidate: {latest['candidate_label']}",
                f"- Mutation focus: {latest['mutation_focus']}",
                f"- Evaluation stage: {latest.get('evaluation_stage', 'full')}",
                f"- Warmup passed: {latest.get('warmup_passed', False)}",
                f"- Warmup streak: {latest.get('warmup_streak', 0)}",
                f"- Promoted: {latest['promoted']}",
                f"- Wins: {latest.get('wins', 0)}",
                f"- Reasons: {', '.join(latest.get('reasons', [])) if latest.get('reasons') else 'passed'}",
                (
                    "- Candidate aggregate: "
                    f"acc={aggregate['accuracy']:.3f}, "
                    f"f1={aggregate['f1_score']:.3f}, "
                    f"true={aggregate['true_accuracy']:.3f}, "
                    f"false={aggregate['false_accuracy']:.3f}, "
                    f"parse={aggregate['parse_success_rate']:.3f}"
                ),
            ]
        )
    paths["status"].parent.mkdir(parents=True, exist_ok=True)
    paths["status"].write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_freeze_legacy(config: dict, paths: dict) -> None:
    legacy_dir = ROOT / config["state"]["legacy_state_dir"]
    if not legacy_dir.exists():
        print(f"legacy dir not found, skipping: {rel(legacy_dir)}")
        return
    archive_dir = ROOT / config["state"]["legacy_archive_root"] / f"frozen_{now_stamp()}"
    archive_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(legacy_dir), str(archive_dir))
    print(f"moved {rel(legacy_dir)} -> {rel(archive_dir)}")


def cmd_init(config: dict, paths: dict) -> None:
    manifest = baseline_from_champion(config, paths)
    write_status(paths, manifest, None)
    print(f"initialized champion: {manifest['champion_label']}")


def cmd_cycle(config: dict, paths: dict) -> dict:
    ensure_gates(config)
    current = load_current_manifest(paths)
    if current is None:
        current = baseline_from_champion(config, paths)

    cycles = read_jsonl(paths["cycles"])
    cycle_number = len(cycles) + 1
    mutation_focus = select_mutation_focus(paths, cycle_number)

    candidate_label = f"candidate_v2_cycle{cycle_number:04d}"
    candidate_path = paths["candidate_dir"] / f"{candidate_label}.txt"
    candidate_path.parent.mkdir(parents=True, exist_ok=True)

    paths["context_dir"].mkdir(parents=True, exist_ok=True)
    failure_summary = paths["context_dir"] / f"failure_summary_cycle{cycle_number:04d}.md"
    failure_summary.write_text(render_failure_summary(current), encoding="utf-8")

    latest_brief: Path | None = None
    latest_witness_brief: Path | None = None
    if paths["distill_dir"].exists():
        briefs = sorted(paths["distill_dir"].glob("*_distillation_brief.md"))
        if briefs:
            latest_brief = briefs[-1]
        witness_briefs = sorted(paths["distill_dir"].glob("*_witness_brief.md"))
        if witness_briefs:
            latest_witness_brief = witness_briefs[-1]

    run_adapter(
        config,
        ROOT / current["champion_path"],
        candidate_path,
        failure_summary,
        mutation_focus,
        latest_brief,
        latest_witness_brief,
    )

    candidate_bytes = candidate_path.stat().st_size
    if candidate_bytes > CHEATSHEET_MAX_BYTES:
        entry = {
            "cycle_number": cycle_number,
            "mode": "shadow" if config["search"].get("shadow_mode", True) else "promote",
            "candidate_label": candidate_label,
            "candidate_path": rel(candidate_path),
            "candidate_bytes": candidate_bytes,
            "mutation_focus": mutation_focus,
            "promoted": False,
            "wins": 0,
            "reasons": [f"oversize candidate: {candidate_bytes} > {CHEATSHEET_MAX_BYTES}"],
            "rejection_kind": "oversize",
            "evaluation_stage": "none",
            "warmup_passed": False,
            "warmup_streak": 0,
            "candidate_aggregate": {
                "accuracy": 0.0,
                "f1_score": 0.0,
                "true_accuracy": 0.0,
                "false_accuracy": 0.0,
                "parse_success_rate": 0.0,
                "avg_time_s": 0.0,
                "estimated_cost_usd": 0.0,
            },
            "timestamp": utc_now(),
        }
        validate_cycle_entry(entry)
        decision_path = write_decision_artifact(
            paths,
            cycle_number,
            {
                "cycle_number": cycle_number,
                "decision": "reject",
                "decision_kind": "oversize",
                "candidate_label": candidate_label,
                "candidate_path": rel(candidate_path),
                "candidate_bytes": candidate_bytes,
                "max_bytes": CHEATSHEET_MAX_BYTES,
                "wins": 0,
                "reasons": entry["reasons"],
                "timestamp": utc_now(),
            },
        )
        entry["decision_artifact"] = rel(decision_path)
        append_jsonl(paths["cycles"], entry)
        write_status(paths, current, entry)
        return entry

    prior_warmup_streak = compute_warmup_streak(cycles)
    warmup_runs = evaluate_runs(config["model"], FIXED_WARMUP_BENCHMARK_STEMS, candidate_path)
    warmup_aggregate = aggregate_metrics(warmup_runs)
    warmup_passed, warmup_reasons = warmup_decide(config, warmup_runs)
    warmup_streak = prior_warmup_streak + 1 if warmup_passed else 0
    required_warmup_streak = int(config["search"].get("warmup_pass_streak_required", 1))

    if not warmup_passed:
        entry = {
            "cycle_number": cycle_number,
            "mode": "shadow" if config["search"].get("shadow_mode", True) else "promote",
            "candidate_label": candidate_label,
            "candidate_path": rel(candidate_path),
            "candidate_bytes": candidate_bytes,
            "mutation_focus": mutation_focus,
            "promoted": False,
            "wins": 0,
            "reasons": warmup_reasons,
            "rejection_kind": "warmup_collapse",
            "evaluation_stage": "warmup_only",
            "warmup_passed": False,
            "warmup_streak": 0,
            "warmup_runs": warmup_runs,
            "warmup_aggregate": warmup_aggregate,
            "candidate_aggregate": warmup_aggregate,
            "timestamp": utc_now(),
        }
        validate_cycle_entry(entry)
        decision_path = write_decision_artifact(
            paths,
            cycle_number,
            {
                "cycle_number": cycle_number,
                "decision": "reject",
                "decision_kind": "warmup_collapse",
                "candidate_label": candidate_label,
                "candidate_path": rel(candidate_path),
                "candidate_bytes": candidate_bytes,
                "warmup_runs": warmup_runs,
                "warmup_aggregate": warmup_aggregate,
                "warmup_passed": False,
                "warmup_streak": 0,
                "reasons": warmup_reasons,
                "timestamp": utc_now(),
            },
        )
        entry["decision_artifact"] = rel(decision_path)
        append_jsonl(paths["cycles"], entry)
        write_status(paths, current, entry)
        return entry

    if warmup_streak < required_warmup_streak:
        reasons = [
            (
                f"warmup passed; holding full eval until non-collapse streak "
                f"{warmup_streak}/{required_warmup_streak}"
            )
        ]
        entry = {
            "cycle_number": cycle_number,
            "mode": "shadow" if config["search"].get("shadow_mode", True) else "promote",
            "candidate_label": candidate_label,
            "candidate_path": rel(candidate_path),
            "candidate_bytes": candidate_bytes,
            "mutation_focus": mutation_focus,
            "promoted": False,
            "wins": 0,
            "reasons": reasons,
            "rejection_kind": "warmup_only",
            "evaluation_stage": "warmup_only",
            "warmup_passed": True,
            "warmup_streak": warmup_streak,
            "warmup_runs": warmup_runs,
            "warmup_aggregate": warmup_aggregate,
            "candidate_aggregate": warmup_aggregate,
            "timestamp": utc_now(),
        }
        validate_cycle_entry(entry)
        decision_path = write_decision_artifact(
            paths,
            cycle_number,
            {
                "cycle_number": cycle_number,
                "decision": "hold",
                "decision_kind": "warmup_only",
                "candidate_label": candidate_label,
                "candidate_path": rel(candidate_path),
                "candidate_bytes": candidate_bytes,
                "warmup_runs": warmup_runs,
                "warmup_aggregate": warmup_aggregate,
                "warmup_passed": True,
                "warmup_streak": warmup_streak,
                "required_warmup_streak": required_warmup_streak,
                "reasons": reasons,
                "timestamp": utc_now(),
            },
        )
        entry["decision_artifact"] = rel(decision_path)
        append_jsonl(paths["cycles"], entry)
        write_status(paths, current, entry)
        return entry

    gate_runs = evaluate_runs(config["model"], FIXED_BENCHMARK_STEMS, candidate_path)
    candidate_manifest = champion_manifest_from_runs(config, candidate_path, gate_runs)

    distill_artifacts = distill.run_distillation(
        manifest=candidate_manifest,
        cycle_number=cycle_number,
        out_dir=paths["distill_dir"],
    )

    decision = strict_decide(config, current, candidate_manifest)

    promoted = False
    if decision.promoted and not config["search"].get("shadow_mode", True):
        promoted_target = ROOT / config["state"]["promotion_target_path"]
        promoted_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate_path, promoted_target)
        promoted_manifest = champion_manifest_from_runs(config, promoted_target, gate_runs)
        save_champion_manifest(paths, promoted_manifest)
        current = promoted_manifest
        promoted = True

    entry = {
        "cycle_number": cycle_number,
        "mode": "shadow" if config["search"].get("shadow_mode", True) else "promote",
        "candidate_label": candidate_label,
        "candidate_path": rel(candidate_path),
        "candidate_bytes": candidate_bytes,
        "mutation_focus": mutation_focus,
        "promoted": promoted,
        "wins": decision.wins,
        "reasons": decision.reasons,
        "rejection_kind": None if decision.promoted else "gate_failure",
        "evaluation_stage": "full",
        "warmup_passed": True,
        "warmup_streak": warmup_streak,
        "warmup_runs": warmup_runs,
        "warmup_aggregate": warmup_aggregate,
        "candidate_aggregate": candidate_manifest["aggregate"],
        "candidate_runs": candidate_manifest["gate_runs"],
        "distillation": distill_artifacts,
        "timestamp": utc_now(),
    }
    validate_cycle_entry(entry)
    decision_path = write_decision_artifact(
        paths,
        cycle_number,
        {
            "cycle_number": cycle_number,
            "decision": "promote" if promoted else "reject",
            "decision_kind": "strict_gate",
            "candidate_label": candidate_label,
            "candidate_path": rel(candidate_path),
            "candidate_bytes": candidate_bytes,
            "wins": decision.wins,
            "required_seed_wins": int(config["promotion"]["required_seed_wins"]),
            "warmup_runs": warmup_runs,
            "warmup_aggregate": warmup_aggregate,
            "warmup_streak": warmup_streak,
            "required_warmup_streak": required_warmup_streak,
            "reasons": decision.reasons,
            "candidate_aggregate": candidate_manifest["aggregate"],
            "timestamp": utc_now(),
        },
    )
    entry["decision_artifact"] = rel(decision_path)
    append_jsonl(paths["cycles"], entry)
    write_status(paths, current, entry)
    return entry


def cmd_loop(config: dict, paths: dict, max_cycles: int, max_budget_usd: float) -> None:
    cycles = max_cycles if max_cycles > 0 else int(config["search"]["max_cycles_per_run"])
    budget = max_budget_usd if max_budget_usd > 0 else float(config["search"]["max_budget_usd"])

    spend = 0.0
    oversize_streak = 0
    max_oversize_streak = int(config["search"].get("max_oversize_streak", 2))

    for _ in range(cycles):
        entry = cmd_cycle(config, paths)
        spend += float(entry["candidate_aggregate"].get("estimated_cost_usd", 0.0))

        if entry.get("rejection_kind") == "oversize":
            oversize_streak += 1
        else:
            oversize_streak = 0

        if oversize_streak >= max_oversize_streak:
            print(f"stopping: oversize streak {oversize_streak} >= {max_oversize_streak}")
            break
        if spend >= budget:
            print(f"stopping: spend {spend:.3f} >= budget {budget:.3f}")
            break


def cmd_status(paths: dict) -> None:
    manifest = load_current_manifest(paths)
    cycles = read_jsonl(paths["cycles"])
    latest = cycles[-1] if cycles else None
    write_status(paths, manifest, latest)
    print(paths["status"].read_text(encoding="utf-8"))


def find_latest_result_file(model: str, benchmark_stem: str, cheatsheet_label: str) -> Path | None:
    model_norm = scoreboard.normalize_model_for_filename(model)
    pattern = f"sim_{model_norm}_{benchmark_stem}_{cheatsheet_label}_*.json"
    matches = sorted((ROOT / "results").glob(pattern))
    if not matches:
        return None
    return matches[-1]


def load_manifest_from_existing_results(config: dict, cheatsheet_label: str) -> dict | None:
    gate_runs: list[dict] = []
    for stem in FIXED_BENCHMARK_STEMS:
        result_path = find_latest_result_file(config["model"], stem, cheatsheet_label)
        if result_path is None:
            return None
        gate_runs.append(summarize_result(result_path))
    path = ROOT / "cheatsheets" / f"{cheatsheet_label}.txt"
    if not path.exists():
        return None
    return champion_manifest_from_runs(config, path, gate_runs)


def cmd_replay_check(config: dict, paths: dict, cheatsheet_labels: list[str]) -> None:
    baseline_label = Path(config["state"]["authoritative_champion_path"]).stem
    baseline_manifest = load_manifest_from_existing_results(config, baseline_label)
    if baseline_manifest is None:
        raise RuntimeError(
            f"Missing replay inputs for baseline {baseline_label}. Run benchmarks first for all fixed seeds."
        )

    results: list[dict] = []
    for label in cheatsheet_labels:
        cand_manifest = load_manifest_from_existing_results(config, label)
        if cand_manifest is None:
            results.append(
                {
                    "cheatsheet": label,
                    "status": "missing_results",
                    "promoted": False,
                    "wins": 0,
                    "reasons": ["missing one or more fixed-seed result files"],
                }
            )
            continue

        decision = strict_decide(config, baseline_manifest, cand_manifest)
        results.append(
            {
                "cheatsheet": label,
                "status": "evaluated",
                "promoted": decision.promoted,
                "wins": decision.wins,
                "reasons": decision.reasons,
                "aggregate": cand_manifest["aggregate"],
            }
        )

    payload = {
        "timestamp": utc_now(),
        "mode": "strict_replay_check",
        "baseline": baseline_label,
        "model": config["model"],
        "benchmarks": FIXED_BENCHMARK_STEMS,
        "results": results,
    }
    paths["replay_dir"].mkdir(parents=True, exist_ok=True)
    out = paths["replay_dir"] / f"replay_{now_stamp()}.json"
    write_json(out, payload)
    print(f"wrote {rel(out)}")
    print(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="VNext Search V2: strict anti-collapse pipeline")
    parser.add_argument("command", choices=("build-gates", "freeze-legacy", "init", "cycle", "loop", "status", "replay-check"))
    parser.add_argument("--config", default="vnext_search_v2_config.json")
    parser.add_argument("--max-cycles", type=int, default=0)
    parser.add_argument("--max-budget-usd", type=float, default=0.0)
    parser.add_argument("--cheatsheets", default="")
    args = parser.parse_args()

    config = ensure_policy_lock(load_json(ROOT / args.config))
    paths = get_state_paths(config)

    if args.command == "build-gates":
        for p in build_gate_benchmarks(config):
            print(f"wrote {rel(p)}")
    elif args.command == "freeze-legacy":
        cmd_freeze_legacy(config, paths)
    elif args.command == "init":
        cmd_init(config, paths)
    elif args.command == "cycle":
        entry = cmd_cycle(config, paths)
        print(json.dumps({"cycle": entry["cycle_number"], "promoted": entry["promoted"], "wins": entry["wins"]}, indent=2))
    elif args.command == "loop":
        cmd_loop(config, paths, args.max_cycles, args.max_budget_usd)
    elif args.command == "status":
        cmd_status(paths)
    elif args.command == "replay-check":
        labels = [s.strip() for s in args.cheatsheets.split(",") if s.strip()]
        if not labels:
            labels = ["v14_proof_required", "v16_early_false_signal", "v17_corrected"]
        cmd_replay_check(config, paths, labels)


if __name__ == "__main__":
    main()
