# Cheatsheet Revamp Notes (2026-03-14)

## Ratings

### pre-robust rules: 4.0/10

The sheet has one good idea: it puts singleton forcing, substitution, and small counterexample tables in one place. But it is still basically a hint list. It tells the model what kinds of arguments exist without teaching it how to execute them.

Example: it says `If Eq2 is a substitution instance of Eq1, TRUE immediately`, but gives no worked substitution. For a 3B model, that is too abstract. A case like `x = y*(z*x) => x = y*(x*x)` is easy for a human and often missed by the model without an explicit template.

The other problem is byte usage. A cheatsheet that uses about 3.1KB out of 10KB while failing TRUE recall is leaving too much value on the table.

### robust rules v1: 5.5/10

This is the best of the old set because it strengthens the FALSE side and adds some discipline against instant collapse to FALSE. That likely explains why it beats the earlier sheet on no-leak overall accuracy.

But it still has the same structural flaw: it is richer on refutation procedure than on proof procedure. The counterexample bank is concrete. The TRUE side is still mostly slogans.

Example: the sheet knows about projection laws, but it does not show a pattern such as `x = x*(y*z) => x = x*(y*x)` by `z<-x`. That omission is exactly where many TRUE misses come from.

### distilled candidate: 1.5/10

This is not a compressed expert cheatsheet. It is generic algebra-study advice.

Example phrases like `Simplify equations`, `Identify patterns`, and `Construct simple magma tables` have almost no operational value here. They do not name concrete substitutions, concrete tables, or concrete decision thresholds. The repo's own measured behavior matches this: the candidate preserved FALSE bias and destroyed TRUE recall.

As a distillation of the implication graph, it is poor. It does not surface the actual dominant proof mode, which is direct specialization, and it does not preserve the actual dominant hard-FALSE workflow, which is a concrete small-magma bank followed by linear tables.

## How Well The Old Cheatsheets Distill The Full Implication Graph

Rough answer: badly on the TRUE side, moderately on the FALSE side.

The graph contains at least three kinds of usable structure for Stage 1:

1. Very high-frequency proof macros.
2. Very high-frequency counterexample tables.
3. A few low-frequency but high-value hard-case families.

The old sheets only distill category 2 well.

Evidence:

- The proof-pattern mining says 6661 direct proofs are specialization, 1807 are structural simplification, and 1661 are rewrite. The old sheets compress this into one sentence per method. That is not real distillation; that is lossy labeling.
- The counterexample mining says 511 sampled hard FALSE pairs are already handled by known small magmas and 67 by linear magmas. The old sheets do encode that bank concretely. That part is real distillation.
- The hardest missed TRUE families called out in the repo report, especially Eq54/Eq1576/Eq2544 types, were not distilled into any worked template at all.

So the graph-to-cheatsheet transfer quality is asymmetric:

- FALSE distillation quality: about 7/10
- TRUE distillation quality: about 2/10
- overall graph distillation quality: about 4/10

## Do The Math Papers And Model-Construction Techniques Add Value?

Yes offline, but only partially in the old artifact.

The paper-driven constructions absolutely add value to the repo:

- They justify the stock small-magma bank.
- They justify linear, translation-invariant, twisted, and constructive counterexample families.
- They support the solver and mining stack that produced the pattern summaries.

But almost none of that value reached the old final artifact. The old sheets use the easiest output of the papers, namely the stock tables, and almost none of the higher-order lessons.

Rough score:

- Value to offline research stack: 8.5/10
- Value realized in old cheatsheets: 3.5/10

Reason:

- `known_small_magma` and `linear_magma` matter directly because the model can execute them from text.
- `translation_invariant` and `twisted_magma` are valuable mostly as mining tools and fallback ideas. They are too rare and too expensive in bytes to dominate the Stage 1 artifact.

## Is The ML Doing Something?

Yes, but not in the live submission artifact.

The ML stack is useful for ranking, triage, and telling you where the information bottleneck is. It is not solving the Stage 1 inference problem directly because the LLM does not see those features at inference time.

What it is doing well:

- Ranking which structures matter.
- Confirming that counterexample existence is the dominant predictive signal.
- Helping choose which proof and counterexample families deserve cheatsheet bytes.

What it is not doing well yet:

- Translating its strong offline signal into compact reasoning macros that a 3B model can actually execute from plain text.

Rough score:

- ML as research triage: 8/10
- ML as current artifact distillation engine: 3/10
- ML as direct submission-time capability: 0/10 by design

## Originality: What Is Actually Novel Enough To Matter Here?

The repo does not need novelty for its own sake. It needs novelty that survives the 10KB boundary and changes model behavior.

The strongest novel directions in this repo are not giant new search systems. They are compact, model-facing compressions of mined structure.

Highest-value ideas:

1. Duality as a mandatory invariant, not a side note.
   The old sheets mention duality once. The new one treats it as a hard constraint because dual-swap inconsistency is a measured failure mode.

2. Family-level proof macros instead of theorem names.
   Examples like `x = x*(y*z) => x = x*(y*x)` are short, executable, and pattern-matchable. That is the right granularity for a small model.

3. Anti-collapse discipline written into the artifact.
   The model's strongest pathology is `uncertain => FALSE`. Encoding explicit guardrails against that is not cosmetic; it is part of the decision procedure.

4. Hard-TRUE templates for the known bad families.
   This is better than blindly adding more FALSE tables, because the measured weakness is not lack of refutation power.

5. Human-authored full-budget compression instead of LLM compression.
   Given the measured failure of distillation, the novel thing is to stop treating LLM summarization as the main artifact-construction step.

## What Changed In This Revamp

- The live `cheatsheet.txt` is now a full-budget human-authored baseline with explicit worked specialization and rewrite patterns.
- The same promoted artifact is archived as `cheatsheets/cheatsheet_2026-03-14_full_budget_v2.txt`.
- The cheatsheet folder now documents which files are baselines versus ablations.
- Top-level docs now present distillation as optional ablation tooling, not the default path.