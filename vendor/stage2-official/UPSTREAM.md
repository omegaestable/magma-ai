# Upstream Snapshot

Vendored repository: https://github.com/SAIRcompetition/equational-theories-lean-stage2

Snapshot commit: `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`

Vendored on: 2026-05-04

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

## Local Provider Compatibility Patch

This change is local harness drift, not a Windows-only patch:

1. `pipeline/proxy.py`, `pipeline/marathon_llm.py`, and `pipeline/marathon_proxy.py` normalize OpenRouter provider strings such as `deepinfra/bf16` into `provider.order=["DeepInfra"]` plus `provider.quantizations=["bf16"]`. This preserves the pinned local config value while avoiding OpenRouter `400` errors in homelab proxy tests.

Current local evidence:

1. `scripts/run_harness.py`: green on native Windows with Lean available and no failing buckets.
2. `scripts/run_marathon_harness.py`: green on native Windows, 25/25 checks with Lean available.
3. `stage2/experiments/homelab_llm_probe.py --run-proxy-smoke --marathon-budget-tokens 4096 --marathon-budget-seconds 180`: Solo `1/1` accepted and Marathon `1/1` accepted through the local OpenRouter proxy path.

To sync upstream later:

1. Record the current snapshot commit.
2. Compare upstream docs, `pipeline/config.json`, `judge/`, and example solvers.
3. Re-run official harness tests after updating.
4. Document any config drift in `CURRENT_STATE.md`.
