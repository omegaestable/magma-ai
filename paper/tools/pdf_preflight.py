#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


ARXIV_ID_RE = re.compile(r"^\d{4}\.\d{5}(v\d+)?$")


@dataclass
class PdfReport:
    pdf: str
    page_count: int
    is_encrypted: bool
    has_text_layer: bool
    sampled_pages: int
    sampled_text_pages: int
    sampled_text_chars: int
    local_tex: str | None
    imported_source_tex: str | None
    extracted_text: str | None
    is_arxiv_id: bool
    classification: str
    reason: str
    next_action: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def paper_root() -> Path:
    return repo_root() / "paper"


def to_repo_rel(path: Path | None) -> str | None:
    if path is None:
        return None
    return str(path.resolve().relative_to(repo_root())).replace("\\", "/")


def load_pdf_reader():
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise SystemExit(
            "This command requires pypdf. Install it with:\n"
            "python -m pip install -r requirements-dev.txt"
        ) from exc
    return PdfReader


def iter_pdfs(values: list[str]) -> list[Path]:
    if not values:
        return sorted(paper_root().glob("*.pdf"))

    resolved: list[Path] = []
    for value in values:
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = repo_root() / candidate
        candidate = candidate.resolve()
        if candidate.is_dir():
            resolved.extend(sorted(candidate.glob("*.pdf")))
            continue
        resolved.append(candidate)
    return resolved


def detect_local_tex(pdf_path: Path) -> Path | None:
    candidate = pdf_path.with_suffix(".tex")
    if candidate.exists():
        return candidate
    return None


def detect_extracted_text(pdf_path: Path) -> Path | None:
    candidate = pdf_path.with_name(f"{pdf_path.stem}_extracted.txt")
    if candidate.exists():
        return candidate
    return None


def detect_imported_source_tex(pdf_path: Path) -> Path | None:
    source_dir = paper_root() / "arxiv_sources" / pdf_path.stem
    if not source_dir.exists():
        return None

    for name in ("main.tex", "arxiv_version.tex"):
        candidate = source_dir / name
        if candidate.exists():
            return candidate

    candidates = sorted(source_dir.glob("*.tex"))
    if candidates:
        return candidates[0]
    return None


def sample_text_layer(reader, max_pages: int) -> tuple[bool, int, int, int]:
    sampled_pages = min(max_pages, len(reader.pages))
    sampled_text_pages = 0
    sampled_text_chars = 0

    for index in range(sampled_pages):
        text = reader.pages[index].extract_text() or ""
        compact = "".join(text.split())
        if compact:
            sampled_text_pages += 1
            sampled_text_chars += len(compact)

    has_text_layer = sampled_text_pages > 0 and sampled_text_chars > 0
    return has_text_layer, sampled_pages, sampled_text_pages, sampled_text_chars


def classify_pdf(
    pdf_path: Path,
    *,
    page_count: int,
    has_text_layer: bool,
    local_tex: Path | None,
    imported_source_tex: Path | None,
    extracted_text: Path | None,
) -> tuple[str, str, str]:
    is_arxiv_id = bool(ARXIV_ID_RE.fullmatch(pdf_path.stem))

    if local_tex is not None:
        return (
            "canonical_local_tex",
            "Local TeX sibling already exists.",
            "Verify and compile the existing TeX instead of regenerating it from the PDF.",
        )
    if imported_source_tex is not None:
        return (
            "imported_arxiv_source",
            "High-fidelity arXiv source tree has been imported under paper/arxiv_sources/.",
            "Compile the imported source tree and preserve it as the canonical TeX reconstruction.",
        )
    if is_arxiv_id:
        if extracted_text is not None:
            reason = "arXiv-style PDF with extracted text but no local TeX sibling."
        else:
            reason = "arXiv-style PDF with no local TeX sibling."
        return (
            "source_first_arxiv",
            reason,
            "Attempt upstream/arXiv source import before any PDF-driven TeX reconstruction.",
        )
    if has_text_layer:
        return (
            "reconstruct_from_pdf",
            f"No local TeX sibling found; sampled text layer looks usable across {page_count} pages.",
            "Generate an extracted-text artifact and bootstrap a TeX scaffold from the PDF.",
        )
    return (
        "manual_transcription_needed",
        "No local TeX sibling found and the sampled PDF pages do not expose a usable text layer.",
        "Bootstrap a page-marked scaffold and plan for manual transcription or an external source import.",
    )


def inspect_pdf(pdf_path: Path, max_pages: int) -> PdfReport:
    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing PDF: {pdf_path}")

    reader_cls = load_pdf_reader()
    reader = reader_cls(str(pdf_path))

    local_tex = detect_local_tex(pdf_path)
    imported_source_tex = detect_imported_source_tex(pdf_path)
    extracted_text = detect_extracted_text(pdf_path)
    has_text_layer, sampled_pages, sampled_text_pages, sampled_text_chars = sample_text_layer(
        reader,
        max_pages=max_pages,
    )
    classification, reason, next_action = classify_pdf(
        pdf_path,
        page_count=len(reader.pages),
        has_text_layer=has_text_layer,
        local_tex=local_tex,
        imported_source_tex=imported_source_tex,
        extracted_text=extracted_text,
    )

    return PdfReport(
        pdf=to_repo_rel(pdf_path) or str(pdf_path),
        page_count=len(reader.pages),
        is_encrypted=bool(reader.is_encrypted),
        has_text_layer=has_text_layer,
        sampled_pages=sampled_pages,
        sampled_text_pages=sampled_text_pages,
        sampled_text_chars=sampled_text_chars,
        local_tex=to_repo_rel(local_tex),
        imported_source_tex=to_repo_rel(imported_source_tex),
        extracted_text=to_repo_rel(extracted_text),
        is_arxiv_id=bool(ARXIV_ID_RE.fullmatch(pdf_path.stem)),
        classification=classification,
        reason=reason,
        next_action=next_action,
    )


def build_summary(reports: list[PdfReport]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for report in reports:
        summary[report.classification] = summary.get(report.classification, 0) + 1
    return dict(sorted(summary.items()))


def emit_text(reports: list[PdfReport]) -> None:
    print(f"ROOT\t{to_repo_rel(paper_root())}")
    print(f"PDF_COUNT\t{len(reports)}")
    for classification, count in build_summary(reports).items():
        print(f"SUMMARY\t{classification}\t{count}")

    for report in reports:
        print("")
        print(f"PDF\t{report.pdf}")
        print(f"PAGES\t{report.page_count}")
        print(f"ENCRYPTED\t{report.is_encrypted}")
        print(f"TEXT_LAYER\t{report.has_text_layer}")
        print(f"SAMPLED_PAGES\t{report.sampled_pages}")
        print(f"SAMPLED_TEXT_PAGES\t{report.sampled_text_pages}")
        print(f"SAMPLED_TEXT_CHARS\t{report.sampled_text_chars}")
        print(f"LOCAL_TEX\t{report.local_tex or '-'}")
        print(f"IMPORTED_SOURCE_TEX\t{report.imported_source_tex or '-'}")
        print(f"EXTRACTED_TEXT\t{report.extracted_text or '-'}")
        print(f"ARXIV_ID\t{report.is_arxiv_id}")
        print(f"CLASSIFICATION\t{report.classification}")
        print(f"REASON\t{report.reason}")
        print(f"NEXT_ACTION\t{report.next_action}")


def emit_json(reports: list[PdfReport]) -> None:
    payload = {
        "root": to_repo_rel(paper_root()),
        "pdf_count": len(reports),
        "summary": build_summary(reports),
        "reports": [asdict(report) for report in reports],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify active paper PDFs into local-source, source-first, and reconstruction buckets."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional PDF files or directories. Defaults to paper/*.pdf.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of the default tab-separated text output.",
    )
    parser.add_argument(
        "--max-sample-pages",
        type=int,
        default=5,
        help="Number of leading pages to sample for text-layer detection.",
    )
    args = parser.parse_args()

    if args.max_sample_pages < 1:
        raise SystemExit("--max-sample-pages must be at least 1")

    reports = [inspect_pdf(pdf_path, max_pages=args.max_sample_pages) for pdf_path in iter_pdfs(args.paths)]
    if args.json:
        emit_json(reports)
    else:
        emit_text(reports)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())