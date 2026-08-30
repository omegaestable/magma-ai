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
| **23357 / 23653** | 0048, 0080 | `gen/_w9_23357.lean` (agent's) / `gen/_w3_23357_cert4.lean` (base) | 13,251 / 11,262 | 1 / 1 |
| **38316** | 0055, 0065 | `gen/q38316.lean` (agent's) / `gen/w38316.lean` (base) | 18,593 / 16,200 | 6 / 1 |
| **17286 / 28626** | 0025, 0040, 0037, 0038 | `gen/_x17286_mut.lean` | 12,659 | 4 |
| **32281** | 0006, 0032, 0068 | `gen/w135_C.lean`, `w135e.lean`, `w135d.lean` (base) | 19,625 / 18,628 / 19,874 | 8 / 10 / 10 |

**Read this table carefully: in three of four cases the agent's in-progress file has MORE sorries and
MORE bytes than the base file it started from.** That is normal mid-restructure — a case analysis is
expanded before it is discharged — but it means **the base files are the known-good starting points**,
not the agent files. Verify both before choosing.

The four base files each compile `exit=0` today with only `sorry` warnings. Confirmed this session:

* `w38316.lean` — 16,200 B, **1 sorry**, `theorem law`, 1 s compile. 3,800 B headroom.
* `_w3_23357_cert4.lean` — 11,262 B, **1 sorry**, `theorem law`, 1 s. 8,738 B headroom.
* `_x17286_mut.lean` — 10,141 B, **2 sorries**, 1 s. 9,859 B headroom.
* `w135d.lean` — 19,874 B, 5 sorries, 2 s. **126 B headroom — the binding constraint here is bytes,
  not mathematics.** Apply `Z`/`Y`/`ZP`/`mx`/`mxl` before proving anything.

In `w38316.lean` and `_w3_23357_cert4.lean` the single remaining `sorry` **is `theorem law` itself** —
all scaffolding, `inst`, `rhs` and `submission` already compile. Those two are the cheapest 4 rows on
the board.

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
2. **`w38316.lean` and `_w3_23357_cert4.lean`** — 4 rows, one `theorem law` each, everything else
   compiling, 3.8 KB and 8.7 KB of headroom. Cheapest work on the board by a wide margin.
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
