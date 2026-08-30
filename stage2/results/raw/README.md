# Raw result archives

This directory is the local home for large, reproducible run output. Durable
claims belong in dated Markdown summaries one level up; active replay fixtures
belong under `stage2/fixtures/` or `stage2/experiments/`.

Policy:

- Keep `stage2/results/` readable: dated `.md` summaries, accepted Lean
  certificates, and small tracked runner bundles only.
- Put completed per-shard JSON/JSONL output into a campaign ZIP here after its
  aggregate summary exists.
- Record file count, uncompressed bytes, archive bytes, SHA-256, and recovery
  command in `MANIFEST.md`.
- Never archive an active residual ledger, judge fixture, accepted certificate,
  or file referenced by a current command.
- New tools should write raw output below this directory when practical. The
  readiness checker writes nowhere unless passed an explicit `--json-out`.

Archives are ignored because their source payloads were already ignored. They
are local reproducibility aids, not part of the Git deliverable.

