# Order-4 miss-elimination plan

**Date:** 2026-08-29  
**Objective:** eliminate the current order-4 misses with general solver
mechanisms, while keeping the solver fast, deterministic, sound, and accepted
by the official Lean judge.

## Current baseline

The latest three campaigns cover **400,000 order-4 rows** (40 batches of
5,000 TRUE and 5,000 FALSE rows). They are the current miss frontier:

| Result | Count |
| --- | ---: |
| Solved | **399,618 / 400,000 (99.9045%)** |
| Skipped | **382** — 362 labelled TRUE, 20 labelled FALSE |
| Crashes / oracle failures / label mismatches | **0 / 0 / 0** |
| Skips with a four-operation hypothesis | **382 / 382** |
| Skips with a bare-variable side on the hypothesis | **293 / 382 (76.7%)** |

The broader recorded order-4 history is larger:

| Coverage slice | Row evaluations |
| --- | ---: |
| Audited campaigns: Aug 20 20k + Aug 25 110k + Aug 26 200k + Aug 27 200k + Aug 29 400k | **930,000** |
| Unique IDs in those audited campaigns | **929,955** |
| Additional Aug 28 uniform reference draw | **2,000** |
| All recorded generated order-4 rows, unique by ID | **932,000 evaluations / 931,955 unique** |

The 45 duplicate IDs are between the latest raw draw and earlier raw
manifests; batch files and `ALL` files are alternate views and are not added
again. The 2,000-row Aug 28 draw is a population reference, not included in
the audited miss ledger.

The source reports are:

- `stage2/results/2026-08-20-full-graph-20k-sample.md`
- `stage2/results/order4-2026-08-25-ALL-summary.md`
- `stage2/results/etp-sweep-200k-2026-08-26-ALL-summary.md`
- `stage2/results/etp-sweep-200k-2026-08-27-ALL-summary.md`
- `stage2/results/etp-sweep-20260829-100k-summary.md`
- `stage2/results/etp-sweep-20260829-200k-summary.md`
- `stage2/results/etp-sweep-20260829-100k-b31-b40-summary.md`

The historical audited failure ledgers are disjoint by row ID and contain
**652 unique misses**: **603 TRUE and 49 FALSE**. The latest 400k campaign's
382 rows are the current fast-tier target; the final acceptance pass must
re-run the full 652-row historical union so older misses are not silently
forgotten.

The two largest hypothesis families account for **202 / 382** misses. The top
eight account for **338 / 382 (88.5%)**:

| Diagnostic eq1 family | Misses |
| --- | ---: |
| `x = (y ◇ y) ◇ (x ◇ (x ◇ z))` (`1517`) | 102 |
| `x = ((y ◇ x) ◇ x) ◇ (z ◇ z)` (`2095`) | 100 |
| `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` (`650`) | 29 |
| `x ◇ y = y ◇ ((z ◇ x) ◇ x)` (`3565`) | 29 |
| `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` (`2923`) | 25 |
| `x ◇ y = y ◇ ((z ◇ w) ◇ x)` (`3577`) | 20 |
| `x ◇ y = (y ◇ (z ◇ w)) ◇ x` (`3983`) | 17 |
| `x ◇ y = (y ◇ (y ◇ z)) ◇ x` (`3967`) | 16 |

The numeric law IDs are a triage index, not solver policy. A successful change
must recognize the structural shape and work on held-out equations.

## Work plan

### 1. Freeze and classify the target

1. Treat the three failure ledgers as one append-only, deduplicated manifest.
   Preserve the original row IDs, equation texts, label, batch seed, elapsed
   time, and `eq1` family.
2. Partition it into TRUE and FALSE queues before changing a route. Do not
   infer TRUE from a finite search that timed out.
3. For each row, record the route frontier: last route reached, whether the
   finite search saw a model, whether it exhausted its scheduled orders, and
   whether the row was stopped by the 60-second audit budget.
4. Reproduce a representative from each of the top families in isolation at
   positive-budget `standard` and `deep` tiers. Keep the broad 400k corpus
   fixed as the held-out regression set, then re-run the historical 652-row
   union before promotion; do not spend another broad sweep on baseline
   collection yet.

### 2. Close the TRUE lane with general helper-law mining

The main opportunity is not another larger undirected completion run. The
misses are dominated by hypotheses of the form `x = F(...)` or a
left/right-division-like equality, where the existing engines spend their
budget without naming the short intermediate law that makes the collapse
obvious.

Implement and measure a bounded, deterministic hypothesis-specific helper-law
miner:

1. Generate self-overlap candidates by unifying a non-variable subterm of one
   side of `eq1` with a renamed occurrence of `eq1`. Include both orientations
   and the dual left/right forms; preserve the occurs check.
2. Normalize each overlap to a small universally quantified equation, reject
   duplicate/renamed candidates, and cap term size, number of candidates, and
   per-row time before any expensive saturation.
3. Prove each candidate from `eq1` using the existing certificate-safe
   `lemma_chain`/guided-chain machinery. Discard anything the independent
   proof kernel cannot verify.
4. Feed only verified helper laws into a small multi-law closure aimed first at
   a collapse `a = b`, then at the actual goal. The emitted certificate must
   remain an existing accepted shape; do not add a new oracle surface.
5. Use the top families as development fixtures, but measure the miner against
   the latest 362 TRUE misses, then the historical 603-row TRUE union and a
   negative-control set. A family-specific rule is
   acceptable only when it is expressed as a parse-tree/motif predicate, not as
   an ID or pasted equation list.

The prompt below is for proposing candidate intermediate laws. It is not an
authority: the solver must re-prove every proposed law and judge-check any new
certificate shape.

### 3. Close the FALSE lane with verified witnesses

The latest 20 labelled FALSE misses, and then the historical 49-row FALSE
union, deserve a separate queue. For each candidate:

1. Run structured finite-model/formula search with a separate budget per order
   or construction family. Do not let one expensive order starve the next.
2. Prefer compact affine/quadratic, permutation-twisted, and propagation
   constructions; vary carrier order and variable arity. A failed search is
   only a skip, never a TRUE result.
3. Exhaustively check the hypothesis and a failing goal assignment in Python,
   then render and verify the certificate under the configured judge caps.
4. Add a real-judge fixture for each genuinely new witness family. Keep the
   solver's answer JSON exactly `{verdict, code}`.

If a FALSE row remains without a witness, leave it unresolved and record the
search frontier. Do not turn the label or a timeout into solver policy.

### 4. Optimize for speed after coverage exists

The current 400k pass has p50 **0.005 s**, p95 **0.329 s**, p99 **0.666 s**;
the misses are the rows that consume roughly the whole 60-second audit budget.
Therefore the acceptance target has two gates:

1. **Coverage:** zero skips on the frozen 382-row latest-frontier manifest and
   then on the full 652-row historical miss union, with zero crashes, oracle
   failures, or label mismatches.
2. **Pacing:** no broad slowdown; report mean/p95/max and route counts, and
   keep the new miner bounded so solved rows do not pay for it unnecessarily.

Run one audit at a time, record worker count and machine load, and diff by row
ID. Re-run the frozen manifest after every route change, then re-run the full
official/HF regression battery and judge-pin representative TRUE and FALSE
certificates. A result is not promoted from local oracles alone.

## Ready-to-paste implementation prompt

```text
You are improving the Stage 2 SAIR magma solver in this repository.

Objective: eliminate the current order-4 miss frontier with a general,
deterministic, fast, sound solver mechanism. The latest evidence is 400,000
rows: 399,618 solved (99.9045%), 382 skipped, 362 labelled TRUE and 20
labelled FALSE, with zero crashes/oracle failures/label mismatches. The
broader audited history is 930,000 row evaluations / 929,955 unique IDs, and
its historical miss union is 652 rows (603 TRUE, 49 FALSE). All 382 latest
hypotheses have four operations; 293 have a bare-variable side. The largest
latest diagnostic families are eq1 shapes 1517 (102 misses), 2095 (100), 650
(29), 3565 (29), 2923 (25), 3577 (20), 3983 (17), and 3967 (16).
Use the failure ledgers and ORDER4_MISS_ELIMINATION_PLAN.md as input, but never
hardcode those IDs or equations into solver policy.

First read CLAUDE.md, stage2/docs/LATEST_HANDOFF.md,
stage2/docs/DEEP_SWEEP_RUNBOOK.md, and this plan. Preserve unrelated worktree
changes. Do not run another broad sweep before reproducing the frozen misses.

Work in two explicit lanes:

1. TRUE lane: build a bounded deterministic self-overlap/helper-law miner for
   four-operation hypotheses. Generate overlap candidates by unifying a
   non-variable subterm of eq1 with a renamed occurrence, with both
   orientations and an occurs check. Deduplicate by canonical renaming and
   bound term size, candidate count, and per-row time. Re-prove every candidate
   from eq1 using the existing kernel-checked lemma-chain/guided-chain path,
   then feed verified helpers into a small multi-law closure aimed at a=b or
   the goal. Do not replace this with another undirected, globally timed
   completion pass.

2. FALSE lane: process the latest 20 labelled FALSE rows, then the historical
   49-row FALSE union, separately. Search compact
   finite/formula witnesses with independent budgets per order/family; verify
   the hypothesis exhaustively, show a failing goal assignment, render under
   the configured judge caps, and real-judge representative new shapes. Never
   infer TRUE from a timed-out or incomplete search.

Acceptance criteria:

- zero skips on the frozen 382-row manifest and then the full 652-row
  historical miss union;
- zero crashes, oracle failures, label mismatches, and no incorrect answers;
- no regression on the official/HF row-id comparison;
- p50/p95/max and route counts reported, with solved rows not paying for
  expensive miss-only work;
- every new certificate family independently kernel-checked and representative
  certificates accepted by the real Lean judge;
- no benchmark-ID policy, no speculative Lean, no simp/aesop/grind shortcut,
  no network/local-secret dependency, and no --budget-tokens 0 evidence.

After each meaningful change run the smallest isolated miss fixture, then the
frozen manifest, then the official/HF regression and judge pins. Record the
result in a dated stage2/results note and update the rails only with measured
facts.
```
