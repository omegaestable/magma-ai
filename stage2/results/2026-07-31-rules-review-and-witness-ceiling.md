# 2026-07-31 — Official rules review, and the witness-order ceiling that was ours

Triggered by three organizer clarifications on the playground forum. Two were
no-ops. Reviewing the third exposed a self-inflicted ceiling that had cost every
FALSE row above order 10 since 2026-07-29.

Everything below was checked against `vendor/stage2-official` at commit
`6805e232` — the same commit the forum thread cites.

## The three rule clarifications

### 1. Marathon cannot call the judge — already compliant

`pipeline/marathon_runner.py:414` spawns the solver with
`stdin=subprocess.DEVNULL`, and `pipeline/marathon_proxy.py` routes only
`/v1/chat/completions` (rejecting anything else at `self.path not in
("/v1/chat/completions", "/chat/completions")`). A judge call from Marathon
would write a stray line to stdout and then block on a stdin already at EOF.

We never did this. `main()` dispatches on `is_marathon_mode()` before any proxy
traffic, and all four `judge_via_solo_proxy` call sites are inside `run_solo`.
Solo keeps its judge channel — that rule did not change.

Pinned by `test_no_judge_call_outside_solo`, which walks the solver's AST and
asserts no function other than `run_solo` calls `judge_via_solo_proxy`,
`send_proxy_call` or `load_json_line`. Structural, because the failure mode is a
silent stall that costs the whole run rather than one row.

### 2. Budgets: Solo 60 min/problem, Marathon 5 min/problem — no code change

`compression_ratio` has been withdrawn from the spec as misleading. The
underlying contradiction was inside the vendored snapshot all along:

| Source | Marathon global budget at N=100 | Per problem |
| --- | --- | --- |
| `rules/evaluation.md` | `0.5 × 100 × 3600` = 180,000 s | ~1800 s |
| `scripts/run_marathon.py` (`REF_PER_PROBLEM_SECONDS = 600`) | `0.5 × 100 × 600` = 30,000 s | 300 s |

The organizers confirmed the CLI. Nothing needed changing because the solver
reads `JUDGE_MARATHON_BUDGET_SECONDS` and Solo's `budget.timeout_seconds` from
the proxy rather than assuming a reference. The one place that had baked in the
withdrawn figure was a comment in `marathon_per_problem_budget`, now corrected.
`test_marathon_reads_its_budget_from_the_environment` pins the behaviour.

Noted as upstream drift in `vendor/stage2-official/UPSTREAM.md`; the vendored
rules file is left unedited.

### 3. Infinite countermodels are allowed — available, not used

The judge's FALSE goal has no finiteness constraint and never did:

```
∃ (G : Type) (_ : Magma G), EquationLHS G ∧ ¬ EquationRHS G
```

Deliberately not taken up. It only pays on a row with *no* finite countermodel,
and it trades `decide` for arithmetic lemmas under a policy with no
`HAdd.hAdd` / `HMul.hMul`. Lifting the finite ceiling was cheaper and was the
actual blocker. Worth revisiting if a row resists every finite order.

## The finding: `finOpTable` was never the only sanctioned constructor

The 2026-07-29 note concluded:

> Building the magma from a formula instead ... does not work either:
> `fun i j => 7 * i + 7 * j` fails the proof policy with
> `DISALLOWED_DECLARATIONS` on `HAdd.hAdd` / `HMul.hMul`. So **`finOpTable` is
> the only sanctioned magma constructor and 10 is a hard ceiling on FALSE
> witness order.**

The premise is right and the conclusion does not follow. `*` and `+` elaborate
to `HMul.hMul` / `HAdd.hAdd`, which have no allowlisted prefix — but
`Nat.add`, `Nat.mul`, `Nat.mod`, `Nat.mod_lt`, `Nat.succ_pos`, `List.getD`,
`Fin.mk` and `Fin.val` are all under prefixes the policy already allows
(`pipeline/proxy.py: DEFAULT_PROOF_POLICY`). It was the notation that failed,
not the construction.

Measured against the real local judge on `hard2_0051` (`x = (y ◇ ((y ◇ x) ◇ x))
◇ y` ⇒ `x ◇ (x ◇ y) = z ◇ (z ◇ y)`), whose smallest countermodel is the linear
model `x ◇ y = 7x + 7y (mod 13)`:

| Variant | Order | Bytes | Time | Result |
| --- | --- | --- | --- | --- |
| `fun i j => 7 * i + 7 * j` | 13 | 299 | 48.2 s | `incomplete_proof` — disallowed `HAdd.hAdd`, `HMul.hMul` |
| `finOpTable` complete table | 13 | 687 | 23.1 s | `incorrect` — `decide` proved the proposition false |
| `magmaFin` (judge's own `List Nat` constructor) | 13 | 644 | 5.6 s | `incomplete_proof` — disallowed `magmaFin` |
| **named-arithmetic formula** | 13 | 385 | 6.0 s | **accepted** |
| **inlined `List.getD` table** | 13 | 767 | 5.8 s | **accepted** |

Both controls reproduced the historical failures exactly. Note the first row:
`decide` *succeeded* there — only the allowlist blocked it, which is what made
the notation the obvious thing to vary.

`magmaFin` is worth recording as a dead end. It is the judge's own
`List Nat`-based constructor in `JudgeMagma/Magma.lean` with no digit parser,
but it is a bare top-level name matching no allowlisted prefix. The lookup has
to be inlined.

### Where the new ceiling actually is

`List.getD` at increasing order, same row, genuine witnesses each time:

| Order | Bytes | Judge time | Result |
| --- | --- | --- | --- |
| 13 | 724 | 7.9 s | accepted |
| 17 | 1,044 | 11.2 s | accepted |
| 25 | 1,972 | 30.2 s | accepted |

Time binds long before the 10,000-byte FALSE cap (order 25 uses 20% of it).
And time does not scale with order — `decideFin!` is exhaustive, so it scales
with `n ** variables`. Order 25 against a 3-variable goal is 15,625
applications; order 13 against a 5-variable goal is 371,293.

## Changes shipped

- `false_certificate_list()` — the `List.getD` renderer. `false_certificate()`
  now dispatches: orders ≤ 10 keep the `finOpTable` shape **byte-for-byte**
  (that is where all the accepted-cert evidence lives), everything above uses
  the new shape. Pinned by
  `test_orders_within_the_legacy_envelope_keep_their_shape`.
- `MAX_WITNESS_ORDER` 10 → 25; `LEGACY_MAX_WITNESS_ORDER = 10` names the proven
  envelope.
- `table_is_renderable()` measures the *rendered* certificate against the byte
  cap instead of inferring shippability from order. No order cap: a wide,
  narrow-ranged table is fine well above 25 when the goal has few variables.
- `witness_decide_is_affordable()` — the cost gate, `n ** variables ≤ 20,000`,
  anchored on the order-25 measurement with ~3x margin. Orders ≤ 10 are exempt;
  a cost model invented for new territory must not veto the envelope that
  already works.
- `large_linear_family_tables()` — linear models over `Z_n` for
  `n ∈ {11,13,16,17,19,23,25}`, linear only (`c = 0`) because the affine sweep
  is O(n³) tables, 15,625 at order 25. Placed late in the FALSE dispatch, after
  the TRUE engines, so solved rows pay nothing.
- **Bug found and fixed while wiring the above**: `witness_check` — the path
  every witness *family* uses — never applied `table_is_renderable` at all. It
  was invisible because every family topped out at order 9, where a table is
  single-digit and small by construction. The new order-11..25 family broke that
  assumption immediately. The gate now lives in `witness_check` itself, so the
  next family above the ceiling inherits it. Pinned by
  `test_witness_check_applies_the_shippability_gate`.
- `table_is_counterexample` reordered: semantics first, rendering last.
  `table_is_renderable` builds a certificate to measure it, and it runs on every
  candidate table of every family — only a genuine counterexample is rendered.

## Evidence

- Offline gate: **202 passed, 2 skipped, 44.9 s** (`-n auto`), up from 196.
- Real judge, end to end through `solve_problem`: `hard2_0051` **accepted** in
  5.6 s as `false:linear:z13:7,7` — the row the retired ceiling had made
  unreachable, and which the v4b note recorded as resisting a 721–737 s
  uncapped search across every order ≤ 10.
- Legacy-shape controls, same run: `normal_0003`, `normal_0006`, `normal_0008`
  (`false:witness:*`) and `hard2_0009` (`false:constraint_fin8`) all
  **accepted**, confirming no working row changed shape. 5/5, then 3/3 again
  after the `witness_check` fix.
- Full corpus audit: see `audit-2026-07-31.json` — **1647 / 1669**, TRUE 803,
  FALSE 844, 22 open, and **0 label mismatches / 0 oracle failures / 0 crashes
  across 1863 solved rows** counting the sample sets.

## Regression triage: the `hard2` 191 → 189 movement

The audit total matched the last measured one exactly (1647), but per-set it
moved: `hard3` 392 → 394, `hard2` 191 → 189. Worth writing down because the
investigation took longer than the change did.

**First, the baseline was not what the docs said.** `CLAUDE.md` carried
"1650 / 1669" as measured state. It never was: the 2026-07-29 audit read 1647
and the doc added +3 for `hard2_0082`, `hard3_0131`, `hard3_0271` — verified
individually, then written into the metrics table as a sum. `hard3_0131` and
`hard3_0271` do land (hence +2 there); `hard2_0082` does not, under parallelism.

**Second, the movement is scheduling, not coverage.** Each suspect row was
re-run standalone:

| Row | Standalone | Reading |
| --- | --- | --- |
| `hard2_0082` | **74.1 s**, `true:egg_bootstrap:product_constant` | needs 74 s to itself; never lands under 16-way parallelism |
| `hard2_0001` | **1.3 s**, `false:dual:...:witness:S5B` — and SKIP at 90.8 s in a second run of the *same code* | the cheap witness portfolio runs on a 2 s budget, so load alone decides it |
| `hard2_0092` | SKIP | open on both versions, see below |
| the other 8 | SKIP at 300-500 s each | genuinely open at `fast` |

`hard2_0001` is the clearest specimen: identical code, opposite outcomes, minutes
apart. Any row whose route sits behind a 2 s budget is a coin flip under load.

**Third, the one row that needed an A/B got one.** `hard2_0092` was the only
suspect not explained by mechanism, so it was run against the true pre-change
solver (commit `9535246`, verified `MAX_WITNESS_ORDER = 10` and zero references
to the new functions):

| Solver | `hard2_0092` | `hard2_0001` (control) |
| --- | --- | --- |
| pre-change `9535246` | SKIP, 100.8 s | SKIP, 92.8 s |
| current | SKIP, **100.9 s** | SKIP, **92.4 s** |

Run back to back in one sequence, so the load is the same for both halves: the
two `hard2_0092` timings land 0.1 s apart on a 100 s row. Note the control
skipped on *both* sides, which says the machine was loaded, not that either
version lost the row — the same current-code binary solved `hard2_0001` in 1.3 s
when the machine was calmer. That is the ceiling on what a loaded A/B can show:
it can demonstrate the two versions behaving identically, which it does, but it
cannot establish either one's clean-machine row set.

Consistent with the mechanical argument,
which is the stronger evidence anyway: the new gate can only reject a witness of
order > 10, and no pre-change route could emit one, so no previously-solved row
can newly fail.

**Caveat on all of the above.** None of it was measured on an idle machine — an
earlier audit was killed with `TaskStop` without confirming its worker pool died,
and an unrelated Solo sweep started partway through. The soundness numbers do not
care (0 mismatches over 1863 rows is not a timing artifact), but the 1647
headline does. An isolated re-audit is still owed.

Methodological notes worth keeping: `git show HEAD:file` emits LF where the
working tree has CRLF, so a byte-size mismatch between the two is not evidence of
different content (8,873 bytes here = 8,873 lines). And piping a long background
run through `tail` buffers the entire output until it exits — use a file and
poll it instead.

## What this cost, and the rail it earned

Two days of every FALSE row above order 10, from one experiment that closed a
door. The experiment was correct; the generalisation from it was not. The rail,
now in `CLAUDE.md` as 3b: **check whether a "judge limit" is actually the
judge's before building a rail on it — when one experiment closes a door, vary
it once before writing the rail down.**

The tell was available at the time and was in the rejection message itself: the
judge named two specific declarations, `HAdd.hAdd` and `HMul.hMul`, not the
construction. A message that specific is an invitation to try a different
spelling.
