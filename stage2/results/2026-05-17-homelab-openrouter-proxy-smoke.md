# Homelab OpenRouter Proxy Smoke - 2026-05-17

Purpose: verify local upstream OpenRouter configuration and the official Solo / Marathon proxy paths without exposing key material or spending hard-problem proof-search time.

## Setup

- Added clipboard mode to `stage2/experiments/set_openrouter_user_env.ps1`.
- Clipboard mode validates `sk-or-v1-` prefix, minimum length, and no whitespace before storing `OPENROUTER_API_KEY` in the Windows User environment.
- Clipboard mode clears the clipboard by default after storing.
- Stored key shape after setup: length `73`, prefix check `true`, whitespace check `false`.
- `homelab_llm_probe.py` now also reads the Windows User environment directly when the current terminal process has not inherited `OPENROUTER_API_KEY`.
- No key value was printed by the helper or probes.

## Harness Compatibility

- Added local OpenRouter provider normalization in the vendored harness:
  - `vendor/stage2-official/pipeline/proxy.py`
  - `vendor/stage2-official/pipeline/marathon_llm.py`
  - `vendor/stage2-official/pipeline/marathon_proxy.py`
- `deepinfra/bf16` is translated to `provider.order=["DeepInfra"]` plus `provider.quantizations=["bf16"]` for OpenRouter requests.
- Pinned provider strings also set `provider.allow_fallbacks=false` so local route behavior matches the pinned config intent.
- Documented the local patch in `vendor/stage2-official/UPSTREAM.md`.

## Evidence

- Direct OpenRouter request shape probe:
  - key present: `true`
  - length `73`, starts `sk-or-v1-`: `true`, whitespace: `false`
  - command: `python stage2/experiments/homelab_llm_probe.py --run-direct-openrouter-smoke`
  - plain request: OK, `total_tokens=87`
  - provider `DeepInfra` + `bf16` + `allow_fallbacks=false`: OK, `total_tokens=74`
  - provider + reasoning low: OK, `total_tokens=74`

- Bounded one-call Solo proxy smoke:
  - command: `python stage2/experiments/homelab_llm_probe.py --run-proxy-smoke --marathon-budget-tokens 4096 --marathon-budget-seconds 180`
  - temp submission: `tmp_stage2_smoke/llm_proxy_smoke_submission`
  - fixture: `tmp_stage2_smoke/llm_proxy_smoke.jsonl`
  - config: `tmp_stage2_smoke/llm_proxy_smoke_config.json`
  - result: `1/1` solved, verdict `true`
  - wall: `5.4s` on the latest rerun; upstream/proxy latency is variable, so this is transport evidence, not a speed benchmark
  - calls: `llm=1`, `judge=1`
  - missing-key rows: `0`
  - solver return code: `0`

- Bounded one-call Marathon proxy smoke:
  - output dir: `tmp_stage2_smoke/llm_proxy_smoke_marathon`
  - result: `1/1` accepted
  - attempted: `1`, not attempted: `0`
  - wall: `3.0s` of `180s`
  - tokens: `74/4096`
  - token exhaustion: `false`
  - solver return code: `0`

## Notes

- A previous full hard TRUE LLM probe is no longer useful as a plumbing check: after the key was fixed, the fast `400` failures disappeared and the actual solver spent minutes in real LLM / judge loops (`374.2s` and `236.1s` for the first two rows) before the run was stopped.
- Use `--run-proxy-smoke` for future local transport checks; use hard unresolved TRUE fixtures only when measuring proof quality or LLM strategy.
- Because an earlier key was pasted into chat or logs during setup troubleshooting, use a rotated key for long runs.
