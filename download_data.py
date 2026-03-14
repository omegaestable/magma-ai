"""
download_data.py — Download training data for TAO Challenge evaluation.

Downloads normal.jsonl and hard.jsonl from HuggingFace.
"""

import os
import urllib.request


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

FILES = {
    'normal.jsonl': 'https://huggingface.co/datasets/tao-challenge/equational-theories-stage1/resolve/main/normal.jsonl',
    'hard.jsonl': 'https://huggingface.co/datasets/tao-challenge/equational-theories-stage1/resolve/main/hard.jsonl',
}


def download():
    os.makedirs(DATA_DIR, exist_ok=True)
    for filename, url in FILES.items():
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            print(f"  {filename} already exists, skipping")
            continue
        print(f"  Downloading {filename}...")
        try:
            urllib.request.urlretrieve(url, filepath)
            size = os.path.getsize(filepath)
            print(f"  Saved {filename} ({size:,} bytes)")
        except Exception as e:
            print(f"  Failed to download {filename}: {e}")
            print(f"  You can manually download from: {url}")


if __name__ == '__main__':
    print("Downloading TAO Challenge training data...")
    download()
    print("Done.")
