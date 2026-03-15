# Repo Diagnose Report (2026-03-14)

## Executive Summary

This repo's submission artifact is a ≤10KB cheatsheet that an LLM reads at inference to decide whether one magma equation implies another. After a full E2E pass, two cheatsheet A/B comparisons, and an LLM-distillation trial, the **blocking failure** is clear: we cannot pass our own acceptance gates because the cheatsheet barely teaches the model how to recognize TRUE implications. FALSE detection is strong; TRUE recall is catastrophic on hard slices.

The single highest-leverage discovery is that **we are using only ~30% of our 10KB byte budget** while simultaneously failing to encode the specific mathematical content (worked specialization examples, rewrite templates, magma evaluation tables) that the model needs. This is not a modeling problem or a pipeline problem — it is a **cheatsheet content problem** with a clear fix path.

## Scope

Runs analyzed (all submission-valid, cheatsheet-only prompting via `run_eval.py`):

| Tag | Cheatsheet | Benchmark | Dual-swap |
|-----|-----------|-----------|-----------|
| pre_no_leak | pre-robust (3143 B) | no_leak_benchmark.jsonl | yes |
| robust_no_leak | robust rules v1 (2759 B) | no_leak_benchmark.jsonl | yes |
| candidate_no_leak | LLM-distilled (2933 B) | no_leak_benchmark.jsonl | yes |
| pre_hardest | pre-robust (3143 B) | hardest_500.jsonl | no |
| robust_hardest | robust rules v1 (2759 B) | hardest_500.jsonl | no |

All runs used `qwen2.5:3b` local via Ollama, `n_eval=100`, `seed=42`, `n_format_examples=0`, `use_rationale_augmentation=true`.

Supporting artifacts: ML cross-validation, feature importance, proof/counterexample pattern mining, public leaderboard snapshot, `repo2_harness` summary with gate verdicts.

## E2E Results

| Run | Acc | True Acc | False Acc | Hard Acc | CE-Easy Acc | Bytes |
|-----|----:|--------:|---------:|--------:|-----------:|------:|
| pre_no_leak | 0.510 | 0.213 | 0.774 | 0.231 | 0.780 | 3143 |
| robust_no_leak | **0.610** | **0.319** | 0.868 | **0.282** | 0.860 | 2759 |
| candidate_no_leak | 0.510 | 0.021 | **0.943** | 0.051 | **0.940** | 2933 |
| pre_hardest | 0.520 | 0.173 | 0.896 | 0.173 | 0.896 | 3143 |
| robust_hardest | 0.470 | 0.038 | 0.938 | 0.038 | 0.938 | 2759 |

### Acceptance Gates (from `repo2_harness.py`)

| Gate | Required | robust_no_leak | candidate_no_leak | Status |
|------|----------|---------------|-------------------|--------|
| overall_accuracy | ≥ 0.60 | **0.61 ✓** | 0.51 ✗ | Baseline passes alone |
| true_accuracy | ≥ 0.45 | 0.319 ✗ | 0.021 ✗ | **BLOCKING — both fail** |
| hard_bucket_accuracy | ≥ 0.35 | 0.282 ✗ | 0.051 ✗ | **BLOCKING — both fail** |
| dual_swap_consistency | ≥ 0.90 | 0.571 ✗ | 0.714 ✗ | **BLOCKING — both fail** |

**Verdict: no candidate is promotable.** The TRUE-side and hard-bucket gates are the primary blockers.

### Key Deltas

- robust_no_leak vs pre_no_leak: +10pp overall, +10.6pp true, +5.1pp hard. Robust rules v1 is better on no-leak.
- robust_hardest vs pre_hardest: −5pp overall, −13.5pp true, −13.5pp hard. **Robust rules v1 regresses on hardest.** Adding more FALSE rules hurts TRUE recall on adversarial slices.
- candidate_no_leak vs robust_no_leak: −10pp overall, −29.8pp true, −23.1pp hard. **Distilled candidate is strictly worse.** LLM distillation destroyed operational content.

## Root-Cause Analysis

### 1. The Cheatsheet is 70% Empty

| Cheatsheet | Bytes Used | Bytes Available | Utilization |
|------------|----------:|---------------:|------------:|
| pre-robust | 3,143 | 7,097 | 30.7% |
| robust v1 | 2,759 | 7,481 | 26.9% |
| distilled candidate | 2,933 | 7,307 | 28.6% |
| **10KB limit** | — | **10,240** | — |

We have **~7,300 bytes of unused capacity** in every cheatsheet variant. This is the single largest missed opportunity: we are starving the model of information while having budget to give it 3–4× more content.

### 2. The Cheatsheet Teaches FALSE Well but TRUE Poorly

All three cheatsheets give the model explicit, concrete tools for FALSE:
- 7 stock size-2 magma tables (const0, const1, left-zero, right-zero, xor, and, or)
- 5 size-3 linear magma tables
- Multiplicity-balance refutation rule
- Clear "if Eq1 holds here and Eq2 fails, answer FALSE" procedure

For TRUE, the cheatsheets say only:
- "If Eq2 is a substitution instance of Eq1, TRUE" (no worked example of how to check)
- "Try a short rewrite chain" (no concrete chain shown)
- "Projection laws often prove nested targets" (no template)

A 3B model cannot invent substitution-checking or rewrite-chain reasoning from a one-sentence hint. It needs **worked examples, step-by-step templates, and explicit decision criteria**.

### 3. Proof Pattern Data Exists But Is Not Used

`workstream_analysis.py` already mined 10,657 TRUE proof patterns and 600 FALSE counterexample patterns from the dense matrix. The method breakdown:

| TRUE Method | Count | Share | In Cheatsheet? |
|-------------|------:|------:|:--------------:|
| Specialization (direct substitution) | 6,661 | 62.5% | 1 sentence |
| Structural simplification | 1,807 | 17.0% | 1 sentence |
| Rewriting | 1,661 | 15.6% | 1 sentence |
| Unresolved direct proof | 460 | 4.3% | No |
| Duality-then-specialization | 68 | 0.6% | 1 sentence |

| FALSE Method | Count | Share | In Cheatsheet? |
|--------------|------:|------:|:--------------:|
| Known small magma | 511 | 85.2% | Yes (good) |
| Linear magma | 67 | 11.2% | Yes (good) |
| Random/exhaustive search | 16 | 2.7% | No |
| Twisted/translation-invariant | 2 | 0.3% | No |

The FALSE side is well-served. The TRUE side has detailed pattern data that has never been encoded into the cheatsheet.

### 4. LLM Distillation Actively Harms Quality

The distilled candidate (produced by `distill.py` via `qwen2.5:3b` with 150 balanced demos, rationale augmentation, and the Honda et al. method) collapsed TRUE accuracy from 31.9% → 2.1%.

Reading the candidate text reveals why: it is generic educational prose ("simplify equations", "identify patterns", "construct simple magma tables") with no executable algebraic procedures. The distillation erased every specialized construction and replaced it with vague advice.

This failure mode matches what the public leaderboard shows for "low-reason" mode: **deceptively moderate accuracy with terrible F1**, driven by FALSE-only bias, exactly the same pathology as our candidate.

Distillation conclusion: **abandon LLM-generated cheatsheets.** Human-authored content with mined data backing is the viable path for a 3B model. The distillation pipeline (`distill.py`) remains useful for ablation testing, not for producing final artifacts.

### 5. The Model Has a FALSE-Default Bias

Across all runs, the model's behavioral signature is:
- When uncertain → predict FALSE
- When equation pairs are complex → predict FALSE
- When rewrite reasoning is needed → skip to FALSE

This produces high false accuracy (77–94%) but catastrophic true accuracy (2–32%). The base rate in the dense matrix is 37.12% TRUE / 62.88% FALSE, so majority-class guessing alone would give ~63% accuracy — some of our "accuracy" is likely just this.

The dual-swap test exposes this directly: on 7 paired problems, consistency is 43–71%, meaning the model flips its answer when equations are dually rewritten, which should not change the truth value.

## Cheatsheet Architecture Rethink

### What's Wrong With the Current Design

The current cheatsheet is a **rule list** — a sequence of labeled conditions the model should check. This works when the model can execute the rules, but `qwen2.5:3b` struggles with:
- Abstract procedural instructions ("check if Eq2 is a substitution instance")
- Implicit context ("try a short rewrite chain" — what does the chain look like?)
- Absence of concrete examples (the rules describe WHAT to check, not HOW)

### Proposed Architecture: Decision Tree + Worked Examples + Lookup Tables

Use the full 10KB budget with this layout:

```
Section 1: INSTANT CHECKS (~300 B)
  Identity, x=x, singleton — keep as-is, these work.

Section 2: SUBSTITUTION WORKED EXAMPLES (~2,000 B)  ← NEW
  5-8 concrete TRUE examples showing step-by-step substitution checking.
  E.g. "Eq1: x◇y=x. Eq2: x◇(y◇z)=x. Substitute y◇z→y in Eq1: x◇y=x.
  Now x◇(y◇z) equals x◇(y)=x. TRUE."
  
  Include the top specialization signatures from proof_patterns:
  - constant→constant (1698 cases)
  - singleton_equiv→singleton_equiv (1023 cases)
  - projection→projection (950 cases)
  
  Include 2-3 rewrite-chain examples with explicit step-by-step.

Section 3: DUALITY (~400 B)  ← EXPANDED
  Explicit dual-swap invariance rule.
  Worked example of duality-then-specialization.
  "CRITICAL: if you would answer differently for dual(Eq1)→dual(Eq2),
   you are wrong. The answer MUST be the same."

Section 4: SINGLETON / E2-TYPE (~500 B)
  Keep current content. Add: "1496 of 4694 equations are singleton-forcing."
  
Section 5: REFUTATION RULES (~400 B)
  Multiplicity balance — keep as-is.
  
Section 6: MAGMA TABLES + EVALUATION PROCEDURE (~2,000 B)  ← EXPANDED
  Size-2 tables with explicit evaluation walkthrough.
  For each table, show how to evaluate both sides of an equation.
  Size-3 linear tables with (a,b,p) parameters.
  One worked FALSE example: "Eq1: x◇y=y◇x. Check const0: 0◇0=0, 0◇1=0,
  1◇0=0, 1◇1=0. LHS always = RHS? Yes. Eq2: x◇y=x. Check const0:
  0◇0=0=LHS 0? Yes. 0◇1=0=LHS 0? Yes. 1◇0=0=LHS 1? No. FALSE."

Section 7: ANTI-COLLAPSE GUARDRAILS (~600 B)  ← NEW
  "If you cannot find a counterexample in ANY of the tables above,
   that is EVIDENCE FOR TRUE, not permission to guess FALSE."
  "If Eq1 has more operations/depth than Eq2 and same variables,
   TRUE is structurally plausible — look for a specialization path."
  "Equations with nested self-application (x◇(x◇x), etc.) often
   imply their simpler variants. Do not default to FALSE."
  Explicit list of 3-5 commonly-missed TRUE patterns from error analysis.

Section 8: HARD TRUE TEMPLATES (~1,500 B)  ← NEW
  Method-tagged examples from the hardest error equations:
  - Eq1576 family: x = (y◇z)◇(y◇(y◇w)) — rewrite approach
  - Eq54 family: x = x◇(y◇(x◇z)) — self-referential substitution
  - Eq2544 family: x = (y◇((y◇y)◇y))◇y — absorption argument

Section 9: DECISION DISCIPLINE (~300 B)
  Two-pass mandate:
  Pass 1: Try refutation (magma tables, multiplicity).
  Pass 2 (MANDATORY if Pass 1 fails): Try specialization/rewrite proof.
  Only answer FALSE if Pass 1 succeeds with an explicit witness.
  Only answer TRUE if you can articulate a substitution or rewrite path.

TOTAL: ~8,000 B of 10,240 — leaves buffer for tuning.
```

### Key Design Principles

1. **Show, don't tell.** Replace "check if Eq2 is a substitution instance" with a worked example the model can pattern-match against.
2. **Fill the budget.** Going from 2.8KB to 8KB triples the information density at zero inference cost.
3. **Balance TRUE and FALSE.** Current cheatsheets are ~60% FALSE procedures, ~15% TRUE procedures, ~25% discipline text. Target: 40% TRUE, 35% FALSE, 25% discipline+structure.
4. **Anti-collapse by design.** Make the model's default state "undecided, need more checking" rather than "probably FALSE."
5. **Surface the mined data.** The 10,657 proof patterns and 600 counterexample patterns are the highest-quality training signal we have — encode the top patterns directly.

### Why Not LLM Distillation

The Honda et al. pipeline in `distill.py` is designed for large models that can compress and generalize. For a 3B model:
- Compression erases procedural detail; the model can't reconstruct what was removed.
- Generalization produces platitudes ("identify patterns") instead of executable rules.
- The seed rationales are long chain-of-thought traces (128–256 tokens each) that consume demo budget without adding cheatsheet-relevant signal.

The better path is **human-authored content backed by systematic data mining**: use `workstream_analysis.py` pattern outputs to select which examples and rules to include, then write them by hand with explicit algebraic steps.

## Dataset and Infrastructure Facts

| Fact | Value | Source |
|------|-------|--------|
| Total equations | 4,694 | equations.txt |
| Dense matrix | 4694×4694 | export_raw_implications_14_3_2026.csv |
| Base rate | 37.12% TRUE, 62.88% FALSE | Matrix cell counts |
| Singleton-equivalent equations | 1,496 (31.8%) | workstream_d_analysis.json |
| Singleton criterion (disjoint-vars) | 1,044 of 1,496 | Partial coverage |
| Small-magma FALSE coverage | 96.3% of all FALSE | 524 magmas size ≤ 4 |
| Proof patterns mined | 10,657 | proof_patterns_robust_rules.json |
| Counterexample patterns mined | 600 (sampled) | counterexample_patterns_robust_rules.json |
| Paper techniques implemented | 8 of 8 | magma_search.py, solver.py, proof_search.py |
| Cheatsheet byte limit | 10,240 | config.py |

### ML Pipeline (Research-Only)

| Metric | Value |
|--------|-------|
| XGBoost 5-fold OOF accuracy | 98.61% |
| OOF log loss | 0.044 |
| Top feature: counterexample_size | 44.8% importance |
| Top feature: has_counterexample | 37.4% importance |
| Test accuracy (10K holdout) | 99.55% |
| Test TRUE accuracy | 100.0% |
| Test FALSE accuracy | 99.1% |

The ML model is excellent for research triage and pattern ranking. It is **not submission-valid** (uses solver-computed features unavailable at inference). Its feature importance confirms that counterexample existence is the dominant signal — but the LLM cheatsheet must teach the model to FIND counterexamples manually, which is a different problem.

## Public Leaderboard Comparison

Source: local copy of SAIR benchmark, 200 hard problems, 25 models, 3 repeats each.

### default_reason Mode (Extended Thinking)

| Model | Accuracy | F1 | Consistency |
|-------|--------:|----|------------:|
| Gemini 3.1 Pro Preview | **0.902** | **0.878** | 0.928 |
| Grok 4.1 Fast | 0.713 | 0.704 | 0.875 |
| Qwen 3.5 397B | 0.637 | 0.655 | 0.885 |
| Kimi K2.5 | 0.650 | 0.650 | 0.808 |
| Claude Sonnet 4.6 | 0.588 | 0.493 | 0.840 |
| GPT-5 Nano | 0.603 | 0.387 | 0.850 |
| Claude Opus 4.6 | 0.530 | 0.316 | 0.977 |
| Deepseek V3.2 | 0.632 | 0.126 | 0.943 |
| Llama 3.3 70B | 0.630 | 0.000 | 1.000 |

### low_reason Mode (No Chain-of-Thought)

| Model | Accuracy | F1 | Consistency |
|-------|--------:|----|------------:|
| Gemini 3.1 Pro Preview | **0.692** | **0.586** | 0.995 |
| Qwen 3.5 397B | 0.640 | 0.561 | 0.845 |
| Claude Opus 4.6 | 0.547 | 0.539 | 0.845 |
| Claude Sonnet 4.6 | 0.573 | 0.500 | 0.808 |
| Grok 4.1 Fast | 0.637 | 0.035 | 0.995 |
| GPT-5.4 | 0.640 | 0.169 | 0.960 |

### What This Tells Us

1. **Our best run (robust_no_leak, 0.61 acc) is in the range of mid-tier public default_reason models** — not embarrassing on aggregate, but our F1 would be poor because of TRUE collapse.

2. **The F1 gap is the critical metric.** Many public models achieve 0.60–0.64 accuracy with F1 near 0.00–0.17, meaning they also have the FALSE-default bias. The competitive models (Gemini Pro, Grok 4.1) solve this with extended reasoning chains, not just better prompts.

3. **low_reason vs default_reason reveals the reasoning bottleneck.** Grok 4.1 drops from 0.713 to 0.637 accuracy and F1 from 0.704 to 0.035 when reasoning is disabled. Our 3B model is effectively in low_reason mode — it cannot do extended multi-step algebraic reasoning. The cheatsheet must **pre-compute** the reasoning steps for it.

4. **The achievable target with a 3B model and 10KB cheatsheet is probably 0.60–0.70 accuracy with balanced F1 around 0.50–0.60**, comparable to mid-tier large models with reasoning. This requires using the full byte budget on concrete, pattern-matchable content.

5. **Caveat:** our local hard slices are not the exact same 200 problems or protocol as the public leaderboard. This is directional, not a strict rank.

## Cheatsheet A/B/C Comparison

### Structure Comparison

| Feature | pre-robust | robust v1 | distilled candidate |
|---------|-----------|-----------|-------------------|
| Byte size | 3,143 | 2,759 | 2,933 |
| Budget used | 30.7% | 26.9% | 28.6% |
| Magma tables | 7 size-2 + 5 size-3 | 11 size-2 + 5 size-3 | 1 generic table |
| TRUE worked examples | 0 | 0 | 0 |
| Specialization template | 1 sentence | 1 sentence | vague paragraph |
| Rewrite template | 1 sentence | 1 sentence | none |
| Anti-FALSE-bias guardrails | weak | stronger | none |
| Duality section | 1 sentence | 1 sentence | 1 sentence |
| Singleton coverage | partial | partial + count | none |
| Multiplicity rule | yes | yes | mentioned |
| Decision discipline | yes | yes (stronger) | generic summary |

### Why Robust v1 Beat Pre-Robust on No-Leak

Robust v1 added:
- 4 more size-2 magma tables (nand, implication-like, left-and-not, right-xor-and)
- Stronger anti-collapse discipline text ("do not answer FALSE only from 'could not find counterexample quickly'")
- Explicit "what counts as a real TRUE/FALSE" section

These changes improved overall accuracy by 10pp and true accuracy by 10.6pp on no-leak. The additional magma tables caught more FALSE cases correctly, and the anti-collapse text slightly reduced FALSE-default behavior.

### Why Robust v1 Regressed on Hardest

The hardest subset is 52% hard-bucket (problems where small finite magmas don't help). Adding more magma tables doesn't help here — it just makes the model more confident about FALSE on cases where it should be uncertain. Without corresponding TRUE skill improvements, the net effect was worse.

### Why Distillation Collapsed

The distilled candidate replaced every specific algebraic procedure with generic advice:
- "Simplify Equations: Break down complex nested expressions into simpler parts" (how?)
- "Identify Patterns: Look for common patterns or structures" (which ones?)
- "Counterexamples: Construct simple magma tables to find counterexamples" (which tables?)

A 3B model reading this produces the same behavior as reading nothing: guess FALSE when uncertain.

## Top Error Equations

| Equation | Errors (5 runs) | Form | Failure Mode |
|----------|:-----:|------|-------------|
| Eq1576 | 11 | x = (y◇z)◇(y◇(y◇w)) | Nested self-referential; TRUE instances need multi-step rewrite |
| Eq54 | 10 | x = x◇(y◇(x◇z)) | Self-application; specialization is non-obvious |
| Eq2544 | 10 | x = (y◇((y◇y)◇y))◇y | Absorption; TRUE via iterated collapse |

These equations share common traits:
- Deep nesting (3+ operation levels)
- Self-referential structure (variable appears multiple times in non-trivial positions)
- TRUE implications exist via constructive arguments the model cannot derive from hints alone
- FALSE is not the right default here, but the model has no positive template to match against

## Bias Decomposition

| Bias Type | Evidence | Impact | Fix |
|-----------|----------|--------|-----|
| FALSE-default | true_acc 0.02–0.32 across all runs; base rate is 37% TRUE | Most errors are missed TRUEs | Anti-collapse guardrails, worked TRUE examples |
| Complexity aversion | Eq1576/Eq54/Eq2544 are all deeply nested and all missed | Model retreats to FALSE on complex-looking equations | Explicit templates for nested-structure families |
| Distillation erasure | candidate eliminated 98% of TRUE recalls | LLM distillation is destructive for 3B target | Human-authored cheatsheet |
| Dual-swap inconsistency | 43–71% consistency (7 paired problems) | Model doesn't internalize that duality preserves truth | Explicit duality section with worked example |

## Concrete Next Steps

### P0: Rewrite the Cheatsheet (Target: 8–9.5KB)

1. **Keep** the structural skeleton (instant → singleton → refutation → discipline).
2. **Add 5–8 worked TRUE examples** from top proof patterns: constant→constant specialization, projection→projection collapse, rewrite-chain with explicit steps.
3. **Add 2–3 worked FALSE examples** showing full magma table evaluation procedure (not just "check const0" — show the actual cell-by-cell computation).
4. **Expand duality section** with a concrete example and the invariance mandate.
5. **Add anti-collapse block** with explicit "if no counterexample found in all tables → this is evidence for TRUE" language and list of commonly-missed TRUE patterns from error analysis.
6. **Add hard-TRUE templates** for Eq1576, Eq54, Eq2544 family structures.
7. **Measure on-disk bytes** (not `len(text)`; Windows CRLF matters). Verify ≤ 10,240.

### P1: Fix Evaluation Infrastructure

1. **Expand dual-swap coverage.** Only 7 paired problems in current no-leak benchmark. Increase to ≥ 30 pairs for statistical significance on the 0.90 gate.
2. **Add F1 and balanced accuracy** to all eval reports (accuracy alone hides TRUE collapse).
3. **Track per-bucket TRUE/FALSE rates** separately in hard and CE-easy slices.

### P2: Abandon LLM Distillation for Final Artifact

1. Keep `distill.py` as an ablation/research tool.
2. Final cheatsheet is human-authored, backed by `workstream_analysis.py` pattern mining.
3. Use the ML model (98.6% OOF) to rank which examples and rules to include: the features with highest importance (counterexample_size, has_counterexample, rewriting_proved) tell us what the model needs to reason about.

### P3: Multi-Model Parity Check

1. Test the rewritten cheatsheet on `qwen2.5:7b` and `gemma2:2b` (both configured in `config.py`).
2. A cheatsheet that only works on one model size is over-fitted to that model's quirks.
3. The public leaderboard shows huge model-dependent variance — validate on at least 2 models before locking.

## Ratings (10-point scale)

### Contest Performance Readiness: 5.0/10

Best run passes only 1 of 4 gates (overall accuracy). TRUE recall and hard-bucket performance are not competitive. The cheatsheet content is the bottleneck, not the pipeline.

### Mathematical Signal Quality: 6.5/10

All 8 paper techniques are implemented in the solver/search code. Pattern mining has produced 11,257 method-tagged examples. But this mathematical knowledge is trapped in JSON files and Python code — none of it reaches the cheatsheet in usable form. The gap between "what the repo knows" and "what the cheatsheet teaches" is the core problem.

### AI/ML Usage Quality: 7.0/10

The research ML pipeline is excellent (98.6% OOF). The E2E harness with acceptance gates is well-designed. The benchmark integrity controls (no-leak, no format-example leakage, submission-validity metadata) are rigorous. But the distillation step is actively harmful and needs to be replaced with human authoring.

### Cheatsheet Engineering: 3.5/10

Using 30% of the byte budget while failing TRUE recall is a clear engineering failure. The gap between available budget and used budget is the single largest fixable issue. This rating should improve dramatically once the cheatsheet is rewritten to ~8KB with worked examples.

### Benchmark Honesty: 8.5/10

No label leakage, submission-valid metadata on every run, clear gate definitions, dual-swap consistency tracking, bucket-level breakdown. The infrastructure is honest; the results are just not good enough yet.
