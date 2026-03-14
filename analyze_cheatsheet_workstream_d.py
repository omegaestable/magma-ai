"""Workstream D analysis for cheatsheet optimization.

Computes:
- true on-disk cheatsheet byte usage
- singleton-equivalent equation membership and compact range encoding
- coverage ranking for the repo's known small counterexample magmas
- landmark behavior tags for concise cheatsheet annotations
"""

from __future__ import annotations

import json
import csv
from pathlib import Path

from analyze_equations import check_magma, get_vars, load_equations, parse_equation
from config import CHEATSHEET_FILE, RAW_IMPL_CSV, RESULTS_DIR
from magma_search import KNOWN_MAGMAS


LANDMARKS = {
    3: "idem",
    4: "left0",
    5: "right0",
    43: "comm",
    4512: "assoc",
}


def is_singleton_equivalent(eq_str: str) -> bool:
    lhs, rhs = parse_equation(eq_str)
    vars_l = get_vars(lhs)
    vars_r = get_vars(rhs)
    if vars_l & vars_r:
        return False
    return not isinstance(lhs, str) or not isinstance(rhs, str)


def encode_ranges(indices: list[int]) -> str:
    if not indices:
        return ""
    ranges: list[str] = []
    start = prev = indices[0]
    for value in indices[1:]:
        if value == prev + 1:
            prev = value
            continue
        ranges.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = value
    ranges.append(str(start) if start == prev else f"{start}-{prev}")
    return ",".join(ranges)


def exact_singleton_class() -> list[int]:
    singleton_indices: list[int] = []
    row2: list[int] | None = None
    col2: list[int] = []

    with open(RAW_IMPL_CSV, "r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row_idx, row in enumerate(reader, start=1):
            if row_idx == 2:
                row2 = [int(value) for value in row]
            col2.append(int(row[1]))

    if row2 is None:
        raise RuntimeError("Could not load Equation 2 row from dense implication matrix")

    for eq_idx, (from_eq2, to_eq2) in enumerate(zip(row2, col2), start=1):
        if eq_idx == 2:
            singleton_indices.append(eq_idx)
            continue
        if from_eq2 > 0 and to_eq2 > 0:
            singleton_indices.append(eq_idx)
    return singleton_indices


def landmark_tags(table: list[list[int]], parsed_landmarks: dict[int, tuple]) -> list[str]:
    tags: list[str] = []
    for eq_idx, label in LANDMARKS.items():
        if check_magma(parsed_landmarks[eq_idx], table):
            tags.append(label)
    return tags


def magma_rows(equations: list[str]) -> list[dict]:
    parsed_equations = [parse_equation(eq) for eq in equations]
    parsed_landmarks = {eq_idx: parsed_equations[eq_idx - 1] for eq_idx in LANDMARKS}
    rows: list[dict] = []
    total_equations = len(parsed_equations)
    for name, table in KNOWN_MAGMAS.items():
        satisfied = [idx for idx, eq in enumerate(parsed_equations, start=1) if check_magma(eq, table)]
        sat_count = len(satisfied)
        rows.append(
            {
                "name": name,
                "size": len(table),
                "sat_count": sat_count,
                "unsat_count": total_equations - sat_count,
                "ordered_pairs": sat_count * (total_equations - sat_count),
                "tags": landmark_tags(table, parsed_landmarks),
                "table": table,
            }
        )
    rows.sort(key=lambda row: (-row["ordered_pairs"], row["size"], row["name"]))
    return rows


def main() -> None:
    equations = load_equations()
    cs_bytes = Path(CHEATSHEET_FILE).read_bytes()
    singleton_by_criterion = [
        2,
        *[
            idx
            for idx, eq in enumerate(equations, start=1)
            if idx != 2 and is_singleton_equivalent(eq)
        ],
    ]
    singleton_indices = exact_singleton_class()
    rows = magma_rows(equations)

    payload = {
        "cheatsheet_bytes": len(cs_bytes),
        "cheatsheet_remaining": 10240 - len(cs_bytes),
        "singleton_count": len(singleton_indices),
        "singleton_ranges": encode_ranges(singleton_indices),
        "singleton_criterion_count": len(singleton_by_criterion),
        "singleton_first_80": singleton_indices[:80],
        "top_magmas": rows[:20],
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "workstream_d_analysis.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()