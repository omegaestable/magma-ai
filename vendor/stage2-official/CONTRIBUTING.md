# Contributing

This repository is a Lean competition judge plus an LLM-driven evaluation
pipeline. Maintenance priorities, in order, are:

1. **Correctness** of contestant verdicts.
2. **Determinism** of the judge across repeated runs.
3. **Sandbox and secret isolation** in the solver runner.
4. **Public-contract consistency** (status mapping, JSON schemas, CLI
   surface, README, rules under `rules/`).
5. **Harness coverage** — every behavioral guarantee must be locally
   testable via `python3 scripts/run_harness.py`.

Contributions that strengthen these are welcome. Contributions that
compromise them, or that cannot be evaluated against them, are not.

## TL;DR

**Open an issue first. Do not open a pull request before the issue is
filed and acknowledged**, with the narrow exceptions listed under
[Trivial fixes](#trivial-fixes). This project aligns on problem
definition, semantic edges, and compatibility impact *before* code is
written — not after.

"Write the code first, discuss later" is not how this repository
operates.

## Issue-first policy

All non-trivial changes must start as a GitHub issue. The following
categories require an issue regardless of patch size:

- Correctness bugs in the judge, harness, pipeline, or sandbox.
- Changes to judge verdict semantics or the public five-status mapping
  (`accepted` / `unparsed` / `malformed` / `incomplete_proof` /
  `incorrect`).
- Changes to the pipeline protocol — stdin/stdout JSON contract,
  `pipeline/config.json` schema, environment-variable surface, LLM
  routing behavior.
- Sandbox or security changes — process isolation, filesystem access,
  network policy, secret handling, dependency-allowlist rules.
- Harness coverage changes — new tests, removed tests, or fixture
  edits that alter what is asserted.
- Documentation changes that alter a documented behavior, contract, or
  example contestants rely on.
- Feature requests of any size.
- Performance changes touching hot paths (judge run loop, Lean
  elaboration, sandbox startup, LLM proxy).
- Architectural changes — new modules, new dependencies, new
  submission shapes, new certificate branches.

See [Trivial fixes](#trivial-fixes) for the exceptions.

## Bar for filing an issue

Before opening an issue:

1. **Search.** Check open issues, closed issues, and Discussions.
   Comment on the existing thread instead of duplicating.
2. **Reproduce on a current build.** Use the latest `main` or latest
   tagged release. Reports against unmerged branches will not be
   investigated.
3. **Minimize.** Strip the reproduction to the smallest input that
   still triggers the behavior — problem JSON, answer JSON, `solver.py`,
   and any config override needed. Inline the inputs or attach as a
   gist; do not link to private workspaces.
4. **State the contract.** For judge / pipeline / harness / sandbox
   reports, name the specific contract being violated: a clause in the
   README, a row in the status-mapping table, an explicit harness
   expectation, or a documented invariant. "It feels wrong" is not a
   contract.
5. **State expected vs. actual concretely.** Both must be verifiable.
   "It should work" is not an expected behavior.

Issues without reproduction, evidence, or contract justification will
be marked `needs-repro` / `needs-contract`, moved to Discussions, or
closed.

## Required fields for bug reports

Every bug report must include:

- **Commit, branch, or release tag** the bug reproduces on.
- **Affected module:** `judge`, `pipeline`, `docs`, or `harness`.
- **Issue type:** `correctness`, `determinism`, `sandbox`, `security`,
  `docs`, `coverage`, or `performance`.
- **Severity:** does this affect the public verdict path, harness exit
  code, or only an internal/dev surface?
- **Reproduction steps**, runnable end-to-end without manual edits.
- **Minimal repro inputs:** problem JSON, answer JSON, `solver.py` if
  relevant, and any config override.
- **Actual output:** exact text, including the `status` field, exit
  code, and any stderr.
- **Expected output:** exact text, or — for under-specified cases —
  the contract that determines the expectation.
- **Logs / stderr / traceback** for the failing run.
- **Why this is a bug, not intended behavior.** Cite the README, the
  status-mapping table, an existing harness expectation, or a
  comparable accepted issue.
- **Suggested regression test**, if you can identify where it would
  slot into the harness.

A report missing the inputs, the actual output, or the contract
justification is not actionable and will be returned with
`needs-repro` or `needs-contract`.

## Feature and enhancement requests

Feature issues must answer:

- **User value.** Who benefits, and in what concrete workflow?
- **Scope.** What is in, what is out. A bounded feature is
  reviewable; a vision statement is not.
- **Public-contract impact.** Does it change status semantics, JSON
  schemas, CLI flags, environment variables, or harness expectations?
- **Backward compatibility.** Does it break existing solvers,
  contestant submissions, or the documented status mapping?
- **Ownership.** Are you proposing to implement, co-implement, or only
  to request?

Open-ended ideas, "wouldn't it be nice if…" suggestions, and unscoped
wishlists belong in Discussions. Maintainers will move them.

## Pull requests

- **Every non-trivial PR must reference a prior issue.** PRs without
  one may be closed with a request to file an issue first.
- **Correctness changes require tests.** Add or update fixtures under
  `tests/` and ensure `python3 scripts/run_harness.py` exits `0`.
- **Behavior-changing PRs update documentation in the same change
  set.** README, the per-track tutorials
  (`examples/solo/TUTORIAL.md`, `examples/marathon/TUTORIAL.md`),
  the per-track specs under `docs/` (`docs/solo_mode.md`,
  `docs/marathon_mode.md`), status-mapping tables, and any rule
  files under `rules/` must stay aligned with the code.
- **One topic per PR.** Do not bundle unrelated refactors with a fix.
  Drive-by cleanup belongs in its own issue and PR.
- **Keep PRs small.** Large rewrites without prior issue alignment
  will be returned.
- **Compatibility impact statement.** PRs touching judge verdict
  semantics, the pipeline protocol, sandbox behavior, or any
  documented public contract must state, in the PR description:
  - what changes for existing solvers,
  - what migration (if any) is required,
  - which fixtures or harness tests demonstrate the new behavior.
- **No skipping hooks or signing.** Do not push with `--no-verify`,
  `--no-gpg-sign`, or equivalent. If a hook fails, fix the cause.
- **Determinism.** PRs that introduce non-determinism — random seeds,
  time-dependent logic, network access in tests — will be rejected.

## Triage and closing

Maintainers use the following labels and actions:

- `needs-repro` — no reproduction, or non-minimal reproduction.
  Author has 14 days to respond before the issue is closed.
- `needs-contract` — no statement of which documented contract is
  violated. Same 14-day clock.
- `discussion` — open-ended; moved to Discussions.
- `duplicate` — closed with a pointer to the canonical issue.
- `stale` — no maintainer-actionable update for 30 days; closed.

Maintainers reserve the right to close issues that are low-quality,
unscoped, or not actionable, regardless of label. Reopen requests are
welcome once new evidence is provided.

## Project-specific emphasis

This project holds a stronger line than typical open-source on:

- **Determinism.** A change that produces different outputs across
  repeated runs of the same input is a regression, even if both
  outputs look "correct".
- **Exact status semantics.** The five public statuses are a contract.
  Do not collapse infrastructure failures into `incorrect`. Do not
  introduce new statuses without an issue and explicit acceptance.
- **Harness-backed regressions.** Every fix needs a test that would
  have caught the bug. "I tested it manually" is not coverage.
- **Sandbox and secret isolation.** Solver code runs untrusted.
  Changes that loosen process isolation, expand filesystem access, or
  expose environment variables to user-supplied code require explicit
  security review.
- **Docs-vs-behavior consistency.** When code and docs disagree, one
  of them is wrong. Both are fixed in the same PR.
- **Skepticism toward unsubstantiated correctness claims.** "I think
  there might be a bug in X" without a reproduction is held until
  evidence appears. Maintainers will not pre-investigate hunches; the
  issue bar applies.

## Security issues

Security-relevant findings — sandbox escapes, secret leaks, judge
bypasses that smuggle accepted verdicts past the contract, anything
that could affect contestant fairness — are welcome as **regular
public issues**, same bar as any other bug report (reproducer,
expected vs. actual, version / commit, normalized status if
applicable). Use the issue type label `security`.

If for some reason you'd rather report privately first, you can email
the maintainer at the address on the GitHub profile, but it is not
required and there is no embargo: filing publicly is the default and
fine.

## Trivial fixes

The following may go directly to a PR without a prior issue:

- Typo fixes in comments, docs, or strings.
- Pure copy-edits to README, the per-track tutorials
  (`examples/solo/TUTORIAL.md`, `examples/marathon/TUTORIAL.md`), or
  files under `rules/` that do not change a documented contract.
- Markdown or formatting cleanup with no semantic change.
- Test-only cleanup that does not change what is asserted.

If you are unsure whether your change qualifies, open an issue first.
The cost of one extra issue is much lower than the cost of an
unwanted PR.
