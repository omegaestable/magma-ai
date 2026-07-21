# 2026-07-20 — Self-verifying LLM TRUE-proof loop + prompt v3

Session goal: use OpenRouter + the rules' OSS model (`openai/gpt-oss-120b`,
`deepinfra/bf16`, temp 0, medium reasoning) to run many real problems, learn from
failures, and improve the solver's TRUE-proof coverage. Solo-first; self-verifying
raw-Lean/chain lane.

## What was built (durable)

- `stage2/experiments/dev_true_loop.py` — a self-verifying dev loop. For each
  problem it runs a repair loop against gpt-oss via OpenRouter, parses the reply
  with the solver's own `candidate_from_llm_text_with_reason`, and **verifies every
  candidate with the local Lean judge** (`judge.verify.verify_answer`). Writes a
  per-round failure ledger + summary. Secret-safe; prefers the fresh repo `.env`
  key over any stale process-env key. Dev-only (talks to OpenRouter directly; the
  shipped solver still only reaches the organizer proxy).
- `stage2/experiments/analyze_true_loop.py` — clusters a ledger by win-round,
  model verdict choice, Lean-error signature, and goal syntactic family.

## Environment facts established

- Local Lean judge works and is cheap: warm valid TRUE verify ~2.3 s (submissions
  import only lightweight `JudgeMagma`, not Mathlib). Cold start ~48 s (one-time
  `lake env` LEAN_PATH resolve). It correctly accepts valid proofs and returns
  `incorrect` for broken ones — the self-verify gate is sound.
- OpenRouter gpt-oss-120b works with the session key stored in the gitignored root
  `.env`. NOTE: a *stale* `OPENROUTER_API_KEY` in the Windows/process env shadows
  `.env` (process-first precedence in `local_runner_env`); tooling must force the
  `.env` key. `reasoning=medium` emits ~8 K tokens/hard-problem (~30–110 s/call);
  DeepInfra effectively serializes concurrent long generations for this key, so
  medium dev runs are slow. `reasoning=low` is ~3× faster but weaker.

## Frontier

456 TRUE implications the deterministic solver skips (from `normal`+`hard2`+`hard3`,
scanning 1600 rows: 795 TRUE, 339 det-solved, 456 skip). Split 280 dev / 176
held-out; A/B subsets under `tmp_stage2_smoke/2026-07-20-true-loop/`.

## Baseline (current prompt) — the bottleneck

On the frontier, the **current prompt makes gpt-oss guess FALSE counterexample
tables on TRUE rows** (≈70 % of outputs) and almost never produces a usable TRUE
proof. On a 12-problem solvable set it scored 3/12 (25 %), still dominated by bad
FALSE-table attempts.

## Failure analysis (from real proofs)

1. The model defaults to `simp`/`simpa`, which **loops** on these non-orientable
   laws ("maximum recursion depth").
2. It **mis-computes hypothesis instantiations** (`h a b c` yields a different term
   than it believes → type mismatch) — term bookkeeping is its weak spot.
3. It **assumes associativity/commutativity** (silently reassociates/reorders),
   invalid in a general magma.
4. The solver's **chain DSL is reliable**: hand-built correct chains (1-step,
   2-step-in-context, 3-step) all render to judge-`accepted` Lean. So if the model
   supplies correct waypoint terms, the solver guarantees a valid proof.

## P1 — shipped changes (`stage2/solver/solver.py`)

- **`PROMPT` rewritten (chain-primary).** Leads with the guided-chain DSL (model
  gives intermediate terms, solver builds Lean — offloading the bookkeeping it gets
  wrong); states the row is almost-certainly TRUE (det countermodel search already
  failed) to stop FALSE-guessing; forbids `simp`/`simpa`/`aesop`/`grind`; warns ◇
  is non-associative/non-commutative; raw Lean is a fallback.
- **Relaxed `sanitize_lean_code`**: dropped the brittle literal `intro G _ h`
  requirement — the local judge is the correctness gate, not a shape pre-filter.
- **Stronger guided-chain edge prover**: `LLM_GUIDED_CHAIN_MAX_DEPTH` 4→8,
  budget 0.18→1.0 s, so the solver bridges the model's coarser waypoints.
- **`LLM_MAX_ROUNDS` 2→6** (Solo has no token meter; more repair rounds are free).
- **`run_solo` feeds parse-level rejects back** via `{solver.feedback}` (the proxy's
  `{history.attempts}` only carries judge results, not pre-judge parse rejects).

Verified: solver parses; proxy AST-extracts the new `PROMPT` with all placeholders;
packaged `stage2/submissions/solver.py` = 226 676 bytes (< 500 KB).

## Measured effect

- **A/B on a 12-problem solvable TRUE set (low reasoning):** current prompt
  **3/12 (25 %)** → prompt v3 **9/12 (75 %)** — 6 `rewrite_chain` + 3
  `guided_chain`, all judge-`accepted`. Confirms the chain-primary + self-verify
  loop works end-to-end and triples the LLM's standalone accept rate.
- **Deterministic-skip frontier (what the LLM actually faces in production):**
  gpt-oss at **low** reasoning still ≈0 — `0/20` mixed, `0/18` normal-difficulty.
  Chains fail on unprovable/oversized steps and free non-goal variables. Medium
  reasoning: `0/4` on an earlier mixed sweep, and a fresh 8-row medium sweep did not
  complete — DeepInfra serializes the long ~8 K-token generations for this key
  (~80–300 s/call), so medium dev sweeps are throughput-bound. Low results plus the
  partial medium point to ≈0 on this frontier regardless of effort tested so far.
- **Deterministic closure ceiling:** a big-budget bidirectional closure
  (depth 8, pool 40, 6 s) solved only **1/20** frontier rows — these need smarter
  hypothesis instantiation, not just more search.

## Honest conclusion

The self-verifying LLM loop and prompt v3 are a clear, safe improvement (no
`incorrect` submissions possible; 3× accept rate on solvable rows) and the dev
harness is a durable capability. But the **deterministic-skip frontier is genuinely
hard for gpt-oss-120b**: the easy TRUE rows are already deterministic, and the rows
left for the LLM need multi-step derivations with exact instantiation that the model
does not reliably find at low effort. Net production accept gains from the LLM lane
are therefore still limited pending the next step.

## Most promising next step

**Hybrid: LLM proposes candidate instantiation / middle terms → seed the
deterministic bidirectional closure pool.** The closure engine
(`_closure_proof_expr_impl`) already meets in the middle but is bounded by which
terms are in `absorption_term_pool`. The model is good at *which terms matter* and
bad at *exact chains*; the solver is the opposite. Feeding LLM-suggested terms into
the closure pool combines both and directly attacks the observed failure (right
endpoints, wrong/oversized middle steps). Also worth trying: a medium-reasoning
frontier sweep, and tighter instantiation guidance in the prompt.

## Evidence

- Harness + analyzer: `stage2/experiments/dev_true_loop.py`,
  `stage2/experiments/analyze_true_loop.py`.
- Ledgers/summaries: `tmp_stage2_smoke/2026-07-20-true-loop/` (`baseline100/`,
  `p1_low20/`, `p1v3_low20/`, `easy_probe/` = 75 %, `easy_probe_baseline/` = 25 %,
  `normal_frontier_low/`, `normal_frontier_med8/`), frontier `dev.jsonl` /
  `heldout.jsonl`, prompt `prompt_current.txt`.
