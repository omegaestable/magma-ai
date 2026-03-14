"""Local benchmark generation helper.

Status:
- Submission-support only as a way to generate local benchmark files.
- Remote download has been removed; all supported paths are local-only.
"""

import argparse
import csv
import json
import os
import random

from benchmark_utils import (
    build_hardest_benchmark_from_matrix,
    build_no_leak_benchmark,
    load_holdout_indices,
    load_equations,
)
from config import DATA_DIR as REPO_DATA_DIR, RAW_IMPL_CSV

DATA_DIR = str(REPO_DATA_DIR)
DEFAULT_MATRIX = str(RAW_IMPL_CSV)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate local TAO Challenge benchmark JSONL files.')
    parser.add_argument(
        '--generate-local',
        action='store_true',
        help='Generate a local benchmark JSONL from the implication CSV matrix (no network needed).',
    )
    parser.add_argument(
        '--generate-no-leak',
        action='store_true',
        help='Generate a no-leak benchmark JSONL from held-out equation indices.',
    )
    parser.add_argument(
        '--generate-hardest',
        action='store_true',
        help='Generate a hardest-case benchmark JSONL from structurally misleading pairs.',
    )
    parser.add_argument(
        '--matrix',
        default=DEFAULT_MATRIX,
        help='Path to raw implications CSV (used with --generate-local).',
    )
    parser.add_argument(
        '--n', type=int, default=200,
        help='Number of balanced pairs to sample for local benchmark (default: 200).',
    )
    parser.add_argument(
        '--seed', type=int, default=42,
        help='Random seed for local benchmark sampling.',
    )
    parser.add_argument(
        '--holdout-count', type=int, default=100,
        help='Number of equations to hold out when using --generate-no-leak.',
    )
    parser.add_argument(
        '--holdout-file', default=None,
        help='Optional JSON file with held-out equation indices to reuse for --generate-no-leak.',
    )
    parser.add_argument(
        '--no-leak-out', default=None,
        help='Optional output path for --generate-no-leak (defaults to data/no_leak_benchmark.jsonl).',
    )
    parser.add_argument(
        '--holdout-metadata-out', default=None,
        help='Optional output path for held-out equation metadata (defaults to data/no_leak_holdout.json).',
    )
    parser.add_argument(
        '--hardest-n', type=int, default=500,
        help='Number of pairs to emit for --generate-hardest.',
    )
    parser.add_argument(
        '--hardest-out', default=None,
        help='Optional output path for --generate-hardest (defaults to data/hardest_{n}.jsonl).',
    )
    return parser.parse_args()


def generate_local_benchmark(matrix_path: str, n: int = 200, seed: int = 42) -> str:
    """Generate a balanced local benchmark JSONL from the implication CSV matrix.

    Returns the output filepath.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, 'local_benchmark.jsonl')

    if not os.path.isfile(matrix_path):
        print(f"  Matrix file not found: {matrix_path}")
        print("  Cannot generate local benchmark without the CSV matrix.")
        return ''

    rng = random.Random(seed)
    half = max(1, n // 2)
    true_pairs: list[dict] = []
    false_pairs: list[dict] = []
    true_seen = 0
    false_seen = 0

    print(f"  Reading matrix from {matrix_path}...")
    with open(matrix_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for eq1_idx, row in enumerate(reader, start=1):
            for eq2_idx, val_str in enumerate(row, start=1):
                if eq1_idx == eq2_idx:
                    continue
                try:
                    val = int(val_str)
                except ValueError:
                    continue
                if val == 0:
                    continue
                rec = {
                    'equation1_index': eq1_idx,
                    'equation2_index': eq2_idx,
                    'implies': val > 0,
                }
                if val > 0:
                    true_seen += 1
                    if len(true_pairs) < half:
                        true_pairs.append(rec)
                    else:
                        j = rng.randint(0, true_seen - 1)
                        if j < half:
                            true_pairs[j] = rec
                else:
                    false_seen += 1
                    if len(false_pairs) < half:
                        false_pairs.append(rec)
                    else:
                        j = rng.randint(0, false_seen - 1)
                        if j < half:
                            false_pairs[j] = rec

    sampled = true_pairs + false_pairs
    rng.shuffle(sampled)

    with open(out_path, 'w', encoding='utf-8') as f:
        for rec in sampled:
            f.write(json.dumps(rec) + '\n')

    print(f"  Generated {len(sampled)} problems ({len(true_pairs)} TRUE, {len(false_pairs)} FALSE)")
    print(f"  Saved to {out_path}")
    return out_path


def generate_no_leak_benchmark(
    matrix_path: str,
    n: int = 200,
    seed: int = 42,
    holdout_count: int = 100,
    holdout_file: str | None = None,
    out_path: str | None = None,
    metadata_path: str | None = None,
) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = out_path or os.path.join(DATA_DIR, 'no_leak_benchmark.jsonl')
    metadata_path = metadata_path or os.path.join(DATA_DIR, 'no_leak_holdout.json')

    if not os.path.isfile(matrix_path):
        print(f"  Matrix file not found: {matrix_path}")
        return ''

    equations = load_equations()
    holdout_indices = load_holdout_indices(holdout_file) if holdout_file else None
    records, holdout_indices = build_no_leak_benchmark(
        equations,
        filepath=matrix_path,
        n=n,
        holdout_equation_count=holdout_count,
        seed=seed,
        holdout_eq_indices=holdout_indices,
    )
    _write_jsonl(out_path, records)
    with open(metadata_path, 'w', encoding='utf-8') as handle:
        json.dump(
            {
                'seed': seed,
                'holdout_count': len(holdout_indices),
                'heldout_equation_indices': holdout_indices,
                'benchmark_path': out_path,
                'matrix_path': matrix_path,
            },
            handle,
            indent=2,
        )

    print(f"  Generated no-leak benchmark with {len(records)} pairs")
    print(f"  Held out {len(holdout_indices)} equation indices")
    print(f"  Benchmark saved to {out_path}")
    print(f"  Holdout metadata saved to {metadata_path}")
    return out_path


def generate_hardest_benchmark(
    matrix_path: str,
    n: int = 500,
    seed: int = 42,
    out_path: str | None = None,
) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = out_path or os.path.join(DATA_DIR, f'hardest_{n}.jsonl')

    if not os.path.isfile(matrix_path):
        print(f"  Matrix file not found: {matrix_path}")
        return ''

    equations = load_equations()
    records = build_hardest_benchmark_from_matrix(
        equations,
        filepath=matrix_path,
        n=n,
        seed=seed,
    )
    _write_jsonl(out_path, records)
    print(f"  Generated hardest benchmark with {len(records)} pairs")
    print(f"  Benchmark saved to {out_path}")
    return out_path


def _write_jsonl(filepath: str, records: list[dict]) -> None:
    with open(filepath, 'w', encoding='utf-8') as handle:
        for record in records:
            payload = dict(record)
            if 'eq1_idx' in payload:
                payload['equation1_index'] = payload.pop('eq1_idx')
            if 'eq2_idx' in payload:
                payload['equation2_index'] = payload.pop('eq2_idx')
            if 'label' in payload and 'implies' not in payload:
                payload['implies'] = payload.pop('label')
            handle.write(json.dumps(payload) + '\n')


if __name__ == '__main__':
    args = parse_args()

    if args.generate_local:
        print("Generating local benchmark from CSV matrix...")
        generate_local_benchmark(args.matrix, n=args.n, seed=args.seed)
    elif args.generate_no_leak:
        print("Generating no-leak benchmark from CSV matrix...")
        generate_no_leak_benchmark(
            args.matrix,
            n=args.n,
            seed=args.seed,
            holdout_count=args.holdout_count,
            holdout_file=args.holdout_file,
            out_path=args.no_leak_out,
            metadata_path=args.holdout_metadata_out,
        )
    elif args.generate_hardest:
        print("Generating hardest-case benchmark from CSV matrix...")
        generate_hardest_benchmark(
            args.matrix,
            n=args.hardest_n,
            seed=args.seed,
            out_path=args.hardest_out,
        )
    else:
        print("No action selected.")
        print("Use one of: --generate-local, --generate-no-leak, --generate-hardest")

    print("Done.")
