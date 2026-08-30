# Session 9 — Austin research set: infrastructure recovery + the 8485 falsification

2026-08-30. Read `CLAUDE.md`, then `stage2/experiments/austin/automata/gen/LEMMA_LIBRARY.md`
(now ~99 KB; **its last section is this session's**), then this file.

**Score unchanged: 60 / 100.** No new row shipped. This session's value is elsewhere and is
real: two blockers that would have silently wasted the next session were found and fixed, one
inherited model was proved false, and the harvest question was closed decisively.

---

## 1. What was actually wrong when the session started

### 1a. `vendor/stage2-official/.artifacts/` had been DELETED

The entire dev-compile loop was gone — every `dev_<eq1>_<eq2>` directory and the `dev5107/leanpath.txt`
that `jlock.py` and `devrow.py` both read. Nothing reports this as a missing prerequisite; it surfaces
as unrelated-looking failures much later.

Rebuilt, and the recipe is worth keeping because `lake env` is slow and load-sensitive:

```python
import sys; sys.path.insert(0,'vendor/stage2-official')
from judge import verify
lp = verify._get_lake_lean_path(verify.JudgeConfig())      # 963 chars
open('vendor/stage2-official/.artifacts/dev5107/leanpath.txt','w').write(lp)
```

Then `devrow.py <eq1> <eq2>` per row (they parallelise; 11 built in one wait). **19 dev dirs are now
on disk**, covering every row the near-certificate work needs.

### 1b. The judge could not find `lean`, and reported it as a broken certificate

`verify_certs.py` returned **`infra_error`** on `research_order5_hard_0001` — a certificate the
ledger records as accepted. Root cause: `jlock.judge_env()` pinned `JUDGE_LEAN_PATH` but never
prepended `~/.elan/bin` to `PATH`, so the judge raised
`JudgeInfrastructureError: missing lean binary: lean`, and `verify_certs.py` **swallowed the
subprocess output**, collapsing it to a status word indistinguishable from a real rejection.

It was latent through all of session 8 because an interactive shell had already exported elan; any
runner launched from anywhere else (an agent, a background task, a fresh shell) had not.

Fixed at the **shared choke point** — `jlock.judge_env()` now prepends elan's bin — rather than in
each caller, because every Austin runner goes through it (rail 3b-iv: *fix every harness that talks to
the same library, at the one place they share*). `verify_certs.py` now also carries the judge's own
`error_code` (or its stderr) into the result and prints it under any non-accepted row.

Verified from a **deliberately stripped PATH**: `--only <two rows> --workers 2` → **2/2 accepted**,
2.6 s and 4.2 s. Judging in parallel works.

> **The general lesson, and it is the session's most portable one:** an environment failure that is
> reported through the same channel as a result failure will be read as a result failure. `infra_error`
> sitting in the same field as `incorrect` cost real debugging time. Anywhere a harness reports "the
> thing failed", check that it can distinguish *the thing was wrong* from *the thing never ran*.

---

## 2. The harvest scan (rail 47) — closed, no free wins

Two-line scan over all **274** `gen/*.lean`: 106 have zero `sorry`s **and** a `def submission`, 64 of
those are under the 20,000-byte FALSE cap. **None of them serves an open row.** The zero-sorry files
that match an open law (`_x12087_proof.lean`, `_w3_23357_body*.lean`, `_x40037_body.lean`) are helper
fragments with no `submission`, and `gen/hole23357.lean` is a **refutation**, as `LEMMA_LIBRARY.md`
already warns.

Session 8 got three rows in fifteen minutes from this scan. This session got zero. **Run it anyway —
it is 30 seconds and it is how you learn which of the two situations you are in.**

---

## 3. Law 8485 is FALSE, and it is a sixth law naming the shared obstruction

Row 0096 was the handover's only *"a validated model, no Lean yet"* entry. It is not a Lean task.
The re-forcing check the agent was instructed to run first killed the model.

**That is now eight of eight** inherited models that failed re-validation across sessions 8 and 9.
Session 8's rule stands and should be treated as a law of this project: **re-validate every model you
inherit, before writing a line of Lean.**

The mechanism is the important part, because it is a **necessity** argument, not another counterexample:

> A rule is a predicate of `(u,v)` alone. R2 was added so the **top** pair decodes, where a conjunct
> guarantees the locator `z = a2 (a2 x)`. It therefore also fires at the inner `P` pair, where nothing
> guarantees it. A constructed fixed point collapses the chain so `sz x = 13 < 33 = sz z` and **`z`
> does not occur in `x` at all**.
>
> **"The rule that closes the P-decoded-by-R1 cell is exactly the rule that manufactures the bad
> decode at the P pair — necessary and fatal."**

No subset escape: **all 11 rule sets on file fall** (83-rule `FULL(noexist)`: 24/24); the only one
surviving the attack, `FULL(exist)` at 102 rules, fails `smallcheck` exh9/1 with **25 fails in 301
assignments**; and *removing* the rule breaks exh9/1 within 4,000 assignments.

Confirmed four independent ways including **Lean's own `#eval` on the shipped `def op`**.

This is the **second independent derivation** of the non-convergence fixed point — 9663's
`inimg`/`IMG` argument is the first, and it comes from the opposite direction. Two independent
derivations is the reason to treat the obstruction as structural rather than as one carrier's artifact.

**Row 0096 moves to the carrier track.** The escape count is now ~26 rows, not ~25.
Full write-up: `gen/NOTES_8485.md` (STOP banner at the top), tooling `gen/_z8485_*`.

### Rung 13 of the oracle ladder, forced by this

Six oracles missed it. The samplers missed it for a known reason (rail 50 — the witness needs
`sz x = 13` **and** a `z` of `sz 33` *that is a function of `x`*: a measure-zero fibre; exh7/2 ran
**1,061,208** assignments with 0 failures).

The **forcing suite** missed it for a worse reason: all **97,000** of its constructed instances build
`x` through `enc(u,w,j)`, whose last step is free, so the locator held **by construction**. *The suite
could not express the case it existed to test*, and reported clean.

> **Rung 13: show that your constructions can BUILD a witness of the shape the rule is supposed to be
> wrong on.** For a decode rule, build an instance where **the payload is not reachable from the first
> argument at all**. Rung 11 asks whether rule *k* fired; rung 13 asks whether the suite can even
> phrase the failure.

Two operational notes now in the library: **`by decide` cannot reduce a well-founded `op`** (the
kernel will not unfold it — use `#eval`; `gen/_z8485_diag2.lean` is the standing demonstration), and
**transcribe the Lean definition into Python and differential-test it** before trusting a Python
oracle about a Lean model (`gen/_z8485_lean.py`: 23,600 pairs vs `closedform.Closed`, 0 disagreements).

---

## 4. Where the near-certificate work stands — START HERE NEXT SESSION

Seven agents were in flight when the session ended; **their working files are on disk**, listed below
with the state measured at cut-off. Compile each before trusting it (`SESSION9_ENV.md` has the loop).
`bytes` is against a hard 20,000-byte cap.

| law | rows | file at cut-off | bytes | sorries |
| --- | --- | --- | --- | --- |
| **23357 / 23653** | 0048, 0080 | ~~`_w3_23357_cert4.lean`~~ **REFUTED MODEL, see §11** → use `gen/_x23357_cert.lean` | 12,808 | 1 |
| **38316** | 0055, 0065 | `gen/q38316.lean` (agent's) / `gen/w38316.lean` (base) | 18,593 / 16,200 | 6 / 1 |
| **17286 / 28626** | 0025, 0040, 0037, 0038 | `gen/_x17286_mut.lean` | 12,659 | 4 |
| **32281** | 0006, 0032, 0068 | `gen/w135_C.lean`, `w135e.lean`, `w135d.lean` (base) | 19,625 / 18,628 / 19,874 | 8 / 10 / 10 |

**Read this table carefully: in three of four cases the agent's in-progress file has MORE sorries and
MORE bytes than the base file it started from.** That is normal mid-restructure — a case analysis is
expanded before it is discharged — but it means **the base files are the known-good starting points**,
not the agent files. Verify both before choosing.

The four base files each compile `exit=0` today with only `sorry` warnings. Confirmed this session:

* `w38316.lean` — 16,200 B, **1 sorry**, `theorem law`, 1 s compile. 3,800 B headroom.
* ~~`_w3_23357_cert4.lean` — 11,262 B, 1 sorry.~~ **ITS MODEL IS FALSE — line 1 of the file says
  "REFUTED MODEL … DO NOT SHIP". See §11.** The replacement is `gen/_x23357_cert.lean` (12,808 B, 1 sorry).
* `_x17286_mut.lean` — 10,141 B, **2 sorries**, 1 s. 9,859 B headroom.
* `w135d.lean` — 19,874 B, 5 sorries, 2 s. **126 B headroom — the binding constraint here is bytes,
  not mathematics.** Apply `Z`/`Y`/`ZP`/`mx`/`mxl` before proving anything.

In `w38316.lean` the single remaining `sorry` **is `theorem law` itself** — all scaffolding, `inst`,
`rhs` and `submission` already compile. **`_w3_23357_cert4.lean` looked identical and its model is
false (§11)** — which is the whole lesson: that shape is necessary for a cheap row, not sufficient.

### Also in flight
* **9663 / 36487 / 12294** (4 rows) — two H3 cells left, each "a one-line reading"; diagnostics at
  `gen/_s9_9663_diag.py`.
* **10218** (1 row) — reassigned mid-session to the agent that falsified 8485, because it is the same
  skill: the 6-rule minimised set is known FALSE, but the **full 140-rule set is correct on the
  instance**, so a sound subset is known to exist. `gen/p10218.lean` compiles with `ROOT` proved.
* **The anchored carrier** (~26 rows) — resumes session 8's cut-off question: *do rules rejected on
  the free carrier become admissible on the image of `op`?* This matters because **every session-8
  impossibility proof quantifies over rule sets on a FREE term algebra**; if the image is genuinely a
  different carrier, up to 13 "closed by proof" rows reopen. First measurements already in:
  the image of `op` is **4.1%** of the term algebra, but 9663's open-cell witness is itself op-built,
  so the invariant must be finer than "is an output of `op`".

---

## 5. Byte budget — measured, not extrapolated (rail 57)

Artifact at 60 certificates: **456,604 B of 500,000 — 43,396 B headroom (8.7%)**, measured by running
`minify_submission.py` over HEAD this session. Matches session 8 exactly, so nothing drifted.

At the measured **1,421 B for a new law + 64 B per sibling row**, the 40 open rows are 26 new laws +
14 siblings ≈ **37.8 KB**. It fits in 43,396 B — with **5.5 KB to spare**. There is no room for a
second data table or a large new route. If a future session adds one, re-measure before adding
certificates, not after.

---

## 6. Shipping pipeline — verified working end to end

Dry-run this session: `ship.py` → 60 entries, 790,673 B of Lean, 60 fixture lines;
`splice_certs.py --out <tmp>` → dropped 60, inserted 60, **source byte-identical** (idempotent).

Order (unchanged from session 8 §5): `verify_certs.py --workers 4` → `append_ledger.py` →
`ship.py` → `splice_certs.py` → `package_solver.ps1` **on an idle box** → `spotcheck.py` → commit.

Standing hazard, still live: several sessions share this tree. `judge_rows.py --write-fixture`
**REPLACES** the fixture and would delete all 60 research pins. Use `--append-fixture`, and check
`git diff --stat` on `solver.py` and the fixture before and after any fixture write (rail 16).

---

## 7. Deterministic corpus — re-measured green this session

Before the Austin work, the standard three checks were run on HEAD:

| check | result |
| --- | --- |
| offline gate (`pytest stage2/tests -n auto`) | **558 passed, 1 skipped** (the skip is `test_spotcheck_regressions`, empty by construction — it only has cases once a spotcheck catches a *wrong verdict*, and none ever has) |
| full official audit (`--all`, 7 sets) | **2089 / 2089 solved**, 0 skipped, 0 crashes, 0 oracle failures, 1029 T / 1060 F, **54.1 s** solver time on 16 workers |
| spotcheck (90 rows, 9 sources) | **90 / 90, 100% accuracy, 0 mistakes** |

`stage2/results/audit-2026-08-30.json`. Coverage matches the documented 2089/2089 baseline; the 54.1 s
is well under the 260.4 s last recorded for the same battery.

---

## 8. Next session, in order

1. **The harvest scan.** 30 seconds. It was empty this time; that is information, not a reason to skip it.
2. **`w38316.lean`** — 2 rows, one `theorem law`, everything else compiling, 3.8 KB headroom.
   **Validate its model before proving** (§11). For 23357 use `gen/_x23357_cert.lean`, not
   `_w3_23357_cert4.lean`, and derive C3 first (§11).
3. **`_x17286_mut.lean`** — 4 rows, 2 sorries, 9.9 KB headroom. Heed the two library sections that
   will otherwise cost hours: `<helper>.induct` is unusable inside a mutual block, and the size lemma
   whose 420-instance clean measurement was retracted because the junk variable was unbounded.
4. **32281** — 3 rows, but **treat it as a byte problem first**. 126 B headroom with 5 lemmas open.
5. **The anchored carrier** — the ~26-row structural prize, and the only item that can move the score
   by more than single digits.

### Agent doctrine — one addition from this session

Session 8's rules stand (waves of 6-8, resume rather than respawn, route findings between agents, ask
what an agent does NOT have). Add:

* **Give a validation instruction teeth by making it the first deliverable.** The 8485 agent was told
  to re-force *before* writing Lean and to report the re-forcing result *separately and explicitly*.
  It found the model false and wrote no Lean. The same agent, told simply to "close the certificate",
  would have spent the session proving something untrue — which is exactly what session 8 did seven
  times. **State the falsification as an acceptable, valued outcome in the prompt**, or the agent will
  treat it as failure and push through.

---

## 9. Leads captured at the moment the agents were stopped

The session ended on a token budget, not on a natural boundary. Each agent's last statement is
recorded verbatim below because several are **partial findings that would cost hours to rediscover**.
Treat every one as an unverified lead — none was confirmed by the orchestrator, and by this session's
own rail 60 an unvalidated claim is not evidence.

| law | the agent's last statement | how to read it |
| --- | --- | --- |
| **38316** | *"the model is missing a `V1-W2` rule that would make the hardest cell trivial. Let me test it."* | **Untested.** And note rail 60's warning applies exactly here: on 8485 the rule that closed the hard cell was the rule that broke the model. Test the proposed `V1-W2` rule against the *other* chain products (rung 8, forced firing) before believing it. |
| **23357** | *"`X` is false for 23357, so 23354's `core_no_fix` can't be ported. Let me empirically test all the lemmas I plan to prove BEFORE writing any Lean proof for them."* | Consistent with the library's existing warning that 23354's architecture ports but its **lemmas may not**. The stated method — test every planned lemma empirically first — is the right one and should be the default. |
| **17286** | *"the `dite` instance mismatch after `simp` is the classic trap — let me restructure with abstract helper lemmas instead."* | A Lean-mechanics obstacle, not a mathematical one. But heed the library's *"Do not state a top-product lemma with abstract `v` and abstract gates (law 17286)"* — that is a recorded negative result for this same law, and "restructure with abstract helper lemmas" is how you walk back into it. |
| **32281** | *"The exception reproduces **exactly** in the Lean-exact `op`: `hk` is false, R3 fires at the top, and A and S are both free there. `oR3` is unavoidable."* | The most concrete lead of the six, and it is a *model* problem surfacing under what was scoped as a byte problem. A rule firing at the top with both arguments free is the 8485 signature (rail 60). **Verify whether 32281's model is actually sound before spending more Lean effort on it.** |
| **10218** | *"90 of 140 rules pin `u` inside `v` (`Pdig`), 50 don't — and `p10218.lean`'s whole size-lemma scaffold depends on `Pdig`."* | Structurally important: it partitions the 140-rule set by exactly the property the existing Lean scaffold assumes, which is a principled starting point for finding the sound subset that is known to exist. |
| **anchored carrier** | *"Let me write up the decisive findings while those run."* | The write-up did not land. Its working files are `gen/_anch_img.py`, `gen/_sep11081.py`, `gen/_sep12087.py`, `gen/_x9663_sep.py`, `gen/sepfind.py`, and `gen/NOTES_ANCHORED_CARRIER.md` (modified this session). **Read those before re-commissioning the question** — the word "decisive" is the agent's, not verified. |

**Do not resume these as if the leads were established.** Re-derive each cheaply first; four of the six
touch the exact failure mode (a rule firing where its locator is not guaranteed) that this session
proved fatal for 8485.

---

## 10. Post-cutoff: the `UD` lemma for 32281 (two independent agents converged on it)

After the stop, the 32281 agent and a sub-agent it had spawned both ran on until they hit the
account's weekly Opus limit. Both reported the **same** structural finding independently, which is
the strongest signal this session produced on that law:

> **"Confirmed: `UD` reduces `SFg`'s main branch to the generalized `SFa` in one line."**
> **"`UD` is exactly the structural tool I said was needed."**

`SFa`'s Q-decoded residue was session 8's named bottleneck for 32281, so a one-line reduction of it
is exactly the missing piece. **Still unverified by the orchestrator** — no compile of the result was
seen, and rail 60 applies.

### 32281 file state at final cutoff — read this before picking a file

| file | bytes | sorries | has `UD` | age |
| --- | --- | --- | --- | --- |
| `w135f.lean` | 26,631 | 11 | **yes** | newest |
| `w135_C.lean` | **15,147** | 7 | no | newest |
| `w135e.lean` | 18,628 | 10 | no | 30 min |
| `w135d.lean` (session-8 base) | 19,874 | 5 | no | stable |
| **`w135b.lean`** | **10,246** | **1** | no | ~15 h |
| **`w135a.lean`** | **9,201** | **1** | no | ~15 h |
| `w135c.lean` | 12,831 | 3 | no | ~15 h |

Two things stand out and neither was known when the byte-pressure task was written:

1. **`w135_C.lean` is 15,147 B — 4,727 B *below* the base file** — because the agent deleted the dead
   `SF`/`SFa`/`SFb`/`SFc` after `UD` subsumed them. **The 126-byte crisis may already be over.** The
   task was scoped as "bytes first, maths second"; `UD` appears to have solved both at once.
2. ~~**`w135a.lean` and `w135b.lean` carry ONE sorry each and are closer to a certificate.**~~
   **CHECKED, AND FALSE — a lower sorry count meant LESS work done, not more.** Both compile
   `exit=0` (9,220 B and 10,265 B) with their single `sorry` on **`theorem law` itself**, which
   superficially matches the `w38316` / `_w3_23357_cert4` shape that makes those two rows cheap. But
   these are the **undecomposed** versions: `w135a` carries only `sz_a1`/`sA1`/`mx`, and `w135b` adds
   `SU`/`oR1`/`op_cases`/`P1`. The 5 sorries in `w135d` are `law` **broken into named sub-lemmas** —
   i.e. session 8's progress, not its debt.

   > **Generalisable, and it nearly cost the next session a day: sorry count is not distance to a
   > certificate.** Decomposing one hard goal into five tractable ones *raises* the count while moving
   > forward. Compare the *helper library* — what is available to prove the goal with — not the number
   > of holes. The rail-47 harvest scan is safe from this (it demands zero sorries *and* a
   > `def submission`), but any eyeball ranking by sorry count is not.

   I wrote the opposite in this file an hour earlier on the file listing alone; the correction cost one
   `grep` and two compiles.

`w135f.lean` at 26,631 B is 6.6 KB over the cap and has more sorries than it started with; it is a
mid-restructure snapshot, not a candidate.

### 32281, the corrected reading

`UD` is real and it bought bytes: **`w135_C.lean` compiles at 15,147 B**, 4,727 B below the session-8
base, after the dead `SF`/`SFa`/`SFb`/`SFc` were deleted. The byte crisis that framed the task is
very likely over. What remains is the mathematics: 7 sorries in `w135_C`, with `UD`'s claimed one-line
reduction of `SFg` → generalized `SFa` **still unverified**.

Start from **`w135_C.lean`** (15,147 B, 7 sorries, compiles) or **`w135d.lean`** (19,874 B, 5 sorries,
the session-8 base). Not from `w135a`/`w135b` (undecomposed) and not from `w135f` (26,631 B, 6.6 KB
over cap, mid-restructure).

---

## 11. Law 23357's model is FALSE — and the orchestration error that sent an agent at it

### The finding

`gen/_w3_23357_cert4.lean`'s 4-rule model **does not satisfy law 23357**. `theorem law` at line 222 is
not hard to prove; it is **unprovable, because it is false**. Demonstrated at the Lean level: the model
text copied verbatim into `gen/_w3_23357_refchk.lean` (4,420 B, `exit=0`) and the law `#eval`'d on two
census witnesses against the file's own `op` — **`false` both times**.

`f4` had passed `rv.run_tests`, an 8,673-family hunter, 3x20k deep tests **and** a 12,000-chain level-k
descent. It was refuted by the **constructed-guard** method: `_w3_23357_ctor.out` shows **1680/1680**
C1 triples and **840/840** C2 triples failing, with positive controls confirming the target cells were
actually produced. Mechanism: f4's `RD`/`As` guards certify by **recomputation**, which silently
requires an inner product to be free; draw that inner pair from decoding pairs and the guard breaks
with no remaining rule covering the cell. Partial repairs (`f4+B1s`, `f4+A0s,B1s`, the 6-rule `g6`)
all pass C1 and fail C2 840/840.

**That makes nine of nine** models that were inherited as validated and then actually re-checked, and
turned out false.

### The error, which is mine and is worth more than the finding

I built an agent task around this file and called it "the cheapest work on the board". **Line 1 of the
file reads `-- REFUTED MODEL: ... DO NOT SHIP.`** I never read it. I "verified the file" by *compiling*
it — `exit=0`, one sorry, 11,262 B — and by trusting session 8's handover table.

> **A compile answers "does this build?", not "should this exist?".** They are different questions and
> only one of them was asked. The `exit=0 / one sorry / sorry is on theorem law` signature is
> **necessary but not sufficient** for a cheap row — `w38316.lean` and `_w3_23357_cert4.lean` had a
> byte-for-byte identical signature and one of them was refuted on disk.
>
> **Read line 1 of a file before building a task around it.** Cost of not doing so: one premium-model
> agent session. Cost of doing so: one `head -1`.

Note the timestamps, because they explain how the session-8 handover got it wrong honestly: the
validation outputs were written at 21:24 on 08-29 and the refutation at 21:29-21:42 — the "fully
validated" claim was **true as measured and superseded within twenty minutes**. Prefer the file's own
header over any handover's table; the header travels with the artifact.

### The viable path for these 2 rows

**`full12`** — spliced certificate `gen/_x23357_cert.lean`, **12,808 B, one sorry (`law`, line 213),
compiles, ~6.7 KB headroom**. It is the only rule set on record surviving *every* oracle: `run_tests`
0 fails, the hunter, 3x20k deep (`_x23357_val12.out`), **and C1 0/1680, C2 0/840**. Generator
`gen/_x23357_rep.py`; rules R1-R12 printed in `_x23357_rep.out`.

**Named precondition, do not skip it:** derive **C3** — one constructed family per remaining `full12`
guard (recipe at the top of `gen/_w3_23357_ctor.py`). The structural `Bs`/`B1s` rules certify by shape
at a **fixed accessor depth**, which is precisely rail 58's infinite-hierarchy risk, so this is a real
check rather than a formality.

Model-independent lemmas that transfer out of the dead `cert4` to any successor: **`SZM`** (state it
from `TR`, never from `SZ`), **`NEFREE`**, **`TOP1`**, **`TOP4G`**, and the `dif_pos` raw-accessor
mechanics note. **`Ufree`** and **`CHAIN2B`** remain empirically solid (24,000-chain and 44,202-triple
censuses). Two lemmas that do **not** transfer, both refuted for 23357: **`X`** ("every decode returns
`a1 v`" — the `Bs` rules return `a2 (a1 u)`) and **`NOSELF`** (`op u v ≠ v`).

Row 0080 (dual 23653) is blocked on the base; `dualcert.py` transplants once a base certificate exists.
