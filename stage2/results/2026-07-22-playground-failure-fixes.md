# 2026-07-22 (session 4): Playground failure triage — 14 rows, root causes, fixes

A playground (Solo, real judge, positive tokens) simulation returned 13
`TRUE INCORRECT` rows and 1 `ERROR`. This session reproduced every row
locally, identified four distinct root causes, and shipped fixes for all of
them. 8 of the 14 rows now produce **judge-accepted deterministic
certificates at the `fast` tier**; the ERROR class is structurally
eliminated; the rest degrade to guarded fallbacks with no scoring downside.

## The 14 rows and their outcomes

| Playground id | Label | Root cause | Now |
| --- | --- | --- | --- |
| `evaluation_normal_true_0048` | TRUE | `true:narrow_grind` emitted a grind cert the official judge rejects (local accept is not transferable) | `true:derived_cp_closure`, judge-accepted, 0.6 s |
| `evaluation_normal_true_0082` | TRUE | solved locally, but playground hardware missed the budgeted window; fallback junk submitted | `true:projection_bootstrap:left`, judge-accepted, 3.1 s |
| `evaluation_extra_hard_true_0148` (**ERROR**) | TRUE | deep-tier closure ballooned past the 2048 MB sandbox cap → OOM kill with no judge call banked | `true:lemma_chain:enum25`, judge-accepted, 0.7 s |
| `evaluation_normal_true_0024` | TRUE | unresolved frontier row | `true:lemma_chain:enum25`, judge-accepted, 1.2 s |
| `hard2_true_0060` | TRUE | unresolved frontier row | `true:lemma_chain:enum291` (CP helpers), judge-accepted, 1.4 s |
| `hard2_true_0078` | TRUE | unresolved frontier row | `true:lemma_chain:product_constant`, judge-accepted, 0.8 s |
| `hard2_true_0153` | TRUE | unresolved frontier row (no small pivot exists) | `true:lemma_chain:direct_goal`, judge-accepted, 5.0 s |
| `normal_true_0582` | TRUE | trivializing hypothesis (ETP: Eq1923 ⇒ x = y); chain reach still short | open; guarded fallback |
| `hard2_true_0178` | TRUE | unresolved frontier row | open; guarded fallback |
| `evaluation_normal_true_0040` | TRUE | unresolved frontier row | open; guarded fallback |
| `hard2_false_0093` | FALSE | no witness of order ≤ 4 exists (DFS-exhausted); fallback TRUE guess submitted | open; no-penalty guess |
| `hard2_false_0123` | FALSE | same | open; no-penalty guess |
| `evaluation_extra_hard_false_0190` | FALSE | same (eq1 is the central groupoid law Eq168; witnesses live on m² carriers) | open; no-penalty guess |

Label mapping: strip the `true/false` segment (`hard2_false_0093` →
`hard2_0093`). All 14 labels cross-check against the ETP outcomes matrix.

## Root causes and fixes

### 1. ERROR row = OOM kill (strict-zero-errors regression)

Deep-tier closure frontiers passed **5–17 GB RSS** locally on permissive
hypotheses; the production sandbox caps the solver at **2048 MB**, so the
playground run died with no judge status. Fixes, all in `solver.py`:

- **Global hard deadline** (`set_hard_deadline`): Solo parses
  `budget.timeout_seconds` from the start message, anchors at process start,
  reserves a tail for the fallback judge call
  (`SOLO_FALLBACK_RESERVE_SECONDS = 90`), caps the deterministic pass at
  `SOLO_DETERMINISTIC_SHARE = 0.55`, and refuses to open an LLM round with
  < `SOLO_LLM_ROUND_MIN_SECONDS = 150` left. Every engine-local deadline is
  clamped via `local_deadline()`; Marathon arms the same bound.
- **Memory guard** (`memory_exceeded`, polled inside `deadline_expired`):
  throttled RSS check against `MAGMA_MEMORY_CAP_MB` (default 1600), armed
  only by the Solo/Marathon entry points so long-lived dev processes are
  unaffected. One `try_reclaim_memory()` (cache clear + gc) lets the cheap
  routes still run after a ballooning engine trips.
- **Insurance judge call**: when the deterministic pass yields nothing, Solo
  banks a cheap reflexive-cert judge status *before* the LLM loop, so even a
  kill mid-round leaves a verdict, not an ERROR.
- **Fallback upgrade**: the final unsolved fallback now submits a grind cert
  (`fallback:unsolved_grind`) instead of the never-passing reflexive cert —
  small but nonzero acceptance odds at zero cost, since scoring carries no
  wrong-answer penalty.
- Solo protocol smoke (120 s budget, no LLM): deterministic pass ends at the
  55 % mark, insurance status banked, LLM round refused near deadline, grind
  fallback judged, clean exit at 67.6 s.

### 2. `true:narrow_grind` demoted

The playground rejected its cert on the exact shape
(`x * y = (y * x) * (y * z)` → `x * y = y * (y * z)`), and the local proof
kernel cannot check the grind shape at all (model-check only). The route now
runs *after* the kernel-verifiable engines (6 of its 9 rows were already
subsumed by `derived_cp_closure`); grind remains only as a last-ditch
attempt on its known-TRUE shapes.

### 3. New proving power: enumerated lemma library + multi-hop lemma chains

ETP mining showed every missed TRUE row is `implicit_proof_true` — the ETP
itself reaches them only through intermediate laws, so a single closure hop
from eq1 cannot. Shipped:

- `enumerated_lemma_library()` — all laws with lhs `a`/`a ◇ b` and rhs up to
  3 ops over ≤ 4 vars (~600 canonical laws, deduped by the new
  `canonical_law_key`); extends the 6-entry curated library behind the same
  verified `lemma_bootstrap` path. This alone cracked the ERROR row via
  `x = (x ◇ y) ◇ z` (ETP Eq27).
- `lemma_chain_bootstrap_route` — multi-hop chains:
  1. **CP helpers** (free): eq1's own critical-pair rules are converted to
     standalone lemmas with ready-made proofs (`cp_rule_helpers`); taking
     critical pairs *of those helpers* (`critical_pair_rules(…, hyp_name)`)
     gives the closure a second derivation level.
  2. **Iterative harvest**: small laws provable from eq1 join the rule set;
     a second round retries failures with the first round's rules.
  3. **Pivot or direct goal**: prove a goal-applying pivot lemma, or aim the
     strengthened closure at the goal itself (`direct_goal`) when no small
     pivot exists.
  Certificates are multi-`have` Lean files; the offline kernel gained a
  multi-hypothesis `ProofKernel`, a `lemma_chain` certificate class, and
  `check_true_lemma_chain_certificate` (each block verified in the scope of
  `h` + previously verified lemmas — sound by induction). `audit_corpus`
  dispatches the new shape; spotcheck inherits it.
- Every emitted chain cert was verified by the offline kernel **and**
  accepted by the real local Lean judge.

### 4. FALSE rows: no small witnesses exist

Exhaustive DFS with eq1-instance propagation proved **no order ≤ 4 witness
exists** for any of the three pairs. Further search all missed: DFS at
n = 5–6 (25 min per size, per pair), n = 9 for the central-groupoid row
(`evaluation_extra_hard_0190`, eq1 = Eq168; natural central groupoids satisfy
both sides, so a non-natural model is required), random-repair at 4–6, and
linear models `x◇y = (ax+by) mod n` to n = 24. These three rows stay open;
Solo scoring has no wrong-answer penalty, so the fallback TRUE guess costs
nothing. Next candidate lever: the ETP's explicit-ancestor construction
(magma witnessing X !⇒ Y with X ⇒ eq1 and eq2 ⇒ Y in the closure also
witnesses eq1 !⇒ eq2), which needs the ETP countermodel tables that the
local caches do not currently hold.

## Validation

- `pytest stage2/tests`: green after each change. Golden fixture regenerated
  from the session-4 audits (250 entries across 154 routes; 251 golden tests
  pass). `make_golden.py` now excludes `true:narrow_grind` rows — their certs
  are model-check-only locally, the cloud judge rejected one in the field,
  and the budgeted lemma routes ahead of them win their rows
  nondeterministically.
- Full official + HF audits at `fast`: see
  `stage2/results/audit-2026-07-22-session4.json` and
  `audit-hf-2026-07-22-session4.json` (numbers appended below).

## Audit deltas (fast tier, offline oracles)

Official sets (`audit-2026-07-22-session4.json` vs session-2 baseline
`audit-2026-07-22-final.json`); compare TRUE counts, not solved counts — the
FALSE lane carries a ±7 noise band:

| Set | Solved | Was | TRUE | Was |
| --- | ---: | ---: | ---: | ---: |
| `normal` | `984/1000` | `957/1000` | `485` | `458` |
| `hard1` | `64/69` | `61/69` | `24` | `21` |
| `hard2` | `172/200` | `155/200` | `87` | `70` |
| `hard3` | `381/400` | `361/400` | `177` | `157` |
| **Total** | **`1601/1669`** | `1534/1669` | **`773`** | `706` |

**+67 official TRUE rows** in one session, zero oracle failures. Route mix on
the new ground: `true:lemma_chain` ×55, `true:lemma_bootstrap` ×25 (the
enumerated library also feeds the single-hop route). One apparent loss
(`hard3_0135`) is the documented projection-budget wall-clock race under
16-worker audit contention — probed solo it solves via two different routes.

HF evaluation sets (`audit-hf-2026-07-22-session4.json`, 8 workers — the
first 16-worker attempt died with a BrokenProcessPool from machine
oversubscription, not a solver defect):

| Set | Solved | Was | TRUE | Was |
| --- | ---: | ---: | ---: | ---: |
| `hf_evaluation_extra_hard` | `170/200` | `168` | `100` | `98` |
| `hf_evaluation_hard` | `196/200` | `195` | `96` | `95` |
| `hf_evaluation_normal` | `195/200` | `188` | `95` | `88` |
| `hf_evaluation_order5` | `188/200` | `176` | `88` | `76` |
| **Total** | **`749/800`** | `727` | **`379`** | `357` |

**+22 HF TRUE rows, zero lost rows, zero oracle failures.** Golden fixture
regenerated from both audits (252 entries across 155 routes).
