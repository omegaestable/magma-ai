# 2026-08-29, deep session 8 — Austin 46 → 60, and the result that reframes the rest

Every number here was measured this session. The method that produced them is
`stage2/experiments/austin/automata/gen/LEMMA_LIBRARY.md` (~85 KB); the per-law state is
`stage2/docs/DEEP_SESSION_8_AUSTIN_HANDOVER.md`. **Read the library first** — it is indexed by what you
are trying to do, and it opens with the oracle ladder.

## Final state — all four commands green

| check | result |
| --- | --- |
| Offline gate (`pytest stage2/tests -n 4`) | **558 passed, 1 skipped**, 9 min 23 s. The skip is the documented spot-check placeholder. Zero failures |
| Spotcheck (`spotcheck.py`) | **90 / 90, 100% accuracy, 0 mistakes** |
| Packaged artifact | **456,604 of 500,000 bytes — 43,396 B headroom**; imports in 0.26 s; `DISTILLED_CERTS` 119 entries; **60/60** research rows served via `aus_e` certs |
| Organizer validators | `_validate_submission_layout` **OK** (`stage2/submissions/` holds `solver.py` and nothing else); `_extract_prompt_from_solver` reads **3,275 chars** |
| Fixture | 238 pins (178 non-research + 60 research); `test_judge_verified` **230 passed, 0 skipped** |
| Austin research set | **60 / 100** judge-accepted, every row re-judged by the orchestrator before entering the ledger |

## What shipped

| law | rows | how |
| --- | --- | --- |
| 27859 | 0050, 0099 | E-quotient carrier; **first compile, two judge calls**, 9,108 B, no induction anywhere in the file |
| 34889 | 0010, 0036, 0070 | **re-classified Track C** — three literal instantiations derive `(g*g)*(g*g) = g*g`; E-quotient carrier, 3 rules, ~2 hours |
| 33020 / 12883 | 0012, 0054, 0031 | **harvested** — a finished zero-sorry proof was on disk, 2,127 B over the cap; squeezed to 19,877 B |
| 12073 | 0007, 0022 | carrier (c) of `PLAYBOOK_QUOTIENT` §3; both accepted first try |
| 13764 / 32294 | 0008, 0081, 0064 | **carrier change**: 67 rules / 54,402 B definition block → 5 rules / ~2,300 B |
| 23354 | 0027 | `ONESIDE` closed through the rule's own guard; one judge call |

## The result that reframes the remaining 40 rows

**The extractor's free model is the wrong carrier for the hard laws, and no amount of rule-finding fixes
it.** `closedform` emits one rule per free/decoded combination of the law's chain — 2^k rules — and reads
the payload off a **fixed accessor path**. For several laws the required rule set is therefore **infinite**:
each extra level of encoding nested in the argument moves the payload one level deeper, and the rule that
reads at depth d is refuted by the level-(k+1) instance. Law 17286's form is the crispest — it reads at
depth 3 and **level k needs depth 3k+2**.

**13764 is the one that got out**, and its construction is the template: replace the free model with a
hand-built term algebra carrying a second constructor, express the model as two or three decidable
predicates rather than N rules, and **replace the structural guard with a recursive re-run of the
encoding**. *The digest compresses a rule SET; only a different CARRIER compresses a DEFINITION BLOCK.*

**Four laws are now closed by proof rather than by search:**

* **22591** — `a = I3(a)` in seven substitution instances, no freeness assumed: no model on the free term
  algebra at all.
* **11081 / 35036** — no rule set over a free term algebra, *whether its decode returns a projection, a
  reconstruction, or is certified by recomputation*. Seven carriers, nineteen rule sets, witnesses of size
  9, 15 and 59.
* **12234** — the one open cell is not closable by another rule on its carrier; four failure positions, a
  structural proof, five candidate rules all H3-clean.
* **12087** — *mark narrowly ⇒ the root reading is unanchored ⇒ it forges; mark broadly ⇒ the free cells
  break.* Eleven model iterations; every finite extractor rule set separately proved false.

**And five laws independently name the same escape.** 11081: *a carrier with a well-formedness invariant,
so the attacker's term is not in the carrier at all.* 12234: *a carrier in which the junk product cannot
decode.* 12087: *a rule needs an anchor — a conjunct only the model can produce.* 21864: the witness was
destroyed by the very decode being certified. 9663: *the separator is one cell wide.*

> **They are one construction: restrict the carrier to the terms the model itself builds.** Then every
> guard is anchored, because a well-formedness invariant **is** a root-vs-inner-position separator — and a
> term algebra cannot supply one, since `op` is a function of `(u,v)` alone and the two positions present
> the same pair. **Worth ~25 rows.**

First measurement, taken before the session ended: **the image of `op` is 4.1% of the term algebra** — so
the restriction is real — **but 9663's open-cell witness is itself op-built**, so the invariant must be
finer than "is an output of `op`". The question to resume with: *do rules rejected on the free carrier
become admissible on the image?* Every impossibility above quantifies over rule sets **on a free term
algebra** and must be re-checked against the image before it is assumed to carry over.

## Eleven models were falsified, and the oracle ladder went from five rungs to twelve

Seven of them passed roughly 10^6 validation chains first. Each would have cost an agent-session of Lean
work. **Nothing false reached the judge.**

Every rung was forced by a model that passed the previous one:

1. `rv.run_tests` · 2. `deep_tests` 20k × 3 · 3. the case tree · 4. the both-decoded census ·
5. `identity_probe` · 6. **the level-k descent, both tower variants, cell census printed** ·
7. **vary the junk variable** · 8. **forced firing** · 9. **H3** · 10. **per-branch, per-construction
firing counts** · 11. **the forcing suite's own positive control** · 12. **every construction ported from
the previous carrier's oracle**.

**H3 is the cheap decisive one** — build `y = enc(j,w,x)` so `y` is a genuine encoding *by x*, then run the
law. Measured at ~1,100× and 170× the kill power per chain of an exhaustive sweep on two different laws,
and on two laws it was the **only** non-vacuous family for the deep rules.

**Two things are not evidence.** `_orch_minim.py`'s `status: "ok"` is **not** a soundness certificate — its
keep-set is "rules that fire under the fuzz battery", and constructed cells are exactly what the battery
misses; a 6-rule minimised model passed 1.5M exhaustive assignments, 16,880 targeted, 6,113 risky cells and
a reachable-cell census, and is false. And any count printed by a counter placed *before* the loop that
fills it.

**Diagnostics worth keeping:** identical fail counts across two versions ⇒ the guard certifies nothing; a
rule's firing set invariant under its guard ⇒ the problem is the **position**, not the guard; a low
semantic-failure count means the witnesses are **big**, not that the carrier is nearly right; and ruling
out a quotient needs a **positive control** (`gen/_x40037_derive3.py` reproduces 6912's whole hand
derivation before finding nothing for 40037).

## Two classification errors corrected

**"Semantic free-model failure ⟹ the carrier must change" is invalid.** `freemodel.Free`'s reading search is
**incomplete**, so its failures can be ordinary decoder holes. `gen/_id_query.py` — congruence closure over
the law's own instances, where **every merge is a sound consequence** — is the test that decides it. It
rediscovers 12073's and 27859's square identity unprompted and finds **0** for 9663, 36487 and 12294 over
689,386 / 2,209,526 congruence nodes. Those four rows were filed as needing new carriers and do not.

**"Near-clean, 1–2 semantic instances" is not a class.** All three members resolved so far are Track C
identity laws: 34889 (shipped 3 rows), 6912 (*all squares equal*, refuting the free algebra over ≥ 2
generators) and its dual 39214.

## Solver and packaging work

* **One shared lzma blob for fifteen data tables** instead of four separate streams plus twelve verbatim
  literals: 97,166 → **72,920 B**, artifact **459,379 → 435,942 B**. A separate stream restarts the
  dictionary and these tables share vocabulary. All 16 tables verified byte-identical; import cost +0.21 s.
* **`PROMPT` must never be packed**, though it is 3,338 B and packs to 2,210. The organizers'
  `proxy._extract_prompt_from_solver` reads it out of the *artifact* by AST and accepts only a top-level
  string constant; packing it makes the extractor return `""` and **the Solo LLM lane runs on an empty
  prompt with no error anywhere**. Caught within a minute by `test_artifact.py`; now pinned by
  `test_prompt_is_never_packed` and by a comment at the packer's table.
* **Measured marginal cost of a certificate**: **1,421 B for the first row of a new law, 64 B for each
  sibling row**. 100 Austin certificates project to ≈ 480 KB.
* **The gate was red at HEAD.** Three `test_judge_verified` pins fail on the committed tree — route drift
  from the `order5hards` commit's distilled routes shadowing the pinned `egg_ladder` ones. Confirmed by
  stashing this session's changes and re-running. Re-solved, re-judged **3/3 accepted**, re-pinned
  surgically. `package_solver.ps1` refuses to package on gate failure, so this was on the critical path.
* **`squeeze.py` is not idempotent** — re-squeezing yields a smaller file that does not compile, and the
  breakage reads as a name collision. Guarded and warned.
* **`verify_certs.py` never wrote the ledger** despite its docstring; `append_ledger.py` now does,
  append-only. `ledger.py` had a stale path and crashed on every invocation. Both fixed.

## New tooling

`gen/LEMMA_LIBRARY.md` (the method), `WAVE3_PROMPT.md` (the wave brief), `append_ledger.py`,
`splice_certs.py` (splices `DISTILLED_CERTS` and rewrites **only** the research pins of the fixture),
`gen/P2_EXISTENTIAL_DECODER.md`, `gen/P2_MECHANISM.md`, `gen/NOTES_<eq>.md` for every law worked
(11 files, 300+ KB), and per-law labs with their oracle stacks wired in
(`gen/_w3_12087_lab.py` runs everything in 2 s; `gen/_x12234_carrier.py` holds 22 carriers and seven
oracles; `gen/_x9663_fast.py` ranks in 40 s).

## Where to start next session

1. **The harvest scan** (rail 47) — it shipped three rows in fifteen minutes this session. Then *compile*
   what it finds: `gen/hole23357.lean` has zero sorries and is a **refutation**.
2. **The eleven rows that need only Lean** — 17286/28626 (4), 32281 (3), 38316 (2), 23357/23653 (2). Each
   has a compiling file and a named list of remaining lemmas. No research required.
3. **The anchored carrier**, with 9663 as the test case: one cell wide, otherwise clean, four rules,
   unconditional gates, a 40-second harness and a non-vacuous forcing suite.
