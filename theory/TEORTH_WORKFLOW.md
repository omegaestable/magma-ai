# Teorth Workflow

This guide is the cache-first path from a solver gap to a judge-accepted Stage 2 certificate motif. Teorth, papers, and proof pages provide provenance and ideas; the official Lean judge is still the proof standard.

## Source Map

Primary local caches:

- `data/exports/equations.txt`: shared equation catalog.
- `data/exports/export_raw_implications_14_3_2026.csv`: raw implication export used for graph and pair analysis.
- `data/teorth_cache/graph.json`: Teorth implication matrix cache.
- `data/teorth_cache/full_entries.json`: proof/provenance metadata cache.
- `data/teorth_cache/duals.json`: dual equation map.
- `data/teorth_cache/smallest_magma.txt`: finite magma witness hints.
- `data/teorth_cache/proof_page_cache/`: cached proof-page HTML and crawl artifacts.
- `paper/`: TeX and extracted-paper notes for construction families and theorem context.

Primary live reference:

- `https://teorth.github.io/equational_theories/implications/`

The live implication explorer has an Equation Explorer, downloadable CSV-style views, a raw implications table, and an upstream commit/timestamp. Use it for manual exploration and explicit cache syncs. Never make submitted solver behavior depend on live network access.

## Gap To Motif Loop

1. Identify the gap.

   Start from official runner output or a date-stamped ledger under `stage2/results/`. Record the problem id, equation ids, expected answer if available, generated route if any, and judge status.

2. Map equations to Teorth ids.

   Prefer explicit `eq1_id` and `eq2_id` from Stage 2 problem rows when present. If mapping from equation text, normalize against `data/exports/equations.txt` with the helpers in `theory/tools/v21_data_infrastructure.py`.

   Be careful about index base. Local catalogs and Stage 2 rows can be zero-based, while Teorth proof-page URLs are displayed as `EquationN` pairs. Record both forms in notes when scraping or copying links.

3. Query graph status, duals, and provenance.

   Use `graph.json`, `full_entries.json`, and `duals.json` before scraping. Classify each pair as explicit proof, implicit proof, conjecture, false witness, or unknown. Dualize promising FALSE witnesses and TRUE motifs when the operation is mathematically valid and the Lean rendering remains standalone.

4. Inspect cached proof pages.

   Look in `data/teorth_cache/proof_page_cache/` first. If the needed proof page is absent, scrape a small focused pair list rather than crawling broadly. Store outputs under a date-stamped directory outside the submitted solver path.

5. Classify the construction family.

   Use proof-page text, `full_entries.json`, and paper notes to classify the proof or countermodel. Examples: projection/constant collapse, affine or linear translation, finite table witness, normal-form/canonizer proof, lifted magma construction, or exceptional hard case.

6. Translate into a solver route.

   FALSE candidates should become semantic witness checks first, then named tables or formulaic families. TRUE candidates should become standalone Lean proof templates or a small deterministic rewrite derivation. Do not import Teorth theorem names into submitted certificates unless the official judge explicitly allowlists them.

7. Validate locally and officially.

   Run a local semantic check before emitting a certificate. Then validate with the official runner, or for direct debugging call `verify_answer(_to_judge_problem(problem), raw_answer)` so the check uses the pipeline proof policy. A plain `verify_answer(problem, ...)` is not runner-equivalent.

8. Promote only with evidence.

   Add the route or witness to `stage2/solver/solver.py`, package it, run focused official smokes, and store durable summaries under `stage2/results/` before updating top-level benchmark claims.

## Tool Commands

Run these from PowerShell at the repo root unless the command changes directory explicitly.

Check local Teorth cache status:

```powershell
Push-Location theory\tools
..\..\.venv\Scripts\python.exe fetch_teorth_data.py --check
Pop-Location
```

Refresh Teorth cache deliberately, with network access:

```powershell
Push-Location theory\tools
..\..\.venv\Scripts\python.exe fetch_teorth_data.py --force
Pop-Location
```

Certify graph/provenance status for a benchmark file:

```powershell
Push-Location theory\tools
..\..\.venv\Scripts\python.exe teorth_true_proof_agent.py certify-benchmark --input ..\..\data\stage2_official_problems\hard3.jsonl --output ..\..\stage2\results\teorth-hard3-certification.jsonl
Pop-Location
```

Scrape a focused proof-page pair list:

```powershell
Push-Location theory\tools
..\..\.venv\Scripts\python.exe proof_scraping_lab.py `
  --pairs "310,118;118,310" `
  --out-prefix ..\..\stage2\results\proof_lab\focused_pairs
Pop-Location
```

Classify a proof-page crawl into construction families:

```powershell
Push-Location theory\tools
..\..\.venv\Scripts\python.exe proof_construction_atlas.py `
  --crawl-jsonl ..\..\stage2\results\proof_lab\focused_pairs.jsonl `
  --out-prefix ..\..\stage2\results\proof_lab\focused_pairs_atlas
Pop-Location
```

Validate problem-set paths and cache policy:

```powershell
.\.venv\Scripts\python.exe theory\tools\smoke_problem_sets.py
```

## Motif Card Convention

Use one small card per reusable proof or witness family. Store durable cards in `stage2/docs/` or a date-stamped `stage2/results/` analysis file when they are tied to benchmark evidence.

Template:

```text
Name:
Verdict lane: TRUE or FALSE
Source pairs:
Teorth status: explicit proof / implicit proof / conjecture / false witness / unknown
Source artifacts: graph cell, proof-page URL or cache path, full_entries record, paper section
Family trigger: syntactic or semantic condition in Stage 2 problem rows
Lean rendering sketch: standalone imports and proof shape, no forbidden theorem imports
Local semantic check: equation evaluator, witness table validation, or rewrite-chain validation
Official evidence: runner command, problem ids, accepted count, judge status
Expected coverage: benchmark files or ledger rows likely affected
Blockers:
```

Promotion rule: Teorth can justify why a route is worth building, but only runner-accepted standalone Lean certificates justify adding it to the solver.

## FALSE Witness Promotion

1. Extract the candidate table or formula from Teorth, paper notes, or finite search.
2. Verify locally that the table satisfies the hypothesis and refutes the goal for the target pair and nearby variants.
3. Check duals and renamed-variable stability where applicable.
4. Emit a `finOpTable`/`decideFin!` certificate and run the official Solo runner on focused fixtures.
5. Add compact reusable witnesses to `WITNESS_TABLES` only after accepted evidence. Keep brute-force bound increases separate from named witness capacity.

Expensive `decide` goals need higher Lean recursion depth, and the axis is the decide cost `n ** variables`, not the order. The solver emits `set_option maxRecDepth 20000` when the order is 7 or more **or** when the goal costs more than 4,096 `decideFin!` applications; a `Fin 6` table against a 5-variable goal (7,776) is judge-rejected without it and accepted with it (2026-08-11). Above order 10 the `finOpTable` digit parser cannot express the table at all — those certificates render as an inlined `List.getD` lookup instead, judge-accepted to order 25.

## TRUE Motif Promotion

1. Extract the proof idea from graph/proof-page/paper provenance.
2. Reduce it to a local syntactic trigger or a bounded semantic search, such as substitution, symmetric rewrite, bridge/constancy, or subterm congruence.
3. Render an explicit standalone Lean proof using only judge-available imports and tactics.
4. Validate with the official runner before broadening the trigger.
5. Track misses and rejects separately; a plausible Teorth theorem name is not a submitted proof.

## Evidence Boundaries

- Canonical full public benchmark claims come from date-stamped `stage2/results/` summaries generated after full `normal/hard1/hard2/hard3` runs.
- Smoke evidence such as `sample_20`, `sample_200`, targeted fixtures, and Marathon slices belongs in smoke docs or a date-stamped note until a full benchmark refresh is performed.
- `tmp_stage2_smoke/` is disposable local debugging output.
- The submitted `solver.py` cannot read repo-local caches, scrape Teorth, or use local secrets. Any knowledge from these sources must be distilled into deterministic code or official LLM calls allowed by the runner.
