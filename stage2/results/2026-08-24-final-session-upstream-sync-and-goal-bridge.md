# 2026-08-24 — Final repo session: upstream re-sync, Lean 4.32.2 judge parity, and the completion goal bridge

The last working session before the 2026-08-31 deadline. Two headline results:
the vendored judge was **16 commits stale** — upstream finalized scoring,
hardened the judge, and bumped the toolchain on 2026-08-20/21, all invisibly to
this repo until today — and the completion engine gained the one inference move
it was missing, closing **6 of the 8 "hopeless" order-4 frontier rows and 111
of the 205 order-5 sample misses** with kernel-verified proofs.

## 1. The upstream re-sync (6805e232 → 4db175c4)

Checked because this session's brief said "latest rules"; the playground pages
are JS shells, so the check went straight to the official GitHub repo. Sixteen
commits, all 2026-08-20/21. What changed, in order of consequence:

1. **Scoring is final, and Order 5 is a quarter of it.** Four equal-weight
   categories — Normal, Hard, Extra Hard, **Order 5** — `accepted` = 1 point,
   anything else 0. No partial credit.
2. **No-reuse guarantee**: no Stage 2 evaluation problem is reused from Stage 1
   or any publicly available selected problem set. The private set is fresh, so
   *generalization to unseen rows is the entire game* — the local corpus is
   training signal, not the target.
3. **Judge hardening** (`judge/verify.py` +96/−20): banned-token list gained
   `run_cmd`, `run_elab`, `@[init`, `skipKernelTC`, and the whole parser-
   extension family (`notation`, `notation3`, `infix`, `infixl`, `infixr`,
   `prefix`, `postfix`); the dependency report is now computed on both
   `submission` and a nonce-named checked theorem and **unioned** (closes
   instance-resolution axiom laundering); `-D linter.defProp=false` suppresses
   Lean 4.32's new linter on the required submission shape.
4. **Toolchain bump**: Lean v4.30.0-rc2 → **v4.32.2**, Mathlib → tag v4.32.2
   (`905b9581`). The judge's own `magmaFin` needed `@[implicit_reducible]`
   under 4.32 — a reminder that toolchain bumps can shift certificate
   behaviour.
5. **Marathon budget formula restated** as flat `N × 300 s` / `N × 32768`
   tokens (numerically identical to the old ratio-0.5 formula);
   `--compression-ratio` removed from the CLI.
6. **Submission note**: solvers carrying generated/non-human-readable data must
   ship a plain-text methodology note. Infinite countermodels now have their
   own upstream test fixtures.
7. `pipeline/config.json` **unchanged** — every judge limit this repo mirrors
   (100,000 / 20,000 / 300 s) still holds, and the CI pin remains valid.

**Sync executed**: 30 files taken verbatim, 2 (`judge/verify.py`,
`scripts/run_harness.py`) merged 3-way with zero conflicts, all 9 documented
local Windows patches preserved, UPSTREAM.md updated. Toolchain + full Mathlib
olean cache fetched in ~4 min; judge libs built in 3 s.

**A tenth Windows patch was required, and the bug it fixes was latent for
months.** On Windows `lean` is an elan shim that resolves the toolchain *from
the working directory*. Two of the judge's three Lean invocations passed no
`cwd`, inherited the repo root, and silently resolved elan's default toolchain
— which happened to equal the vendored one until today. First post-bump smoke
test failed with `incompatible header`; fixed by passing `cwd=art_dir` in both
invocations (UPSTREAM.md patch #9). Zero effect on Linux deployment.

**Judge parity re-established on v4.32.2**: `normal_0747` (TRUE),
`hard2_0080` (TRUE projection collapse), `hard2_0051` (FALSE, order-13
`List.getD` table), `hard2_0027` (FALSE, infinite Nat carrier + `omega`) — all
**accepted**, 2.7–4.6 s.

## 2. Compliance work driven by the new rules

- **The judge's banned-token scan is now mirrored in three places**: the
  offline oracle (`oracles.find_judge_banned_token`, wired into
  `check_no_banned_tactics`, so every audit/golden/spotcheck cert is scanned),
  the solver's LLM sanitizer (`sanitize_lean_code`), and — the diagnosis
  workflow's finding — **`judge_answer_payload()`**, the single choke point
  every certificate passes through, so no future route change can ship a
  banned token. Matching replicates the judge exactly (literal substring for
  `#`/`@`-prefixed tokens, case-sensitive word boundary otherwise). All 99
  pinned certs and all 65 `DISTILLED_CERTS` entries scan clean.
- **Marathon LLM lane now requests `reasoning_effort=low`** (was `medium`),
  matching the deployed gpt-oss-120b configuration, env-overridable via
  `JUDGE_MARATHON_REASONING_EFFORT`. The Marathon proxy forwards
  solver-supplied reasoning params untouched, so this value is what DeepInfra
  actually runs, and reasoning tokens bill against the same N × 32768 budget
  the answers need. The proxy's own comments record 840 s of runaway trickle
  at `high` on this exact model.
- **`truncated` is now forwarded** from `call_llm` into the Marathon result and
  the `llm:reject` log record, so a token-exhausted call is distinguishable
  from a malformed answer at triage (the 2026-07-23 failure mode).
- **`SUBMISSION_NOTE.md`** written (`stage2/solver/`): methodology disclosure
  for `DISTILLED_CERTS`, witness tables and the lemma library, per the new
  human-interpretable-artifacts rule.
- **`LICENSE`** added (MIT, scoped to exclude `vendor/` and third-party
  material) — the README's standing open question.
- Local wrappers that passed the removed `--compression-ratio` flag fixed:
  `run_marathon_batch.py`, `run_playground_parity_llm.py` (ratio now applied
  as an explicit budget), `run_positive_token_sweeps.py`.

## 3. The completion goal bridge (`true:completion:bridge`)

The 2026-08-21 brief left 8 order-4 rows "completion genuinely saturates on"
and marked two ideas untried. Both shipped today, informed by a five-pillar
diagnosis workflow (10 agents, findings adversarially verified):

- **Ground-unoriented rewriting** (`_rewrite_ground_unoriented`): an equation
  whose variable condition fails in a direction (`z ◇ x = w ◇ x`) was never
  usable as a rewrite — `ori == []` — even on the skolemised goal where the
  variable condition is vacuous. On the goal, an unbound target-side variable
  is universally quantified, so it is instantiated (at the smallest constant of
  the matched subterm) and **bound explicitly in the recorded substitution**,
  which keeps the renderer's replay byte-exact. Still gated by ground KBO, so
  termination is untouched. This sidesteps the `subsumed()` wall that sank the
  2026-08-21 instance-pushing attempt — it never touches `push`/`subsumed`.
- **The post-saturation goal bridge** (`goal_bridge`): ordered rewriting only
  ever moves *down* the ground KBO, so two goal sides whose meeting point is
  *up* the order can never join — this is exactly what real unfailing
  completion buys by superposing into the goal disequality. Implemented as a
  bounded bidirectional best-first search between the goal's two normal forms
  using **every direction of every active equation** (6,000-node cap as a
  memory guard, size slack +8, deadline polled per unit of work). Runs **only
  after saturation** — i.e. only on rows completion would otherwise lose — and
  only in the tier-scaled slot, not the unscaled probe: measured, the bridge
  can turn the probe's ~0 s saturation loss into a full-budget loss on ~1 row
  in 8, which is precisely the asymmetry the early slot's placement depends on
  (the probe's loss profile is unchanged: 6.5 s for 25 random rows, identical
  with the new code disabled).

**Results, all kernel-verified (0 kernel failures anywhere):**

| Target | Before | After |
| --- | --- | --- |
| The 8 saturating order-4 frontier rows | 0/8 | **6/8** (5 bridge + 1 join via the unoriented rewrite), ≤ 0.07 s each, 695–1,588 B |
| The 205 order-5 sample misses | 0/205 (as of 2026-08-20; the 08-21 port closed ~9/25 of a probe) | **111/205** (69 collapse / 40 join / 2 bridge), 131.8 s total |
| The 5 TRUE `DISTILLED_CERTS` families no live engine could re-derive | 0/5 | **2/5** (`e469_e4090` bridge 0.02 s; `e20115_e21404` collapse 3.35 s) |

Order-5 frontier on the 4,000-row generated sample: **5.1% → 2.35% missing** —
directly score-relevant now that Order 5 is one of the four categories.

Still open: `etp_1366_3436` and `etp_3569_4653` (both saturate with the bridge
exhausting the reachable theory in < 1 s even at 10× the node cap — their goals
need facts self-superposition never derives), and 3 distilled-only TRUE
families (`e2923_e1623`, `e1517_e735`, `e3067_e3082`).

## 4. `etp_1661_3524` — diagnosed as far as cheap evidence goes

The single FALSE miss in 20,000 unseen order-4 rows. Today's evidence:

- **Order ≤ 4 is exhausted** — proven, 8.7 s, no countermodel exists there.
- Orders 5–12 at the deployed 45 s/order: all deadline-bound, 61k–617k nodes
  each, no conclusion. The search is branching-bound, not node-bound.
- **No FinitePoly witness**: all 241 teorth FinitePoly magmas of order 5–16
  tested directly — none satisfies 1661 while refuting 3524. Brute force over
  *all* quadratic polynomial magmas on Z₅–Z₉ (~120k): nothing.
- teorth refutes the pair **only by composition** (no direct
  `Equation1661_not_implies_Equation3524` exists), the same profile as
  `hard2_0027` — which turned out to need an infinite countermodel.
- An XOR-additive infinite family (`op a b = a ⊕ g b`) provably cannot
  separate this pair: eq1's invariance condition and eq2's refutation
  condition range over the same shift set.

Conclusion: eq1 forces every right-multiplication to be a bijection with
`P_{(y◇z)◇y} = P_y⁻¹` for **all** z — a rigid structure. If a finite witness
exists it is order ≥ 5 and needs either a much longer targeted run (a deep
sweep item) or a structure-aware search over column-permutation assignments;
otherwise this row wants a bespoke infinite construction. Left open, 1 row in
20,000.

## 5. Structural hardening

- `derived_rule_steps` now polls the deadline per rule and per 64 fill
  combinations, matching its twin `filled_absorption_steps` (rail 5f-v; the
  asymmetry was latent — measured max 619 steps/call — but it was the last
  known twin asymmetry in the file).
- The twin-signature gate test the 2026-08-21 brief asked for **already
  exists** (`test_engine_twins_take_the_same_bounding_parameters`,
  `test_egg_saturation_polls_the_deadline_per_match`) — the brief's item 3.4
  was already discharged; noted here so nobody re-plans it.

## 6. Evidence runs (this session, on the synced judge)

- Offline gate: green after every change — **257 passed** ×4, then **260
  passed** ×2 after the fixture rebuild added three entries.
- **Full audit**: official **1669/1669**, HF **800/800**, `sample_200`
  200/200, `sample_20` 20/20 — row-id diff vs
  `audit-2026-08-21-completion.json`: **0 lost, 0 gained, 0 verdict flips over
  2,669 common rows**, 0 crashes, 0 oracle failures
  (`audit-2026-08-24-goalbridge.json`, `-hf.json`).
- **Order-5 4,000-row end-to-end sweep**: **3,920/4,000 solved (98.0%)**, 80
  skips, 0 crashes, 0 oracle failures — was 3,795/4,000 (94.9%) on
  2026-08-20. `completion` serves 374 rows of that set
  (`audit-2026-08-24-order5-4000.json`).
- **102-row re-judge sweep on the v4.32.2 judge: 102/102 accepted** — all 99
  pinned certificate families plus the envelope rows (`hard2_0092`
  maxRecDepth boundary, `hard2_0027` infinite Nat + omega, `hard2_0051`
  order-13 `List.getD`, completion join/collapse). The fixture
  (`judge_verified_certs.jsonl`) was rebuilt from this sweep: **102 entries,
  every one re-dated 2026-08-24 on the new toolchain**
  (`judge-rejudge-v4322-b1/b2/b3.json`).
- **New bridge certificates through the real judge: 10/10 accepted** (rail
  3c) — 6 order-4 frontier rows, 2 order-5 bridge rows, 2 formerly
  distilled-only families, 730–11,061 B, 2.7–3.7 s each
  (`2026-08-24-bridge-certs-judged.jsonl`).
- **Packaged: 472,504 / 500,000 bytes** (27,496 free, 5.5%) — today's engine
  changes cost ~6.2 KB; gate green inside packaging.
- **Spotcheck: 90 rows / 9 sources, 100% accuracy, 100% coverage, 0
  mistakes.**
- **Real Solo, 25 `hard2` rows on the final artifact: 25/25 solved, 0
  failed, 0 LLM calls**, ~5–8 s/row through the official `pipeline.runner` —
  the first end-to-end tier-ladder evidence (it had been the top open
  evidence item for three sessions).
- **Real Marathon, 1,000 fresh unseen ETP rows (seed `20260824`, benchmark
  ids excluded, 0 overlap with prior samples): 1,000/1,000 accepted, 0
  rejected, 0 `not_attempted`, 0 tokens of a 32,768,000-token budget.** The
  solver used **1,186.5 s of its 300,000 s budget (~1.2 s/row)**; total wall
  including the Lean scoring pass 4,408 s. The largest unseen-row real-judge
  run in the repo, on the final artifact, on the v4.32.2 judge
  (`tmp_stage2_smoke/marathon-etp1000-2026-08-24/`).
- **Real Marathon, 200 order-5 rows (seed `20260824`, drawn from the 4,000-row
  generated sample, 11 of them from its former unsolved list): 193/200
  accepted, 0 rejected, 7 `not_attempted`.** Run as two batches on the same
  artifact — the first process was killed at 117/200 by a session-console
  close (exit `0x40010004`), recovered with `--score-only` (117/117
  accepted), and the 83 unanswered rows re-run as a second manifest (76/83
  accepted, 39,809 real tokens spent by the LLM lane at
  `reasoning_effort=low` on the hard rows, no accepted candidate). All 7
  not-attempted rows are from the known order-5 tail; 4 of the 11
  formerly-unsolved rows now pass end-to-end. Order-5 rows have no ground
  truth — this measures judge acceptance and self-consistency, and every
  answer the solver emitted was accepted
  (`tmp_stage2_smoke/marathon-order5-200-2026-08-24{,-batch2}/`).
- **Final package: 472,522 bytes** (27,478 free, 5.5%), gate 260 passed
  inside packaging. ruff clean; judge-limit constants pin to
  `pipeline/config.json`.

## 7. What remains

Upload (`stage2/docs/NEXT_SESSION_BRIEF.md` §1) and optional deep sweeps
(§2). The repo is in its final state.
