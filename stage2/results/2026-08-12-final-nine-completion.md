# 2026-08-12 — The final nine: ordered completion closes the corpus

**Official 1666 → 1669/1669. HF 795 → 800/800. Combined 2469/2469. The benchmark
corpus is complete.**

All nine remaining rows were closed in one session, every certificate accepted by
the real Lean judge before it shipped:

| Row | eq1 ⇒ eq2 | Cert bytes | Judge |
| --- | --- | ---: | --- |
| `hard2_0073` | Eq2920 ⇒ Eq1248 | 1,682 | accepted (4.4 s) |
| `hard3_0214` | Eq2042 ⇒ Eq2692 | 2,130 | accepted (38.2 s) |
| `hard3_0314` | Eq2923 ⇒ Eq1623 | 6,444 | accepted (3.0 s) |
| `evaluation_hard_0116` | Eq469 ⇒ Eq4090 | 948 | accepted (2.9 s) |
| `evaluation_hard_0196` | Eq1689 ⇒ Eq2391 | 2,409 | accepted (2.9 s) |
| `evaluation_order5_0014` | Eq8502 ⇒ Eq27144 | 2,284 | accepted (2.9 s) |
| `evaluation_order5_0040` | Eq6605 ⇒ Eq32838 | 1,566 | accepted (2.9 s) |
| `evaluation_order5_0042` | Eq20115 ⇒ Eq21404 | 7,484 | accepted (3.0 s) |
| `evaluation_order5_0164` | Eq12716 ⇒ Eq23224 | 679 | accepted (2.9 s) |

9/9 judge-accepted, 9/9 independently kernel-verified, 9/9 model-checked.

## The mechanism: ordered completion, not saturation

Every engine in the solver had failed these rows at every budget — `hard2_0073`
alone had absorbed 1336 s of `deep`-effort equality saturation across every
curated pivot, every goal generalisation and the full rung scan. The ranked
next-lever list named the answer and it turned out to be right:
**ordered completion (Knuth–Bendix) with proof recording**.

Why it is strictly stronger than the e-graph here: completion **derives new
rules by superposition and then rewrites with them**. An e-graph only propagates
congruence over terms it has already built, so a proof that must pass through a
term nobody thought to construct is unreachable no matter how long it runs.

Two shapes of proof came out of it:

- **Collapse rows** (`hard2_0073`, `evaluation_hard_0196`, `order5_0014`): eq1
  forces the one-element magma; completion derives `a = b` and the goal is a
  one-line instantiation.
- **Non-collapse rows** (`hard3_0214`, `hard3_0314`, …): eq1 has non-trivial
  models (left projection for 0214, right projection for 0314), so `a = b` is
  the *wrong* target. What works: run completion to **saturation**, then
  normalise both sides of eq2 under the completed system. Both normal forms
  coincide, and the joining rewrite sequence *is* the proof. (`hard3_0214`:
  MAXSIZE 24, ~90 s, 23 rules. `hard3_0314`: MAXSIZE 34, ~200 s, 93 rules.)

## The claim that was blocking this, and why it was wrong

`CLAUDE.md` carried, as settled fact:

> eq1 for this family has **no critical pairs with itself** (the pattern has 4
> operations; every proper subterm has at most 3), so any proof must go through
> expanded terms.

**That is false, and the size argument behind it is invalid.** A critical pair
does not require the subterm to be *larger* than the rule's pattern — it
requires the subterm to **unify** with it, and unification is free to
instantiate the subterm's own variables. Orient `hard2_0073`'s eq1 as

    ((Y ◇ (X ◇ Z)) ◇ X) ◇ Y  →  X

and overlap it with itself at the proper subterm `X ◇ Z` — non-variable, hence a
legal overlap position. The mgu is `X ↦ (Y' ◇ (X' ◇ Z')) ◇ X'`, `Z ↦ Y'`, and
that single overlap unlocks the entire row:

    (H) (a◇b) ◇ (a◇((a◇b)◇c)) = a          -- the critical pair
    (J) (a◇b) ◇ (a◇a) = a                   -- H at c := B; squaring is an involution
    (K) ((a◇a)◇b) ◇ a = a◇a
        (a◇b) ◇ (a◇b) = a                   -- σ(a◇b) = a
        ((a◇b)◇c) ◇ a = a◇b
        a ◇ (b◇c) = b                       -- the killer law
        a = b

Completion reproduced this in **0.0 s, 23 critical pairs, 10 rules**.

The claim was also **self-refuting**, which is the part worth remembering: with
no self-critical-pair the one-rule system would be terminating *and* trivially
confluent, so `x = y` could not follow from it — contradicting the TRUE label
the ETP matrix had already assigned. A structural-impossibility claim that
contradicts known ground truth is a bug in the claim.

This is the same failure mode as rail 3b ("check whether a judge limit is
actually the judge's"): a hard impossibility inferred from a single insufficient
argument, then written down as a rail and trusted for sessions.

## What shipped

Nine new `DISTILLED_CERTS` entries (25,626 cert bytes), keyed by canonical
equation text like every other entry — content, never row ids (rail 5h/9), so
each also covers its HF `*`-notation mirror and any future ETP sample of the
same implication. All nine byte-pinned in
`stage2/fixtures/judge_verified_certs.jsonl`.

- Gate: **210 passed, 2 skipped**.
- Packaged: **382,824 bytes** of 500,000 (23.4% headroom), submission layout
  validated clean.
- Packaged artifact re-verified on all 9 rows plus 8 controls: **17/17 solved**,
  every verdict matching its label, the 9 distilled rows returning in 0.0 s.

## Also measured: a tier inversion worth fixing

Chasing these rows surfaced an unrelated and shippable problem. Several rows
that solve at `fast` **fail at higher tiers**:

| Row | fast | standard | deep (900 s cap) |
| --- | --- | --- | --- |
| `normal_0491` | **SOLVED** 65 s (`egg_ladder:collapse:h1`) | SKIP (198 s) | SKIP (323 s) |
| `hard2_0162` | **SOLVED** 168 s | SOLVED 386 s | SKIP (465 s) |
| `hard3_0266` | **SOLVED** 107 s | SOLVED 134 s | SKIP (205 s) |
| `normal_0090` | SOLVED | — | SOLVED 522 s |

Cause: `EFFORT_TIERS` scales *every* engine budget together (`deep` = 22×), so
on a row whose answer lives in a **late** engine, the early engines consume the
whole per-problem clock before the late one is reached. More budget makes the
solver strictly worse on exactly the rows that need the last engine.

This matters in deployment: **Solo picks its tier from the real 3600 s budget
and therefore runs `deep`.** These rows are all distilled or ladder-solved now,
so nothing is currently lost, but the scheduling defect is live for any future
row of that shape. The fix is the long-standing "step-count instead of
wall-clock budgets" item, or simply reserving a floor for the late engines. Not
attempted this session — it is a real change needing a full audit to validate.

## Provenance

Derivations, completion transcripts and per-row notes:
`<scratch>/final9/<row_id>/`. Judge results: `<scratch>/final9/judge_results.json`.
