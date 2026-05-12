---
name: theory-paper-to-tex
description: 'Use when: organizing math papers, converting PDFs to TeX or structured notes, extracting theorem cards, reading Teorth blueprint material, or preparing literature-search outputs.'
argument-hint: 'Provide the paper path, URL, or theory topic.'
---

# Theory Paper To TeX

Use this workflow for turning papers and blueprints into solver-facing theory assets.

## Procedure

1. Scope the request first. For this repo, active paper work means top-level `paper/*.pdf` unless the user explicitly asks for `stage1/paper/` archaeology.
2. Run the repo-local preflight before extracting:

    ```powershell
    c:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe paper/tools/pdf_preflight.py --max-sample-pages 5
    ```

3. Prefer source-first recovery in this order: existing local `.tex` sibling, imported upstream/arXiv source tree, then PDF text-layer reconstruction. Imported arXiv sources belong under `paper/arxiv_sources/<arxiv-id>/` with the original archive kept as `paper/arxiv_sources/<arxiv-id>.src`.
4. For `paper/blueprint.pdf`, use the local upstream source at `../equational_theories/blueprint/src`, imported under `paper/blueprint_source/`, instead of the PDF text-layer scaffold.
5. Use the private math tooling in `../math-priv/skills/pdf-to-latex/scripts/` for patterns and helper behavior when needed, but keep reproducible wrappers and generated outputs in this repo.
6. If only a PDF text layer is available, use `paper/tools/pdf_to_tex.py` to write `<stem>_extracted.txt` and, when requested, a split scaffold. Treat generated verbatim scaffolds as review aids, not high-fidelity source TeX.
7. Create theory cards only when requested. For extraction-only requests, preserve provenance and do not expand into theorem-card work.
8. Store notes under `paper/` or `stage2/docs/` with clear provenance.

## Compile Checks

- `latexmk` is currently unreliable on this Windows machine because Strawberry Perl reports a library/executable version mismatch. Use direct `pdflatex`/`bibtex` commands until that local toolchain is fixed.
- Always compile into a build directory. Never compile a generated TeX file in-place when it shares the source PDF stem, because `pdflatex blueprint.tex` will write `blueprint.pdf` and can overwrite the tracked source PDF.

  ```powershell
  Push-Location paper
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build blueprint.tex
  Pop-Location
  ```

- For arXiv source trees with bibliographies, run `pdflatex`, then `bibtex` from the build directory, then enough `pdflatex` passes to clear undefined citations and cross-reference rerun warnings. If BibTeX cannot find the `.bib` file because of `-output-directory`, copy the `.bib` into the build directory or adjust the source path explicitly.

## Guardrails

- Do not replace human-readable math with lossy OCR if source TeX exists.
- Preserve source PDFs. If a compile accidentally rewrites one, restore it before continuing and switch back to `-output-directory=build`.
