# Cleanup and Archive Manifest

Updated: 2026-08-30 (final cleanup executed after all release gates)

This manifest records the measured pre-cleanup inventory, the recoverable
archives created, and the generated material removed. Use it before any future
cleanup commit so raw artifacts are not lost accidentally.

## 2026-08-30 completed cleanup

- Compressed 280 ignored shard files from four completed order-4 campaigns:
  560,024,985 raw bytes to 36,708,652 archive bytes. Exact per-campaign counts,
  byte totals, and hashes are in `stage2/results/raw/MANIFEST.md`.
- Archived the entire ignored `tmp_stage2_smoke/` tree after the final runner
  checks: 21,226 files / 122,469,288 B to a verified 35,786,384 B ZIP,
  SHA-256 `4401f58ffc67d649e40a80152dfa38d3943b6db0d5659eb61c283f72ef9e26ae`,
  then removed the source tree. This includes the final Solo-20 and
  positive-budget Marathon-5 raw outputs.
- Removed `vendor/stage2-official/.artifacts/` only after both official
  harnesses and both packaged-solver runner checks passed: 8,823 files /
  354,129,163 B. It is regenerable by the judge.
- Removed repo-side `__pycache__`, `.pytest_cache`, `.ruff_cache`, `chain.log`,
  and `stop_after_b08.log`. Virtual-environment and `.lake` caches were not
  touched.
- Added an Austin notebook index instead of deleting research files. Session 8
  demonstrated that underscore-prefixed and apparently failed artifacts can
  contain complete proofs.

## 2026-08-30 pre-cleanup disk inventory

Before cleanup, the working tree was **7,983,088,854 B across 152,246 files** when
ignored build and scratch output is included. Tracked content is **195,212,538 B
across 3,025 files**. The dominant size is generated infrastructure, not source:

| Path | Bytes | Files | Disposition |
| --- | ---: | ---: | --- |
| `vendor/stage2-official/.lake/` | 7,624,619,406 | 143,317 | **Keep.** Required Lean/Mathlib build cache; do not rebuild or delete before upload. |
| `vendor/stage2-official/.artifacts/` | 353,634,665 | 8,698 | Removed after final judge pass; regenerates on demand. |
| `.venv/` | 456,241,912 | 17,378 | Local Python 3.14 environment; retained, not a release gate. |
| `.venv311/` | 123,088,354 | 6,143 | Python 3.11 release environment; retained. |
| `tmp_stage2_smoke/` | 122,672,590 | 21,242 | Archived in full and removed after final validation. |
| `stage2/experiments/austin/automata/gen/` | 9,475,103 | 1,670 | Active research workspace; archive scratch only after session 8 is frozen. |
| `data/` | 126,548,145 | 318 | **Keep.** Benchmark, graph, and provenance data. |
| `paper/` | 18,445,060 | 150 | **Keep.** Source papers and generated reading artifacts. |

The tracked Austin `gen/` subset is 1,442 files / 8,494,140 B. A filename-based
scratch pass identifies 1,161 files / 5,637,186 B, but that bucket includes
useful `NOTES_*` and large research proofs; it is **not** a safe delete set.

The largest tracked mathematical assets are the full implication export
(57.9 MB), closure export (23.9 MB), outcome matrix (22.0 MB), and Teorth graph
cache (9.1 MB). They are provenance inputs for the full order-4 graph pass and
must not be shed as “junk.”

## Historical 2026-07-29 measured disk inventory

The working tree is **~7.4 GB across ~154k files**. Almost none of it is tracked
content, but it is why `du`/`find` at the repo root hang and why unscoped file
searches are slow.

| Path | Size | Files | Verdict |
| --- | ---: | ---: | --- |
| `vendor/stage2-official/.lake` | 7.06 GB | 117,609 | **Keep.** Lean + Mathlib build cache; it is what makes the local Lean judge work. Gitignored. |
| `tmp_stage2_smoke/` | 103 MB | 20,747 | Prunable scratch, gitignored. See below. |
| `vendor/stage2-official/.artifacts` | 57 MB | 15,573 | Prunable judge run artifacts, regenerated on demand. Gitignored. |
| `data/` | 103 MB | 311 | Keep — benchmark problems, ETP exports, Teorth cache. |
| `stage1/` | 25 MB | 340 | Keep as archive. |
| `paper/` | 18 MB | 150 | Keep — upstream ETP reading material. |
| `stage2/` | 13 MB | 266 | Keep — active work. |

### Removed 2026-07-29

- `.agents/` — empty directory, referenced by nothing.
- `Untitled-1.md` — a bare URL already present in `README.md`'s external links.

### Removed 2026-08-13

- `.git/logs/errorsaug.py` — a pasted error log saved with a `.py` extension
  inside `.git/`. It was not a source file and nothing referenced it, but
  `ruff.toml` used `exclude` (which *replaces* ruff's defaults) instead of
  `extend-exclude`, so ruff walked into `.git/` and reported 443 invalid-syntax
  errors from it, keeping CI Lint red. Backed up outside the repo before
  deletion; the `ruff.toml` key was fixed in the same pass.

### Executed after final validation

The following former recommendations were completed with path validation and
archive verification. Recovery is now:

```powershell
# Restore ignored scratch evidence when needed.
Expand-Archive stage2/results/raw/tmp-stage2-smoke-through-2026-08-30.zip tmp_stage2_smoke

# Judge artifacts regenerate on the next verify_answer call; do not restore them.
```

The source scratch tree and judge artifacts were removed only after the final
evidence had been summarized and the archive had been verified.
Do **not** touch `vendor/stage2-official/.lake`: rebuilding Mathlib costs hours.

## Completed Archive Batches

| Batch | Manifest | Summary | Notes |
| --- | --- | --- | --- |
| 2026-05-20 optimization readiness | `stage2/results/archive/optimization-readiness-2026-05-20/MANIFEST.md` | `stage2/results/2026-05-20-optimization-readiness.md` | Moved summarized optimization profiles, legacy no-LLM Marathon runs, aborted Solo attempts, and positive-token parity output out of `tmp_stage2_smoke/`. |
| 2026-05-25 generated bytecode cleanup | n/a | `stage2/results/2026-05-25-cleanup-and-smoke.md` | Removed repo-side `__pycache__` directories generated by local tests; left `.venv/` caches alone. |
| 2026-05-25 tracked LaTeX build cleanup | n/a | `stage2/results/2026-05-25-cleanup-and-smoke.md` | Removed tracked build byproducts already covered by `.gitignore`; kept source TeX, PDFs, figures, and bibliographies. |
| 2026-08-30 competition readiness | `stage2/results/raw/MANIFEST.md` | `stage2/results/2026-08-30-competition-readiness.md` | Archived completed order-4 shards and all ignored smoke output; removed judge artifacts and caches after final gates. |

## Policy

- Do not delete dated result summaries under `stage2/results/`.
- Do not delete raw evidence that is the only source for a promoted claim.
- Prefer archive-with-manifest over deletion for judge artifacts and Marathon outputs.
- Treat `tmp_stage2_smoke/` as scratch; archive and hash it before removal when it contains unique evidence.
- Ask before deleting or moving anything outside `tmp_stage2_smoke/`.

## Keep In Place

| Path / pattern | Reason |
| --- | --- |
| `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md` | Historical public baseline; includes now-disabled grind wins and must remain caveated. |
| `stage2/results/2026-05-17-hard-mix-witness-summary.md` | Compact witness provenance for S4D/S4E/S5D. |
| `stage2/results/2026-05-17-homelab-openrouter-proxy-smoke.md` | Local OpenRouter/proxy transport precedent. |
| `stage2/results/2026-05-15-theory-diagnosis.md` | Teorth proof-page and finite-model diagnosis. |
| `stage2/experiments/*.py` | Active tooling unless a future audit marks a script obsolete. |
| `stage2/docs/solver-route-ledger.md` and `stage2/docs/motif-cards/` | Current route review artifacts. |

## Suggested Future Archive Manifest Format

```text
# Archive Batch YYYY-MM-DD

Source: tmp_stage2_smoke/<path>
Destination: stage2/results/archive/<path>
Reason: <obsolete tuning | representative smoke | grind archaeology | witness tuning>
Summary artifact: stage2/results/<dated-summary>.md or none
Safe to delete later: yes/no
```

## Current disposition

The approved cleanup is complete. No branch, environment, `.lake` content,
tracked mathematical asset, fixture, accepted certificate, paper, or Austin
research source was deleted. Future cleanup again requires an inventory and a
fresh evidence-retention decision.
