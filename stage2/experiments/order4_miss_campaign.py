#!/usr/bin/env python3
"""Build and summarize the frozen historical order-4 miss ledger.

The campaign reports under ``stage2/results`` are intentionally gitignored raw
measurement artifacts.  This helper turns their seven failure ledgers into one
stable, deduplicated manifest suitable for ``audit_corpus.py --file``.  It is a
diagnostic tool only: row ids and labels never enter solver policy.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "stage2" / "results"

LEDGERS = (
    RESULTS_DIR / "etp-sample-failures-2026-08-20.jsonl",
    RESULTS_DIR / "order4-2026-08-25-ALL-failures.jsonl",
    RESULTS_DIR / "etp-sweep-200k-2026-08-26-ALL-failures.jsonl",
    RESULTS_DIR / "etp-sweep-200k-2026-08-27-ALL-failures.jsonl",
    RESULTS_DIR / "etp-sweep-20260829-100k-failures.jsonl",
    RESULTS_DIR / "etp-sweep-20260829-200k-failures.jsonl",
    RESULTS_DIR / "etp-sweep-20260829-100k-b31-b40-failures.jsonl",
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: expected a JSON object")
            rows.append(row)
    return rows


def frozen_union() -> tuple[list[dict[str, Any]], dict[str, int]]:
    by_id: dict[str, dict[str, Any]] = {}
    ledger_counts: dict[str, int] = {}
    identity_fields = ("eq1_id", "eq2_id", "equation1", "equation2", "label")

    for path in LEDGERS:
        if not path.is_file():
            raise FileNotFoundError(f"missing campaign ledger: {path}")
        rows = read_jsonl(path)
        ledger_counts[path.name] = len(rows)
        for source_row in rows:
            row = dict(source_row)
            # The 2026-08-20 ledger predates the sweep reporter's ``label``
            # field and carries ``answer`` instead.  Newer ledgers do the
            # reverse.  Preserve both so audit_corpus performs its independent
            # label/verdict cross-check on every historical row.
            if "label" not in row and isinstance(row.get("answer"), bool):
                row["label"] = "true" if row["answer"] else "false"
            if "answer" not in row and row.get("label") in {"true", "false"}:
                row["answer"] = row["label"] == "true"
            if "seconds" not in row and "deterministic_seconds" in row:
                row["seconds"] = row["deterministic_seconds"]
            row_id = str(row.get("id", ""))
            if not row_id:
                raise ValueError(f"{path}: row without id")
            previous = by_id.get(row_id)
            if previous is not None:
                disagreements = [
                    field
                    for field in identity_fields
                    if previous.get(field) != row.get(field)
                ]
                if disagreements:
                    raise ValueError(
                        f"conflicting duplicate {row_id}: {', '.join(disagreements)}"
                    )
                previous.setdefault("campaign_ledgers", []).append(path.name)
                previous["seconds"] = max(
                    float(previous.get("seconds", 0.0)),
                    float(row.get("seconds", 0.0)),
                )
                continue
            row["campaign_ledgers"] = [path.name]
            by_id[row_id] = row

    def row_key(row: dict[str, Any]) -> tuple[int, int, str]:
        return (
            int(row.get("eq1_id", -1)),
            int(row.get("eq2_id", -1)),
            str(row["id"]),
        )

    return sorted(by_id.values(), key=row_key), ledger_counts


def summarize(rows: list[dict[str, Any]], ledger_counts: dict[str, int]) -> dict[str, Any]:
    labels = Counter(str(row.get("label", "unknown")) for row in rows)
    families = Counter(int(row.get("eq1_id", -1)) for row in rows)
    duplicate_memberships = sum(
        max(0, len(row.get("campaign_ledgers", ())) - 1) for row in rows
    )
    return {
        "ledger_rows": sum(ledger_counts.values()),
        "unique_rows": len(rows),
        "duplicate_memberships": duplicate_memberships,
        "labels": dict(sorted(labels.items())),
        "ledger_counts": ledger_counts,
        "top_eq1_families": [
            {"eq1_id": eq1_id, "count": count}
            for eq1_id, count in families.most_common(30)
        ],
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        help="optional output JSONL path for the frozen deduplicated manifest",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        help="optional output path for the machine-readable summary JSON",
    )
    parser.add_argument(
        "--eq1-ids",
        default="",
        help="optional comma-separated diagnostic family filter",
    )
    parser.add_argument("--label", choices=("true", "false"))
    parser.add_argument(
        "--per-family",
        type=int,
        default=0,
        help="take this many rows from each selected eq1 family before --limit",
    )
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    rows, ledger_counts = frozen_union()
    selected_ids = {
        int(value) for value in args.eq1_ids.split(",") if value.strip()
    }
    if selected_ids:
        rows = [row for row in rows if int(row.get("eq1_id", -1)) in selected_ids]
    if args.label:
        rows = [row for row in rows if row.get("label") == args.label]
    if args.per_family > 0:
        family_counts: Counter[int] = Counter()
        balanced: list[dict[str, Any]] = []
        for row in rows:
            family = int(row.get("eq1_id", -1))
            if family_counts[family] >= args.per_family:
                continue
            family_counts[family] += 1
            balanced.append(row)
        rows = balanced
    if args.limit is not None:
        rows = rows[: args.limit]
    summary = summarize(rows, ledger_counts)
    if args.out:
        output = args.out if args.out.is_absolute() else REPO_ROOT / args.out
        write_jsonl(output, rows)
        summary["manifest"] = str(output.relative_to(REPO_ROOT))
    if args.summary_out:
        output = (
            args.summary_out
            if args.summary_out.is_absolute()
            else REPO_ROOT / args.summary_out
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
