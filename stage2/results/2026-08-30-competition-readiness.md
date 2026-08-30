# Competition readiness and repository cleanup — 2026-08-30

## Outcome

The Stage 2 repository is ready for the final competition submission and for a
solver-focused follow-up session. This pass changed rails, tooling,
documentation, experiment organization, and generated-output retention; it did
**not** edit `stage2/solver/solver.py` or alter solver policy.

The organizer's public repository was checked on 2026-08-30. Its `main` branch
still ended at `817a4653bf762584931d49c6714c9fcfab7df66a`, matching the vendored
snapshot. Live `pipeline/config.json`, `lean-toolchain`, and
`rules/evaluation.md` match the local 500,000-byte solver cap, 100,000-byte Lean
code cap, 20,000-byte FALSE cap, 300-second per-Lean-phase timeout, Solo 3,600
seconds, Marathon `N × 300` seconds / `N × 32768` tokens, model allowlist, and
Lean/Mathlib 4.33.1 environment.

## Final artifact

| Item | Measurement |
| --- | --- |
| Source | 1,516,437 B; SHA-256 `b4a16e67baf44b224e4a73af24a73a23463d9725467828e9650a01bc4edc1093` |
| Packaged `solver.py` | 456,604 B; SHA-256 `784f5ce2e7aed8dfbed87de84fd5808cae425fb14969cbc978362c8b2770c5f4` |
| Headroom | 43,396 B (8.68%) |
| Submission layout | exactly `solver.py`; official layout validator accepted |
| Generated-data disclosure | 15 packed payloads disclosed; `PROMPT` remains a top-level unpacked string |
| Fixture | 1,154,719 B; 238 pins; SHA-256 `ec50b4d568723b1f848364acaf633267d305f361eb789c11f8234004f48be22e` |

The rebuilt artifact hash is identical to the pre-cleanup session-8 artifact,
so the surrounding-repository work did not perturb the submitted program.
Submit it together with `stage2/solver/SUBMISSION_NOTE.md`.

## Validation

| Gate | Result |
| --- | --- |
| `ruff check .` | all executable-code checks passed |
| Offline pytest, standalone | 558 passed, 1 expected skip in 529.76 s |
| Canonical packager gate | 558 passed, 1 expected skip in 526.80 s; package and official layout checks passed |
| Standing spot-check | 90/90 across nine sources; seed 1788102804; 0 skips/misses |
| Official Solo harness | all buckets green: 70 cases, 24 banned-token cases, 33 judge-internal, 7 loader, 57 pipeline, 11 CLI, 4 repeatability, 4 verify-branch, 92 public attacks, 4 infrastructure attacks |
| Official Marathon harness | 27 passed, 0 failed; Lean enabled |
| Packaged artifact, official Solo | sample 20: 20/20 accepted, 0 failed, 69.3 s, 0 LLM calls |
| Packaged artifact, official Marathon | normal 5: 5/5 accepted, positive 163,840-token budget, 0 tokens used, 1.0 s wall |
| Readiness preflight | official limits/toolchain, layout, syntax, prompt, disclosure, current docs, eq-size-5 mirror, secret-shaped tracked files, and fixture all pass |
| Markdown pass | 287 files checked one by one; 74 local links; 0 broken, 0 encoding errors, 0 missing final newlines |

The Marathon smoke deliberately retained a positive token allowance even
though deterministic routes solved every row. It is valid runner evidence; no
zero-token-budget run was used or promoted.

## Cleanup and standardization

- Replaced the stale hard-coded preflight report generator with a read-only
  readiness audit. It writes only when `--json-out` is explicit and checks new
  untracked/unignored Markdown before commit.
- Standardized active commands and the packager on `.venv311`; packaging now
  fails clearly under a non-3.11 interpreter.
- Corrected current docs for Lean 4.33.1, the removed Marathon compression
  ratio, current budgets, artifact size, fixture state, and the packer's 15
  payloads. Stage 1's V25A prompt is explicitly archived.
- Scoped lint to executable code. The Austin notebook is excluded because it
  intentionally contains partial generators and non-module fragments; five
  current diagnostic scripts were fixed and the resulting production lint is
  clean.
- Indexed the Austin lab and its `gen/` notebook with canonical entry points,
  evidence labels, and retention rules. No proof or experiment source was
  removed.
- Moved ignored completed output into verified local ZIPs. Exact counts,
  uncompressed bytes, archive bytes, hashes, and recovery instructions are in
  [`raw/MANIFEST.md`](raw/MANIFEST.md). These archives are ignored local
  reproducibility aids, not submission contents.
- Removed 354,129,163 B of regenerable judge artifacts after validation, plus
  Python bytecode and test/lint caches. The 7.62 GB Lean/Mathlib `.lake` cache,
  both Python environments, data exports, Teorth caches, papers, fixtures, and
  accepted certificates remain.

## Remaining administrative state

- `main` began one commit ahead of `origin/main`; the readiness changes are
  intentionally uncommitted for review.
- One unmerged experimental ref remains:
  `worktree-wf_2be84d37-297-3` at `c58c29e`. It contains a solver completion
  experiment and was neither merged nor deleted during a no-solver-edit pass.
- `.venv` is Python 3.14 and retained; `.venv311` is the competition release
  environment. Do not substitute the former in final gates.

## Solver-focused handoff

Read `CLAUDE.md`, then
[`DEEP_SESSION_8_AUSTIN_HANDOVER.md`](../docs/DEEP_SESSION_8_AUSTIN_HANDOVER.md),
then
[`LEMMA_LIBRARY.md`](../experiments/austin/automata/gen/LEMMA_LIBRARY.md).
Run the zero-sorry harvest scan first. Then close the four compiling,
one-lemma-set families (11 rows total) before returning to the anchored/image-
of-`op` carrier, whose shared leverage is about 25 of the remaining 40 Austin
rows; 9663 is the best first test case. Preserve the twelve-rung validation
ladder and independent judge verification before any splice.
