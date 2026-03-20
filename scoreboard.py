#!/usr/bin/env python3

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
CSV_PATH = RESULTS_DIR / "scoreboard.csv"
MD_PATH = RESULTS_DIR / "scoreboard.md"

TIMESTAMP_RE = re.compile(r"_(\d{8}(?:_\d{6})?)$")


@dataclass
class ScoreRow:
    result_file: str
    benchmark: str
    difficulty: str
    model: str
    cheatsheet: str
    total: int
    accuracy: float
    f1_score: float
    true_accuracy: float
    false_accuracy: float
    parse_success_rate: float
    avg_time_s: float
    timestamp: str


def normalize_model_for_filename(model: str) -> str:
    return model.replace(":", "_").replace("/", "_")


def normalize_cheatsheet_label(cheatsheet_path: str) -> str:
    if cheatsheet_path == "(none)":
        return "no_cheatsheet_control"
    return Path(cheatsheet_path).stem


def infer_benchmark(stem: str, model: str, cheatsheet_path: str) -> str:
    prefix = f"sim_{normalize_model_for_filename(model)}_"
    remainder = stem[len(prefix):] if stem.startswith(prefix) else stem.removeprefix("sim_")
    remainder = TIMESTAMP_RE.sub("", remainder)
    cheatsheet_label = normalize_cheatsheet_label(cheatsheet_path)
    suffix = f"_{cheatsheet_label}"
    if remainder.endswith(suffix):
        remainder = remainder[: -len(suffix)]
    return remainder or "unknown"


def infer_difficulty(payload: dict, benchmark: str) -> str:
    result_ids = [item.get("id", "") for item in payload.get("results", []) if item.get("id")]
    prefixes = {result_id.split("_", 1)[0] for result_id in result_ids}
    if len(prefixes) == 1:
        return next(iter(prefixes))

    benchmark_prefix = benchmark.split("_", 1)[0]
    if benchmark_prefix:
        return benchmark_prefix
    return "unknown"


def parse_result_file(path: Path) -> ScoreRow:
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload["summary"]
    benchmark = infer_benchmark(path.stem, payload["model"], payload["cheatsheet"])
    total = summary["total"]
    unparsed = summary.get("unparsed", 0)
    parse_success_rate = summary.get("parse_success_rate")
    if parse_success_rate is None:
        parse_success_rate = (total - unparsed) / total if total else 0.0
    return ScoreRow(
        result_file=path.name,
        benchmark=benchmark,
        difficulty=infer_difficulty(payload, benchmark),
        model=payload["model"],
        cheatsheet=normalize_cheatsheet_label(payload["cheatsheet"]),
        total=total,
        accuracy=summary["accuracy"],
        f1_score=summary.get("f1_score", summary.get("f1", 0.0)),
        true_accuracy=summary["true_accuracy"],
        false_accuracy=summary["false_accuracy"],
        parse_success_rate=parse_success_rate,
        avg_time_s=summary["avg_time_s"],
        timestamp=payload["timestamp"],
    )


def load_rows() -> list[ScoreRow]:
    rows = [parse_result_file(path) for path in sorted(RESULTS_DIR.glob("sim_*.json"))]
    rows.sort(key=lambda row: (row.benchmark, row.model, row.cheatsheet, row.timestamp))
    return rows


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_seconds(value: float) -> str:
    return f"{value:.2f}"


def write_csv(rows: list[ScoreRow]) -> None:
    fieldnames = [
        "benchmark",
        "difficulty",
        "model",
        "cheatsheet",
        "total",
        "accuracy",
        "f1_score",
        "true_accuracy",
        "false_accuracy",
        "parse_success_rate",
        "avg_time_s",
        "timestamp",
        "result_file",
    ]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "benchmark": row.benchmark,
                    "difficulty": row.difficulty,
                    "model": row.model,
                    "cheatsheet": row.cheatsheet,
                    "total": row.total,
                    "accuracy": f"{row.accuracy:.4f}",
                    "f1_score": f"{row.f1_score:.4f}",
                    "true_accuracy": f"{row.true_accuracy:.4f}",
                    "false_accuracy": f"{row.false_accuracy:.4f}",
                    "parse_success_rate": f"{row.parse_success_rate:.4f}",
                    "avg_time_s": f"{row.avg_time_s:.2f}",
                    "timestamp": row.timestamp,
                    "result_file": row.result_file,
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
                -row.avg_time_s,
                row.timestamp,
            ),
            reverse=True,
        )
        best_rows.append(ranked[0])
    return best_rows


def build_markdown(rows: list[ScoreRow]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Experiment Scoreboard",
        "",
        f"Generated: {generated_at}",
        f"Runs indexed: {len(rows)}",
        "",
        "## Best By Benchmark And Model",
        "",
        "| Benchmark | Difficulty | Model | Cheatsheet | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Result |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]

    for row in best_rows_by_benchmark_model(rows):
        lines.append(
            "| {benchmark} | {difficulty} | {model} | {cheatsheet} | {total} | {accuracy} | {f1_score} | {true_accuracy} | {false_accuracy} | {parse_success_rate} | {avg_time_s} | {result_file} |".format(
                benchmark=row.benchmark,
                difficulty=row.difficulty,
                model=row.model,
                cheatsheet=row.cheatsheet,
                total=row.total,
                accuracy=format_pct(row.accuracy),
                f1_score=format_pct(row.f1_score),
                true_accuracy=format_pct(row.true_accuracy),
                false_accuracy=format_pct(row.false_accuracy),
                parse_success_rate=format_pct(row.parse_success_rate),
                avg_time_s=format_seconds(row.avg_time_s),
                result_file=row.result_file,
            )
        )

    lines.extend(
        [
            "",
            "## All Runs",
            "",
            "| Benchmark | Difficulty | Model | Cheatsheet | N | Acc | F1 | T Acc | F Acc | Parse | Avg s | Timestamp | Result |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )

    for row in rows:
        lines.append(
            "| {benchmark} | {difficulty} | {model} | {cheatsheet} | {total} | {accuracy} | {f1_score} | {true_accuracy} | {false_accuracy} | {parse_success_rate} | {avg_time_s} | {timestamp} | {result_file} |".format(
                benchmark=row.benchmark,
                difficulty=row.difficulty,
                model=row.model,
                cheatsheet=row.cheatsheet,
                total=row.total,
                accuracy=format_pct(row.accuracy),
                f1_score=format_pct(row.f1_score),
                true_accuracy=format_pct(row.true_accuracy),
                false_accuracy=format_pct(row.false_accuracy),
                parse_success_rate=format_pct(row.parse_success_rate),
                avg_time_s=format_seconds(row.avg_time_s),
                timestamp=row.timestamp,
                result_file=row.result_file,
            )
        )

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