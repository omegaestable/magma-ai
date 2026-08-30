# 2026-08-29 order-4 miss-learning session

## Outcome

The 652-row union of seven historical order-4 failure ledgers contained 603
TRUE and 49 FALSE rows.  Under the final solver, the bounded fast-tier replay
solved 611/652 (93.712%): 588/603 TRUE (97.512%) and 23/49 FALSE (46.939%).
There were 0 label mismatches, 0 oracle failures, and 0 crashes.  The 41
remaining skips are 15 TRUE and 26 FALSE.

The directly measured checkpoint after the helper-collapse route was 326/652
(50.000%).  The distilled routes raised that to 611/652, a net gain of 285
rows.  Aggregate solver time over the corpus fell from 19,732.8 s to 3,184.4 s
(-83.9%) because most former 60-second skips became short deterministic proofs.
Final solved-row timing: mean 4.884 s, p50 0.547 s, p95 3.792 s, p99 4.252 s,
slowest 5.084 s.

## Learned structural families

The solver policy contains structural equation matchers and reusable proof
families, never row ids or benchmark answer literals.

| Family | Structural motifs | Historical route hits | Focused campaign |
|---|---:|---:|---:|
| helper collapse | 2 | 202 | included in the 652-row replay |
| anchored projection (dual) | 2 | 150 | 150/150 |
| product constancy | 4 | 110 | 110/110 |
| spine constancy | 5 | 33 | 33/33 |
| **total** | **13** | **495** | **293/293 distilled-family rows** |

All three focused distilled campaigns had 0 oracle failures and 0 crashes.
Eight of the 495 route hits replace older successful completion/egg routes, so
route hits are not identical to net-new solves.

Exact final 652-row route counts:

- helper collapse: 202
- anchored projection: 150
- product constancy: 110 (25 outer-left-free, 29 outer-left-repeated,
  40 outer-right-free, 16 outer-right-repeated)
- spine constancy: 33 (6 left-inner-free, 10 left-power, 2 right-crossed,
  2 right-inner-free, 13 right-power)
- other TRUE completion: 93 (49 bridge, 32 collapse, 12 join)
- pre-existing distilled FALSE certificates: 10
- finite witnesses: 13

## Completed 100k backtest

The completed pre-change 2026-08-29 100k campaign scored 99,909/100,000
(99.909%), with 91 skips, 0 label mismatches, and 0 crashes.  All 91 misses
occur in the 652-row replay, so an exact id-level reconciliation gives the
post-change result on those same rows:

- 84/91 old misses recovered (92.308%)
- corrected score: **99,993/100,000 (99.993%)**
- remaining: 7 skips, 0 incorrect, 0 crashes
- recovered routes: 56 helper collapse, 7 anchored projection, 19 product
  constancy, 2 spine constancy

The seven remaining old-sweep rows are three TRUE rows (eq1 families 3676 and
4560) and four FALSE rows (eq1 families 1979, 2473, and 3698).

## Completed fresh 20k unseen sweep

After the interrupted 100k attempt, a new manifest was drawn with seed
20260831.  It contains 10,000 TRUE and 10,000 FALSE rows and excludes every
prior `etp-sample-*`, `etp-sweep-*`, and interrupted 100k manifest.  The final
audit used `--effort fast --row-budget 60 --workers 3`.

- solved: **20,000/20,000 (100.000%)**
- TRUE solved: **10,000/10,000**
- FALSE solved: **10,000/10,000**
- skips, crashes, oracle failures, label mismatches: **0, 0, 0, 0**
- aggregate audit time: 1,447.3 s; report row-time sum: 1,564.1 s
- row-time mean 0.078 s, p50 0.003 s, p95 0.267 s, p99 0.458 s,
  slowest 25.136 s
- certificate shapes: exact_expr 918, lemma_chain 4,273, singleton 4,693,
  other 109, lemma 7
- route families: witness 9,394; singleton 4,693; completion 4,683;
  spine 342; constancy 253; linear 223; universal_identity 79; rewrite 71;
  absorption_context_bridge 37; enum_fin3 31; tail_square_singleton 18;
  equational_closure 17; absorption_closure 16; derived_cp_closure 12;
  distilled 9; paired_tail_singleton 9; nested_square_singleton 9;
  forked_square_singleton 8; bridge 8; affine 7; outer_sandwich_singleton 7;
  reverse_deep_repeat_singleton 6; wrapped_tail_singleton 6;
  sandwich_repeat_singleton 5; deep_repeat_singleton 5

The 109 `other` certificates are accepted by the audit's label/oracle path but
are not independently checked by the proof-kernel classifier; this does not
change the zero soundness-event result.  The complete artifacts are
`etp-unseen-20k-20260829-final.jsonl`, its audit JSON, and the generated sweep
summary in this directory.

## Fresh sweep status

A fresh balanced manifest of 100,000 rows (seed 20260830; 50,000 TRUE and
50,000 FALSE) was generated after excluding all prior `etp-sample-*` and
`etp-sweep-*` manifests plus the standing coverage ledger.  The user halted
the audit after the last logged completed prefix of 67,700 rows.  The runner
had reported no crash or infrastructure failure, but it writes its report only
at normal completion, so **there is no valid accuracy numerator for this
partial run**.  Do not quote it as a completed 100k sweep.

## Verification and package

- five representative spine-constancy certificates: 5/5 accepted by the
  official local Lean judge (3.1--8.9 s)
- judge fixture: 234 accepted certificate pins after append
- focused certificate-pin gate before append: 229 passed, 1 skipped
- final package gate: 553 passed, 2 skipped
- official layout validator: OK
- packaged solver: 456,604 bytes / 500,000 bytes (43,396 bytes headroom)

The Windows judge utility now prepends elan's shim directory itself.  The ETP
sampler now expands exclusion globs independently of shell behavior, so the
documented disjoint-sampling command works on PowerShell.

## Remaining bottleneck

The residual historical set is small but asymmetric: TRUE proof coverage is
97.5%, while FALSE witness coverage is 46.9%.  The next useful work is not more
general completion depth.  It is:

1. finite/infinite countermodel families for the 26 FALSE residuals, especially
   repeated eq1 families 481, 1979, and 2531 (three each);
2. new proof motifs for the 15 TRUE residuals, led by eq1 families 3567, 3676,
   and 4560 (two each);
3. checkpointing in `audit_corpus.py` before another multi-hour sweep, so a
   requested halt preserves prefix statistics.

No external LLM equations were disclosed.  The attempted cheap-agent lane was
not used because sending repo-derived equations to OpenRouter lacked explicit
data-disclosure approval; all promoted gains are deterministic.
