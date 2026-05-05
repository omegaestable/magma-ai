---
name: teorth-graph-dive
description: 'Use when: exploring Teorth equations, implication graph paths, random equation dives, proof provenance, cached proof pages, finite magma hints, or implication explorer data.'
argument-hint: 'Provide equation ids, a pair, or ask for a random dive.'
---

# Teorth Graph Dive

Use this workflow to turn Teorth graph exploration into Stage 2 solver evidence.

## Data Sources

- `data/exports/equations.txt`
- `data/exports/export_raw_implications_14_3_2026.csv`
- `data/teorth_cache/graph.json`
- `data/teorth_cache/full_entries.json`
- `data/teorth_cache/proof_page_cache/`
- `data/teorth_cache/smallest_magma.txt`

## Procedure

1. Identify the equation or implication pair.
2. Load equation strings and known implication status.
3. Find direct proof provenance, graph paths, dual relationships, and witness hints.
4. Classify as true-proof candidate, false-witness candidate, unknown, or data-conflict audit.
5. Save useful findings as structured notes for later solver ingestion.

## Guardrails

- Teorth data guides generation; the official Lean judge decides acceptance.
- Do not hardcode private benchmark pairs as policy.
- Mark stale or conflicting data explicitly.
