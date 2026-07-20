#!/usr/bin/env python3
"""Build the leakage-audited 100-TRUE/50-FALSE Hugging Face fixture.

The solver-visible manifests omit ``answer``.  Matching labeled manifests and
one deterministic metadata file retain labels, provenance, exclusions, and
hashes for analysis.  Selection uses SHA-256 ranking instead of interpreter-
specific pseudo-random sampling.  Exposure discovery reads tracked analysis
roots plus a pinned ID-only snapshot; it never depends on generated tmp output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
HF_CACHE = REPO_ROOT / "data" / "hf_cache"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "tmp_stage2_smoke" / "2026-07-17-hf150-baseline"
EXPOSURE_SNAPSHOT = REPO_ROOT / "stage2" / "experiments" / "hf150_exposure_snapshot_2026-07-17.json"

AUDITED_REPO_HEAD = "b90fa579ff62d6b0c4fe165b73180efbe9dc2a8b"
DEFAULT_SALT = f"sair-stage2-hf150|2026-07-17|{AUDITED_REPO_HEAD}"
EXPECTED_COMBINED_ID_SHA256 = "903c2e1aa23b579639379e540d325f00b05e58f86e01d1adb1f8ee4eebcf778a"
EXPECTED_EXPOSURE_ID_SHA256 = "81963b3186ab5e24cff523cf85b24af27c27d5c15ad48f4443f12b15c42174d0"
EXPECTED_EXPOSURE_SNAPSHOT_SHA256 = "78d9c3bc674f717d0d4b494ee52d2ed1fe69b8969418af51fad63d14effa8e0c"
EXPECTED_SOURCE_SHA256 = {
    "evaluation_hard": "5dcef7a57e3a6500247b92bd671d60032f6fe0d397d5388b85f4ebf4d9288213",
    "evaluation_order5": "040016d463efdff41625bffda2c4bfbba0caa093fa5936b42c232ccf1ab104f2",
}

SOURCE_ORDER = ("evaluation_hard", "evaluation_order5")
ALL_EVALUATION_SOURCES = (
    "evaluation_normal",
    "evaluation_hard",
    "evaluation_extra_hard",
    "evaluation_order5",
)
SELECTION_QUOTAS = {
    ("evaluation_hard", True): 34,
    ("evaluation_hard", False): 17,
    ("evaluation_order5", True): 66,
    ("evaluation_order5", False): 33,
}
HOLDOUT_QUOTAS = {
    ("evaluation_hard", True): 7,
    ("evaluation_hard", False): 3,
    ("evaluation_order5", True): 13,
    ("evaluation_order5", False): 7,
}
DISCOVERY_SHARD_QUOTAS = (
    {
        ("evaluation_hard", True): 9,
        ("evaluation_hard", False): 5,
        ("evaluation_order5", True): 18,
        ("evaluation_order5", False): 8,
    },
    {
        ("evaluation_hard", True): 9,
        ("evaluation_hard", False): 5,
        ("evaluation_order5", True): 18,
        ("evaluation_order5", False): 8,
    },
    {
        ("evaluation_hard", True): 9,
        ("evaluation_hard", False): 4,
        ("evaluation_order5", True): 17,
        ("evaluation_order5", False): 10,
    },
)

REQUIRED_KEYS = {
    "id",
    "index",
    "difficulty",
    "eq1_id",
    "eq2_id",
    "equation1",
    "equation2",
    "answer",
}
EXPOSURE_ROOTS = (
    REPO_ROOT / "stage2" / "docs",
    REPO_ROOT / "stage2" / "results",
    REPO_ROOT / "stage2" / "fixtures",
    REPO_ROOT / "stage2" / "experiments",
    REPO_ROOT / "theory",
)
EXPOSURE_SUFFIXES = {".md", ".json", ".jsonl", ".py", ".log", ".txt"}
ORDERED_ID_HASH_SEPARATOR = "\\n"
RANK_SEPARATOR = "\\0"
EXPOSURE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(?:"
    + "|".join(re.escape(name) for name in ALL_EVALUATION_SOURCES)
    + r")_[0-9]{4}(?![0-9])"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def ordered_id_sha256(rows_or_ids: list[dict[str, Any]] | list[str]) -> str:
    if rows_or_ids and isinstance(rows_or_ids[0], dict):
        ids = [str(item["id"]) for item in rows_or_ids]
    else:
        ids = [str(item) for item in rows_or_ids]
    payload = ORDERED_ID_HASH_SEPARATOR.join(ids) + ORDERED_ID_HASH_SEPARATOR
    return sha256_bytes(payload.encode("utf-8"))


def repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: expected a JSON object")
        rows.append(row)
    return rows


def validate_source_rows(source: str, rows: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for index, row in enumerate(rows, 1):
        missing = REQUIRED_KEYS - set(row)
        if missing:
            raise ValueError(f"{source}: row {index} missing keys {sorted(missing)}")
        row_id = row["id"]
        if not isinstance(row_id, str) or not row_id:
            raise ValueError(f"{source}: row {index} has invalid id")
        if row_id in seen:
            raise ValueError(f"{source}: duplicate id {row_id}")
        seen.add(row_id)
        if not isinstance(row["answer"], bool):
            raise ValueError(f"{source}: {row_id} has a non-boolean answer")


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def load_exposure_snapshot() -> set[str]:
    actual_sha256 = sha256_file(EXPOSURE_SNAPSHOT)
    if actual_sha256 != EXPECTED_EXPOSURE_SNAPSHOT_SHA256:
        raise ValueError(
            "exposure snapshot hash drift: "
            f"expected {EXPECTED_EXPOSURE_SNAPSHOT_SHA256}, found {actual_sha256}"
        )
    payload = json.loads(EXPOSURE_SNAPSHOT.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("exposure snapshot has an unsupported schema")
    indices = payload.get("indices")
    if not isinstance(indices, dict) or set(indices) != set(ALL_EVALUATION_SOURCES):
        raise ValueError("exposure snapshot sources do not match the audited evaluation sources")

    exposed: set[str] = set()
    for source in ALL_EVALUATION_SOURCES:
        source_indices = indices[source]
        if not isinstance(source_indices, list):
            raise ValueError(f"exposure snapshot {source} indices must be a list")
        for index in source_indices:
            if isinstance(index, bool) or not isinstance(index, int) or not 0 < index < 10_000:
                raise ValueError(f"exposure snapshot {source} has invalid index {index!r}")
            row_id = f"{source}_{index:04d}"
            if row_id in exposed:
                raise ValueError(f"exposure snapshot contains duplicate id {row_id}")
            exposed.add(row_id)
    return exposed


def scan_exposed_ids(output_root: Path) -> tuple[set[str], dict[str, list[str]]]:
    exposed = load_exposure_snapshot()
    for root in EXPOSURE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in EXPOSURE_SUFFIXES:
                continue
            if is_within(path, output_root):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            exposed.update(match.group(0) for match in EXPOSURE_PATTERN.finditer(text))

    by_source = {
        source: sorted(row_id for row_id in exposed if row_id.startswith(f"{source}_"))
        for source in ALL_EVALUATION_SOURCES
    }
    return exposed, by_source


def stable_rank(salt: str, tag: str, row: dict[str, Any]) -> bytes:
    payload = f"{salt}{RANK_SEPARATOR}{tag}{RANK_SEPARATOR}{row['id']}".encode("utf-8")
    return hashlib.sha256(payload).digest()


def sorted_by_rank(rows: list[dict[str, Any]], salt: str, tag: str) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: stable_rank(salt, tag, row))


def label_name(value: bool) -> str:
    return "true" if value else "false"


def count_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_source: Counter[str] = Counter()
    by_stratum: Counter[str] = Counter()
    for row in rows:
        source = str(row["id"]).rsplit("_", 1)[0]
        by_source[source] += 1
        by_stratum[f"{source}:{label_name(bool(row['answer']))}"] += 1
    return {
        "rows": len(rows),
        "true": sum(row["answer"] is True for row in rows),
        "false": sum(row["answer"] is False for row in rows),
        "by_source": dict(sorted(by_source.items())),
        "by_stratum": dict(sorted(by_stratum.items())),
        "ordered_id_sha256": ordered_id_sha256(rows),
        "ids": [row["id"] for row in rows],
    }


def without_answer(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key != "answer"}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def write_manifest_pair(
    output_root: Path,
    stem: str,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    labeled_path = output_root / f"{stem}.labeled.jsonl"
    runner_path = output_root / f"{stem}.runner.jsonl"
    write_jsonl(labeled_path, rows)
    write_jsonl(runner_path, [without_answer(row) for row in rows])
    return {
        "labeled": repo_path(labeled_path),
        "labeled_sha256": sha256_file(labeled_path),
        "runner": repo_path(runner_path),
        "runner_sha256": sha256_file(runner_path),
        **count_rows(rows),
    }


def allocate_discovery_shards(
    discovery: list[dict[str, Any]],
    salt: str,
) -> list[list[dict[str, Any]]]:
    shards: list[list[dict[str, Any]]] = [[] for _ in DISCOVERY_SHARD_QUOTAS]
    for source in SOURCE_ORDER:
        for answer in (True, False):
            pool = [
                row
                for row in discovery
                if str(row["id"]).startswith(f"{source}_") and row["answer"] is answer
            ]
            pool = sorted_by_rank(pool, salt, f"discovery-shard|{source}|{answer}")
            offset = 0
            for shard_index, quotas in enumerate(DISCOVERY_SHARD_QUOTAS):
                count = quotas[(source, answer)]
                shards[shard_index].extend(pool[offset : offset + count])
                offset += count
            if offset != len(pool):
                raise AssertionError(
                    f"discovery allocation mismatch for {source}/{answer}: allocated {offset}, have {len(pool)}"
                )

    return [
        sorted_by_rank(rows, salt, f"discovery-shard-{index:02d}-order")
        for index, rows in enumerate(shards, 1)
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--salt", default=DEFAULT_SALT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()

    source_rows: dict[str, list[dict[str, Any]]] = {}
    source_metadata: dict[str, Any] = {}
    for source in SOURCE_ORDER:
        path = HF_CACHE / f"{source}.jsonl"
        actual_sha256 = sha256_file(path)
        expected_sha256 = EXPECTED_SOURCE_SHA256[source]
        if actual_sha256 != expected_sha256:
            raise SystemExit(
                f"source hash drift for {source}: expected {expected_sha256}, found {actual_sha256}"
            )
        rows = load_jsonl(path)
        validate_source_rows(source, rows)
        source_rows[source] = rows
        source_metadata[source] = {
            "path": repo_path(path),
            "sha256": actual_sha256,
            "rows": len(rows),
            "true": sum(row["answer"] is True for row in rows),
            "false": sum(row["answer"] is False for row in rows),
        }

    exposed, exposed_by_source = scan_exposed_ids(output_root)
    exposure_digest = ordered_id_sha256(sorted(exposed))
    if args.salt == DEFAULT_SALT and exposure_digest != EXPECTED_EXPOSURE_ID_SHA256:
        raise SystemExit(
            "exposure audit drift: "
            f"expected {EXPECTED_EXPOSURE_ID_SHA256}, found {exposure_digest}. "
            "Review new evaluation-row references before changing the audited fixture."
        )

    selected: list[dict[str, Any]] = []
    selected_by_stratum: dict[tuple[str, bool], list[dict[str, Any]]] = {}
    available_by_stratum: dict[str, int] = {}
    for source in SOURCE_ORDER:
        for answer in (True, False):
            pool = [
                row
                for row in source_rows[source]
                if row["answer"] is answer and row["id"] not in exposed
            ]
            pool = sorted_by_rank(pool, args.salt, f"{source}|{answer}")
            quota = SELECTION_QUOTAS[(source, answer)]
            if len(pool) < quota:
                raise SystemExit(
                    f"insufficient unexposed rows for {source}/{answer}: need {quota}, have {len(pool)}"
                )
            take = pool[:quota]
            selected_by_stratum[(source, answer)] = take
            selected.extend(take)
            available_by_stratum[f"{source}:{label_name(answer)}"] = len(pool)

    combined = sorted_by_rank(selected, args.salt, "combined-order")
    combined_digest = ordered_id_sha256(combined)
    if args.salt == DEFAULT_SALT and combined_digest != EXPECTED_COMBINED_ID_SHA256:
        raise SystemExit(
            f"combined selection drift: expected {EXPECTED_COMBINED_ID_SHA256}, found {combined_digest}"
        )

    holdout: list[dict[str, Any]] = []
    for source in SOURCE_ORDER:
        for answer in (True, False):
            ranked = sorted_by_rank(
                selected_by_stratum[(source, answer)],
                args.salt,
                f"holdout|{source}|{answer}",
            )
            holdout.extend(ranked[: HOLDOUT_QUOTAS[(source, answer)]])
    holdout = sorted_by_rank(holdout, args.salt, "holdout-order")
    holdout_ids = {row["id"] for row in holdout}
    discovery = sorted_by_rank(
        [row for row in selected if row["id"] not in holdout_ids],
        args.salt,
        "discovery-order",
    )
    discovery_shards = allocate_discovery_shards(discovery, args.salt)

    if count_rows(combined)["true"] != 100 or count_rows(combined)["false"] != 50:
        raise AssertionError("combined label counts are not 100 TRUE / 50 FALSE")
    if count_rows(discovery)["true"] != 80 or count_rows(discovery)["false"] != 40:
        raise AssertionError("discovery label counts are not 80 TRUE / 40 FALSE")
    if count_rows(holdout)["true"] != 20 or count_rows(holdout)["false"] != 10:
        raise AssertionError("holdout label counts are not 20 TRUE / 10 FALSE")
    if any(len(shard) != 40 for shard in discovery_shards):
        raise AssertionError("each discovery shard must contain exactly 40 rows")

    output_root.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "combined": write_manifest_pair(output_root, "combined", combined),
        "discovery": write_manifest_pair(output_root, "discovery", discovery),
        "holdout_locked": write_manifest_pair(output_root, "holdout_locked", holdout),
        "discovery_shards": [
            write_manifest_pair(output_root, f"discovery_shard_{index:02d}", rows)
            for index, rows in enumerate(discovery_shards, 1)
        ],
    }

    metadata = {
        "schema_version": 1,
        "purpose": "HF analysis-only 100-TRUE/50-FALSE baseline fixture",
        "analysis_only": True,
        "audited_repo_head": AUDITED_REPO_HEAD,
        "salt": args.salt,
        "expected_combined_ordered_id_sha256": EXPECTED_COMBINED_ID_SHA256,
        "ordered_id_hash_encoding": "UTF-8 IDs joined and terminated by bytes 0x5c 0x6e (backslash+n)",
        "rank_encoding": "SHA-256 of salt/tag/id joined by bytes 0x5c 0x30 (backslash+zero)",
        "sources": source_metadata,
        "selection_quotas": {
            f"{source}:{label_name(answer)}": count
            for (source, answer), count in SELECTION_QUOTAS.items()
        },
        "holdout_quotas": {
            f"{source}:{label_name(answer)}": count
            for (source, answer), count in HOLDOUT_QUOTAS.items()
        },
        "discovery_shard_quotas": [
            {
                f"{source}:{label_name(answer)}": count
                for (source, answer), count in quotas.items()
            }
            for quotas in DISCOVERY_SHARD_QUOTAS
        ],
        "available_unexposed": available_by_stratum,
        "exposure_audit": {
            "scan_roots": [repo_path(path) for path in EXPOSURE_ROOTS],
            "snapshot": repo_path(EXPOSURE_SNAPSHOT),
            "snapshot_sha256": EXPECTED_EXPOSURE_SNAPSHOT_SHA256,
            "snapshot_ids": len(load_exposure_snapshot()),
            "excluded_output_root": repo_path(output_root),
            "suffixes": sorted(EXPOSURE_SUFFIXES),
            "pattern": EXPOSURE_PATTERN.pattern,
            "ordered_id_sha256": exposure_digest,
            "expected_ordered_id_sha256": EXPECTED_EXPOSURE_ID_SHA256,
            "counts": {source: len(ids) for source, ids in exposed_by_source.items()},
            "excluded_ids": exposed_by_source,
        },
        "runner_manifest_policy": {
            "answer_removed": True,
            "labeled_sidecars_not_solver_visible_in_official_runner": True,
        },
        "artifacts": artifacts,
    }
    metadata_path = output_root / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"output_root={repo_path(output_root)}")
    print(f"metadata={repo_path(metadata_path)} sha256={sha256_file(metadata_path)}")
    print(
        "combined_rows={rows} true={true} false={false} ordered_id_sha256={ordered_id_sha256}".format(
            **artifacts["combined"]
        )
    )
    for index, shard in enumerate(artifacts["discovery_shards"], 1):
        print(
            f"discovery_shard_{index:02d}_rows={shard['rows']} "
            f"true={shard['true']} false={shard['false']} "
            f"runner_sha256={shard['runner_sha256']}"
        )
    holdout_info = artifacts["holdout_locked"]
    print(
        f"holdout_locked_rows={holdout_info['rows']} true={holdout_info['true']} "
        f"false={holdout_info['false']} runner_sha256={holdout_info['runner_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
