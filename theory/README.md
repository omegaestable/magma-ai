# Theory Workspace

This directory is for reusable mathematical assets that survive the Stage 1 to Stage 2 reset.

## Canonical Data

- `data/exports/equations.txt`: equation catalog.
- `data/exports/export_raw_implications_14_3_2026.csv`: implication data.
- `data/hf_cache/`: canonical local mirror of Hugging Face problem subsets.
- `data/stage2_official_problems/`: canonical local mirror of vendored Stage 2 public problem files.
- `data/teorth_cache/graph.json`: Teorth implication graph cache.
- `data/teorth_cache/full_entries.json`: proof/provenance entry cache.
- `data/teorth_cache/proof_page_cache/`: cached proof pages.
- `data/teorth_cache/smallest_magma.txt`: finite magma witness hints.

## Problem Set Policy

- `data/hf_cache/normal|hard|hard1|hard2|hard3` are active root-cache problem corpora for theory analysis.
- `data/hf_cache/evaluation_*` subsets are imported and validated, but treated as analysis-only until explicitly promoted into a benchmark or evaluation workflow.
- `data/stage2_official_problems/` is the runner-facing mirror for official Stage 2 public fixtures and should remain aligned with `vendor/stage2-official/examples/problems/`.

## Tools

Reusable theory and proof-mining scripts live under `theory/tools/`. Some scripts were migrated from the Stage 1 root and may still need import-path cleanup before direct execution.

## Stage 2 Theory Products

Create these as work proceeds:

1. Teorth graph index with shortest paths and proof provenance.
2. Finite magma witness library with Lean certificate generation.
3. True-proof motif cards with standalone Lean translation sketches.
4. Literature notes from papers and the Teorth blueprint.
5. Random equation dive logs that feed the solver, not just chat history.

## Guardrail

The official Stage 2 judge is self-contained. Teorth data can guide proof generation, but submitted certificates must compile in the official judge environment.
