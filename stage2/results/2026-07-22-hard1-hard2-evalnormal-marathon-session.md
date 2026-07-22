# 2026-07-22 — hard1/hard2/evaluation_normal deep dive + real Marathon LLM lane

Session goal: long improvement pass focused on `hard1`, `hard2`, and
`evaluation_normal` (HF discovery set), ending in a real Marathon simulation
(official proxy, real gpt-oss-120b calls, no `--budget-tokens 0`). Report below;
no solver.py changes were made this session — every lead found either needed
more dedicated proof engineering than was safe to rush, or needed working LLM
evidence gathered for the first time here.

## Headline

1. **Deterministic baselines** (offline, no LLM, `standard` effort):
   hard1 `60/69`, hard2 `152/200`, evaluation_normal `181/200`.
2. **Real Marathon LLM lane, gpt-oss-120b, positive tokens**: hard1 `59/69`,
   hard2 `149/200`, evaluation_normal `178/200` — in all three cases identical
   to the deterministic-only score at the tier used. Real tokens were spent
   (129,806 / 791,519 / 263,165) and real responses came back, but **zero**
   were accepted anywhere.
3. **One real, verified win, no code change**: running the existing
   `derived_cp_closure` engine at full Marathon-scale (`deep` tier) budget
   recovers **4 genuine new TRUE proofs** out of 76 known misses across all
   three sets, independently checked sound by the offline proof kernel. Modest,
   but free and real.
4. **Found and fixed two session-blocking infra bugs** (see below) and
   **discovered one un-fixed scalability risk** in the packaged solver
   (unbounded module-level caches).

## Deterministic-only audits (no LLM, free)

| Set | Effort | Solved | TRUE miss | FALSE miss |
| --- | --- | ---: | ---: | ---: |
| hard1 | standard | 60/69 | 4 | 5 |
| hard2 | standard | 152/200 | 34 | 14 |
| evaluation_normal | standard | 181/200 | 19 | 0 |

Every FALSE-labeled miss in `evaluation_normal` disappeared at `standard`
effort — the remaining gap there is 100% TRUE proofs. hard1/hard2 keep a small
residual FALSE gap (see "genuinely resistant" below).

## Does more deterministic budget help? (76 known misses, `deep` tier, no code change)

Probed all 76 standard-tier misses (hard1's 9 + hard2's 48 + evaluation_normal's
19) directly through `solve_problem()` at `deep` effort (~150-490s/row when
unsolved — this is what real Marathon budgets actually afford at this scale).

**Result: 5/76 solved.**

- `hard2_0092` — `false:dual:false:witness:S5B` in 2.3s. This one is a
  diagnostic-tool artifact, not a real gap: it only needed slightly more than
  `audit_corpus.py`'s stingy 2s default FALSE-search budget, and real Marathon
  already grants ~60s at this scale.
- `hard2_0120`, `hard2_0154`, `evaluation_normal_0096`, `evaluation_normal_0172`
  — **`true:derived_cp_closure`**, 111-239s each. These are genuine new wins:
  the existing unification-based critical-pair closure engine, given real
  budget, closes proofs it couldn't reach before. Re-verified independently
  through the offline proof kernel (`oracles.check_true_exact_certificate` +
  `oracles.model_check_true`) — all 4 pass clean (`KERNEL_OK`).

The other 71/76 (93%) do **not** yield to more deterministic budget, even at
150-490s/row. This reconfirms the 2026-07-20 session's finding
("big-budget deterministic closure cracks only ~1/20") with fresh evidence on
the current solver.

**Practical implication**: real Marathon runs at this scale should keep using
`deep` tier (they already do, automatically, via `effort_for_seconds`) — it's a
small but real and free win. No code change needed; this is confirmation the
2026-07-21 effort-scaling work is paying off, not a new lever.

## A structural lead that wasn't shipped

Scanned all 57 remaining TRUE misses for a recognizable shape not covered by
any existing route: **`x = A(other vars) ◇ x`** (or the mirror), where `A`
doesn't mention `x` — i.e. `A` is a *universal one-sided identity family*.
Found in 5/57 (~9%): `hard1_0007`, `evaluation_normal_0018`,
`evaluation_normal_0082`, `evaluation_normal_0088`, `evaluation_normal_0112`.

Worked the algebra by hand: the fact "`A(y,z)` is a left/right identity for
every `x,y,z`" does **not** trivially close the corresponding goals — you can't
just substitute your way from "some family of terms acts as identity" to
"element `x` is idempotent" without picking a problem-specific instantiation
trick, the same kind of hand-derivation behind the existing
`singleton_from_1111_block`-style routes. That's real proof engineering, not a
quick pattern-match add, so it wasn't rushed blind this session. Flagging as
the best next-session lead for TRUE coverage.

## Real Marathon simulation (official proxy, positive tokens, gpt-oss-120b)

Ran through `vendor/stage2-official/scripts/run_marathon.py` via
`stage2/experiments/run_positive_token_sweeps.py`, packaged single-file
`solver.py`, `fast` effort tier (chosen for a practical session timeline —
see the sizing note below).

| Set | Score | LLM calls | Tokens used | Wall time | LLM accepts |
| --- | ---: | ---: | ---: | ---: | ---: |
| hard1 | 59/69 | 10 | 129,806 | 567s | **0** |
| hard2 | 149/200 | 51 | 791,519 | 2,679s | **0** |
| evaluation_normal | 178/200 | 22 | 263,165 | 969s | **0** |

hard2's 51 LLM attempts split 33 transport/timeout errors and 18 rejects — a
much higher error rate than hard1 (4/10) or evaluation_normal (3/22); see
finding #5 below (Windows-local proxy connection resets).

Reject-reason breakdown, pooled across all three sets (83 total attempts):

| Reason | Count |
| --- | ---: |
| `guided_chain_unproved_or_bad_endpoints; seeded bidirectional closure around your terms also failed` | 27 |
| `no_json_object` | 13 |
| `rewrite_chain_uses_non_goal_variables` (+ seeded-closure-also-failed variant) | 3 |
| transport/timeout errors (no usable response) | 40 |
| **Total LLM attempts** | **83** |
| **Total accepted** | **0** |

This exactly matches the historical pattern from the 2026-05-30 session
(`guided_chain_unproved_or_bad_endpoints` was the dominant reject there too,
71/86). **Fresh conclusion with the current, already-fixed prompt: gpt-oss-120b
still cannot close this specific frontier** — the model proposes plausible-
looking chains/waypoints, but the solver's own bridging search (including the
seeded bidirectional closure fallback) can't complete them. This is a
solver-search problem, not primarily a prompt problem, on this frontier.

### Why `fast` tier, not `deep`, for the real runs

The original plan used playground-equivalent budgets
(`compression_ratio=0.5 × N × 3600s`), matching true competition scale. Measured
that at this scale the deterministic retry pass alone costs ~300-400s per
unresolved row (`deep` tier) *before* the LLM lane even gets a turn — for
hard2's ~48 misses that's up to ~4-5 hours just to clear the deterministic
phase. Switched to `fast` tier (smaller `--budget-seconds`, generous
`--budget-tokens`, kept independent of each other) to get a complete real-LLM
report within a practical session window. `fast` tier's deterministic score is
a few points below `standard`/`deep` (see table above vs. the audits), but the
LLM lane's behavior — call volume, reject mix, zero accepts — is what mattered
here and isn't tier-sensitive.

## Infra issues found and fixed this session

1. **My own bug (self-fixed)**: first fast-tier attempt derived
   `budget_tokens` from the same `compression_ratio` as the time budget,
   which came out too small (90,439 tokens for hard1) — every concurrent
   8-call batch's reservation exceeded the total budget, so **every** LLM
   call failed with HTTP 402 "token budget exhausted" before ever reaching
   upstream. Fixed by decoupling: small `--budget-seconds` (drives the
   effort-tier choice) with a generously large flat `--budget-tokens`
   (2,000,000) independent of it.
2. **Real blocker (needed the user)**: the OpenRouter key in `.env` was
   rejected upstream with `401 User not found` on every call shape — confirmed
   independently via `homelab_llm_probe.py --run-direct-openrouter-smoke`.
   Not a solver bug; the key itself was invalid. User rotated it.
3. **Stale cached key, same session**: after rotation, this shell's process
   environment still carried the *old* key (likely inherited at shell/profile
   startup, independent of the edited `.env`), so `--key-status` kept
   reporting `source=process_env` with the dead value even after the `.env`
   edit. `local_runner_env.load_local_runner_env()` prioritizes process env
   over `.env` by design, so the stale value silently won. Worked around with
   `env -u OPENROUTER_API_KEY -u OPENAI_API_KEY` prefixed on every subsequent
   command so the fresh `.env` value is read instead. **Not a solver bug** —
   a local shell-environment staleness issue — but worth knowing: editing
   `.env` alone does not guarantee a new terminal/process picks it up if a
   process-level env var of the same name is already set upstream.
4. **New, not yet fixed — scalability risk**: partway through the hard2 real
   run (~150 problems processed in one long-lived Marathon process), the
   packaged `solver.py` subprocess measured **1086+ CPU-seconds and 11.2 GB
   resident memory**, with periods of near-zero CPU progress for minutes at a
   time. Root cause is almost certainly the module-level
   `@lru_cache(maxsize=None)` decorators on term-utility functions
   (`term_vars_tuple`, `term_size`, `term_depth`, `term_to_lean`, `dual_term`,
   `term_subterms_tuple`, `boundary_vars`, `subterm_paths_tuple`,
   `term_at_path`, `replace_subterm`, `context_to_lean`, plus
   `_DERIVED_RULES_CACHE`) — none of these are cleared or bounded across
   problems within one Marathon process lifetime, so they accumulate entries
   from every problem solved so far, unboundedly, for the life of the run.
   For a 200-row set this reached double-digit GB; a real playground-scale
   Marathon run (larger N, e.g. `normal`'s 1000 rows, or the true evaluation
   manifest size) could plausibly hit memory pressure or serious slowdown.
   **Recommendation for next session**: bound these caches (e.g.
   `maxsize=<N>` instead of `None`) or clear them per-problem in
   `run_marathon()`'s main loop. Not fixed this session — found late, and a
   cache-clearing change to the hot path deserves its own test pass rather
   than a rushed edit.
5. Also observed intermittent `ConnectionAbortedError [WinError 10053]` in the
   local HTTP proxy's `do_POST` handler throughout all three real runs. This
   matches a **documented** benign teardown-noise pattern from the 2026-05-30
   session and did not, by itself, block completion — but combined with
   finding #4 above, some of the multi-minute stalls observed in hard2's LLM
   batches may be this same Windows-socket-layer quirk rather than genuine
   upstream latency. Likely specific to this local Windows dev environment,
   not necessarily the actual playground infrastructure.

## Starters for next session

### Starter 1 — bound/clear the unbounded `lru_cache`s (highest value, mechanical)

13 module-level `@lru_cache(maxsize=None)` decorators in `stage2/solver/solver.py`,
all keyed on `Term` (nested tuples), none ever cleared across problems within
one process lifetime: lines **581, 592, 599, 606, 613, 630, 643, 652, 665,
673, 685, 2215, 2354** (`term_vars_tuple`, `term_size`, `term_depth`,
`term_to_lean`, `dual_term`, `term_subterms_tuple`, `boundary_vars`,
`subterm_paths_tuple`, `term_at_path`, `replace_subterm`, `context_to_lean`,
`left_row_constancy_key`, `commutative_term_key`). `_DERIVED_RULES_CACHE`
already self-evicts at 64 entries (`critical_pair_rules`, ~line 4732) and
`narrow_grind_true_shape_keys` is `maxsize=1` (static) — neither needs touching.

Proposed fix: a single helper clearing all 13, called once per problem inside
`run_marathon()`'s main loop (`stage2/solver/solver.py:6350`, the
`for priority, problem in prioritized:` loop) — clearing *between* problems
is free (different problems essentially never share `Term` tuples) and does
not hurt the within-problem reuse these caches exist for.

```python
_TERM_CACHE_FUNCS = (
    term_vars_tuple, term_size, term_depth, term_to_lean, dual_term,
    term_subterms_tuple, boundary_vars, subterm_paths_tuple, term_at_path,
    replace_subterm, context_to_lean, left_row_constancy_key, commutative_term_key,
)

def clear_term_caches() -> None:
    for fn in _TERM_CACHE_FUNCS:
        fn.cache_clear()
```

Test plan: (1) `pytest stage2/tests` must stay green — clearing is pure
memoization, changes no behavior; (2) re-run hard2 through
`run_positive_token_sweeps.py` and watch `Get-Process` RSS stay flat instead of
climbing past ~11GB; (3) consider whether `audit_corpus.py`'s
`ProcessPoolExecutor` workers need the same treatment (they process multiple
problems per worker too, just distributed across 16 processes so less severe).

### Starter 2 — "universal one-sided identity" TRUE route (needs real derivation)

Fixture staged: `stage2/fixtures/universal_one_sided_identity_misses_2026-07-22.jsonl`
(5 rows: `hard1_0007`, `evaluation_normal_0018/0082/0088/0112`).

Shape: `x = A(other vars) ◇ x` (or the mirror `x = x ◇ A(...)`), `A` not
containing `x` — distinct from `singleton_route` (which needs the bare-variable
side entirely absent from the other side). Already established this session:
the raw fact "`A(y,z)` is a one-sided identity for all `x,y,z`" does not
trivially close any of these 5 goals by itself — some problem-specific
instantiation trick is needed, the same kind of work behind the existing
`singleton_from_1111_block`-style hand-derived proofs.

Concrete next step, cheaper than deriving a bespoke proof from scratch: since
`eq1` in each row is literally the bidirectional rewrite rule
`x ↔ A(y,z) ◇ x`, and `derived_cp_closure_route` already seeds its rule set
from `_derived_base_rules(eq1)` + `critical_pair_rules(eq1)`, for one fixture
row work out **by hand** which concrete instantiation of `A(y,z)` (i.e. which
values substituted for `y,z`) is needed to make `A(y,z) ◇ x → x` fire on a
term actually appearing in the goal's rewrite path. Then check whether that
specific instantiation is present in `absorption_term_pool(eq1, eq2,
pool_limit=...)`'s output (`stage2/solver/solver.py:4068`) — if it's missing,
that's the actual gap (a pool-generation heuristic miss, likely fixable
generally), not a missing algebraic fact. This reframes "derive a bespoke
proof" as "debug why the existing general engine's term pool doesn't contain
the one term it needs" — cheaper and more likely to generalize beyond these 5
rows.

### Starter 3 — bridging-search limitation (open-ended, lower priority)

`guided_chain_unproved_or_bad_endpoints` is now the dominant LLM reject across
three independent sessions (2026-05-30, 2026-07-20, this one) — confirmed
solver-side, not prompt-side. The 2026-07-20 session's own next-step note
("adaptive pool sizing based on problem shape") and a depth-2 critical-pair
extension (composing already-derived rules with each other, not just `eq1`
with itself, in `critical_pair_rules`) are the two most promising untried
levers, but neither has been scoped or tested yet — treat as a research
spike, not a ready-to-execute starter.
