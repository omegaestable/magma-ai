---
name: theory-paper-to-tex
description: 'Use when: organizing math papers, converting PDFs to TeX or structured notes, extracting theorem cards, reading Teorth blueprint material, or preparing literature-search outputs.'
argument-hint: 'Provide the paper path, URL, or theory topic.'
---

# Theory Paper To TeX

Use this workflow for turning papers and blueprints into solver-facing theory assets.

## Procedure

1. Prefer upstream TeX or arXiv source tarballs when available.
2. If only a PDF exists, extract text first and convert selectively into notes or TeX.
3. Create theory cards with: statement, proof idea, Lean translation sketch, solver relevance, witness relevance, and source.
4. Separate competition-relevant proof templates from background reading.
5. Store notes under `paper/` or `stage2/docs/` with clear provenance.

## Guardrails

- The private math skills mentioned by the user were not found in this workspace during the initial reset; locate or import them before building a large PDF-to-TeX pipeline.
- Do not replace human-readable math with lossy OCR if source TeX exists.
