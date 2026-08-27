# Upstream Snapshot

Vendored repository: https://github.com/SAIRcompetition/equational-theories-lean-stage2

Snapshot commit: `13648682a5553717ea91b86513ed140b39160cf5`

Vendored on: 2026-05-04 (initial snapshot `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`)

Synced to upstream HEAD on: 2026-08-26 (from `4db175c4`, 4 commits ahead,
0 behind). Upstream changed 16 files and added 5 (three size-cap answer
fixtures, one lone-surrogate challenger answer, one Marathon size-cap
manifest). Verbatim copies for everything except the five locally patched
files — `judge/verify.py`, `scripts/run_harness.py`, `pipeline/proxy.py`,
`pipeline/marathon_runner.py`, `scripts/run_marathon_harness.py` — which were
3-way merged (`git merge-file` against the old and new upstream versions).
Four merged clean; `pipeline/proxy.py` had two conflicts where the local
provider-normalization patch meets upstream's new per-model allowlist
(`_resolve_model` / `UnknownModelError`): resolved by keeping both — the
chosen model's provider string is still routed through
`_openrouter_provider_config`. Every documented local patch below remains
present (patch #9's `cwd=art_dir` verified by grep after the merge).
Notable upstream changes: Lean toolchain `v4.32.2` → **`v4.33.1`** with Mathlib
`905b9581` → `0df444a360eaa60ab8c11dca51a86af692955474` (the kernel-soundness
hardening release; organizers state valid certificates stay valid);
`judge/verify.py`'s no-config fallbacks now equal the deployed
100,000 / 20,000 / 300 (the rail-3b drift is closed at the source) and a new
`CODE_NOT_UTF8` malformed status for lone-surrogate code; `pipeline/config.json`
judge block **unchanged** (CI pin still valid), `llm.reasoning_effort`
`medium` → `low` and a per-model `llm.models` allowlist (gpt-oss-120b at low,
gemma-4-31b-it with reasoning disabled); Marathon scoring now snapshots the
judge config and proof policy before the solver launches.

Synced to upstream HEAD on: 2026-08-24. Upstream changed 16 files and added 14
(12 challenger answers plus 2 infinite-countermodel fixtures). All were taken
verbatim from upstream except `judge/verify.py` and `scripts/run_harness.py`,
which carry local patches: those two were re-applied via a 3-way merge
(`git merge-file` against the old and new upstream versions). Both merged with
zero conflicts; every documented local patch below remains present and valid,
verified by diffing the merged files against the pristine upstream versions.
Notable upstream changes in this sync: Lean toolchain `v4.30.0-rc2` →
`v4.32.2` with Mathlib pin `896cc56a` → `905b95818eb32af7874a58b427f50c1711a5e96c`;
`judge/verify.py` security hardening (banned tokens now include `run_cmd`,
`run_elab`, `@[init`, the `notation`/`infix`/`prefix`/`postfix` family and
`skipKernelTC`; `Problem.lean` binds a named `_judge_checked_<nonce>` theorem
and the dependency policy is applied to the union of two required reports); and
new `-D linter.defProp=false` flags on both Lean invocations (Lean 4.32's
default-on `linter.defProp` fires on the judge's own required
`def submission : Goal := …` shape).

## Policy

Treat this directory as an upstream snapshot of the official Stage 2 harness. Avoid local edits inside `vendor/stage2-official/` unless the change is explicitly a local patch and is documented here or in a patch note.

## Local Windows Patches

These changes are local compatibility patches on top of the upstream snapshot:

1. `judge/verify.py` decodes Lean subprocess output as UTF-8 with replacement and uses `cmd /C echo %LEAN_PATH%` for `lake env` on Windows instead of requiring `bash`.
2. `scripts/run_harness.py` treats the symlink-layout regression as skipped when Windows denies symlink creation with `WinError 1314`.
3. `pipeline/marathon_runner.py` uses Windows process groups, Ctrl-Break/terminate, and `taskkill /T /F` instead of POSIX-only `os.killpg` when running on Windows.
4. `judge/verify.py` strips judge artifact paths using both POSIX and Windows separators.
5. `scripts/run_harness.py` uses explicit fake TTY/non-TTY streams for submit CLI color assertions so the tests do not depend on the host terminal.
6. `pipeline/proxy.py` and `pipeline/marathon_runner.py` preserve non-secret Windows runtime environment variables such as `SYSTEMROOT`, `WINDIR`, `TEMP`, `TMP`, and `USERPROFILE` for solver subprocesses.
7. `pipeline/marathon_proxy.py` treats Windows `ConnectionAbortedError` as an expected broken-client condition when rejecting slowloris-style requests.
8. `tests/marathon_fixtures/solvers/late_writer/solver.py` also registers a `SIGBREAK` handler when available, and `scripts/run_marathon_harness.py` skips the POSIX-only post-SIGTERM duplicate-write assertion on Windows where Python child processes do not receive catchable `SIGTERM` semantics.
9. (added 2026-08-24) `judge/verify.py` passes `cwd=art_dir` to the Submission-compile and Problem-verify `lean` invocations, matching what `_write_problem_module` already does. On Windows `lean` is an elan shim that resolves the toolchain from the working directory's `lean-toolchain`; with the caller's cwd inherited (e.g. the magma-ai repo root, which has no toolchain file), those two invocations resolved elan's *default* toolchain while `JudgeProblem.olean` was compiled by the vendored `v4.32.2`, failing every verify with `failed to read file 'JudgeProblem.olean', incompatible header`. This was latent before the v4.32.2 bump only because elan's default happened to equal the vendored toolchain (`v4.30.0-rc2`). No semantic change on Linux deployment, where `lean` is a direct binary and cwd is irrelevant (all paths passed are absolute).

## Local Provider Compatibility Patch

This change is local harness drift, not a Windows-only patch:

1. `pipeline/proxy.py`, `pipeline/marathon_llm.py`, and `pipeline/marathon_proxy.py` normalize OpenRouter provider strings such as `deepinfra/bf16` into `provider.order=["DeepInfra"]`, `provider.quantizations=["bf16"]`, and `provider.allow_fallbacks=false`. This preserves the pinned local config value while avoiding OpenRouter `400` errors in homelab proxy tests.

Current local evidence:

1. `scripts/run_harness.py`: green on native Windows with Lean available and no failing buckets.
2. `scripts/run_marathon_harness.py`: green on native Windows, 25/25 checks with Lean available.
3. `stage2/experiments/homelab_llm_probe.py --run-direct-openrouter-smoke`: plain, pinned-provider, and pinned-provider-plus-reasoning OpenRouter request shapes all returned OK.
4. `stage2/experiments/homelab_llm_probe.py --run-proxy-smoke --marathon-budget-tokens 4096 --marathon-budget-seconds 180`: Solo `1/1` accepted and Marathon `1/1` accepted through the local OpenRouter proxy path.

## Known upstream drift (do not "fix" locally)

**Both drift points below were resolved upstream and landed in the 2026-08-24
sync** — `rules/evaluation.md` now derives Marathon's budget as `N × 5 minutes`
with no `compression_ratio`, and describes a FALSE certificate as allowing a
finite *or infinite* carrier, matching the judge's actual goal. Kept for
history:

1. (resolved) `rules/evaluation.md` derived the Marathon budget as
   `compression_ratio × N × 3600 s` (180,000 s at N=100). `scripts/run_marathon.py`
   used a 600 s reference instead (30,000 s at N=100). The organizers confirmed
   the CLI: **Solo 60 min per problem, Marathon 5 min per problem on average**,
   and `compression_ratio` was withdrawn from the spec as misleading.
2. (resolved) `rules/evaluation.md` described a FALSE certificate as "a Lean 4
   proof that there exists a **finite** magma …". The judge's actual goal
   (`judge/verify.py`) is `∃ (G : Type) (_ : Magma G), EquationLHS G ∧ ¬
   EquationRHS G`, with no `Finite`/`Fintype` constraint, and the organizers
   confirmed verified infinite countermodels are allowed. Upstream now ships
   `tests/fixtures/answers/accepted_false_infinite_{nat,tree}.answer.json`
   pinning exactly this.

To sync upstream later:

1. Record the current snapshot commit.
2. Compare upstream docs, `pipeline/config.json`, `judge/`, and example solvers.
3. Re-run official harness tests after updating.
4. Document any config drift in `CURRENT_STATE.md`.
