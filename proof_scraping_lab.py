#!/usr/bin/env python3
"""
proof_scraping_lab.py

Bulk scraper and archival crawler for Teorth implication proof pages.

It fetches pages like:
  https://teorth.github.io/equational_theories/implications/show_proof.html?pair=310,118

and writes structured artifacts for downstream distillation:
  - JSONL with parsed proof-page rows
  - Markdown summary table
  - JSON crawl manifest for recursive archival runs

Pair input sources:
  1) --pairs "310,118;320,118;118,310"
  2) --pairs-file path/to/pairs.txt        (one "a,b" pair per line)
  3) --from-jsonl path/to/benchmark.jsonl  (maps equation text to ids)
  4) --from-results path/to/sim_result.json (maps failed examples to ids)
  5) --from-full-entries                   (seed crawl from full_entries.json implications)

Examples:
  python proof_scraping_lab.py --pairs "310,118;118,310" --out-prefix results/proof_lab/smoke

  python proof_scraping_lab.py \
    --from-jsonl data/benchmark/<current_hard3_rotation>.jsonl \
    --only-false --limit 40 --out-prefix results/proof_lab/hard3_rotation

  python proof_scraping_lab.py \
    --from-results results/sim_paid_hard3_seed20260401_v22_witness.json \
    --failed-only --out-prefix results/proof_lab/hard3_failures_seed20260401

  python proof_scraping_lab.py \
    --from-full-entries --recursive --limit 500 \
    --out-prefix results/proof_lab/archive_seed
"""
from __future__ import annotations

import argparse
import html
import json
import re
import time
from collections import deque
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urljoin, urlparse

import requests

from fetch_teorth_data import load_full_entries
from v21_data_infrastructure import build_equation_map, load_equations, normalize_eq

BASE = "https://teorth.github.io/equational_theories/implications/"
PROOF_PATH = "show_proof.html?pair={a},{b}"
DEFAULT_CACHE_DIR = Path(__file__).resolve().parent / "data" / "teorth_cache" / "proof_page_cache"

H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
A_RE = re.compile(r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL)
EQ_TOKEN_RE = re.compile(r"Equation(\d+)\[(.*?)\]")
PRE_RE = re.compile(r"<pre[^>]*>(.*?)</pre>", re.IGNORECASE | re.DOTALL)
CODE_RE = re.compile(r"<code[^>]*>(.*?)</code>", re.IGNORECASE | re.DOTALL)
TABLE_RE = re.compile(r"<table[^>]*>(.*?)</table>", re.IGNORECASE | re.DOTALL)
PAIR_RE = re.compile(r"pair=(\d+)\s*,\s*(\d+)")


def parse_pairs_text(text: str) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    text = text.replace("\n", ";")
    for token in text.split(";"):
        token = token.strip()
        if not token:
            continue
        m = re.match(r"^\s*(\d+)\s*,\s*(\d+)\s*$", token)
        if not m:
            continue
        pairs.append((int(m.group(1)), int(m.group(2))))
    return pairs


def pairs_from_file(path: Path) -> list[tuple[int, int]]:
    return parse_pairs_text(path.read_text(encoding="utf-8"))


def pairs_from_jsonl(path: Path, only_false: bool) -> list[tuple[int, int]]:
    equations = load_equations()
    eq_map = build_equation_map(equations)
    pairs: list[tuple[int, int]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if only_false and bool(row.get("answer")):
                continue
            e1 = eq_map.get(normalize_eq(row["equation1"]))
            e2 = eq_map.get(normalize_eq(row["equation2"]))
            if e1 is None or e2 is None:
                continue
            pairs.append((e1 + 1, e2 + 1))
    return pairs


def pairs_from_results(path: Path, failed_only: bool) -> list[tuple[int, int]]:
    equations = load_equations()
    eq_map = build_equation_map(equations)
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("results", [])
    out: list[tuple[int, int]] = []
    for r in rows:
        if failed_only and bool(r.get("correct")):
            continue
        e1 = eq_map.get(normalize_eq(r["equation1"]))
        e2 = eq_map.get(normalize_eq(r["equation2"]))
        if e1 is None or e2 is None:
            continue
        out.append((e1 + 1, e2 + 1))
    return out


def pairs_from_full_entries_cache() -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for entry in load_full_entries():
        variant = entry.get("variant") or {}
        implication = variant.get("implication") or {}
        lhs = implication.get("lhs", "")
        rhs = implication.get("rhs", "")
        if not (lhs.startswith("Equation") and rhs.startswith("Equation")):
            continue
        try:
            left = int(lhs.replace("Equation", ""))
            right = int(rhs.replace("Equation", ""))
        except ValueError:
            continue
        pairs.append((left, right))
    return pairs


def dedupe_pairs(pairs: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    seen = set()
    out = []
    for p in pairs:
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def _strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(" ".join(s.split()))


def extract_pair_from_href(href: str) -> tuple[int, int] | None:
    parsed = urlparse(href)
    match = PAIR_RE.search(parsed.query or href)
    if match:
        return int(match.group(1)), int(match.group(2))
    query = parse_qs(parsed.query)
    pair_values = query.get("pair")
    if not pair_values:
        return None
    inner = parse_pairs_text(pair_values[0])
    return inner[0] if inner else None


def _extract_blocks(pattern: re.Pattern[str], body: str, limit: int = 8) -> list[str]:
    blocks: list[str] = []
    for match in pattern.findall(body):
        clean = _strip_tags(match)
        if clean:
            blocks.append(clean)
        if len(blocks) >= limit:
            break
    return blocks


def parse_proof_page(body: str, url: str, a: int, b: int) -> dict:
    h1_match = H1_RE.search(body)
    title = _strip_tags(h1_match.group(1)) if h1_match else ""

    links = []
    eq_nodes = []
    theorem_links = []
    fact_links = []
    pair_links = []

    for href, text in A_RE.findall(body):
        clean_text = _strip_tags(text)
        full_href = urljoin(url, href)
        links.append({"text": clean_text, "href": full_href})

        eq_match = EQ_TOKEN_RE.search(clean_text)
        if eq_match:
            eq_nodes.append(
                {
                    "id": int(eq_match.group(1)),
                    "expr": eq_match.group(2),
                    "href": full_href,
                }
            )

        pair = extract_pair_from_href(full_href)
        if pair is not None:
            pair_links.append({"pair": [pair[0], pair[1]], "text": clean_text, "href": full_href})

        if "implies" in clean_text or "Rewrite" in clean_text or "Equation" in clean_text:
            if "github.com/teorth/equational_theories" in full_href:
                theorem_links.append({"name": clean_text, "href": full_href})

        if "Facts" in clean_text and "github.com/teorth/equational_theories" in full_href:
            fact_links.append({"name": clean_text, "href": full_href})

    def uniq(items: list[dict], key_name: str) -> list[dict]:
        seen = set()
        out = []
        for it in items:
            key = json.dumps(it.get(key_name), sort_keys=True) if isinstance(it.get(key_name), list) else it.get(key_name)
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
        return out

    theorem_links = uniq(theorem_links, "href")
    fact_links = uniq(fact_links, "href")
    pair_links = uniq(pair_links, "pair")

    return {
        "pair": [a, b],
        "url": url,
        "title": title,
        "equation_nodes": eq_nodes,
        "theorem_links": theorem_links,
        "fact_links": fact_links,
        "pair_links": pair_links,
        "code_blocks": _extract_blocks(CODE_RE, body),
        "pre_blocks": _extract_blocks(PRE_RE, body),
        "table_blocks": _extract_blocks(TABLE_RE, body),
        "all_links": links,
    }


def pair_cache_path(cache_dir: Path, a: int, b: int) -> Path:
    return cache_dir / f"pair_{a}_{b}.json"


def fetch_one(session: requests.Session, a: int, b: int, timeout_s: int, retries: int, sleep_s: float) -> dict:
    url = urljoin(BASE, PROOF_PATH.format(a=a, b=b))
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=timeout_s)
            resp.raise_for_status()
            parsed = parse_proof_page(resp.text, url, a, b)
            parsed["ok"] = True
            parsed["status_code"] = resp.status_code
            parsed["fetched_from"] = "network"
            return parsed
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)
            if attempt < retries:
                time.sleep(sleep_s)
    return {
        "pair": [a, b],
        "url": url,
        "ok": False,
        "error": last_err,
        "title": "",
        "equation_nodes": [],
        "theorem_links": [],
        "fact_links": [],
        "pair_links": [],
        "code_blocks": [],
        "pre_blocks": [],
        "table_blocks": [],
        "all_links": [],
        "fetched_from": "network",
    }


def fetch_with_cache(
    session: requests.Session,
    a: int,
    b: int,
    timeout_s: int,
    retries: int,
    sleep_s: float,
    cache_dir: Path,
    refresh_cache: bool,
) -> dict:
    cache_path = pair_cache_path(cache_dir, a, b)
    if cache_path.exists() and not refresh_cache:
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        cached["fetched_from"] = "cache"
        return cached

    cache_dir.mkdir(parents=True, exist_ok=True)
    row = fetch_one(session, a, b, timeout_s=timeout_s, retries=retries, sleep_s=sleep_s)
    cache_path.write_text(json.dumps(row, indent=2), encoding="utf-8")
    return row


def crawl_pairs(
    seed_pairs: list[tuple[int, int]],
    recursive: bool,
    limit: int,
    session: requests.Session,
    timeout_s: int,
    retries: int,
    sleep_s: float,
    cache_dir: Path,
    refresh_cache: bool,
) -> tuple[list[dict], dict]:
    queue: deque[tuple[int, int]] = deque(dedupe_pairs(seed_pairs))
    seen: set[tuple[int, int]] = set()
    rows: list[dict] = []
    discovered_edges: list[dict] = []
    failures: list[dict] = []
    seed_count = len(queue)

    while queue:
        if limit > 0 and len(rows) >= limit:
            break
        pair = queue.popleft()
        if pair in seen:
            continue
        seen.add(pair)
        a, b = pair
        row = fetch_with_cache(
            session=session,
            a=a,
            b=b,
            timeout_s=timeout_s,
            retries=retries,
            sleep_s=sleep_s,
            cache_dir=cache_dir,
            refresh_cache=refresh_cache,
        )
        rows.append(row)
        if not row.get("ok"):
            failures.append({"pair": [a, b], "error": row.get("error", "")})
            continue

        if recursive:
            for link in row.get("pair_links", []):
                child = tuple(link["pair"])
                discovered_edges.append({"from": [a, b], "to": [child[0], child[1]], "href": link.get("href", "")})
                if child not in seen:
                    queue.append(child)

    manifest = {
        "seed_pair_count": seed_count,
        "visited_pair_count": len(rows),
        "ok_count": sum(1 for row in rows if row.get("ok")),
        "failed_count": sum(1 for row in rows if not row.get("ok")),
        "recursive": recursive,
        "limit": limit,
        "cache_dir": cache_dir.as_posix(),
        "discovered_edge_count": len(discovered_edges),
        "discovered_edges": discovered_edges,
        "failures": failures,
        "remaining_queue": [list(pair) for pair in queue],
    }
    return rows, manifest


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_markdown(path: Path, rows: list[dict], manifest: dict | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Teorth Proof Scrape Report",
        "",
        f"total_pairs={len(rows)}",
        f"ok={sum(1 for r in rows if r.get('ok'))}",
        f"failed={sum(1 for r in rows if not r.get('ok'))}",
    ]
    if manifest is not None:
        lines.extend(
            [
                f"recursive={manifest.get('recursive')}",
                f"discovered_edge_count={manifest.get('discovered_edge_count')}",
                f"remaining_queue={len(manifest.get('remaining_queue', []))}",
            ]
        )
    lines.extend(
        [
            "",
            "| Pair | OK | Source | Title | Pair Links | Theorems | Facts | URL |",
            "|---|---:|---|---|---:|---:|---:|---|",
        ]
    )
    for r in rows:
        a, b = r["pair"]
        title = (r.get("title") or "").replace("|", "\\|")
        url = r.get("url", "")
        lines.append(
            f"| {a},{b} | {'Y' if r.get('ok') else 'N'} | {r.get('fetched_from','')} | {title} | "
            f"{len(r.get('pair_links', []))} | {len(r.get('theorem_links', []))} | {len(r.get('fact_links', []))} | {url} |"
        )

    lines.append("")
    lines.append("## Detailed Rows")
    lines.append("")
    for r in rows:
        a, b = r["pair"]
        lines.append(f"### Pair {a},{b}")
        lines.append(f"- ok={r.get('ok')}")
        lines.append(f"- fetched_from={r.get('fetched_from','')}")
        lines.append(f"- title={r.get('title','')}")
        if not r.get("ok"):
            lines.append(f"- error={r.get('error','')}")
            lines.append("")
            continue
        if r.get("pair_links"):
            preview = ", ".join(f"{item['pair'][0]},{item['pair'][1]}" for item in r["pair_links"][:8])
            lines.append(f"- pair_links_preview={preview}")
        if r.get("equation_nodes"):
            preview = ", ".join(f"E{n['id']}" for n in r["equation_nodes"][:8])
            lines.append(f"- equation_nodes_preview={preview}")
        if r.get("theorem_links"):
            lines.append(f"- theorem_head={r['theorem_links'][0]['name']}")
        if r.get("fact_links"):
            lines.append(f"- fact_head={r['fact_links'][0]['name']}")
        if r.get("code_blocks"):
            lines.append(f"- code_block_head={r['code_blocks'][0][:160]}")
        if r.get("table_blocks"):
            lines.append(f"- table_block_head={r['table_blocks'][0][:160]}")
        lines.append(f"- url={r.get('url','')}")
        lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def collect_pairs(args: argparse.Namespace) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    if args.pairs.strip():
        pairs.extend(parse_pairs_text(args.pairs))
    if args.pairs_file.strip():
        pairs.extend(pairs_from_file(Path(args.pairs_file)))
    if args.from_jsonl.strip():
        pairs.extend(pairs_from_jsonl(Path(args.from_jsonl), only_false=args.only_false))
    if args.from_results.strip():
        pairs.extend(pairs_from_results(Path(args.from_results), failed_only=args.failed_only))
    if args.from_full_entries:
        pairs.extend(pairs_from_full_entries_cache())
    return dedupe_pairs(pairs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk scraper and archival crawler for Teorth show_proof pages")
    parser.add_argument("--pairs", default="", help="Semicolon-separated 'a,b' list")
    parser.add_argument("--pairs-file", default="", help="Text file with one 'a,b' pair per line")
    parser.add_argument("--from-jsonl", default="", help="Benchmark JSONL to map to equation IDs")
    parser.add_argument("--only-false", action="store_true", help="With --from-jsonl, include only answer=false rows")
    parser.add_argument("--from-results", default="", help="sim_lab results JSON to map rows to equation IDs")
    parser.add_argument("--failed-only", action="store_true", help="With --from-results, include only incorrect rows")
    parser.add_argument("--from-full-entries", action="store_true", help="Seed scrape from implication pairs in full_entries.json")
    parser.add_argument("--recursive", action="store_true", help="Follow discovered proof-page pair links recursively")
    parser.add_argument("--limit", type=int, default=0, help="Max number of visited pairs after dedupe (0=no cap)")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR), help="Directory for cached proof-page JSON")
    parser.add_argument("--refresh-cache", action="store_true", help="Re-fetch pages even if cached")
    parser.add_argument("--out-prefix", default="results/proof_lab/proofs")
    args = parser.parse_args()

    pairs = collect_pairs(args)
    if args.limit > 0 and not args.recursive:
        pairs = pairs[: args.limit]

    if not pairs:
        raise SystemExit(
            "No pairs selected. Use --pairs, --pairs-file, --from-jsonl, --from-results, or --from-full-entries."
        )

    print(f"pairs_selected={len(pairs)}")
    with requests.Session() as session:
        session.headers.update({"User-Agent": "magma-ai-proof-scraping-lab/2.0"})
        rows, manifest = crawl_pairs(
            seed_pairs=pairs,
            recursive=args.recursive,
            limit=args.limit,
            session=session,
            timeout_s=args.timeout,
            retries=args.retries,
            sleep_s=args.sleep,
            cache_dir=Path(args.cache_dir),
            refresh_cache=args.refresh_cache,
        )

    for idx, row in enumerate(rows, 1):
        a, b = row["pair"]
        status = "OK" if row.get("ok") else "ERR"
        source = row.get("fetched_from", "")
        print(f"[{idx:4d}/{len(rows)}] {a},{b} {status} {source}")

    out_prefix = Path(args.out_prefix)
    jsonl_path = out_prefix.with_suffix(".jsonl")
    md_path = out_prefix.with_suffix(".md")
    manifest_path = out_prefix.with_name(out_prefix.name + "_manifest").with_suffix(".json")

    write_jsonl(jsonl_path, rows)
    write_markdown(md_path, rows, manifest=manifest)
    write_manifest(manifest_path, manifest)

    ok = sum(1 for r in rows if r.get("ok"))
    print("=" * 80)
    print(f"WROTE {jsonl_path.as_posix()} rows={len(rows)}")
    print(f"WROTE {md_path.as_posix()}")
    print(f"WROTE {manifest_path.as_posix()}")
    print(f"ok={ok} failed={len(rows)-ok}")
    print("=" * 80)


if __name__ == "__main__":
    main()
