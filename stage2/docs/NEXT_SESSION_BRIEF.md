# Next session brief — improvement pass (fix from the merged frontier, real LLM tests)

Written 2026-08-27 at the end of three order-4 measurement campaigns (110,000
+ 200,000 + 200,000 rows) plus the 2026-08-25 order-5/order-6 tracks. Read
`CLAUDE.md` first; this file only covers what the next session does.

## Nothing is running

Confirmed at handover: `Get-Process python*` empty. All three sweep chains
finished naturally (`### CHAIN COMPLETE`), none were killed mid-batch.

## This is a FIX session, not another measurement session

Every prior session since 2026-08-25 was pure logging by instruction (see
memory `feedback-measurement-then-bulk-improve`) — accumulate findings across
independently-drawn batches, defer all solver changes to one bulk pass. **This
is that pass.** The standing bar for anything that ships: offline gate green,
an isolated audit diffed by row id showing 0 lost, and — for any
certificate-builder change — real-judge verification (rails 3, 3c). Diff by
row id, never by total (rail 2).

## The merged ledger: what to fix, ranked

Combined evidence base for order-4: **530,000 rows across three independent
draws** (110,000 on 2026-08-25, seed `20260825`/`202608251`; 200,000 on
2026-08-26, seed `20260826`; 200,000 on 2026-08-27, seed `20260827` — 0
overlap between any of the three, verified by row id each time).

### Lever 1 — order-4's frontier is FOUR laws, and this is now proven, not sampled

| eq1 | 110k (08-25) | 200k (08-26) | 200k (08-27) | **Total** | % of all 218 misses |
| --- | --- | --- | --- | --- | --- |
| `650` | 5 | 15 | 27 | **47** | |
| `2923` | 16 | 15 | 18 | **49** | |
| `3569` | 7 | 13 | 14 | **34** | |
| `3983` | 4 | 9 | 10 | **23** | |
| **top-4 sum** | | | | **153** | **70.2%** |
| all misses | 46 | 80 | 92 | **218** | 100% |

The concentration was 70% at 110k, 65% at the first 200k, 75% at the second —
it isn't drifting toward or away from anything, it's noise around a stable
**70%**. Three independently-drawn 100k+ samples agreeing this precisely means
this is the real shape of the frontier, not an artifact of any one batch.

The four patterns (canonical eq1 text):
- `650`: `x = x ◇ (y ◇ ((z ◇ x) ◇ y))`
- `2923`: `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x`
- `3569`: `x ◇ y = y ◇ ((z ◇ y) ◇ x)`
- `3983`: `x ◇ y = (y ◇ (z ◇ w)) ◇ x`

Two rows from this family (`etp_1366_3436`, `etp_3569_4653`, see CLAUDE.md
"Known open frontier") are already characterised: the goal bridge exhausts the
*reachable* theory under self-superposition in under 1 s even at 10× the node
cap, so more clock will not help — their goals need facts self-superposition
structurally cannot derive. **The untried idea on record**: seed completion
with instances of eq1 at goal subterms, `egg_ladder`-style, rather than
relying on saturation alone to reach them.

Merged failure ledgers with full eq1/eq2 text for every miss are on disk:
`stage2/results/order4-2026-08-25-ALL-failures.jsonl`,
`stage2/results/etp-sweep-200k-2026-08-26-ALL-failures.jsonl`,
`stage2/results/etp-sweep-200k-2026-08-27-ALL-failures.jsonl`.

### Lever 2 — order-5 is a size/arity wall, not a family wall, and it's a quarter of the score

20,000 rows (2026-08-25), 353 misses (98.235%). No family dominates — largest
single-id cluster is 4, and 15 different eq1 ids tie at 3. Instead: **all 353
have exactly 5 operations, 352 of 353 have exactly 3 variables, and 325 of 353
(92%) are `eq1_bare_variable_side`** (collapse-shaped hypotheses, `x =
F(y,z,...)`). Whatever fixes lever 1 will not touch this — different shape of
defect entirely.

**Every one of the 353 misses timed out at the exact 300 s row budget**
(`299.6`–`300.0` s across the board) — these are not fast fails, the search
spent its whole budget and didn't get there. That's the single most useful
fact for scoping a fix: it means "not found in time," not "no path exists,"
and a targeted engine or a bigger budget on this specific shape (5 ops, ≤3
vars, bare-variable eq1) is the lever, not a new proof technique.

Order-5 sits at **98.24%** against order-4's **99.96%**, and it's one of four
equal-weight scoring categories — this is where the points are.

Ledger: `stage2/results/order5-sweep-20k-2026-08-25-ALL-failures.jsonl`.

### Lever 3 — the wide countermodel search burns 37–76% of clock hunting witnesses that can't exist

From `sweep_report --diagnose` on 5 profiled order-4 misses (2026-08-25):
`constraint_countermodel`'s wide tier is the single largest consumer on every
one, and on 4 of 5 it's provably wasted — those rows are TRUE and no
countermodel exists at any order the search would reach. Not a deadline bug
(rail 5f-vii is already fixed); the budget is spent exactly as configured, so
the question is whether the *configuration* — scheduling `constraint_countermodel`
ahead of a cheap "can a witness even exist" gate — is right. **Not yet
measured at scale**: re-run `sweep_report.py --diagnose` against the full
218-row combined order-4 ledger (all three campaigns merged) before touching
any scheduling — 5 rows was a pilot, 218 is a population.

### Lever 4 — the FALSE-side frontier, now with enough data to look for structure

27 FALSE misses across the combined 530,000 rows (vs. 6 in just the first
110k). Repeat eq1 ids: `481` (3×), `898` (3×), `2162` (2×), `1979` (2×),
`2531` (2×), `854` (2×) — no single dominant law like the TRUE side, but
enough repetition to be worth a look rather than treating each as a one-off.

### Order-6 — essentially closed, no scoring category, cut first if short on time

1,400 rows total across three pilots (900 general + 500 hard-region
stratified), **1 skip** (`order6_16514_17426`). Answered its only real
question — nothing in the solver is quietly tuned to term size ≤5 — and
there's no order-6 category in the official scoring. Lowest priority by
design.

## The real question this session should also answer: is the LLM lane worth its keep?

Directly asked going into this session, and there's real evidence pointing
both ways — worth resolving with fresh real calls, not re-litigating from
memory.

**The case for skepticism**, from three prior LLM sessions:
- 2026-07-20 (`gpt-oss-120b`, low reasoning): **0/18** on the deterministic-skip
  frontier, 0/20 on a mixed set. A big deterministic closure budget alone
  cracked only 1/20 of the same rows.
- 2026-07-22 (repeat on hard1/hard2/eval_normal): still 0 real accepts — third
  session confirming the same ceiling.
- 2026-07-29 (the one LLM session that *did* generalize, 9 rows / 0 kernel
  rejects): every single winning lemma was one of three trivial shapes —
  collapse (`a = b`), projection (`a ◇ b = a`/`b`), or product-constant
  (`a ◇ b = c ◇ d`). All nine now solve **deterministically** via
  `egg_priority_bootstrap`, which exists *because of* that finding. The LLM's
  real output that day wasn't coverage, it was the discovery of which laws
  deserved a bigger search budget — a one-time contribution already banked.
- The deployed Marathon LLM lane runs at `reasoning_effort=low` (2026-08-24) —
  exactly the regime that scored 0/38 combined across the two 2026-07 sweeps.
- Real Marathon evidence to date shows the deterministic routes carrying
  everything: 1,000/1,000 ETP rows accepted using **0 tokens** (2026-08-24),
  and even the harder 200-row order-5 Marathon manifest the same day logged
  `not_attempted` rather than LLM engagement on its 7 misses.

**The case it might still matter**: the four order-4 frontier laws (lever 1)
and the order-5 size/arity wall (lever 2) are exactly the shape of problem the
2026-07-21 hybrid idea was aimed at and never tried — LLM proposes a candidate
*middle term or instantiation*, fed into the deterministic closure
(`egg_ladder`/`completion`) rather than asking the LLM to write the whole
proof. That's different from every LLM experiment run so far, all of which
asked for either a full proof or a standalone lemma.

**Concrete experiment for this session**, since the frontier ledger now exists
and is large enough to be a real test population (218 order-4 + 353 order-5 =
571 genuinely-hard rows, not a hand-picked sample):
1. Run the *current production* LLM lane (real OpenRouter calls, deployed
   `reasoning_effort=low`) against the merged frontier ledger through an
   actual Solo or Marathon invocation (not the offline audit, which never
   calls the proxy) — count real kernel-accepted proofs attributable to the
   LLM lane specifically, and their token/latency cost.
2. Separately try the untried hybrid: LLM proposes candidate lemmas/middle
   terms only, `egg_ladder`/`completion` do the derivation and the kernel
   check, same as `egg_priority_bootstrap` already does for hand-picked
   lemmas. Compare hit rate and cost against (1).
3. If reasoning effort is the binding constraint (plausible, given every 0/N
   result above was at low reasoning), a small controlled comparison at a
   higher tier on a capped row subset would settle whether it's the model or
   the shape of the ask that's failing — but note real cost/latency
   implications before scaling that up.
4. Report real accepts, real token spend, and — critically — whether any
   accept is on a row *none* of the deterministic engines were close to,
   versus a row already near-solved that the LLM only nudged.

Answer with real numbers, not the prior sessions' extrapolated pessimism —
but go in expecting the deterministic engines to have already absorbed most
of what a low-reasoning LLM lane can find, per the pattern above.

## Rails to keep in view while fixing

- **Rail 2**: diff by row id, never by total — solved counts swing ±7 on
  timing noise alone.
- **Rail 9**: no benchmark ids in solver policy. Any fix for lever 1/2 must
  generalise into a proof or witness family (like `egg_ladder`,
  `DISTILLED_CERTS` keyed by canonical text), never a per-row-id special case.
- **Rails 3/3c**: real-judge verification is mandatory for any
  certificate-builder change. Local oracle acceptance is an upper bound, not
  evidence.
- **Rail 5f-v** (`rail-5fv-fix-the-twin-not-just-the-engine`): if lever 3's fix
  touches a budget/scheduling function, check whether it has a twin (e.g. the
  single-rule vs multi-rule engines have historically drifted from each other
  five times running).
- **Rail 16**: if any newly-derived certificate gets pinned into
  `judge_verified_certs.jsonl`, use `--append-fixture`, never
  `--write-fixture`, and compare the **skip count** after, not just pass count.

## Tooling already built and ready to use

| Tool | Use for |
| --- | --- |
| `stage2/experiments/sweep_report.py --diagnose --diagnose-budget 300` | Lever 3 — re-solves a batch of misses with all 19 engines timed, names the overrunning one directly |
| `stage2/experiments/completion/solve_row.py <row_id> [budget_s]` | Prints the actual derivation for a lever-1 row — the right tool for "why doesn't this close" |
| `stage2/experiments/filter_hard_region.py` | If any new stratified sampling is needed |
| `stage2/experiments/judge_rows.py --ids <id1,id2> --append-fixture` | Real-judge verification for anything lever 1/2/3 produces |
| `.\.venv\Scripts\python.exe -m pytest stage2/tests -q -n auto` | Gate — run before AND after every change |

## Suggested starting sequence

1. Gate green as a baseline (~14 s).
2. Merge the three order-4 failure ledgers into one 218-row file (already
   distinct by construction — 0 overlap across all three draws — so a plain
   concatenation is safe) and run `sweep_report.py --diagnose` on it for a
   full-scale version of the lever-3 profile table.
3. Take 2–3 of the lever-1 rows to `stage2/experiments/completion/solve_row.py`
   by hand and see whether goal-subterm seeding closes them.
4. Design and run the LLM experiment above in parallel — it doesn't block
   1–3, and its answer changes how much lever-1/2 effort is worth spending on
   deterministic engines versus a hybrid LLM approach.
5. Whatever ships: isolated audit diffed by row id against this session's
   corpus baseline (2669/2669), 0 lost required; real-judge sample for any
   cert-builder touch; gate green again before calling it done.
