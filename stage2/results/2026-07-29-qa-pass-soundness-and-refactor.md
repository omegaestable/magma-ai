# 2026-07-29 — QA pass: soundness gaps, judge-verified pinning, dispatcher refactor

Full assessment of the repo (layout, math, algorithms, testing, agent
onboarding, competitiveness), then fixes. No new solver coverage was attempted;
this session was about making the existing coverage *provably* correct and making
the repo cheap to improve.

## Baseline reproduced

The documented headline is honest. A clean audit on unmodified code:

| Set | Solved | TRUE |
| --- | ---: | ---: |
| `normal` | 990/1000 | 491 |
| `hard1` | 64/69 | 24 |
| `hard2` | 176/200 | 92 |
| `hard3` | 387/400 | 183 |
| **Official total** | **1617/1669** | **790** |

`0` oracle failures, `0` crashes, 430 s on 16 workers. Documented value is
`1617/1669` TRUE `789`; TRUE came out at 790, inside the ±noise band the docs
already flag. `spotcheck.py` on 72 rows across 9 sources: 100% accuracy, 0
mistakes.

## Findings and fixes

### 1. `grind` inside a deterministic route (real risk, fixed)

`right_projection_from_2788_block()` emitted:

```lean
  have eq42 (X0 : G) : X0 ◇ (X0 ◇ X0) = X0 := by
    grind
```

plus `set_option maxHeartbeats 5000000`, inside
`true:right_projection_collapse:left_pair_tail`. Three problems: the project has
field evidence that the cloud judge rejects grind proofs the local judge accepts;
the proof kernel cannot check a tactic step, so the certificate had no offline
verification; and it consumed 37.0 s of the judge's 120 s Lean timeout.

**The lemma is derivable from facts already in the same certificate.** Write
`P := X0 ◇ (X0 ◇ X0)`.

1. `eq19 X0 (X0◇X0) t : X0 ◇ P = t ◇ P` — eq19 says the outer left factor is
   free. With `eq34 X0 : X0 ◇ P = X0` this gives **(★) `∀t, t ◇ P = X0`**.
2. (★) at `t := P`: `P ◇ P = X0`.
3. `eq22 P P : (P ◇ (P ◇ P)) ◇ P = P`; rewriting the inner `P ◇ P` by step 2
   gives `(P ◇ X0) ◇ P = P`.
4. (★) at `t := P ◇ X0`: `(P ◇ X0) ◇ P = X0`. With step 3, `P = X0`. ∎

Shipped as a proof term. **Real Lean judge: `accepted`, 4.8–7.9 s** (from 37.0 s),
with the heartbeat bump removed too.

**Systemic fix.** `sanitize_lean_code` enforced the no-`grind` rule on *LLM*
output but never on solver-generated code. Added `check_no_banned_tactics()`,
called per row from `test_golden.py` and `audit_corpus.py`, exempting only
`true:narrow_grind` and `fallback:unsolved_grind`; plus a static scan of the
solver source so a template no pinned row exercises is still caught.

### 2. The finite-model oracle was vacuous on 28% of rows (dead code)

`oracles.model_battery` seeded the battery with the trivial magma `[[0]]`. Every
equation holds in `Fin 1`, so the battery was never empty — which made the
exhaustive-`Fin 3` escalation guarded by `if not battery:` **unreachable**. Its
own comment named the family it was meant to cover ("central groupoids, model
orders k²"), i.e. the `Eq168` family behind the eight playground `TRUE INCORRECT`
rows.

Measured: **536 / 1889 official rows (28.4%)** — `normal` 431/1000, `hard2`
64/200 — were "model_checked" against the trivial magma alone.

Fixed by keying escalation off a new `nontrivial_model_count()`, then escalating
exhaustive `Fin 3` → a budgeted order-4/5 hill-climb (`search_models`). The
search is real: it finds a verified order-4 central groupoid in ~0.1 s, where
enumeration (4¹⁶ ≈ 4.3e9) and uniform sampling both fail. `audit_corpus.audit_row`
now records `nontrivial_models` and reports `model_check_vacuous` instead of
`model_checked` when it is zero.

**A limit worth internalising:** every `*_singleton` / `*_collapse` route asserts
eq1 forces a one-element magma. For those laws **no non-trivial finite model
exists at any order**, so model-checking is inherently powerless — not broken.
Those rows can only be verified by proof-checking. The hill-climb is budgeted
(0.25 s) precisely because on that family it can only ever fail; unbudgeted it
cost 0.6–4.3 s per row.

### 3. Ten certificates had zero verification — all ten are Lean-correct

Cross-referencing unsupported cert shape against vacuous battery found **10
official TRUE certificates with no correctness evidence of any kind**, across
`nested_square_singleton`, `wrapped_tail_singleton`, `tail_square_singleton`,
`repeated_prefix_product_constancy`, `middle_self_collapse`,
`paired_tail_singleton` and `right_projection_collapse:left_pair_tail`
(plus 26 more on the HF sets).

All were run through the real judge. **10/10 `accepted`.** So the math shipping
today is right; the defect was coverage, not correctness.

Extended to the whole class: all **34** official `other`-shape certificates
(18 routes) were judged — **34/34 `accepted`**, 4.3–7.3 s each — and pinned
byte-for-byte in `stage2/fixtures/judge_verified_certs.jsonl`, guarded by
`stage2/tests/test_judge_verified.py`. If a builder changes, the test fails and
tells you to re-verify with `judge_rows.py`. Route drift is tolerated (documented
wall-clock nondeterminism); a changed certificate on the same route is not.

### 4. Solver size caps were twice the judge's (latent)

| Constant | Was | Judge limit | Now |
| --- | ---: | ---: | ---: |
| `MAX_LEAN_CODE_BYTES` | 100_000 | 50_000 | 49_500 |
| `MAX_FALSE_CERT_BYTES` | 20_000 | 10_000 | 9_500 |
| `UNIVERSAL_IDENTITY_MAX_CODE` | 60000 | 50_000 | 49_500 |

Derived from new `JUDGE_MAX_CODE_LENGTH` / `JUDGE_MAX_FALSE_CERT_BYTES` mirroring
`vendor/stage2-official/judge/verify.py`. **No benchmark row exceeded the judge's
limits** (measured 0 in two archived audits), so this closes a latent hole rather
than recovering rows — an oversized cert is rejected with the row scored as
attempted, strictly worse than skipping.

### 5. `narrow_grind` ran without an engine gate

Every general engine in `solve_problem` was preceded by `_engine_gate()` (global
hard deadline + memory guard modelling the 2048 MB sandbox) except
`narrow_grind_true_route`. It therefore fired after a memory trip or a passed
deadline — the OOM/ERROR class eliminated everywhere else in 2026-07-22 session 4.

## Dispatcher refactor

`solve_problem` was **510 lines**, ~380 of them copy-pasted
`x = fn(eq1, eq2); if x is not None: route, code = x; return {...}` blocks. That
shape is why finding #5 and an unreachable duplicate
`sandwich_left_projection_route` call both survived review.

Now **104 lines**: a `TRUE_ROUTES` table of 41 entries with a uniform
`(eq1, eq2) -> (route, code) | None` signature, four thin adapters for the routes
with a different return shape, and one loop. The general engines are a second
list built around the single `closure_first` conditional, with the gate checked
once per engine.

**Order was verified mechanically**, not by eye: the old invocation sequence was
re-extracted from `git show HEAD` and compared element-by-element against
`TRUE_ROUTES`. Identical, modulo the removed unreachable duplicate. Adding a
route is now a one-line change.

**One intentional behaviour change**, stated plainly: the loop checks
`_engine_gate()` before *every* general engine, where the old code skipped it in
two places — before the `if not closure_first` call to `equational_closure_route`,
and before `narrow_grind_true_route`. This can only cause an earlier stop under
memory or deadline pressure, never a later one, and it is the point of finding #5.
It is invisible to the audit (no hard deadline is set and the memory guard is
armed only in the Solo/Marathon entry points, so the gate is always false there);
it matters in the sandbox, which is where the OOM kills happened.

Behaviour evidence: gate green, official audit route-diffed by row id, and an
end-to-end Solo protocol smoke (correct `verdict`+`code`-only payload, exit 0,
route logged to stderr).

## Testing and velocity

- Gate: **146 s → 47 s** via `pytest-xdist -n auto`, and **196 → 237 tests**.
  Speed matters because a slow gate is one people skip with `-SkipTests`.
  `package_solver.ps1` uses `-n auto` with a serial fallback.
- **CI added** (`.github/workflows/gate.yml`): lint, gate, size check. Nothing
  enforced the gate outside the packaging script before.
- `ruff check .` is now **clean repo-wide** (was 16 findings). Added `ruff.toml`
  that ignores `E402` under `stage2/experiments`, `stage2/tests` and
  `theory/tools` — the single-file submission contract *requires* `sys.path`
  setup before `import solver`, so those are correct, not smells. 31 real
  findings auto-fixed, 1 dead assignment removed.

## Onboarding

- **`CLAUDE.md` added** as the single authoritative entry point. The mandated
  cold-start read was **142,842 chars ≈ 36k tokens across 13 files** that
  disagreed with each other. Worst case: `AGENTS.md`, the first file an agent
  reads, presented `1201/1669` and a `138939`-byte package as the "latest
  snapshot" — stale by 416 rows and 2.4× on size — so a cold agent planned
  against the wrong numbers. `AGENTS.md` and `.github/copilot-instructions.md`
  now defer to it, so all three agent surfaces agree.
- Stale figures corrected across `README.md`, `stage2/README.md`,
  `playground-preflight.md`, `smoke-tests.md`, `CURRENT_STATE.md`, and the
  `LATEST_HANDOFF.md` self-contradiction on HF (`754` vs `783` in the same file).
- Documented two environment traps that cost real time: printing `◇` crashes on
  Windows cp1252 (`PYTHONIOENCODING=utf-8`), and the working tree is ~7.4 GB /
  154k files (`vendor/.lake` alone is 7.06 GB / 117,609 files), so unscoped
  `du`/`find` at the repo root hang.
- **The local Lean judge works on Windows** via `elan`, contradicting the setup
  docs. It is the strongest verification available locally and was tribal
  knowledge. New `stage2/experiments/judge_rows.py` makes it one command.

## Junk

Removed: `.agents/` (empty), `Untitled-1.md` (a bare URL already in the README).
Disk inventory and a **recommended-but-not-executed** prune for
`tmp_stage2_smoke/` (103 MB / 20,747 files) and `vendor/.artifacts` (57 MB /
15,573 files) recorded in `stage2/docs/cleanup-manifest.md`. Do not touch
`vendor/.lake` — rebuilding Mathlib costs hours.

## Not done (deliberate)

- **No route deletions.** The 2026-07-21 rail stands: subsumed routes are cheap
  fast paths, and 29 look dead on official but live on HF.
- **No new coverage.** The ranked levers (egg at `standard`, shrink egg
  extraction, step-count budgets, LLM lemma lane) are untouched and remain the
  next session's work.
- **No full kernel for the `*_block` dialect.** 34 rows split across two proof
  dialects (combinator `T`/`S`/`R`/`C`/`M` and nested `have`); a new ~400-line
  oracle could itself be wrong, and judge-pinning gives stronger evidence for
  less risk. Extending the kernel remains the cleaner long-term answer.
