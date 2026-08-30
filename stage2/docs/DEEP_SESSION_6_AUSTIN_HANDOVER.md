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
| Accepted / shipped | **46 / 100** (`certs/ledger.jsonl`; 46 `DISTILLED_CERTS` entries; 46 fixture pins) — updated 2026-08-29 evening, session 7 |
| Artifact | **423,307 B (76.7 KB headroom)** measured on HEAD + the 46 certificates, after the packer moved to lzma |
| Open | 54 rows, 29 hypotheses; up to duality **20 distinct laws** |
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

---

# Session 7 (2026-08-29, evening) — 37 → 46, and the open set re-sorted

Nine rows shipped, each re-verified by an independent second judge pass (`verify_certs.py`, 9/9 accepted):

| rows | law | how |
| --- | --- | --- |
| 0034, 0044, 0075 | 6878 / 39126 | `gen/rec6878_rep.lean` was already a **complete, correct, macro-free proof** sitting on disk at 22,681 B against the 20,000 B cap. `squeeze.py --rename` took it to 19,205 B, accepted unchanged; `dualcert.py` transplanted it to both dual rows |
| 0002 | 39163 | the five tactic macros replaced by ordinary lemmas; 19,360 B, accepted on judge call 1 of 20 |
| 0001, 0087 | 24200 | proved. The invariant this document asked for ("T2 and T4 always free") was proved **in general** as `FREE (a b) : op (op a b) b = J (op a b) b`, not just along the chain |
| 0021, 0045 | 5837 | all six sorries closed; `main` rewritten rather than patched |
| 0077 | 38565 | model 30 rules → 3; **the 3-rule set was FALSE** and the agent found it — see the validation section |

## Four corrections to this document's own diagnoses, each measured

1. **The `revalidate.py` "extraction timeout" is not extraction.** `Extractor.rules()` costs **0.2–0.3 s** on
   every one of 10222 / 36524 / 12294 / 10218 / 8485. What it returns is **83–218 rules**; `Closed.op` is
   O(rules) per call, so one deep test costs 25–63 ms, and the full validator — re-run once per rule by the
   minimiser — is quadratic in the rule count. **Capping `cap2` buys nothing**: extraction is under two
   seconds at any `cap2`, and with subsumption the rule count stops depending on it at all. The fix is fewer
   rules. See `gen/EXTRACTOR_NOTES.md` and `gen/SEMANTIC_TABLE.md`.
2. **The identity-law class is bigger than five.** `python smallcheck.py <eq> 9 1` runs the law over all
   12,167 one-generator assignments in the SEMANTIC free model; `--closed` does the same in the extracted
   rule system. Semantic-clean plus extracted-broken means an extractor hole; semantic-broken means no rule
   set can work. Measured for every open law in `gen/SEMANTIC_TABLE.md`. **9663 / 36487 (3 rows),
   10222 / 35836 (2 rows) and 12294 (1 row) are identity laws**, not repair tasks — 9663 is filed here as
   "49 rules, one fuzz failure", which was the extracted system faithfully agreeing with a wrong model.
   Conversely **32281 (0 semantic fails against 134 extracted), 33020 / 12883 (0 against a wholly false
   skeleton) and 34889 (2 against 192) are pure extractor holes** — nine rows filed here as broken models.
3. **21866 is not in the identity class either.** 18,515 failures at one generator and 7,744 at two
   generators, against 13–68 with **zero** two-generator failures for the identity laws. Its distinguishing
   feature: `w` occurs exactly once, so the reading is existential in `w`. That is plausibly
   *under-determination* — resolvable by choosing a canonical witness — rather than a forced identity, which
   would make it easier, not harder. Nobody has tested that.
4. **A real, general bug in the extractor, now fixed** in `gen/closedform2.py` (a drop-in replacement;
   `closedform.py` untouched): `decoder_expr` / `decoder_of` hardcoded the decoder variable as the literal
   name **`y`**. The decoder is the variable on the bare side of the law, which after `normalise` +
   `dual_pat` is `z` for **32281, 34889 and 40037** — all three dualised. Every lazy-decode rule for those
   laws located the decoder at the wrong position, which is exactly their extracted-versus-semantic gap.
   `closedform2` also prunes subsumed rules: 10222 168→88, 12294 218→132, 10218 140→63, 8485 83→38,
   12234 169→61, 6878 98→44, 39163 100→60.

## The validation standard has to rise again — the 38565 finding

38565's model passed `revalidate.py` (OK, 30 rules → 3, 0 failures), then **126 hand-built coincidence
instances, `rv.run_tests` on 9 seeds, and 13 × 20,000 deep tests** — and was still FALSE. The hole was found
only by writing the **free/decoded case tree** of the law's own evaluation chain and building an instance per
cell. For 38565 the chain is `s1 = op x z`, `s2 = op z s1`, `s3 = op s2 y`, `s4 = op y s3`, and the missing
cell was `(s1 DECODED and s3 DECODED)`, which occurs **0 times in 30,000 random draws** of any shape the
fuzzers generate. To force `op(a,b)` to decode, set `b` to the free encoding of the law's right-hand side with
`y := a`, then nest that construction for a second decoded product (`gen/_x38565_dd.py`).

**New standard, before any proof work: enumerate the 2^k free/decoded combinations of the k chain products,
build one instance per reachable combination by chained encoding, and check every one.** The deep and fuzz
suites only ever reach the one or two shallow cells. The same finding condemns validated removal on its own:
it drops exactly the rules whose only witnesses live in the deep cells.

## Method artifacts written this session — read these before assigning any agent

| file | what it is |
| --- | --- |
| `gen/PLAYBOOK_PROOF.md` | the Lean method distilled from the accepted certificates, 27 snippets all compiled. **Section 3 is the lever for heavy laws**: `TRpre` / `Pdig` / `Wdig` collapse a 24-rule model to a ~1,900-byte digest with no per-rule lemma, and `gen/_pb_common.py` computes the digest precondition. It also establishes a hard wall — `split` fails with "maximum number of steps exceeded" past about ten rules and there is no option to raise it, so the digest is not an optimisation, it is the only route |
| `gen/PLAYBOOK_REPAIR.md` | the repair method, self-validated by re-doing law 9667's repair end to end. Its section 9 decision rule is what re-sorted the open set |
| `gen/EXTRACTOR_NOTES.md`, `gen/closedform2.py` | the extractor fixes above, with before/after rule counts |
| `gen/SEMANTIC_TABLE.md` | semantic versus extracted failure counts for every open law, and the track each belongs to |
| `gen/IDENTITY_INSTANCES.md` | the smallest failing instances of every semantically-broken law |
| `jlock.py` | pins `JUDGE_LEAN_PATH` and caps concurrent Lean judges (`JUDGE_SLOTS`, default 5). **Parallel judging is safe now** — two simultaneous calls measured 13 s each |
| `verify_certs.py` | re-judges every `certs/*.lean` against the real judge. An agent's claim of acceptance is not evidence |
| `xtrans.py` | the cross-model transplant screen |
| `gen/_orch_minim.py` | extract, then minimise, then full-validate, for the huge rule sets |

## Byte budget: solved, with room

`minify_submission.py` now packs with **lzma (preset 9 | EXTREME) instead of zlib**. The certificate table is
about 600 KB of Lean whose entries share a long preamble, and zlib's 32 KB window cannot see across two 19 KB
certificates. Measured on the 46-entry table: **zlib + base85 112,379 B, lzma + base85 50,155 B**. The
artifact built from HEAD plus all 46 certificates is **423,307 B, 76.7 KB headroom** — smaller than the
444,643 B this session started from, while carrying nine more certificates. `lzma` is stdlib. Verified: the
packed artifact imports and all 46 certificates round-trip byte-exact. `SUBMISSION_NOTE.md` should name lzma
alongside zlib.

## The quotient construction — three independent designs converged

Three agents attacked the identity laws from different directions (tag constructors on the free magma;
normal forms of a completed rewrite system; a carrier that is not the free magma) and **all three concluded
that every square must be identified with a single element**. Two produced carriers for 12073
(`x = y ◇ (((y◇x)◇x)◇(z◇z))`):

* normal-form, no quotient type: `M ::= g n | K | E t | J a b`, with `K` the normal form of every square and
  `E u` the normal form of `u ◇ K`, and `op` computing straight into normal form;
* tag: `M ::= g n | E | J u v` with `E` a single **0-ary** constructor identified with every square — *not*
  the argument-carrying `K y` this document proposed — and `op` a six-branch ordered chain over a
  well-founded measure.

The third derived it as a theorem: with `S_z = z◇z`, `psi_y(x) = (y◇x)◇x` and `E(y,z) = psi_y(y)◇S_z`, the
substitutions `x := y` and then `x := E(y,z')` give `psi_y(E) = y`, hence `E(y,z') = y◇(y◇S_z)`, so `E` does
not depend on `z'`. Their full reports are in the workflow journal at
`.claude/projects/.../subagents/workflows/wf_511b985a-b21/journal.jsonl`.

**The synthesis agent that was to verify these and write `gen/PLAYBOOK_QUOTIENT.md` died on the session
limit; that file does not exist.** Writing it — re-running each claimed model under the case-tree standard
above before trusting any of them — is the first job of the next session, and it is worth 17 rows.

## Where the remaining 54 rows stand

* **Track A — model validated, proof outstanding (13 rows):** 12087 (3-rule model, 2 rows), 23354 (3-rule,
  1 row, blocked on `core_no_fix` by strong induction), 12234 (1), 38316 (2), 17286 / 28626 (4),
  11081 / 35036 (4 — 24 rules, use PLAYBOOK_PROOF section 3), 13764 / 32294 (3 — 67 rules, whose definition
  block alone is 54,402 B, 2.7× the cap, so minimise first or the law is unreachable).
* **Track B — extractor holes (15 rows):** 32281 (3), 33020 / 12883 (3), 34889 (3) — re-extract with
  `closedform2` first, the hardcoded-`y` bug is theirs — plus 40037 (1), 8485 (1), 10218 (1), 36524 (1),
  6912 / 39214 (3, gate-cut), 21864 / 24199 (2).
* **Track C — identity laws (17 rows):** 12073 (2), 27859 (2), 21865 (2), 22591 (3), 9663 / 36487 (3),
  10222 / 35836 (2), 12294 (1), 21866 (2 — the outlier, see correction 3).

## Two things that cost this session, so they need not cost the next

* **`fable` ran out of credits mid-run and killed 16 agents at once**, then the session limit killed 22 more.
  Agents that write findings to `gen/` as they go lose nothing; agents that report only at the end lose
  everything. Prefer prompts that persist incrementally. Replacing the `fable` override with the session
  model worked — the 24200 and 5837 proofs came from that second wave.
* **A concurrent session was editing `stage2/solver/solver.py`** — 609 lines of new anchored-projection
  routes appeared mid-session. Three `test_judge_verified` pins (`etp_2923_156`, `etp_3983_3800`,
  `etp_3983_4296`) fail in the working tree and pass at HEAD; they belong to that work, not to the Austin
  certificates. Check `git status` for a foreign diff before blaming the gate.
