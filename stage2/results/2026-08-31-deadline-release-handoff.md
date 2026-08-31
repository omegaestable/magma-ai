# Deadline release handoff — 2026-08-31

## Candidate artifact

- Source commit: `121efbea8b474fe99d6410f257d6aa1faa4b7700` before the
  uncommitted deadline-release changes.
- Packaged artifact: `stage2/submissions/solver.py`, **454,993 bytes**,
  SHA-256 `d301adea8132f964ff41aa50141de58db05fb4cdd248e16d2ee912230d914a70`.
- Submission note (kept outside the submission directory):
  `stage2/solver/SUBMISSION_NOTE.md`, SHA-256
  `a90fbe702dd51db90c1fb72355a7c94ccc1836e1371ed2a747fb531a636769e0`.
- The packager completed its AST-equivalence/minification check and the
  organizer layout validator.  The submission directory contains only
  `solver.py`.

## Shipped change

Removed the `fallback:marathon_grind` block.  It converted unresolved rows
with model-search telemetry into an unjudged TRUE certificate, contrary to the
release rule that every emitted certificate must be deterministic/oracle
validated or accepted through the official Solo judge loop.  The two
deterministic Marathon passes and proxy evidence bookkeeping remain unchanged.
`stage2/tests/test_pacing.py` now asserts that this telemetry emits no Marathon
answer.  Focused pacing regression: **20 passed**.

The package gate now directs pytest temporary files to the ignored
`stage2/results/pytest_package_gate` scratch area.  This repairs a managed
Windows runner failure caused by an unreadable shared `%TEMP%` pytest root; it
does not skip or relax the gate.

## Evidence obtained this release

- Python 3.11 source and artifact syntax checks: pass.
- Targeted regression suites: artifact/minifier **8 passed**, compliance and
  banned-token scan **15 passed**, FALSE certificates **19 passed**, and
  Marathon pacing **20 passed**.
- Secret scan, including untracked files: `secret_scan_ok`.
- Package/layout check: pass; size under the 500,000-byte cap.
- Public deterministic audit: **1,669/1,669**, zero crashes, zero oracle
  failures (`hard1` 69/69, `hard2` 200/200, `hard3` 400/400, `normal` 1000/1000).
- Unseen Order-5 ≤3-variable audit (10,000 rows): **9,915/10,000 solved**
  (2,163 TRUE; 7,752 FALSE), **85 skipped**, **0 crashes**, and **0 oracle
  failures**; aggregate solver time **19,561.2 s**.  The machine-readable
  record is `stage2/results/audit-order5-20260831-deadline-le3-10k.json`.
- HF audit completed for extra-hard, hard, and normal: **600/600**, zero crashes
  and zero oracle failures.  The separate HF Order-5 all-set run completed:
  **200/200**, zero skips, crashes, and oracle failures.
- Official harness under the direct Lean 4.33.1 wrapper: Solo **70/70** plus
  all 92 public and 4 infrastructure attacks; Marathon **27 passed, 0 failed**.
- Full offline gate: **558 passed, 1 skipped** in 9m19s.

## Explicitly unresolved / not promotion evidence

- No live LLM smoke was run.  Use only a newly rotated key through the ignored
  local `.env` helper and record a positive token budget; never use a key pasted
  into chat history.
- No new Austin certificate was promoted.  `v38316.lean`/`v38316b.lean` retain
  five `sorry` cells; 23357's four-rule certificate remains refuted.  The
  image-of-`op` carrier is retired; see the updated current rails.
- The completed 10k Order-5 audit covers only ≤3-variable rows.  **Order-5
  ≥4-variable work and all Order-6 work are intentionally deferred to the next
  session, whose focus is Austin.**  Any future sweeps must be sequential,
  labelled where required, and accompanied by a dated result summary before any
  solver change.
- The reproducible workspace-local pytest scratch directories could not be
  removed because this managed filesystem denied deletion.  They are outside
  the submission directory and contain no release artifact or evidence.
