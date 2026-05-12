#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path


CONTROL_GLYPH_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
SUSPICIOUS_OPERATOR_GLYPHS = frozenset(("\u0000", "\u0001", "\u0002", "\u0003", "\u0008", "\u000f", "\u0011", "\u0012", "\u0013", "\u0014", "\u0015", "\u0016"))


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def to_repo_rel(path: Path) -> str:
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


def resolve_pdf(value: str) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = repo_root() / candidate
    candidate = candidate.resolve()
    if not candidate.exists() or candidate.suffix.lower() != ".pdf":
        raise SystemExit(f"Missing PDF: {candidate}")
    return candidate


def default_text_output(pdf_path: Path) -> Path:
    return pdf_path.with_name(f"{pdf_path.stem}_extracted.txt")


def default_tex_output(pdf_path: Path) -> Path:
    return pdf_path.with_suffix(".tex")


def default_parts_dir(tex_path: Path) -> Path:
    return tex_path.with_name(f"{tex_path.stem}_parts")


def ensure_writable(path: Path, *, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"Refusing to overwrite existing file without --force: {to_repo_rel(path)}")
    path.parent.mkdir(parents=True, exist_ok=True)


def chunk_ranges(page_count: int, chunk_size: int) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start = 1
    while start <= page_count:
        end = min(page_count, start + chunk_size - 1)
        ranges.append((start, end))
        start = end + 1
    return ranges


def normalize_text(text: str) -> str:
    replacements = {
        "\u0085": "fi",
        "\u0087": "fl",
        "\u0091": "'",
        "\u0092": "'",
        "\u0093": '"',
        "\u0094": '"',
        "\u0096": "-",
        "\u0097": "--",
        "\u00a0": " ",
        "\u0000": " ",
        "\u0016": " * ",
        "∈": " in ",
        "∩": " cap ",
        "∪": " cup ",
        "≤": " <= ",
        "≥": " >= ",
        "≠": " != ",
        "≈": " ~= ",
        "→": " -> ",
        "←": " <- ",
        "↔": " <-> ",
        "⇒": " => ",
        "⇔": " <=> ",
        "◇": " <> ",
        "□": " [] ",
        "α": "alpha",
        "β": "beta",
        "γ": "gamma",
        "δ": "delta",
        "ε": "epsilon",
        "λ": "lambda",
        "μ": "mu",
        "π": "pi",
        "σ": "sigma",
        "τ": "tau",
        "φ": "phi",
        "ω": "omega",
    }
    for raw, clean in replacements.items():
        text = text.replace(raw, clean)

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = CONTROL_GLYPH_RE.sub(" ", text)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.replace(r"\end{verbatim}", r"\textbackslash{}end{verbatim}").strip()


def risk_flags(raw_text: str, normalized_text: str) -> list[str]:
    flags: list[str] = []
    if any(token in raw_text for token in SUSPICIOUS_OPERATOR_GLYPHS):
        flags.append("suspicious-operator-substitution")
    if sum(normalized_text.count(token) for token in ("=", "\\", "<", ">", "->", "<->", "=>")) >= 10:
        flags.append("dense-math")
    if re.search(r"(^|\n)(Figure|FIGURE|Table|TABLE|Lemma|LEMMA|Theorem|THEOREM)\b", normalized_text):
        flags.append("figure-or-structure")
    return flags


def render_page_block(page_number: int, raw_text: str) -> str:
    normalized = normalize_text(raw_text)
    if not normalized:
        return (
            f"% --- Source PDF page {page_number} ---\n"
            "% Flags: blank-page\n"
            "\\mbox{}\n"
            "\\clearpage\n"
        )

    flags = risk_flags(raw_text, normalized)
    flag_line = ", ".join(flags) if flags else "none"
    return (
        f"% --- Source PDF page {page_number} ---\n"
        f"% Flags: {flag_line}\n"
        "\\begingroup\n"
        "\\small\n"
        "\\begin{verbatim}\n"
        f"{normalized}\n"
        "\\end{verbatim}\n"
        "\\endgroup\n"
        "\\clearpage\n"
    )


def write_extracted_text(output_path: Path, page_texts: list[str]) -> None:
    lines: list[str] = []
    for page_number, text in enumerate(page_texts, start=1):
        lines.append(f"=== Page {page_number} ===")
        lines.append("")
        lines.append(normalize_text(text))
        lines.append("")
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


def write_tex_scaffold(tex_path: Path, parts_dir: Path, pdf_path: Path, page_texts: list[str], chunk_size: int) -> None:
    parts_dir.mkdir(parents=True, exist_ok=True)
    part_names: list[str] = []

    for index, (start_page, end_page) in enumerate(chunk_ranges(len(page_texts), chunk_size)):
        part_name = f"{index:02d}_pages_{start_page:03d}_{end_page:03d}.tex"
        part_names.append(part_name)
        blocks = [render_page_block(page_number, page_texts[page_number - 1]) for page_number in range(start_page, end_page + 1)]
        (parts_dir / part_name).write_text(
            "\n".join(blocks).rstrip() + "\n",
            encoding="utf-8",
            newline="\n",
        )

    lines = [
        r"\documentclass[11pt]{article}",
        "",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage{hyperref}",
        r"\usepackage{verbatim}",
        "",
        r"\begin{document}",
        "",
        f"% Source PDF: {to_repo_rel(pdf_path)}",
        "% Machine-transcribed baseline scaffold from the PDF text layer.",
        "% Review flagged pages before treating this as canonical source.",
        "",
    ]
    for part_name in part_names:
        lines.append(rf"\input{{{parts_dir.name}/{part_name}}}")
    lines.extend(["", r"\end{document}", ""])
    tex_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract a paper PDF into normalized text and an optional TeX scaffold."
    )
    parser.add_argument("pdf", help="PDF path to process.")
    parser.add_argument(
        "--write-extracted-text",
        action="store_true",
        help="Write a normalized <stem>_extracted.txt artifact.",
    )
    parser.add_argument(
        "--bootstrap-tex",
        action="store_true",
        help="Write a split TeX scaffold beside the PDF.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=20,
        help="Pages per generated part file when --bootstrap-tex is enabled.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output files.",
    )
    args = parser.parse_args()

    if not args.write_extracted_text and not args.bootstrap_tex:
        raise SystemExit("Specify at least one of --write-extracted-text or --bootstrap-tex")
    if args.chunk_size < 1:
        raise SystemExit("--chunk-size must be at least 1")

    pdf_path = resolve_pdf(args.pdf)
    reader_cls = load_pdf_reader()
    reader = reader_cls(str(pdf_path))
    page_texts = [page.extract_text() or "" for page in reader.pages]

    if args.write_extracted_text:
        text_output = default_text_output(pdf_path)
        ensure_writable(text_output, force=args.force)
        write_extracted_text(text_output, page_texts)
        print(f"EXTRACTED_TEXT\t{to_repo_rel(text_output)}")

    if args.bootstrap_tex:
        tex_output = default_tex_output(pdf_path)
        ensure_writable(tex_output, force=args.force)
        parts_dir = default_parts_dir(tex_output)
        if parts_dir.exists() and not args.force:
            raise SystemExit(f"Refusing to overwrite existing parts directory without --force: {to_repo_rel(parts_dir)}")
        write_tex_scaffold(tex_output, parts_dir, pdf_path, page_texts, args.chunk_size)
        print(f"TEX\t{to_repo_rel(tex_output)}")
        print(f"PARTS\t{to_repo_rel(parts_dir)}")

    print(f"PAGES\t{len(page_texts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())