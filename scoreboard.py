#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
CSV_PATH = RESULTS_DIR / "scoreboard.csv"
MD_PATH = RESULTS_DIR / "scoreboard.md"
BENCHMARK_DIR = ROOT / "data" / "benchmark"

TIMESTAMP_RE = re.compile(r"_(\d{8}(?:_\d{6})?)$")

PAID_MODEL_PRICING = {
    "google/gemini-2.5-pro": {"label": "Gemini 2.5 Pro", "input_per_m": 0.956, "output_per_m": 10.02},
    "meta-llama/llama-3.3-70b-instruct": {"label": "Llama 3.3 70B", "input_per_m": 0.342, "output_per_m": 0.563},
    "qwen/qwen3.5-122b-a10b": {"label": "Qwen3.5 122B", "input_per_m": 0.384, "output_per_m": 2.88},
}

CHEATSHEET_LABELS = {
    "control_blank": "Control",
    "graph_v10": "Graph V10",
    "graph_v11": "Graph V11",
    "no_cheatsheet_control": "Control",
    "v10_proof_required": "V10",
    "v12_proof_required": "V12",
    "v13_proof_required": "V13",
}

BENCHMARK_ALIASES = {
    "control_blank_balanced100_25x4": "control_balanced100_25x4_seed17",
    "v10_proof_hard20": "control_hard20_seed17",
    "v10_proof_req_v2_hard20": "control_hard20_seed17",
    "v10_proof_req_v3_hard20": "control_hard20_seed17",
    "v10_proof_req_v4_hard20": "control_hard20_seed17",
    "v10_proof_req_v5_hard20": "control_hard20_seed17",
    "v10_proof_req_v6_hard20": "control_hard20_seed17",
}

KNOWN_BENCHMARK_STEMS = {path.stem for path in BENCHMARK_DIR.glob("*.jsonl")}


@dataclass
class ScoreRow:
    result_file: str
    benchmark: str
    benchmark_file: str
    difficulty: str
    model: str
    model_label: str
    cheatsheet: str
    cheatsheet_label: str
    total: int
    accuracy: float
    f1_score: float
    true_accuracy: float
    false_accuracy: float
    parse_success_rate: float
    avg_time_s: float
    estimated_cost_usd: float
    cost_basis: str
    timestamp: str


def normalize_model_for_filename(model: str) -> str:
    return model.replace(":", "_").replace("/", "_")


def normalize_cheatsheet_label(cheatsheet_path: str) -> str:
    if cheatsheet_path == "(none)":
        return "no_cheatsheet_control"
    return Path(cheatsheet_path).stem


def format_cheatsheet_label(cheatsheet: str) -> str:
    return CHEATSHEET_LABELS.get(cheatsheet, cheatsheet)


def format_model_label(model: str) -> str:
    pricing = PAID_MODEL_PRICING.get(model)
    if pricing:
        return pricing["label"]
    return model


def standardize_benchmark_name(benchmark: str) -> str:
    if benchmark in KNOWN_BENCHMARK_STEMS:
        return benchmark
    return BENCHMARK_ALIASES.get(benchmark, benchmark)


def benchmark_filename(benchmark: str) -> str:
    return f"{benchmark}.jsonl"


def infer_benchmark(stem: str, model: str, cheatsheet_path: str) -> str:
    prefix = f"sim_{normalize_model_for_filename(model)}_"
    remainder = stem[len(prefix):] if stem.startswith(prefix) else stem.removeprefix("sim_")
    remainder = TIMESTAMP_RE.sub("", remainder)
    cheatsheet_label = normalize_cheatsheet_label(cheatsheet_path)
    suffix = f"_{cheatsheet_label}"
    if remainder.endswith(suffix):
        remainder = remainder[: -len(suffix)]
    return standardize_benchmark_name(remainder or "unknown")


def infer_difficulty(payload: dict, benchmark: str) -> str:
    result_ids = [item.get("id", "") for item in payload.get("results", []) if item.get("id")]
    prefixes = {result_id.split("_", 1)[0] for result_id in result_ids}
    if len(prefixes) == 1:
        return next(iter(prefixes))

    benchmark_prefix = benchmark.split("_", 1)[0]
    if benchmark_prefix:
        return benchmark_prefix
    return "unknown"


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def render_prompt_text(equation1: str, equation2: str, cheatsheet_text: str) -> str:
    prompt = (
        "You are a mathematician specializing in equational theories of magmas.\n"
        f"Your task is to determine whether Equation 1 ({equation1}) implies Equation 2 ({equation2}) over all magmas.\n"
    )
    if cheatsheet_text:
        prompt += f"{cheatsheet_text}\n"
    prompt += (
        "Output format (use exact headers without any additional text or formatting):\n"
        "VERDICT: must be exactly TRUE or FALSE (in the same line).\n"
        "REASONING: must be non-empty.\n"
        "PROOF: required if VERDICT is TRUE, empty otherwise.\n"
        "COUNTEREXAMPLE: required if VERDICT is FALSE, empty otherwise.\n"
    )
    return prompt


def load_cheatsheet_text(cheatsheet_path: str) -> str:
    if not cheatsheet_path or cheatsheet_path == "(none)":
        return ""
    path = ROOT / cheatsheet_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def normalize_usage_counts(usage: dict | None) -> tuple[int, int]:
    if not usage:
        return 0, 0
    prompt_tokens = int(
        usage.get("prompt_tokens")
        or usage.get("input_tokens")
        or usage.get("promptTokens")
        or 0
    )
    completion_tokens = int(
        usage.get("completion_tokens")
        or usage.get("output_tokens")
        or usage.get("completionTokens")
        or 0
    )
    return prompt_tokens, completion_tokens


def estimate_run_cost(payload: dict) -> tuple[float, str]:
    pricing = PAID_MODEL_PRICING.get(payload["model"])
    if not pricing:
        return 0.0, "n/a"

    prompt_tokens = 0
    completion_tokens = 0
    exact_usage = False

    summary_prompt_tokens = int(payload.get("summary", {}).get("prompt_tokens", 0) or 0)
    summary_completion_tokens = int(payload.get("summary", {}).get("completion_tokens", 0) or 0)
    if summary_prompt_tokens or summary_completion_tokens:
        prompt_tokens = summary_prompt_tokens
        completion_tokens = summary_completion_tokens
        exact_usage = True
    else:
        cheatsheet_text = load_cheatsheet_text(payload.get("cheatsheet", ""))
        for result in payload.get("results", []):
            usage_prompt_tokens, usage_completion_tokens = normalize_usage_counts(result.get("usage"))
            if usage_prompt_tokens or usage_completion_tokens:
                prompt_tokens += usage_prompt_tokens
                completion_tokens += usage_completion_tokens
                exact_usage = True
                continue
            prompt_tokens += estimate_tokens(
                render_prompt_text(
                    result.get("equation1", ""),
                    result.get("equation2", ""),
                    cheatsheet_text,
                )
            )
            completion_tokens += estimate_tokens(result.get("raw_response", ""))

    cost = (
        (prompt_tokens / 1_000_000) * pricing["input_per_m"]
        + (completion_tokens / 1_000_000) * pricing["output_per_m"]
    )
    return cost, "exact" if exact_usage else "estimated"


def parse_result_file(path: Path) -> ScoreRow:
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload["summary"]
    benchmark = infer_benchmark(path.stem, payload["model"], payload["cheatsheet"])
    estimated_cost_usd, cost_basis = estimate_run_cost(payload)
    total = summary["total"]
    unparsed = summary.get("unparsed", 0)
    parse_success_rate = summary.get("parse_success_rate")
    if parse_success_rate is None:
        parse_success_rate = (total - unparsed) / total if total else 0.0
    return ScoreRow(
        result_file=path.name,
        benchmark=benchmark,
        benchmark_file=benchmark_filename(benchmark),
        difficulty=infer_difficulty(payload, benchmark),
        model=payload["model"],
        model_label=format_model_label(payload["model"]),
        cheatsheet=normalize_cheatsheet_label(payload["cheatsheet"]),
        cheatsheet_label=format_cheatsheet_label(normalize_cheatsheet_label(payload["cheatsheet"])),
        total=total,
        accuracy=summary["accuracy"],
        f1_score=summary.get("f1_score", summary.get("f1", 0.0)),
        true_accuracy=summary["true_accuracy"],
        false_accuracy=summary["false_accuracy"],
        parse_success_rate=parse_success_rate,
        avg_time_s=summary["avg_time_s"],
        estimated_cost_usd=estimated_cost_usd,
        cost_basis=cost_basis,
        timestamp=payload["timestamp"],
    )


def load_rows() -> list[ScoreRow]:
    rows = [parse_result_file(path) for path in sorted(RESULTS_DIR.glob("sim_*.json"))]
    rows = [row for row in rows if row.model in PAID_MODEL_PRICING]
    rows.sort(key=lambda row: (row.benchmark, row.model_label, row.cheatsheet_label, row.timestamp))
    return rows


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_seconds(value: float) -> str:
    return f"{value:.2f}"


def format_cost(value: float) -> str:
    return f"${value:.3f}"


def write_csv(rows: list[ScoreRow]) -> None:
    fieldnames = [
        "benchmark",
        "benchmark_file",
        "difficulty",
        "model",
        "model_label",
        "cheatsheet",
        "cheatsheet_label",
        "total",
        "accuracy",
        "f1_score",
        "true_accuracy",
        "false_accuracy",
        "parse_success_rate",
        "avg_time_s",
        "estimated_cost_usd",
        "cost_basis",
        "timestamp",
    ]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "benchmark": row.benchmark,
                    "benchmark_file": row.benchmark_file,
                    "difficulty": row.difficulty,
                    "model": row.model,
                    "model_label": row.model_label,
                    "cheatsheet": row.cheatsheet,
                    "cheatsheet_label": row.cheatsheet_label,
                    "total": row.total,
                    "accuracy": f"{row.accuracy:.4f}",
                    "f1_score": f"{row.f1_score:.4f}",
                    "true_accuracy": f"{row.true_accuracy:.4f}",
                    "false_accuracy": f"{row.false_accuracy:.4f}",
                    "parse_success_rate": f"{row.parse_success_rate:.4f}",
                    "avg_time_s": f"{row.avg_time_s:.2f}",
                    "estimated_cost_usd": f"{row.estimated_cost_usd:.6f}",
                    "cost_basis": row.cost_basis,
                    "timestamp": row.timestamp,
                }
            )


def best_rows_by_benchmark_model(rows: list[ScoreRow]) -> list[ScoreRow]:
    groups: dict[tuple[str, str], list[ScoreRow]] = defaultdict(list)
    for row in rows:
        groups[(row.benchmark, row.model)].append(row)

    best_rows: list[ScoreRow] = []
    for key in sorted(groups):
        ranked = sorted(
            groups[key],
            key=lambda row: (
                row.f1_score,
                row.accuracy,
                row.true_accuracy,
                row.false_accuracy,
                row.parse_success_rate,
                -row.estimated_cost_usd,
                -row.avg_time_s,
                row.timestamp,
            ),
            reverse=True,
        )
        best_rows.append(ranked[0])
    return best_rows


def best_overall_row(rows: list[ScoreRow]) -> ScoreRow | None:
    if not rows:
        return None
    return max(
        rows,
        key=lambda row: (
            row.f1_score,
            row.accuracy,
            row.true_accuracy,
            row.false_accuracy,
            row.parse_success_rate,
            -row.estimated_cost_usd,
            -row.avg_time_s,
        ),
    )


def cheapest_row(rows: list[ScoreRow]) -> ScoreRow | None:
    if not rows:
        return None
    return min(rows, key=lambda row: (row.estimated_cost_usd, -row.f1_score, -row.accuracy, row.avg_time_s))


def fastest_row(rows: list[ScoreRow]) -> ScoreRow | None:
    if not rows:
        return None
    return min(rows, key=lambda row: (row.avg_time_s, row.estimated_cost_usd, -row.f1_score))


def append_run_table(lines: list[str], rows: list[ScoreRow], include_timestamp: bool) -> None:
    if include_timestamp:
        lines.extend(
            [
                "| Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost | Timestamp |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for row in rows:
            lines.append(
                "| {model} | {cheatsheet} | {total} | {accuracy} | {f1_score} | {true_accuracy} | {false_accuracy} | {parse_success_rate} | {avg_time_s} | {cost} | {timestamp} |".format(
                    model=row.model_label,
                    cheatsheet=row.cheatsheet_label,
                    total=row.total,
                    accuracy=format_pct(row.accuracy),
                    f1_score=format_pct(row.f1_score),
                    true_accuracy=format_pct(row.true_accuracy),
                    false_accuracy=format_pct(row.false_accuracy),
                    parse_success_rate=format_pct(row.parse_success_rate),
                    avg_time_s=format_seconds(row.avg_time_s),
                    cost=format_cost(row.estimated_cost_usd),
                    timestamp=row.timestamp,
                )
            )
        return

    lines.extend(
        [
            "| Benchmark File | Difficulty | Model | Prompt | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Cost |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            "| {benchmark_file} | {difficulty} | {model} | {cheatsheet} | {total} | {accuracy} | {f1_score} | {true_accuracy} | {false_accuracy} | {parse_success_rate} | {avg_time_s} | {cost} |".format(
                benchmark_file=row.benchmark_file,
                difficulty=row.difficulty,
                model=row.model_label,
                cheatsheet=row.cheatsheet_label,
                total=row.total,
                accuracy=format_pct(row.accuracy),
                f1_score=format_pct(row.f1_score),
                true_accuracy=format_pct(row.true_accuracy),
                false_accuracy=format_pct(row.false_accuracy),
                parse_success_rate=format_pct(row.parse_success_rate),
                avg_time_s=format_seconds(row.avg_time_s),
                cost=format_cost(row.estimated_cost_usd),
            )
        )


def build_markdown(rows: list[ScoreRow]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    best_row = best_overall_row(rows)
    cheapest = cheapest_row(rows)
    fastest = fastest_row(rows)
    unique_benchmarks = sorted({row.benchmark_file for row in rows})
    best_rows = best_rows_by_benchmark_model(rows)

    lines = [
        "# Paid Model Scoreboard",
        "",
        f"Generated: {generated_at}",
        f"Runs indexed: {len(rows)}",
        f"Benchmarks indexed: {len(unique_benchmarks)}",
        f"Models indexed: {len({row.model for row in rows})}",
        "",
        "Paid-model runs only. Local/free runs are excluded from this view.",
        "Cost is exact when token usage was saved in the run JSON; otherwise it is reconstructed from the prompt/response text and priced with current OpenRouter weighted-average input/output rates.",
        "",
        "## Pricing Basis",
        "",
        "| Model | Input $/1M | Output $/1M |",
        "| --- | ---: | ---: |",
    ]

    for model, pricing in PAID_MODEL_PRICING.items():
        lines.append(
            f"| {pricing['label']} | {format_cost(pricing['input_per_m'])} | {format_cost(pricing['output_per_m'])} |"
        )

    lines.extend([
        "",
        "## Highlights",
        "",
        "| View | Run |",
        "| --- | --- |",
    ])

    if best_row is not None:
        lines.append(
            f"| Best overall | {best_row.model_label} on {best_row.benchmark_file} with {best_row.cheatsheet_label} · F1 {format_pct(best_row.f1_score)} · Acc {format_pct(best_row.accuracy)} · Cost {format_cost(best_row.estimated_cost_usd)} |"
        )
    if cheapest is not None:
        lines.append(
            f"| Lowest cost | {cheapest.model_label} on {cheapest.benchmark_file} with {cheapest.cheatsheet_label} · Cost {format_cost(cheapest.estimated_cost_usd)} · F1 {format_pct(cheapest.f1_score)} |"
        )
    if fastest is not None:
        lines.append(
            f"| Fastest avg time | {fastest.model_label} on {fastest.benchmark_file} with {fastest.cheatsheet_label} · Avg {format_seconds(fastest.avg_time_s)}s · F1 {format_pct(fastest.f1_score)} |"
        )

    lines.extend([
        "",
        "## Best By Benchmark And Model",
        "",
    ])
    append_run_table(lines, best_rows, include_timestamp=False)

    lines.extend([
        "",
        "## All Paid Runs By Benchmark",
    ])

    grouped_rows: dict[str, list[ScoreRow]] = defaultdict(list)
    for row in rows:
        grouped_rows[row.benchmark_file].append(row)

    for benchmark_file in sorted(grouped_rows):
        benchmark_rows = sorted(
            grouped_rows[benchmark_file],
            key=lambda row: (
                row.f1_score,
                row.accuracy,
                row.true_accuracy,
                row.false_accuracy,
                row.parse_success_rate,
                -row.estimated_cost_usd,
                -row.avg_time_s,
                row.timestamp,
            ),
            reverse=True,
        )
        lines.extend(["", f"### {benchmark_file}", ""])
        append_run_table(lines, benchmark_rows, include_timestamp=True)

    return "\n".join(lines) + "\n"


def write_markdown(rows: list[ScoreRow]) -> None:
    MD_PATH.write_text(build_markdown(rows), encoding="utf-8")


def main() -> None:
    rows = load_rows()
    write_csv(rows)
    write_markdown(rows)
    print(f"Wrote {CSV_PATH}")
    print(f"Wrote {MD_PATH}")
    print(f"Indexed {len(rows)} run files")


if __name__ == "__main__":
    main()