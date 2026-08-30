# Deep session 8 — the Austin research set, 46 → 100 (live log + handover)

Started 2026-08-29 from `DEEP_SESSION_7_AUSTIN_HANDOVER.md`, which is still the reference for the
four-problem decomposition (P1–P4) and the agent doctrine. **This file records what session 8 measured,
including five places where session 7's plan was wrong.** Read `CLAUDE.md` first, then session 7's file,
then this one.

## Score

| law shipped this session | rows | how |
| --- | --- | --- |
| session 7 close | — | 46 / 100 |
| 27859 | 0050, 0099 | E-quotient carrier, **first compile, 2 judge calls**, 9,108 B |
| 34889 | 0010, 0036, 0070 | **re-classified Track C**, E-quotient carrier, 3 rules, ~2 hours |
| 33020 / 12883 | 0012, 0054, 0031 | **harvested** — a finished zero-sorry proof on disk, squeezed 22,127 → 19,877 B |
| 12073 | 0007, 0022 | carrier (c), `qz12073_skel`; 2 judge calls, both accepted first try |
| 13764 / 32294 | 0008, 0081, 0064 | **carrier change**: 67 rules / 54,402 B definition block → 5 rules / ~2,300 B |
| 23354 | 0027 | `ONESIDE` closed through the rule's own guard; one judge call, accepted first try |
| | | **60 / 100** |

Artifact at 60 certificates: **456,604 B** (43,396 B headroom). Measured **1,476 B per certificate** over
the fourteen added this session, consistent with the 1,421 B/new-law + 64 B/sibling model; projecting the
remaining 40 rows gives **≈ 480 KB**, about 20 KB inside the cap.

> **Coordination hazard, live.** Four other interactive sessions share this working tree. One of them added
> five `true:distilled:spine_constancy:*` pins to `stage2/fixtures/judge_verified_certs.jsonl` during this
> session. `splice_certs.py` preserves them because it rewrites **only** the `false:distilled:aus_e*` lines
> (rail 16), and `stage2/solver/solver.py` shows only this session's own +14 lines — but a peer running
> `judge_rows.py --write-fixture`, which **REPLACES** the file, would delete all 60 research pins. Check
> `git diff --stat` on both files before and after any fixture write.

Every row is re-judged by the orchestrator with `verify_certs.py` before it enters `certs/ledger.jsonl` —
an agent's claim of acceptance is not evidence.

---

## 1. Corrections to session 7's handover

**C1. The byte budget was wrong, and it mattered.** Session 7 recorded "the artifact built from HEAD plus
all 46 certificates is 423,307 B — 76.7 KB headroom". Measured 2026-08-29 by running
`minify_submission.py` over the pre-session base (`b73e50f`, which added ~36 KB of anchored-projection routes):
**459,379 B, 40,621 B headroom.** The marginal cost of a certificate, measured rather than extrapolated,
is **1,421 B for the first row of a new law and 64 B for each sibling row** (a second row of the same law
differs only in `def rhs`, and lzma sees that). The 52 open rows are 24 new laws plus 28 siblings, so 100
certificates project to **≈ 475 KB**. That fits — but only after C2.

**C2. One shared compression blob, not four — worth 23,437 B.** The packer compressed four data tables,
each in its own lzma stream, and shipped every other data literal verbatim. A separate stream restarts the
dictionary, and the tables share vocabulary. Now **fifteen** tables go into **one** blob (measured:
97,166 B before; 77,635 B as separate blobs; **72,920 B shared**). Artifact **459,379 → 435,942 B**. All
fifteen payloads verified byte-identical afterwards, artifact import cost +0.21 s, `test_artifact.py` 8/8. A new
`"lit"` kind carries any top-level literal as its `repr`, rebuilt with `ast.literal_eval`, so
tuple/list/str types survive exactly.

> **`PROMPT` must never be packed**, though it is 3,338 B and packs to 2,210.
> `pipeline/proxy.py:_extract_prompt_from_solver` reads it out of the artifact by AST and accepts **only** a
> top-level `PROMPT = <str constant>`; packing it makes the extractor return `""` and the Solo LLM lane
> runs on an empty prompt with no error anywhere. Caught within a minute by
> `test_the_official_extractor_still_finds_a_usable_prompt`. Now pinned twice: by a comment at the packer's
> table, where the next person will add an entry, and by `test_prompt_is_never_packed`.

**C3. Law 33020 was already proved, and filed as open.** `gen/_sq33020.lean` — 22,127 B, **zero sorries**,
complete `def submission : Goal` — compiles with **0 errors** against row 0012's real JudgeProblem. It is
2,127 B over the 20,000-byte FALSE cap, which is the only reason it was never judged. Rail 47 again: *a
proof that is over the byte cap is a finished proof, not a failed one.* Worth 3 rows (0012, 0054, and dual
12883's 0031). The harvest scan that finds these is two lines and should open every session.

**C4. Law 12087's model was FALSE, not "3 rules, validated twice".** Session 7's own
`gen/_x12087_cens3.log`, written eight minutes after the certificate it belongs to, already read
`rep4 hits=2000 BAD=649`. Reproduced this session: the 3-rule model is **2000/2000 BAD**, the 4-rule model
**649/2000**. Both minimal single-rule repairs pass exhaustive size ≤ 9, `rv.run_tests`, `deep_tests`
20k × 4 seeds *and* four census seeds — and are still false at a two-generation encoding pool. The smallest
sound set is **7 rules** (`S7`, verbatim in `gen/NOTES_12087.md`); its helper library compiles and only
`theorem law` is open. This is the fifth escalation of the validation standard.

**C5. Two tools lied about what they do.** `verify_certs.py`'s docstring claimed it "rewrites
`certs/ledger.jsonl`'s accepted set"; it writes only `verify_certs.json` and never touches the ledger, so
every re-judged row since it was written had to be appended by hand or was silently lost. Appending is now
`append_ledger.py` — append-only and idempotent, deliberately a separate script (rail 16). And `ledger.py`
read `../certs/ledger.jsonl`, a path left from when it lived in `gen/`, so it crashed on every invocation.
Both fixed.

**C6. The gate was RED at HEAD, and it blocked packaging.** Three `test_judge_verified` pins —
`etp_2923_156`, `etp_3983_4296`, `etp_3983_3800` — fail on the committed tree. Session 7's handover
attributed them to a concurrent session's *in-flight* work and told the reader not to revert it; that work
is now committed as `b73e50f order5hards`, so they fail **at HEAD**. Confirmed by stashing this session's
`solver.py` and fixture changes and re-running: 3 failed with the changes stashed, identically.

The cause is route drift, not soundness: `order5hards` added distilled routes
(`true:distilled:anchored_projection`, `true:distilled:product_constant:outer_right_free`) that now shadow
the pinned `true:completion:join` and `true:egg_ladder:*` routes, so the solver emits a different
certificate from the pinned text. Fixed the way rail 3c requires — **re-solved all three, judged the new
certificates against the real judge (3/3 `accepted`, 36.8 s / 4.8 s / 4.0 s), and re-pinned surgically**,
rewriting only those three lines. This mattered on the critical path: `package_solver.ps1` re-runs the gate
and refuses to package on failure.

`test_judge_verified.py` now reads **230 passed, 0 failed, 0 skipped** with all 56 research pins in place
(rail 16: the skip count is the number to watch, and it is zero).

## 2. The P2 mathematics — the existential decoder

Four results derived and computationally verified this session; full write-up in
`gen/P2_EXISTENTIAL_DECODER.md`. They change what the mechanism has to be, and they are worth 11 rows.

For `22591: x = (y*(y*x)) * ((x*x)*z)`, with `S(x) = x*x`, `T(x) = {y*(y*x)}`, `E(x) = S(x)*M`, the law says
exactly `A * b = x` for every `A ∈ T(x)` and every `b ∈ E(x)`.

* **R1. Every element is a square.** `y := x*x`, `z := (x*x)*x` makes the two factors equal, so `x = W*W`.
  Hence `S` is surjective, and **no carrier with recognizable, invertible squares can work** — the encode
  rule would fire on every left argument and the decode rule could never fire. That refutes a priori the
  entire family that ships 12073 and 27859, which is the family session 7 would have reached for next.
* **R2. No linear and no affine model over any abelian group, and no Z-grading.** Coefficient matching
  gives `q² = 0`, `p² + pqp = 0`, `pq² + qp² + qpq = 1`; left-multiplying the third by `q` forces `q = 0`,
  hence `0 = 1`. A proof, not a timeout — this closes the affine-over-ℚ, ℤ-piecewise-linear and graded
  families for 22591.
* **R3.** In the recorded refutation, `op(y,x) = g0` and `op(x,x) = g0` are both **genuinely forced by the
  law** (`y ∈ T(g0)`, `x ∈ E(g0)`, `x ∈ T(g0)`), so the law forces `op(J y g0, J g0 z) = x` for every `z` —
  a pair carrying the payload on neither side. Reproduced exactly.
* **R4. The quantifier is eliminable, with a closed form.** `invsq(s) := J (op s s) (J (op s s) s)` is the
  `x` with `op(x,x) = s` — verified on 8/8 targets, and `invsq(g0)` is *literally* the refutation's `x`. The
  accompanying guard reduces to a purely structural test on `a1 u`, so the whole thing is an ordinary DSL
  rule with a single `op` call on the strict subterm `a1 v`. **Termination is not the obstacle it looked
  like.**
  Honest negative: bolting that rule onto a one-rule toy makes the toy worse (507 → 951 failures over the
  197 one-generator terms of size ≤ 7). That is a statement about the toy; the real experiment is against
  `gen/q22591b.py`, and it is the assigned agent's first task.

## 2b. Seven inherited models were proved FALSE, and the validation standard rose twice more

This is the session's dominant finding and it is not about any one law. **Every model this session inherited
from session 7 and actually re-validated turned out to be false.** Seven of them:

| law | inherited state | what it actually was |
| --- | --- | --- |
| 12087 | "3 rules, validated twice" | 3-rule **2000/2000 bad**; 4-rule 649/2000; minimal sound set is **7 rules** |
| 17286 / 28626 | 7-rule model, `rec28626.lean` "1 sorry" | FALSE at a **two-generator** instance; repaired to 7 rules, re-validated |
| 38316 | `rep38316.lean`, "1 sorry away" | FALSE — 4 generators, total size 35; the validated set is `cand4`, **12 rules** |
| 40037 | "4 rules, 1-2 rare holes" | FALSE, **refuted in Lean**; no rule set in this vocabulary is a model |
| 11081 | 24-rule, minimised to 6 in session 7 and logged CLEAN | the 6-rule set is FALSE; the real model is **3 rules** |
| 10218 | `_orch_min10218.json`, 3 rules | FALSE — **73 fails in 15 s** of `rv.run_tests` |
| 32281 | 2-rule `[R1, R3]` | FALSE — one exception in **202,599** decoded pairs, found by census |

Two new requirements follow, both now in `WAVE3_PROMPT.md` W3-6 and `gen/LEMMA_LIBRARY.md`:

1. **Vary the junk variable.** Every one of these laws has an argument no rule constrains. Law 17286
   measured a size lemma at **0 violations over 420 constructed decoded pairs**, planned six proof leaves on
   it, and then refuted it: the gap is *unbounded* through that junk variable, and a pool built out of
   encodings never contains a large one. Its agent's formulation is the rule to keep — *"when I hand you a
   measured claim, treat the pool's construction as part of the claim."*
2. **For each rule, construct an instance that makes it fire at every product of the law's chain, not only
   its own.** A rule whose precondition constrains only `a1 v` (or only `u`), with `v` pinned solely by a
   recomputation guard, fires elsewhere in the chain. Law 40037's model survived `rv.run_tests`,
   `deep_tests` 20,000 x 3 **and a 1,560,896-assignment exhaustive sweep**, and is false.

And a third, from 12087: **a greedy minimisation is only as sound as the census it minimises against.** Its
agent's greedy pass against the 16-cell tree drove the 7-rule set down to a 4-rule set it had *itself proved
false* that morning. Four different oracles each rejected a set the others accepted; acceptance for that law
is the conjunction of all four.

## 2c. Three laws were the wrong track, and "near-clean" is not a class

`gen/SEMANTIC_TABLE.md` had a bucket labelled **"near-clean, 1-2 instances"**, read as "an extractor hole
that is nearly repaired". Three of its members have now been resolved and **all three are Track C identity
laws**:

* **34889** (2 semantic fails) forces *every square is idempotent* — three literal instantiations — and
  **shipped 3 rows** on the E-quotient carrier in about two hours.
* **6912** (1 fail) forces `(a*a) = ((a*a)*(a*a))` and then `(b*b) = (a*a)`: **all squares equal**
  (mechanically verified). The free term algebra is refuted over >= 2 generators.
* **39214** (1 fail) is 6912's dual and inherits all of it.

**A low semantic-failure count means the witnesses are BIG, not that the carrier is nearly right.** 6912's
two-generator witnesses need terms of size >= 9, which is why `smallcheck 6912 5 2` reads 0 fails and
`trace.py 6912 --n 400` reads "no failure found". Neither is evidence of a working model at that scale.

34889 also widens the E-quotient: 12073 and 27859 force *all squares equal and idempotent*, 34889 forces only
*squares are idempotent* — strictly weaker — and collapsing every square to one 0-ary constant `E` is still
consistent. But it is not automatic: for 6912 the E-quotient is refuted by a **forced collision**
(`op(q,t) = E => q = t` is forced, and two witnesses of its failure are forced too), and for all seven P2
laws substituting every variable by `x` gives `x = W*W`, so all-squares-equal trivialises. **Derive the
forced identity, then test the carrier. Assume neither.**

## 2d. 22591 has no model on the free term algebra — proof, not timeout

The P2 agent closed 22591's three rows to this entire construction family. With
`I1 = (a*a)*((a*a)*a)`, `I2 = a*(a*I1)`, `I3 = I1*(I1*I2)`, `Y = b*(b*I2)`, **seven substitution instances of
the law** give `a = I3`, i.e. `x = ((x*x)*((x*x)*x)) * (((x*x)*((x*x)*x)) * (x*(x*((x*x)*((x*x)*x)))))` —
size 1 against size 33, distinct free terms, **no freeness of any product assumed**, every step checked
mechanically by `gen/_p2_ident22591.py`.

It also found the criterion for why the argument does *not* transfer to 21865/21866: steps (4)–(5) need two
distinct known elements encoding the same `x`, and 22591 gets them because its encoding side `(x*x)*z` has
`z` free in the **right slot of the outer product**, making `E(x,M)` a full left-translate. 21865's is
`x*(x*z)` with `z` shared, 21866's is `x*(x*w)` with `w` nested — neither is a coset. Table in
`gen/P2_MECHANISM.md` §2.1.

The existential decoder itself is **real and eliminable** (the closed form of R4 works, and 21864's
hand-written `RA` is an independent discovery of the same move), but it was never what blocked 22591.

## 2e. The remaining set is ONE problem, and there are two working escapes

By the end of the session the 40 open rows had collapsed onto a single obstruction, reached from two
directions and named twice:

* **rail 58's infinite hierarchy** — `closedform`'s free model reads the payload off a *fixed accessor
  path*, so each extra level of nesting needs one more rule (17286: the rule reads at depth 3, **level k
  needs depth 3k+2**). Refuted this way today: 12087, 11081, 17286, 21864, 13764's first three models,
  12234's first fifteen, 9663's `q9663c` and `q9663d`, 32281's 2-rule set, 10218's, 38316's.
* **the existential decoder** — the *witness set* is not structurally definable. Law 9663's agent found
  why the "add another rule" loop cannot converge: `inimg A u` under-approximates `im(R_u)` and the proof
  needs it closed under the operation, but **every witness rule added to make the root decode enlarges
  `im(R_u)`**, because the new witnesses are subterms of the *first* argument, about which a predicate on
  `(A, u)` has no handle. Each rule breaks `IMG`; repairing `IMG` widens the decoder.
  **The fixed point of that loop is the existential decoder.**

They are the same thing. **25 of the 40 open rows depend on solving it once**: 12087 (2), 11081 (4),
17286 (4), 21864/24199 (2), 9663/36487 (3), 12294 (1), 21865 (2), 21866 (2), 22591 (3), 10222/35836 (2).

**Two escapes now exist, both validated, one shipped.**

1. **The tag carrier** (13764 — *shipped, 3 rows*; 12234 and 12087 one cell each from it).
   `M ::= g n | J a b | E a b`, the model as two or three decidable predicates instead of N rules, `op` a
   3–4 branch `if`-chain with one `let` and one recursive call, and **the structural guard replaced by a
   recursive re-run of the encoding**. 67 rules → 5; 54,402 B definition block → ~2,300 B. Choose the
   recursive call's arguments to be proper subterms of one side and **the Lean gate is unconditional** —
   measure `sz u + sz v`, no `msr`, no fuel induction, which is the 27859 shape that shipped at 9,108 B on
   the first compile.
2. **The search decoder** (17286 — validated at levels 0–3, termination not yet designed away).
   **No second constructor.** Keep `M ::= g n | J a b` and replace the fixed-depth read with a bounded
   search over candidate payloads, unwrapping proper subterms: **level k costs k unwraps instead of one
   more rule.**

The full write-up, with every design rail and the ten-rung oracle ladder, is
`stage2/experiments/austin/automata/gen/LEMMA_LIBRARY.md` — that file, not this one, is what the next
session should read first.

## 2f. Per-law state of the 40 open rows (end of session)

Ordered by distance from a certificate. Per-law detail is in `gen/NOTES_<eq>.md`; the method is in
`gen/LEMMA_LIBRARY.md`.

**One lemma set from a certificate (9 rows):**

| law | rows | state |
| --- | --- | --- |
| **17286 / 28626** | 0025, 0040, 0037, 0038 | **Everything except `theorem law` compiles** — `gen/_x17286_mut.lean`, 9,380 B, mutual `op`/`find`/`opTail` with termination, `inst`, `rhs` (both goals refute), `findN`/`findOK`, `SND`, `TOPU`, `lhs`, `submission`. ~10.6 KB left. Remaining: `F1`, `F2`, the A-decoded converse. Five carriers, three refuted; the current one is the first to survive a check it did not itself motivate. |
| **38316** | 0055, 0065 | `cand4` validated to every standard incl. the level-3 descent. Two files compile, differ only in `rhs`, each verified against its own dev dir. 15,757 B, ~7 KB left. `law` cases on 16 combinations, 6 reachable — the ~9 impossible ones are the expensive half. |
| **32281** | 0006, 0032, 0068 | `gen/w135d.lean` 17,782 B compiles, `TOP` (the whole decoded case) proved; 4 sorries, bottleneck is `SFa`'s Q-decoded residue. Junk check and a per-rule x per-product census both passed. |
| **23357 / 23653** | 0048, 0080 | **New 4-rule model, fully validated** (the inherited 6-rule set was FALSE and had never been validated by anything). `gen/_w3_23357_cert4.lean` 11,095 B compiles, one sorry. Next lemma `CHAIN2B` has a 44,202-triple census behind it. Architecture ported from law 23354, which is its **left half** and shipped today. |

**A validated model, no Lean yet (1 row):**

| law | rows | state |
| --- | --- | --- |
| 8485 | 0096 | Model survived the full validator; `gen/f8485q.lean` 8,611 B compiles, digest and all-free cell proved. Needs re-forcing (it was minimised) then `op_R2` + `SZOP`. |

**Model search in progress, converging (5 rows):**

| law | rows | state |
| --- | --- | --- |
| 9663 / 36487 (+ 12294) | 0018, 0051, 0098, 0093 | Four-constructor carrier: **50,560 -> 632 L1 failures from one character** (`TAGF` must fire on `J`-products too). Fast harness 1468 -> 1197. Two H3 cells left, each a one-line reading. Carrier transfers to 12294. Forces **no identity**, so the carrier is plain free terms plus tags. |
| 10218 | 0079 | 6-rule minimised model **FALSE** (`_orch_minim`'s bulk drop is unsound); a correct subset exists since the full 140-rule set is correct on the instance. Repair at 135 -> 27. `gen/p10218.lean` compiles with `ROOT` proved and re-emits with at most `P_k` index changes. |

**Closed by proof — the free carrier is refuted (13 rows):**

| law | rows | what was proved |
| --- | --- | --- |
| 22591 | 0017, 0052, 0069 | `a = I3(a)` in seven substitution instances, no freeness assumed — **no model on the free term algebra at all** |
| 11081 / 35036 | 0003, 0030, 0073, 0074 | No rule set over a free term algebra, **whether its decode projects, reconstructs, or is certified by recomputation**. Eight carriers, twenty-two rule sets. Best model v20 at **76 / 431,232** with the anchor built and measured (killer 2,400 -> 400) |
| 12234 | 0061 | The open cell is **not closable by another rule on this carrier** — structural proof, four failure positions, K19-K23 all H3-clean |
| 12087 | 0024, 0097 | **Mark narrowly ⇒ the root reading is unanchored ⇒ it forges; mark broadly ⇒ the free cells break.** Eleven iterations; every finite extractor rule set separately proved false |
| 21864 / 24199 | 0033, 0086 | The recursive `codes` finds **nothing** the non-recursive one did — the witness was destroyed by the very decode being certified. **A search decoder moves the existential decoder into the certificate; it does not remove it** |

**Blocked, with the obstruction named (12 rows):**

| law | rows | state |
| --- | --- | --- |
| 21865, 21866 | 0039, 0057, 0020, 0028 | Track C; 22591's argument does not transfer and the **coset criterion** says why. No generator merges in an e-graph over two generators, so no evidence of triviality either |
| 6912 / 39214 | 0049, 0091, 0026 | **All squares equal and idempotent** (mechanically verified) refutes the free algebra over >= 2 generators; the E-quotient is refuted by a **forced collision**. Open: a triviality proof would make all three rows TRUE |
| 10222 / 35836 | 0005, 0095 | Forced identity known, tag must be **unary**; needs the quotient **and** the decoder |
| 36524 | 0063 | The full 97-rule extraction is not a model, so no subset is — a repair task. The older 17-rule set passes a 1.5M census but that is the evidence class that just failed for 10218 |
| 40037 | 0078 | 4-rule model refuted **in Lean**; forces no identity either (positive-controlled saturation), so no quotient. Needs a new reading or a non-free carrier |
| 13764-family leftovers | — | none; all three rows shipped |

## 3. The single most important number in this file

**Seven models this session passed roughly 10^6 validation chains and were false.** Eleven were falsified
in total. Every one of them would have cost an agent-session of Lean work, and **not one false certificate
reached the judge** — every shipped row was re-judged independently by the orchestrator.

That is why `gen/LEMMA_LIBRARY.md` is now ~93 KB and why its **twelve-rung oracle ladder** is the first
thing to read. Each rung was forced by a model that passed the previous one:

1. `rv.run_tests` · 2. `deep_tests` 20k x 3 · 3. the case tree · 4. the both-decoded census ·
5. `identity_probe` · 6. **the level-k descent, both variants, cell census printed** · 7. **vary the junk
variable** · 8. **forced firing** · 9. **H3** (~1,100x kill power per chain) · 10. **per-branch,
per-construction firing counts** · 11. **the forcing suite's own positive control** · 12. **every
construction ported from the previous carrier's oracle**.

Two things that are *not* evidence: `_orch_minim.py`'s `status: "ok"` — its keep-set is "rules that fire
under the fuzz battery", so its bulk drop is **unsound**, and it produced a model that passed rungs 1-5 and
10 — and any count printed by a counter placed before the loop that fills it.

## 3b. Where to start next session — in order

**Read `gen/LEMMA_LIBRARY.md` first, not this file.** It is ~93 KB, has a table of contents keyed to what
you are doing, and opens with the twelve-rung oracle ladder. This file has the score and the per-law state;
that one has the method.

1. **The harvest scan** (rail 47), 30 minutes, no agents: every `gen/*.lean` with zero `sorry`s, byte count,
   banned-token grep. It shipped three rows in fifteen minutes this session from a file the previous
   handover had written off. **Then compile them** — `gen/hole23357.lean` has zero sorries and is a
   *refutation*, so zero sorries means "nothing left to prove in this file", not "this file proves the law".
2. **The four laws whose certificate is one lemma set away** — 17286/28626 (4 rows), 38316 (2), 32281 (3),
   23357/23653 (2). **11 rows, no research required.** Each has a compiling file and a named list of
   remaining lemmas in its `gen/NOTES_<eq>.md`. This is the cheapest work on the board and it should be
   done before anything else.
3. **The anchored carrier** — the shared target, worth ~25 rows. Its first measurement is in: **the image
   of `op` is 4.1% of the term algebra**, so the restriction is real; but **9663's open-cell witness is
   itself op-built**, so "restrict to the image" is not sufficient alone. The question that was running
   when the session ended is the one to resume: *do rules rejected on the free carrier become admissible on
   the image?* Every impossibility proved this session quantifies over rule sets **on a free term algebra**
   and must be re-checked against the image before it is assumed to carry over.
4. **9663 is the best test case for it** — one cell wide on an otherwise clean four-rule model with
   unconditional gates, a 40-second harness, and a non-vacuous forcing suite.

### Agent doctrine, revised by this session

Session 7's rules stand (waves of 6-8, write findings as you go, do the shared step before the fan-out,
judge in parallel, re-judge everything). Four additions, each measured here:

* **Resume agents rather than spawning new ones.** Twelve agents were resumed 2-6 times each; every one
  carried its context forward and several produced their best result on the fourth round. Nothing was lost
  to a resume.
* **Send findings between agents.** Nearly every rail in the library was found by one agent and used by
  another within the hour — `mxl`, `Z`/`Y`/`ZP`, the level-k descent, H3, the forcing-suite positive
  control. The orchestrator's main job was routing.
* **Ask an agent to state what it does NOT have.** The most valuable reports were retractions:
  *"my measured claim was worthless — the pool could not build the shape"*, *"this is the fourth round I
  have been asked to finish and have not; F1 and the converse are independent, give them to another
  agent"*. Both changed what was done next.
* **Kill your own orphans, not your neighbours'.** Rail 15: stopping ten agents left ten orphaned worker
  processes; a peer session's 100k audit was running in the same tree. Identify by command line before
  killing (`Get-CimInstance Win32_Process -Filter "Name like 'python%'"`).

## 4. New tooling

| file | what |
| --- | --- |
| `WAVE3_PROMPT.md` | the wave-3 delta: harvest first, write as you go, decide the track before proving, minimise before proving, the byte tools, the validation standard |
| `gen/P2_EXISTENTIAL_DECODER.md` | R1–R4 above, and the experiment to run |
| `append_ledger.py` | append accepted rows to `certs/ledger.jsonl`; append-only, idempotent |
| `splice_certs.py` | splice `certs/ship_certs.py` into `DISTILLED_CERTS` and rewrite only the research pins of the fixture; `--out` for a dry run |
| `stage2/tests/test_artifact.py` | now iterates the minifier's own `PACKED_TABLES`, so a newly packed table cannot escape the round-trip check, and pins that `PROMPT` is never packed |

## 5. Shipping

1. `verify_certs.py --workers 4` — re-judge everything; an agent's claim is not evidence.
2. `append_ledger.py` — append the accepted rows to the ledger.
3. `ship.py` — regenerate `certs/ship_certs.py` and `certs/ship_fixture.jsonl`.
4. `splice_certs.py` — into `DISTILLED_CERTS` and the fixture.
5. `package_solver.ps1` **on an idle box** — kill every agent first and confirm `Get-Process python*` is
   empty (rail 22; a loaded box produced four spurious gate failures in session 7).
6. `spotcheck.py`, then commit.
