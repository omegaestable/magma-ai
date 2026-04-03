#!/usr/bin/env python3
"""
proof_scraping_lab.py

Bulk scraper for Teorth implication proof pages.

It fetches pages like:
  https://teorth.github.io/equational_theories/implications/show_proof.html?pair=310,118

and writes structured artifacts for downstream distillation:
  - JSONL with parsed chains and links
  - Markdown summary table

Pair input sources:
  1) --pairs "310,118;320,118;118,310"
  2) --pairs-file path/to/pairs.txt        (one "a,b" pair per line)
  3) --from-jsonl path/to/benchmark.jsonl  (maps equation text to ids)
  4) --from-results path/to/sim_result.json (maps failed examples to ids)

Examples:
  python proof_scraping_lab.py --pairs "310,118;118,310" --out-prefix results/proof_lab/smoke

    python proof_scraping_lab.py \
        --from-jsonl data/benchmark/<current_hard3_rotation>.jsonl \
        --only-false --limit 40 --out-prefix results/proof_lab/hard3_rotation

  python proof_scraping_lab.py \
    --from-results results/sim_paid_hard3_seed20260401_v22_witness.json \
    --failed-only --out-prefix results/proof_lab/hard3_failures_seed20260401
"""
from __future__ import annotations

import argparse
import html
import json
import re
import time
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests

from v21_data_infrastructure import build_equation_map, load_equations, normalize_eq

BASE = "https://teorth.github.io/equational_theories/implications/"
PROOF_PATH = "show_proof.html?pair={a},{b}"

H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
A_RE = re.compile(r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL)
EQ_TOKEN_RE = re.compile(r"Equation(\d+)\[(.*?)\]")


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


def parse_proof_page(body: str, url: str, a: int, b: int) -> dict:
    h1_match = H1_RE.search(body)
    title = _strip_tags(h1_match.group(1)) if h1_match else ""

    links = []
    eq_nodes = []
    theorem_links = []
    fact_links = []

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

        if "implies" in clean_text or "Rewrite" in clean_text or "Equation" in clean_text:
            if "github.com/teorth/equational_theories" in full_href:
                theorem_links.append({"name": clean_text, "href": full_href})

        if "Facts" in clean_text and "github.com/teorth/equational_theories" in full_href:
            fact_links.append({"name": clean_text, "href": full_href})

    # Keep unique theorem/facts by href
    def uniq(items: list[dict]) -> list[dict]:
        seen = set()
        out = []
        for it in items:
            h = it.get("href")
            if h in seen:
                continue
            seen.add(h)
            out.append(it)
        return out

    theorem_links = uniq(theorem_links)
    fact_links = uniq(fact_links)

    return {
        "pair": [a, b],
        "url": url,
        "title": title,
        "equation_nodes": eq_nodes,
        "theorem_links": theorem_links,
        "fact_links": fact_links,
        "all_links": links,
    }


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
        "all_links": [],
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_markdown(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Teorth Proof Scrape Report",
        "",
        f"total_pairs={len(rows)}",
        f"ok={sum(1 for r in rows if r.get('ok'))}",
        f"failed={sum(1 for r in rows if not r.get('ok'))}",
        "",
        "| Pair | OK | Title | Theorems | Facts | URL |",
        "|---|---:|---|---:|---:|---|",
    ]
    for r in rows:
        a, b = r["pair"]
        title = (r.get("title") or "").replace("|", "\\|")
        url = r.get("url", "")
        lines.append(
            f"| {a},{b} | {'Y' if r.get('ok') else 'N'} | {title} | "
            f"{len(r.get('theorem_links', []))} | {len(r.get('fact_links', []))} | {url} |"
        )

    lines.append("")
    lines.append("## Detailed Rows")
    lines.append("")
    for r in rows:
        a, b = r["pair"]
        lines.append(f"### Pair {a},{b}")
        lines.append(f"- ok={r.get('ok')}")
        lines.append(f"- title={r.get('title','')}")
        if not r.get("ok"):
            lines.append(f"- error={r.get('error','')}")
            lines.append("")
            continue
        if r.get("equation_nodes"):
            preview = ", ".join(f"E{n['id']}" for n in r["equation_nodes"][:8])
            lines.append(f"- equation_nodes_preview={preview}")
        if r.get("theorem_links"):
            lines.append(f"- theorem_head={r['theorem_links'][0]['name']}")
        if r.get("fact_links"):
            lines.append(f"- fact_head={r['fact_links'][0]['name']}")
        lines.append(f"- url={r.get('url','')}")
        lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk scraper for Teorth show_proof pages")
    parser.add_argument("--pairs", default="", help="Semicolon-separated 'a,b' list")
    parser.add_argument("--pairs-file", default="", help="Text file with one 'a,b' pair per line")
    parser.add_argument("--from-jsonl", default="", help="Benchmark JSONL to map to equation IDs")
    parser.add_argument("--only-false", action="store_true", help="With --from-jsonl, include only answer=false rows")
    parser.add_argument("--from-results", default="", help="sim_lab results JSON to map rows to equation IDs")
    parser.add_argument("--failed-only", action="store_true", help="With --from-results, include only incorrect rows")
    parser.add_argument("--limit", type=int, default=0, help="Max number of pairs after dedupe (0=no cap)")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--out-prefix", default="results/proof_lab/proofs")
    args = parser.parse_args()

    pairs: list[tuple[int, int]] = []
    if args.pairs.strip():
        pairs.extend(parse_pairs_text(args.pairs))
    if args.pairs_file.strip():
        pairs.extend(pairs_from_file(Path(args.pairs_file)))
    if args.from_jsonl.strip():
        pairs.extend(pairs_from_jsonl(Path(args.from_jsonl), only_false=args.only_false))
    if args.from_results.strip():
        pairs.extend(pairs_from_results(Path(args.from_results), failed_only=args.failed_only))

    pairs = dedupe_pairs(pairs)
    if args.limit > 0:
        pairs = pairs[: args.limit]

    if not pairs:
        raise SystemExit("No pairs selected. Use --pairs, --pairs-file, --from-jsonl, or --from-results.")

    print(f"pairs_selected={len(pairs)}")
    with requests.Session() as session:
        session.headers.update({"User-Agent": "magma-ai-proof-scraping-lab/1.0"})
        rows = []
        for idx, (a, b) in enumerate(pairs, 1):
            row = fetch_one(session, a, b, timeout_s=args.timeout, retries=args.retries, sleep_s=args.sleep)
            rows.append(row)
            status = "OK" if row.get("ok") else "ERR"
            print(f"[{idx:4d}/{len(pairs)}] {a},{b} {status}")

    out_prefix = Path(args.out_prefix)
    jsonl_path = out_prefix.with_suffix(".jsonl")
    md_path = out_prefix.with_suffix(".md")

    write_jsonl(jsonl_path, rows)
    write_markdown(md_path, rows)

    ok = sum(1 for r in rows if r.get("ok"))
    print("=" * 80)
    print(f"WROTE {jsonl_path.as_posix()} rows={len(rows)}")
    print(f"WROTE {md_path.as_posix()}")
    print(f"ok={ok} failed={len(rows)-ok}")
    print("=" * 80)


if __name__ == "__main__":
    main()
