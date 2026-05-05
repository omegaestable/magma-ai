# Theory Workspace

This directory is for reusable mathematical assets that survive the Stage 1 to Stage 2 reset.

## Canonical Data

- `data/exports/equations.txt`: equation catalog.
- `data/exports/export_raw_implications_14_3_2026.csv`: implication data.
- `data/teorth_cache/graph.json`: Teorth implication graph cache.
- `data/teorth_cache/full_entries.json`: proof/provenance entry cache.
- `data/teorth_cache/proof_page_cache/`: cached proof pages.
- `data/teorth_cache/smallest_magma.txt`: finite magma witness hints.

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
