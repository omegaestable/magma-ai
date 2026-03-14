"""Download helper for offline benchmark data.

Status:
- Submission-support only as a way to fetch local benchmark files.
- The old hardcoded Hugging Face dataset slug may be stale; local generation is
    the supported fallback.
"""

import argparse
import csv
import json
import os
import random
import urllib.error
import urllib.request

from config import DATA_DIR as REPO_DATA_DIR, RAW_IMPL_CSV

DATA_DIR = str(REPO_DATA_DIR)
DEFAULT_MATRIX = str(RAW_IMPL_CSV)

FILES = {
    'normal.jsonl': 'https://huggingface.co/datasets/tao-challenge/equational-theories-stage1/resolve/main/normal.jsonl',
    'hard.jsonl': 'https://huggingface.co/datasets/tao-challenge/equational-theories-stage1/resolve/main/hard.jsonl',
}


def resolve_token(explicit_token: str | None = None) -> str | None:
    if explicit_token:
        return explicit_token
    return (
        os.environ.get('HF_TOKEN')
        or os.environ.get('HUGGINGFACE_HUB_TOKEN')
        or os.environ.get('HUGGINGFACE_TOKEN')
    )


def build_request(url: str, token: str | None = None) -> urllib.request.Request:
    headers = {
        'User-Agent': 'magma-ai-download-data/1.0',
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return urllib.request.Request(url, headers=headers)


def download_file(url: str, filepath: str, token: str | None = None) -> int:
    request = build_request(url, token=token)
    with urllib.request.urlopen(request) as response, open(filepath, 'wb') as output_file:
        output_file.write(response.read())
    return os.path.getsize(filepath)


def explain_http_error(error: urllib.error.HTTPError, url: str, token_present: bool) -> None:
    print(f"  Failed: HTTP {error.code} {error.reason}")
    if error.code == 401:
        print("  The dataset appears to require Hugging Face authentication.")
        if token_present:
            print("  A token was provided, but this account likely lacks access to the dataset.")
        else:
            print("  No Hugging Face token was provided to the downloader.")
        print("  Required next step: use a Hugging Face account that can open this dataset and supply a read token.")
        print("  Set one of: HF_TOKEN, HUGGINGFACE_HUB_TOKEN, HUGGINGFACE_TOKEN")
    elif error.code == 403:
        print("  The token is valid but does not have permission for this dataset, or the dataset is gated.")
    elif error.code == 404:
        print("  The dataset path or filename was not found. The hardcoded dataset slug may be stale.")
        print("  Supported fallback: python download_data.py --generate-local")
    print(f"  URL: {url}")


def download(token: str | None = None, force: bool = False):
    os.makedirs(DATA_DIR, exist_ok=True)
    for filename, url in FILES.items():
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath) and not force:
            print(f"  {filename} already exists, skipping")
            continue
        print(f"  Downloading {filename}...")
        try:
            size = download_file(url, filepath, token=token)
            print(f"  Saved {filename} ({size:,} bytes)")
        except urllib.error.HTTPError as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            explain_http_error(e, url, token_present=bool(token))
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            print(f"  Failed to download {filename}: {e}")
            print(f"  You can manually download from: {url}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Download TAO Challenge benchmark JSONL files.')
    parser.add_argument(
        '--token',
        default=None,
        help='Optional Hugging Face read token. If omitted, uses HF_TOKEN or HUGGINGFACE_HUB_TOKEN.',
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Redownload files even if they already exist locally.',
    )
    parser.add_argument(
        '--generate-local',
        action='store_true',
        help='Generate a local benchmark JSONL from the implication CSV matrix (no network needed).',
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


if __name__ == '__main__':
    args = parse_args()

    if args.generate_local:
        print("Generating local benchmark from CSV matrix...")
        generate_local_benchmark(args.matrix, n=args.n, seed=args.seed)
    else:
        token = resolve_token(args.token)
        print("Downloading TAO Challenge training data...")
        if token:
            print("Using Hugging Face token from CLI or environment.")
        else:
            print("No Hugging Face token detected; private or gated datasets will return HTTP 401/403.")
        download(token=token, force=args.force)

    print("Done.")
