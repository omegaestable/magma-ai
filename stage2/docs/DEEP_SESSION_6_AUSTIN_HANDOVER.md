# Deep session 6 — the Austin research set, 37 → 100 (handover)

Written 2026-08-29 evening. Read `CLAUDE.md` first, then this file; the evidence for every number is in
`stage2/results/2026-08-29-free-models-recursive-certs.md` (the construction) and
`stage2/results/2026-08-29-austin-wave-37.md` (the waves). Tooling: `stage2/experiments/austin/automata/`
(`AGENT_BRIEF.md`, `WAVE2_PROMPT.md` are the proof-agent briefs; every script named below lives there).

## The goal

**All 100 rows of `data/hf_cache/research_order5_hard.jsonl` accepted by the real judge and shipped as
`false:distilled:aus_e*`.** 37 are. The session ends at 100/100, or with a measured reason per remaining row
(a Lean-checked counterexample to a candidate model, or a proof that the law derives an identity the
construction cannot carry) — not a budget.

## State (2026-08-29 evening, all real-judge)

| | |
| --- | --- |
| Accepted / shipped | **37 / 100** (`certs/ledger.jsonl`; 37 `DISTILLED_CERTS` entries; 37 fixture pins) |
| Artifact | 444,643 B (55 KB headroom), gate 514 passed / 2 skipped, spotcheck 90/90 |
| Open | 63 rows, 40 hypotheses; up to duality **27 distinct laws** (the ledger below) |
| Accepted construction | the **free model** (readings) as a finite recursive rule system, certified by the 5107 template; dual rows by transplant (`dualcert.py`, both directions) |

## The mathematics, stated once

For a law `x = A ◇ B` the **free model** is the free magma on generators with `op(u,v) := x` iff `(u,v)` is a
*reading* — some assignment of the law's variables evaluates `A` to `u` and `B` to `v` (inner products
evaluated with `op` itself) — and `J(u,v)` otherwise. It is a least fixed point; the law holds by construction
wherever readings are unique. Three facts govern everything below:

1. **A reading is a mode vector.** Each internal node of the pattern is either *free* (the target is a
   `J`-node whose children match) or *decoded* (the node's value is itself a reading of the whole law). The
   closed form (`closedform.py`) enumerates mode vectors and emits one accessor rule per feasible vector; the
   Lean `op` is the ordered if-chain of those rules, gated by the recursion measure `msr = max²+sum`.
2. **The hard holes are decoded nodes in the wrong place** — a decoder that must be located through an
   occurrence that is itself decoded (level 2/3), the outer product of the encoding decoded (`v = u`), a
   decoded product inside a struct-decoded root, a decoded inner product of the *encoding* on the root-pattern
   side (both-compound laws). The extractor now has modes for all four; what it still lacks is the **existential
   decoder for both-compound laws** (`∃ z, op(x, op(y,z)) = v` with `z` forgotten) and rules whose result is a
   nested `op` (the "chain descent" of 18137's model).
3. **Two things are not modes.** (a) *Quotient laws*: the law derives an identity between distinct free terms
   (12073: `y◇(y◇(z◇z)) = ((y◇y)◇y)◇(z'◇z')`, then `K(S)=S` for squares; also 27859, 21865, 21866, 22591,
   which fail on one-generator terms of size ≤ 9). The carrier must be a quotient — tags. (b) *Gate-cut
   readings*: a genuine reading whose nested guard pair is not below `msr(u,v)` (6912, 8485). Structural
   expansion (`~` rules) buys one level; the self-squaring family of 6912 needs a rule with a negative
   constraint the DSL does not have.

## Mistakes of the last two sessions, and the fix each got

| Mistake | Cost | Fix (in place) |
| --- | --- | --- |
| Validating skeletons with 3,000 random tests | 7 of 10 wave-1 skeletons were FALSE; an hour of agent time each | `revalidate.run_tests`: exhaustive one-generator terms ≤ 9 and two-generator ≤ 5, deep, rule-shaped fuzz, **closure fuzz**, **critical-pair fuzz**. Still not enough alone — two holes appeared only at 20,000 deep tests. **Standard: 20k deep + `run_tests` on 3 seeds before an agent is assigned** |
| Minimising rules by "fired on one seed" | 24200 (0 → 21 fails after minimisation), 28626 (a 2/20,000 rule dropped) | validated-removal minimiser (`revalidate.py`); for both-compound laws keep the full set |
| Sonnet agents for the Lean proofs | 8 agents, 0 accepts (all left `sorry`s with correct diagnoses) | proofs are fable work; sonnet only for validation/repair scripts |
| Byte cap not planned for | 18137 (23 KB), 39163 (24.5 KB) proved but unshippable | `squeeze.py` (−15 %, 18137 accepted at 19,705 B); solver FALSE margin 50 B; **`macro`/`syntax`/`elab` are banned tokens** — never save bytes with macros |
| Running the gate under a batch | a spurious failure cost the packaging | idle box for the gate (rail 22); `killbatch.py` before it |
| One-line `rhs` proofs broke `dualcert.py` | one wasted judge call | fixed; `dualcert.py` also handles R-form → L-form |
| `chk<eq>.py` tested the un-dualised law for R-form laws | agents saw 3000/3000 spurious fails | fixed in `leangen` |

## The plan — three tracks, run concurrently, with stop conditions

### Track A — prove the validated skeletons (fable agents; ~16 rows; first)

Each has a validated model and a partial proof; the brief is `WAVE2_PROMPT.md` + the file named here.
Assign one fable agent per law, 20k-deep-validated first, `squeeze.py` before judging.

| Law | Rows | File / state |
| --- | --- | --- |
| 5837 | 0021, 0045 | `gen/rec5837_proof.lean`: 6 sorries in `main`; key lemma `L1` stated; `Tfree_L3` proved |
| 28626 (+17286 dual) | 0037, 0038, 0025, 0040 | `gen/rec28626.lean`: 10 rules, `op_cases`/`TR10`/`TRs`/`P1_of_free` proved; `law` open |
| 24200 | 0001, 0087 | `gen/rec24200.lean`: 15 rules validated; needs the "T2/T4 always free" invariant (see `gen/_probe24200*.py`) |
| 12087 | 0024, 0097 | 4-rule repair; `TR4`/`TRv` proved; `V_free_partial` 4 sorries |
| 12234 | 0061 | `gen/rec12234.lean`: 8 sorries in `Dfree`, everything else proved |
| 23354 | 0027 | 4-rule repair; blocked on `core_no_fix (x) : a1 x ≠ op (a2 x) x` (strong induction on `sz x`) |
| 38316 | 0055, 0065 | `gen/rep38316.lean`: 10-rule model validated to size 11; no proof |
| 39163 | 0002 | complete proof, 24.5 KB with macros: rewrite `CFN` (5.4 KB) without macros, squeeze |
| 33020 (+12883 dual) | 0012, 0054, 0031 | repair candidate `gen/fix33020.py` (needs gate-safe inlining of `R4full`) |
| 6878 (+39126 dual) | 0034, 0044, 0075 | repair in `gen/rep6878/` (interrupted by the API error) |

Stop condition per law: 35 judge iterations. The recurring proof shape: `op_cases` (pack the gated lets),
`TR` (one unfold), "the k-th chain product is free unless coincidence C_k" by size, rule lemmas, `law` by
cases; leaves `have := congrArg sz h; simp only [sz] at this; omega`. Where a chain product can *recursively*
coincide (12234, 23354, 24200), state the invariant as a strong induction on `msr` exactly like 18137's `CMP`.

### Track B — make the extractor complete for the remaining L-form/dualised laws (~20 rows)

Laws whose regenerated packages still fail: 11081/35036 (4 rows; 28 rules validated but heavy — minimise
with validated removal), 13764/32294 (3; 82 rules), 9663/36487 (3), 40037 (1; 2 rare holes), 10222/35836 (2;
extraction times out at 2,400 s — cap `level2` combos), 36524, 32281 (3), 34889 (3), 12294, 10218, 38565.
Procedure per law: `python revalidate.py <eq>` → `trace.py <eq>` on the first failure → classify (missing
mode / gate cut / quotient) → add the mode to `closedform.py` (never a per-law hack) → re-run the batch.
The two modes to add first: (i) **existential decoder for both-compound laws** (a root-reading variable that
occurs only inside the decoded node is unconstrained; the encoding side gives the structural conditions),
which is exactly what 23357/23653, 21864/24199 need; (ii) **nested-op results** (`x = op u B`) for the chain
descent. Stop condition: a law whose failing instance is a derived identity goes to Track C.

### Track C — quotient carriers for the identity laws (12073, 27859, 21865, 21866, 22591: 11 rows)

The free magma cannot satisfy `X_z = X_{z'}`. Construction: carrier = free magma **plus tag constructors**,
one per derived identity family (`K y` for 12073's `((y◇y)◇y)◇(w◇w)`), `op` maps the identified terms to the
tag and reads the tag as the payload it stands for (`op(y, K y) = y`). Derive the identity family
mechanically: run `smallcheck.exhaustive` on the semantic model, take the failing instances, and let the
law's own evaluation say which two terms it identifies; iterate until the exhaustive check passes (the
cascade `K(S) = S` for squares is the first iteration for 12073). The symbolic verifier of the tag-automaton
session (`symb.py`) is the right checker for tag carriers. Stop condition: the cascade does not close after
three tags — then the row's reason is "quotient hierarchy not finitely tagged", written with the instances.

### Not on any track (measured dead)

Table search, z3, affine/PWL templates, Prover9, exact completion on this set; `reasoning_effort` tricks;
lexicographic gate; tactic macros; sonnet proofs; the `exist` mode and `cap2=10000` on 6912.

## Testing protocol (mandatory before a judge call)

1. `rv.run_tests(law, rules, [3,4,5], 3000, 12000)` = 0 fails **and** `cf.deep_tests` 20,000 on two more
   seeds = 0 fails, on the *dualised* law for R-form laws.
2. The certificate compiles against the row's exact `JudgeProblem` (`devrow.py` + `devlean2.sh`).
3. `squeeze.py in out --rename` when > 19,000 B; recompile; the banned-token list in `WAVE2_PROMPT.md` §6.
4. One judge call (`judge1.py`), then `dualcert.py` for the dual rows, then `certs/<row>.lean` + ledger.
5. Ship in bulk: `ship.py` → splice `certs/ship_certs.py` into `DISTILLED_CERTS` (drop old `aus_e*` lines
   first, as done on 2026-08-29), replace the research fixture lines with `certs/ship_fixture.jsonl`,
   `package_solver.ps1` on an idle box, spotcheck, commit.

## Commands

```powershell
# regenerate + validate + minimise + emit one law (emits even when it FAILS, header says which)
.\.venv\Scripts\python.exe stage2/experiments/austin/automata/revalidate.py 11081
# many laws, 6 workers, 40 min cap each
.\.venv\Scripts\python.exe stage2/experiments/austin/automata/revalbatch.py out.jsonl 2400 6 11081,13764
# explain the first failing instance
.\.venv\Scripts\python.exe stage2/experiments/austin/automata/trace.py 11081
# exhaustive small-term check of the closed form / the semantic model
.\.venv\Scripts\python.exe stage2/experiments/austin/automata/smallcheck.py 11081 9 1 --closed
```
