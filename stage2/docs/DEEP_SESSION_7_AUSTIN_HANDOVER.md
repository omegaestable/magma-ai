# Deep session 7 → 8 — the Austin research set, 46 → 100 (handover)

> **Superseded in five places by `DEEP_SESSION_8_AUSTIN_HANDOVER.md` (2026-08-29). Read that file's §1
> before acting on this one.** In short: the byte budget here (423,307 B / 76.7 KB headroom) is wrong —
> HEAD measures 459,379 B; law **33020 already has a complete zero-sorry proof on disk**, 2,127 B over the
> cap, worth 3 rows; law **12087's "3 rules, validated twice" is FALSE** (2000/2000 bad — the smallest
> sound set is 7 rules); `verify_certs.py` does **not** write the ledger despite its docstring; and the P2
> existential decoder now has a **closed form**, so it is not the open-ended research problem §1 describes.
> Law 27859 (P1) is shipped: 48/100.

Written 2026-08-29, late. Read `CLAUDE.md` first, then this file. The previous handover
(`DEEP_SESSION_6_AUSTIN_HANDOVER.md`) is still the reference for the *construction* and for the per-law
history; its "Session 7" section records what changed. **This file is the plan.**

## The goal

**All 100 rows of `data/hf_cache/research_order5_hard.jsonl` judge-accepted and shipped as
`false:distilled:aus_e*`.** 46 are. 54 remain, in 25 groups up to duality.

100/100 is reachable this session. It is not reachable by spawning 25 agents and hoping — that was tried,
and the arithmetic of why it failed is in §3. It is reachable because **the 54 rows are only four problems**,
one of which is pure Lean labour, two of which are nearly mechanical, and one of which is a single piece of
mathematics worth 11 rows.

---

## 1. The four problems, and nothing else

| # | problem | rows | what it actually needs | parallel? |
| --- | --- | --- | --- | --- |
| **P1** | **Write `theorem law`** on a model that is already validated and whose Lean skeleton already compiles | **18** | Lean labour with a compiled playbook. No research. | yes, perfectly — one agent per law |
| **P2** | **The existential decoder** — one missing inference, blocking five laws | **11** | one person's mathematics, then one rule form | **no** — do not fan this out |
| **P3** | **Re-extract with `gen/closedform2.py`**, whose bug fix is exactly these laws' failure | **9** | mechanical: re-extract, case-tree validate, prove | yes, after one shared re-extraction pass |
| **P4** | The remainder — gate-cut laws, huge rule sets, the byte wall | **16** | case by case; two have measured stop conditions | partly |

### P1 — 18 rows that need only a Lean proof (do these first, they are certain)

| law | rows | model | skeleton | note |
| --- | --- | --- | --- | --- |
| 27859 | 0050, 0099 | `gen/q27859.py` | `gen/qlean27859.lean` 3,302 B | **start here.** 4 branches, 3 nested calls; DEC and SELF both return `a2 u`, so `law` is a 2-leaf case split |
| 12073 | 0007, 0022 | `gen/q12073e.py` | `gen/qlean12073.lean`, or `gen/nf12073.lean` (3,153 B), or `gen/qz12073_skel.lean` (2,259 B) | three independent validated carriers; pick by proof cost |
| 12087 | 0024, 0097 | 3 rules, validated twice | regenerate from the 3-rule set | smallest open free model |
| 23354 | 0027 | 3 rules, validated twice | `gen/rec23354.lean`, 4 sorries | blocked on `core_no_fix (x) : a1 x ≠ op (a2 x) x`, strong induction on `sz x` |
| 12234 | 0061 | needs re-validation | `gen/rec12234.lean`, 8 sorries, 26,873 B | also 6.9 KB over the cap when proved — budget from the start |
| 38316 | 0055, 0065 | 10-rule repair | `gen/rep38316.lean`, 1 sorry | re-validate to the case-tree standard first |
| 17286/28626 | 0025, 0037, 0038, 0040 | 10 rules | `gen/rec28626.lean`, 1 sorry | four rows from one proof — the largest single win on the board |
| 11081/35036 | 0003, 0030, 0073, 0074 | 24 rules, validated both orientations | `gen/rec11081.lean` | four rows; **must** use PLAYBOOK_PROOF §3, see the byte note below |

12073 and 27859 are new this session: `gen/PLAYBOOK_QUOTIENT.md` has their carriers, the theorem behind
them, and the proof plans. Both models were re-run by the orchestrator — 302,500 exhaustive one-generator
assignments each, 0 failures.

### P2 — the existential decoder: 11 rows, one mechanism

Blocks **21865 (2), 21866 (2), 22591 (3), 23357/23653 (2), 21864/24199 (2)**.

Two design agents identified it independently, from opposite directions, and the refutations are proofs,
not guesses (`gen/PLAYBOOK_QUOTIENT.md` §4). The shape of the obstruction:

> a term is simultaneously a legal A-term and a legal B-term of the law, so two instances of the law demand
> **different values of the same product `(u,v)`**. A rule is a function of `(u,v)`, so no additional rule
> can separate them. Recovering the payload needs an inference that quantifies over a **forgotten witness**
> rather than reading it out of the term.

The concrete witness, from `gen/q22591b.py` — a model that survives 1,061,208 exhaustive assignments at
size ≤ 7 and 5,722,200 with `y ≤ 9`:

```
22591:  x = ((g0◇g0)◇((g0◇g0)◇g0)),  y = (g0◇(g0◇g0)),  any z
        ->  got (((g0◇(g0◇g0))◇g0)◇(g0◇z)),  want x
        because op(y,x) = g0 and op(x,x) = g0 are BOTH forced readings
```

**Treat this as the session's research problem and give it one agent, not five.** Fanning it out produces
five per-law hacks; it wants one general mechanism. The two forms already named as worth building:

* a **bounded inverse rule** — when the payload has been destroyed on both sides, quantify over the
  bounded set of witnesses that could have produced the observed pair, and require uniqueness;
* a rule with a **negative constraint** ("this pair is NOT a reading"), which the DSL cannot currently
  express. 6912 and 8485's gate-cut families want the same thing, so it may be worth 14 rows, not 11.

Stop condition: if after a serious attempt the mechanism does not exist, the deliverable is the written
argument for why — the three square-collapse refutations in `PLAYBOOK_QUOTIENT.md` §4 are the model for
what that looks like.

### P3 — 9 rows the extractor bug already explains

**32281 (3), 33020/12883 (3), 34889 (3).** All three have a *clean semantic model* (0, 0, 2 failures) and a
*badly broken extracted rule set* (134, a wholly false skeleton, 192). `gen/EXTRACTOR_NOTES.md` found why:
`closedform.decoder_expr` / `decoder_of` hardcoded the decoder variable as the literal name `y`, and for
these three dualised laws it is `z`, so every lazy-decode rule read the wrong subterm.

**One shared step first, then fan out:** re-extract all three with `gen/closedform2.py`, validate to the
case-tree standard, and only then assign one proof agent per law. Do not assign three agents to rediscover
the same fix.

### P4 — the remainder, 16 rows

| law | rows | state |
| --- | --- | --- |
| 9663/36487 | 3 | **identity law** (23 semantic failures), not the repair task the old handover describes. Needs P2 or a carrier |
| 10222/35836 | 2 | identity law (45 failures each orientation) |
| 12294 | 1 | identity law (22 failures) |
| 13764/32294 | 3 | 67 rules. **Definition block alone is 54,402 B — 2.7× the cap.** Minimise below ~20 rules or the law is unreachable; say so with the arithmetic if it is |
| 6912/39214 | 3 | gate-cut; wants P2's negative constraint, or the lexicographic gate (`closedform.GATE = 'lex'`) |
| 8485 | 1 | gate-cut, semantic model clean |
| 10218 | 1 | semantic clean, 140 rules → 63 with `closedform2`; then minimise and prove |
| 36524 | 1 | 97 rules → 60/78 with `closedform2` |
| 40037 | 1 | 4 rules, 1–2 rare holes. Small and nearly right |

---

## 2. The mathematics, polished — five techniques, each with its evidence

These are the techniques that have actually produced accepted certificates. Use them in this order.

**(i) Decide the track by an exhaustive check, before touching anything.**
`smallcheck.py <eq> 9 1` evaluates the law on all 12,167 one-generator assignments in the *semantic* free
model; `--closed` does the same in the *extracted* rule system. Semantic clean + extracted broken ⇒ the
extractor is incomplete and the fix is generic. Semantic broken ⇒ no rule set can help, the carrier must
change. Costs 2–30 s. `gen/SEMANTIC_TABLE.md` has it for every open law. Skipping this misassigned 15 rows
in the previous handover.

**(ii) Find the law's forced identities by hand, then build the carrier on them.**
The 12073 breakthrough was not a search — it was three substitutions. With `S_z = z◇z`,
`psi_y(x) = (y◇x)◇x`, `E(y,z) = psi_y(y)◇S_z`: `x := y` gives `psi_y(E) = y`, so `E` is independent of `z`;
instantiating `y` at a square forces `y◇y = y`; and `L[y := a◇a, x := b◇b]` gives `b◇b = a◇a`. **All squares
are equal and idempotent.** Once that constant is a *constructor*, the offending variable disappears
definitionally — no quotient type, no `Quot.sound`. Ask what identities the law forces before asking what
model to build.

**(iii) The tag must be nullary.** An argument-carrying tag `K y` was built and **measured to cascade**
(holes at `Q^3 u`, then `Q^4 u`, …). A 0-ary constructor cannot grow, is never itself decoded, and is what
makes the well-founded measure go through.

**(iv) Collapse the rule set with a digest, never rule-by-rule.** PLAYBOOK_PROOF §3. `split` fails with
"maximum number of steps exceeded" past about ten rules and there is **no option to raise it**, so for the
heavy laws the digest is not an optimisation, it is the only route. `TRpre` (2 lines) + `Pdig` (generated by
a five-line loop, never counted by hand) + `Wdig` took a 24-rule model to **1,913 bytes**. `gen/_pb_common.py`
computes the digest precondition; the rule preconditions have *no* conjunct common to all rules on the
heaviest laws, so the near-common split is the thing to compute, not guess.

**(v) Prove one general invariant instead of a chain of special cases.** 24200 was shipped by proving
`FREE (a b) : op (op a b) b = J (op a b) b` in general rather than the "T2 and T4 are free" the handover
asked for along the chain. 38565 fell to `FREE2 (a b) : op a (op b a) = J a (op b a)` — one lemma that
collapsed a 16-cell case tree to 4. 5012 used a single `NOFIRE` invariant. **When a law's chain has a
repeated variable, look for the freeness lemma before writing any case analysis.**

### And the validation bar, which has now risen four times

3,000 random → `rv.run_tests` → 20k deep on three seeds → **the case tree**. Each escalation was forced by a
model that passed the previous one. Law 38565 passed `revalidate.py`, 126 hand-built coincidence instances,
9 seeds of `run_tests` and 13 × 20,000 deep tests — and was FALSE. The hole was a cell where two specific
chain products are both decoded, which occurs **0 times in 30,000 random draws**.

> **Standard.** Before any proof work: enumerate the `2^k` free/decoded combinations of the `k` products in
> the law's evaluation chain, and construct one instance per reachable cell by chained encoding — to force
> `op(a,b)` to decode, set `b` to the free encoding of the law's RHS with `y := a`, and nest for a second.
> `gen/_x38565_dd.py` is the worked example. Add `qz_lib.identity_probe` (build `x` from the model's own
> codes, three levels) — it killed four carriers that had passed 4M exhaustive assignments, in 0.1 s.

A sampler cannot find a cell of measure zero. Only construction can.

---

## 3. Agent doctrine — read this before spawning anything

Session 7 spawned 36 agents. **Three finished.** Not because they were bad — the three that finished shipped
three laws on the first or second judge call — but because `fable` exhausted its credits mid-run (16 agents
killed at once) and then the session limit killed 22 more. Everything those 22 had discovered was lost,
because they were built to report at the end.

**The rules that follow from that, in order of how much they cost:**

1. **Waves of 6–8, never 25.** Read the results between waves. A wave costs roughly an hour of wall clock
   and a law per agent; a session's budget is not 36 agents.
2. **Every agent writes its findings to `gen/` as it goes**, not only in its final report. Make this an
   explicit instruction. An agent killed at 80% should leave 80% behind.
3. **Do not set `model: 'fable'`.** The session model works — the three completed laws (24200, 5837, 38565)
   were all on it, 3 for 3.
4. **Never assign a law whose track you have not decided** (technique (i)). Session 7 sent an agent to
   "repair" 9663, which is an identity law; that agent could not have succeeded.
5. **One shared file, one owner.** The extractor agent owned `gen/closedform2.py` as a private copy and
   produced a fix that serves nine rows; had three law agents each edited `closedform.py`, all three would
   have lost.
6. **Do the shared step before the fan-out.** P3's re-extraction and P2's mechanism are single pieces of
   work whose output every downstream agent needs.
7. **Judge in parallel — it is safe now.** `jlock.py` pins `JUDGE_LEAN_PATH` (no `lake env` subprocess) and
   caps concurrent judges at `JUDGE_SLOTS`, default 5. Measured: two simultaneous certificates, 12.6 s and
   12.4 s, both accepted.
8. **Re-judge everything the agents claim.** `verify_certs.py` does the whole `certs/` directory. An agent's
   assertion of acceptance is not evidence; the judge is.

### The suggested wave order

* **Wave 0 (no agents, 30 minutes, yourself):** the harvest scan — every `gen/*.lean` with zero `sorry`s,
  with byte count and a banned-token grep. It produced three shipped rows in fifteen minutes this session
  from a file the handover had written off as "unshippable". Then re-extract P3's three laws with
  `closedform2`.
* **Wave 1 (7 agents):** P1's certain rows — 27859, 12073, 12087, 23354, 17286/28626, 11081/35036, 38316.
  That is 15 rows if they all land, and they are proof work with a compiled playbook.
* **Wave 2 (1 agent + 4):** the existential decoder as a single research agent, alongside P3's three proof
  agents and 40037.
* **Wave 3:** whatever P2 unlocked, plus P4's remainder, plus 12234 and 13764's byte problem.

---

## 4. Byte budget — solved, with room, and one law still over

`minify_submission.py` packs with **lzma (preset 9|EXTREME)** since this session, not zlib: the certificate
table is ~600 KB of Lean whose entries share a long preamble, and zlib's 32 KB window cannot see across two
19 KB certificates. Measured on the 46-entry table: **112,379 B → 50,155 B**. The artifact built from HEAD
plus all 46 certificates is **423,307 B — 76.7 KB headroom**, smaller than before nine certificates were
added. Verified: it imports and all 46 round-trip byte-exact.

So the cap is not binding on the *table*. It is still binding on *individual certificates* (20,000 B each):

* **13764/32294**: definition block alone 54,402 B. Unreachable without minimising to ~20 rules.
* **11081/35036**: definition block 16,723 B (14,371 squeezed) — 84% of the cap with zero proof written.
  The digest of technique (iv) is ~1,900 B, which fits; a per-rule lemma set does not.
* **12234**: 26,873 B with 8 sorries still open.

Cost is 530–780 B per rule on top of 2,171 B of fixed boilerplate. **Minimise before you prove, always.**

---

## 5. Measured dead — do not re-run any of these

Everything in `DEEP_SESSION_6_AUSTIN_HANDOVER.md` § "Not on any track", plus, from session 7:

* **Cross-model transplant.** All 74 stored models and their opposites against all 40 open hypotheses —
  2,960 tests, 3 minutes, `xtrans.py`. **No row that duality did not already cover.** The free-model
  construction is genuinely law-specific; per-law work is not avoidable by search.
* **`--values` restriction in `smallcheck`.** The one-generator pool of size ≤ 9 has 23 terms and all of
  them are values. It changes nothing at this size.
* **Capping `cap2` / `level2` to fix the `revalidate.py` timeouts.** Extraction is 0.2–0.3 s at any `cap2`;
  the cost is the validator, quadratic in rule count. With `closedform2`'s subsumption the rule count stops
  depending on `cap2` at all.
* **An argument-carrying tag `K y` for the identity laws.** Measured to cascade without end.
* **Square collapse for 21865, 21866, 22591.** Proved impossible three ways — see `PLAYBOOK_QUOTIENT.md` §4.
* **A fourth carrier for 12073.** Three independent designs already converged and all three validate.
* **A proof generator emitting `law` mechanically.** Two agents attempted it; both died on credits, and
  PLAYBOOK_PROOF §3 delivered most of the value anyway. Only worth revisiting if P1 turns out slower than
  one law per agent-hour.

---

## 6. Reference — the files this session produced

| file | what |
| --- | --- |
| `gen/PLAYBOOK_PROOF.md` | the Lean method, 27 compiled snippets; **§3 is the lever for heavy laws** |
| `gen/PLAYBOOK_REPAIR.md` | the repair method, self-validated on law 9667 |
| `gen/PLAYBOOK_QUOTIENT.md` | the identity laws: the theorem, three carriers, the three refutations |
| `gen/EXTRACTOR_NOTES.md` + `gen/closedform2.py` | the hardcoded-`y` bug and subsumption pruning |
| `gen/SEMANTIC_TABLE.md` | semantic vs extracted failures for every open law, and its track |
| `gen/IDENTITY_INSTANCES.md` | smallest failing instances of every semantically-broken law |
| `jlock.py` | safe parallel judging |
| `verify_certs.py` | re-judge every `certs/*.lean` |
| `xtrans.py` | the cross-model screen (negative, see §5) |
| `gen/_orch_minim.py` | extract → minimise → full-validate for huge rule sets |
| `gen/_pb_common.py`, `gen/_pb_gencases.py` | digest precondition; `op_cases` generator |
| `gen/_x38565_dd.py` | the case-tree instance constructor |

## 7. Shipping, when the rows are in

1. `verify_certs.py --workers 4` — re-judge everything; an agent's claim is not evidence.
2. Append the verified rows to `certs/ledger.jsonl`, then `ship.py`.
3. Splice `certs/ship_certs.py` into `DISTILLED_CERTS` (drop the old `aus_e*` lines first) and replace the
   research fixture lines with `certs/ship_fixture.jsonl`.
4. `package_solver.ps1` **on an idle box** — kill every background job first and confirm
   `Get-Process python*` is empty (rail 22; a loaded box produced four spurious gate failures this session).
5. Spotcheck, then commit.

**One warning from this session.** A concurrent Claude session was editing `stage2/solver/solver.py` — 609
lines of anchored-projection routes appeared mid-session, and three `test_judge_verified` pins
(`etp_2923_156`, `etp_3983_3800`, `etp_3983_4296`) fail in the working tree while passing at HEAD. They
belong to that work, not to the Austin certificates. **Check `git status` for a foreign diff before blaming
the gate**, and do not revert someone else's in-flight work to make your own gate green.
