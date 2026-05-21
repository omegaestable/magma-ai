# 2026-05-20 Unresolved TRUE Proxy Round

Focused round against three deterministic misses from the 2026-05-16 hard-mix unresolved TRUE frontier.

## Inputs

- Fixture: `tmp_stage2_smoke/2026-05-20-unresolved-true-proxy-fixture.jsonl`
- Source manifest: `tmp_stage2_smoke/2026-05-16-hard-mix-150-seed20260516.jsonl`
- Source summary: `tmp_stage2_smoke/2026-05-16-marathon-hard-mix-150-seed20260516-after-witness-zero-token/summary.json`
- Row ids: `hard3_0140`, `hard3_0114`, `hard3_0196`
- Packaged solver at run start: `stage2/submissions/solver.py`, `71662` bytes, single-file directory

## Readiness

- Local upstream key shape check passed without printing secrets.
- `py_compile`, `smoke_llm_dsl.py`, `theory/tools/smoke_problem_sets.py`, and packaging passed before the proxy run.
- Direct OpenRouter request-shape smokes passed for plain and `deepinfra/bf16` provider settings.

## Harness-Support Fix

The first parity attempt failed before useful proxy evidence because relative fixture/output paths were handed to official runners executed from `vendor/stage2-official`. That made the runner look for `tmp_stage2_smoke/...` under the vendor directory.

Fix applied: `stage2/experiments/run_playground_parity_llm.py` now resolves `--manifest`, `--summary`, `--fixture`, `--mixed-manifest`, and `--output-dir` before invoking official runners.

## Proxy Results

| Lane | Score | LLM calls | Judge calls | Tokens | Main failure |
| --- | ---: | ---: | ---: | ---: | --- |
| Solo | `0/3` | `6` | `3` | runner-local | fallback judge rejection after LLM candidate rejection |
| Marathon | `0/3` | `2` | `0` | `3761/131072` | rejected LLM output plus upstream token-budget exhaustion |

Solo behavior was consistent across all rows: the model returned short `rewrite_chain` JSON, the solver rejected the chain as not solver-proveable, then made the required final schema-valid fallback judge call. The fallback proof `exact h` was incorrect for all three rows, as expected.

Marathon submitted no answers. `run.log` recorded one `llm:reject` for `hard3_0196`, then one `llm:error` for `hard3_0140` with upstream `token budget exhausted`. The official summary therefore reports all three rows as `not_attempted`.

## Provenance Lookup

- `theory/tools/fetch_teorth_data.py --check` passed against the local cache.
- `theory/tools/teorth_true_proof_agent.py certify-benchmark` wrote `stage2/results/2026-05-20-unresolved-true-teorth.jsonl`.
- All three rows are `implicit_proof_true`; the tool records 0-based equation indices internally, while the official rows and proof-page URLs use 1-based ids.
- `theory/tools/proof_scraping_lab.py --pairs "1072,1251;922,1444;1806,545"` fetched all three proof pages, but the pages exposed only a JS shell: no theorem links, code blocks, fact links, or pair links were extracted.

## Learning

Two rows point at a reusable `C9` absorption-collapse motif:

- `hard3_0140`: likely needs a local collapse from `E1072` into an `E19` or related C9 representative, then existing absorption-style reasoning toward `E1251`.
- `hard3_0196`: `E1806` is in the same C9 source class as `E13/E19`; once the solver can prove `E1806 -> E13` or `E1806 -> E19`, existing deeper absorption routes should be able to compose toward `E545`.

`hard3_0114` has graph path clues through `VampireProven` legs and simple rewrite intermediates, but it looks less immediately reusable. Treat it as proof-mining material rather than a reason to raise broad closure bounds.

## Reapplied To Solver

Two small code changes were applied for the next round:

1. `stage2/experiments/run_playground_parity_llm.py` now normalizes CLI paths before official runner calls.
2. `stage2/solver/solver.py` now reports structured LLM rejection reasons from `candidate_from_llm_text_with_reason`, so future proxy ledgers can distinguish parse failures, unproved rewrite chains, bad endpoints, sanitizer rejections, and invalid finite tables.
3. `stage2/solver/solver.py` now has a narrow structural `E1072`-shape collapse route. It proves a local `h19 : ∀ a b c, a = b ◇ (c ◇ a)` from `x = y ◇ ((x ◇ (x ◇ x)) ◇ x)` and composes through existing simple `E19` proof-expression routes.

Focused official Solo evidence after the route was added:

- Fixture: `tmp_stage2_smoke/2026-05-20-c9-hard3-0140.jsonl`
- Result: `hard3_0140` (`E1072 -> E1251`) solved, `0` LLM calls, `1` judge call.
- Output: `tmp_stage2_smoke/2026-05-20-c9-hard3-0140-solo-result-after-guard.json`
- Packaged solver size for this smoke: `76088` bytes.

## Next Route Work

Do not revive broad `true:grind` and do not raise global closure bounds from this evidence alone. The conservative next implementation target is the remaining C9 absorption collapse work:

- try `E1806 -> E19` or `E1806 -> E13`, then compose toward `E545`
- keep `hard3_0114` as a separate theorem-chain proof-mining target
- fixture candidates: `hard3_0140`, `hard3_0139`, `hard3_0114`, `hard3_0196`, `hard3_0197`, and `normal_0203`

## Durable Artifacts

- Row error ledger: `stage2/results/2026-05-20-unresolved-true-proxy-errors.jsonl`
- Teorth labels: `stage2/results/2026-05-20-unresolved-true-teorth.jsonl`
- Proof-page scrape: `stage2/results/2026-05-20-unresolved-true-proof-pages.md`
- Raw Solo output: `tmp_stage2_smoke/2026-05-20-unresolved-true-proxy-round/solo_result.json`
- Raw Marathon output: `tmp_stage2_smoke/2026-05-20-unresolved-true-proxy-round/marathon/`