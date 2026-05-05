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

To sync upstream later:

1. Record the current snapshot commit.
2. Compare upstream docs, `pipeline/config.json`, `judge/`, and example solvers.
3. Re-run official harness tests after updating.
4. Document any config drift in `CURRENT_STATE.md`.
