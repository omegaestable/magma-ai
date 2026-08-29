# 2026-08-29 — Free models of the Austin research laws: 10 → 24/100, paused mid-wave

Continues `2026-08-28-austin-tag-automata.md`. Everything below is measured; the judge is Lean 4.33.1
through `stage2/experiments/judge_cert_text.py` at the deployed caps.

## Headline

| Metric | Value |
| --- | --- |
| Rows accepted by the real judge | **24 / 100** (was 10). New today: `0082` (5107), `0059` (5295), `0015`/`0019` (5012), `0041` (9345), `0066` (5141), `0076`/`0085` (13992), and by dual transplant `0004` (41253), `0014` (40909), `0067` (40951), `0035`/`0083`/`0089` (36713). 4952 and 5066 were re-proved as recursive models (their rows were already accepted) |
| Integrated | all 24 are `DISTILLED_CERTS` entries (`aus_e*`, marker `recursive free models (2026-08-29)`), 24 fixture pins with their own equations; the **source** solver serves every one in 0.0 s. **The packaged artifact is still the 2026-08-28 build (10 rows)** — `package_solver.ps1` refused: the offline gate failed under heavy load and was not diagnosed before the pause |
| Laws with a verified free model (semantic search, 3,000 two-level adversarial tests, 0 fails / 0 conflicts) | **40 / 69** directly — every L-form law except 6912; the R-form laws are their duals; both-compound laws need the same machinery with a compound left pattern |
| Closed-form packages validated (deep tests + structured fuzz, 0 fails) at the pause | 15 regenerated with the final extractor (`gen7.jsonl`): 5833, 5837, 6878, 6912†, 7701, 8485, 9667, 10218, 11081, 11280, 12087, 12234 ready; 9663, 10222, 12073 still fail. 37 laws not yet regenerated (batch stopped at the pause) |

† 6912's closed form passes the tests but is provably not a model: the law derives `(a◇a)◇(a◇a) = a◇a`
(four instances, checked by hand), so the free model must be quotiented; the search does not handle the
quotient yet (modulo the identity: 0 conflicts, 165 fails). Its dual 39214 shares the problem (3 rows).

## The mathematics

**The free model.** For a law `x = A ◇ B` take the free magma on generators and define
`op(u,v) := x` exactly when `(u,v)` is a *reading* — some assignment evaluates `A` to `u` and `B` to `v`
with x-value `x` — and `J(u,v)` (the free product) otherwise. This is a least fixed point (readings are
resolved with `op` itself on smaller pairs, well-founded on the lexicographic measure
`(max size, total size)`; the plain sum is the wrong measure — it cuts genuine readings when `u` is
tiny). The law holds by construction wherever readings are unique. `freemodel.py` searches readings
structurally: a pattern node against a target is read freely (the target is a `J` whose children match)
or as a decode (the node's value is a root reading with the target as x-value), decodes are resolved by
matching the root pattern against the concrete encoding, variables bound by later siblings are handled
by deferred *obligations* witnessed with fresh generators, a reading that needs itself is cut (least fixed
point) with the cut released while the generator is suspended, and every accepted reading is
re-evaluated. Search bugs, not mathematics, caused every "failure" seen on the way (junk-filled
variables, wrong measure, a readings cycle, unstable memoisation under provisional cuts, vacuous
obligations, a suspended generator holding a cycle key).

**Closed forms.** `closedform.py` turns the search into a finite rule system: per pattern node, modes
free / lazy (nested guard `op(dec, enc) = w`, the recursion that keeps the rule set finite) / struct
(unify with the root pattern; placeholders refined `F := J(F1,F2)` with the occurs check) / vdec (a node
evaluated inside an encoding decodes) / exist (fallback). Decodes are deferred until the free structure
has bound the variables; a decoder may have to be located through a *level-2* reading of the encoding
(an inner node of the encoding itself decoded). Three agents found their generated skeletons false
before this was in place (11081, 9345, 13992 — depth-3 coincidences that 3,000 random tests miss); the
repair they used by hand — recover the payload through an occurrence that is provably free — is what the
level-2 enumeration produces automatically. `fuzz.py` builds rule-shaped instances that honour the
nested guards; `best_rules` minimises by firing counts. Rules whose conditions keep an unresolved
placeholder are infeasible; a vacuous (existential) decoder is admissible only in a level-1 structural
reading (17286-type both-compound laws).

**Certification.** `leangen.py` emits the 5107 template: accessor guards, shared gated
`let p_k := if hs_k : msr a b < msr u v then op a b else J u v` (`msr = max² + sum` with two helper
lemmas), a flat if-chain over named structural preconditions `P_k`, a refutation by
`simp (config := {decide := true}) [op.eq_1, sz, P1, …]`, and the law as `sorry` for the agent. Every
agent proof had the same shape: pack the nested calls as ∃-variables (`op_cases`), prove the decoding
chain's products free by size, collapse the rule set to R1 + one recursive rule, close leaves with
`congrArg sz … ; omega`. Certificates 7.9–19.4 KB, 4–7 s judge time. `dualcert.py` builds the R-form row's
certificate from an accepted L-form file (flip `inst`, recompute the refutation with the free model,
`lhs` by `first` over the six variable permutations) — six rows for zero proof effort.

## Resume checklist (in this order)

1. **Diagnose the gate failure and package.** `pytest stage2/tests -q -n auto` on an idle box (the run
   that failed shared the CPU with a 6-worker extraction batch and 98 stray processes — rail 22); compare
   the skip count (rail 16); then `package_solver.ps1`, check the artifact ≤ 500,000 B (expected ≈ 410 KB:
   +246 KB of Lean packed zlib+base85), spotcheck, commit.
2. **Next agent wave** on the validated packages (`AGENT_BRIEF.md` is the brief; skip laws whose rows are
   already accepted — check `certs/ledger.jsonl` first): 5833 (row 22818; dual 40070 → 17522), 5837 (22818,
   25964), 6878 (28770; dual 39126 → 22455, 30591), 7701 (15535), 8485 (4916), 9667 (25964; dual 36638 →
   28770), 11081 (41082, 22818; dual 35036 → 17522, 41082), 11280 (25964), 12087 (28770, 22818), 12234
   (22818), 10218 (30591). After each acceptance run `dualcert.py` for the dual rows.
3. **Finish the package batch** (`genbatch.py gen7b.jsonl 1200 6 <remaining ids>` — 6 workers, nothing
   else running): the 37 laws not regenerated yet, including the 26 R-form laws (dualised automatically)
   and the 16 both-compound laws (17286, 18137, 21864 validate; the rest need the extractor's
   both-compound path checked).
4. Residual failures 9663, 10222, 12073, 13764, 32281/13849, 34889/11082: read the failing chain
   (`closedform.py <eq>` prints it against the semantic model) — each so far was one more mode.
5. 6912 / 39214: quotient model (squares idempotent) — needs the search to normalise `J(t,t)` for a
   square `t` and to match encodings modulo it.
6. Record everything in `CLAUDE.md` (measured-state row, rails on the search bugs above) and the memory.

Tooling and the accepted certificates are committed (`41a69e6`); the batch logs `gen*.jsonl`,
`free*.jsonl` and the dev compile dirs under `vendor/stage2-official/.artifacts/dev_*` are gitignored
scratch.
