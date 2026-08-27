# Submission note — Stage 2 solver

Submitted alongside `solver.py` per the Stage 2 rules on human-interpretable
artifacts (rules/overview.md, "Human-Interpretable Artifacts"; rules/
evaluation.md, "Submission Note").

## What the solver is

A deterministic-first decision engine for magma-equation implications. For each
problem it walks a fixed cheap-to-expensive ladder of proof and countermodel
engines, and emits a Lean 4 certificate only after verifying it locally —
either an independent proof-kernel replay (TRUE) or a finite-model check
(FALSE). Nothing is submitted on heuristic confidence: every certificate is a
complete, kernel-checkable Lean term or a `decide`-checkable witness.

The main engines, in dispatch order:

1. **Syntactic law families** — a table of equation patterns (projection,
   collapse, singleton, absorption families), each mapped to a certificate
   template. Data-driven: one table row per family.
2. **Equality saturation ("egg")** — a ground e-graph with congruence closure
   and proof recording; explanations are extracted, shortened, and replayed
   syntactically before rendering.
3. **Ordered (unfailing) Knuth–Bendix completion** with proof recording — the
   only engine that derives new rewrite rules by superposition. It closes
   goals by joinability or by deriving a collapse equation `t = v` (with `v`
   not in `t`), and emits chain-of-rewrites certificates.
4. **Critical-pair / lemma-chain closures** — forward chaining from the
   hypothesis, targeting small intermediate laws rather than the goal
   (proof-search cost scales with goal size).
5. **Countermodel search** — named small witness tables, structured
   (affine/quadratic/linear) families over `Fin n`, bounded enumeration, and a
   Mace4-style constraint-propagation search. FALSE certificates are Cayley
   tables checked by `decide`/`decideFin!` (orders 2-36, rendered either as a
   `finOpTable` string, an inlined `List.getD` lookup, or a closed-form bit
   formula), plus several infinite carriers (`Nat` with a parity operation,
   proved with `omega`).
6. **LLM lane** (optional, via the organizer proxy only) — the model proposes
   candidate lemmas or rewrite chains; the solver derives and kernel-checks
   them itself. Nothing the model says is trusted or emitted unverified.

## Generated data payloads (disclosure)

The solver contains no compressed data and no binary blobs. All embedded data
is plain Python/Lean text, and every payload below is reproducible from the
sources named. Sizes are of the packaged artifact measured 2026-08-27.

- **`DISTILLED_CERTS` — 59 complete Lean certificates (~99 KB of source, the
  single largest payload).** Keyed by the renaming-invariant canonical text of
  the (hypothesis, goal) equation pair, never by a problem id, so one entry
  serves every spelling of the same implication. 37 are TRUE certificates and
  22 are FALSE. Methodology: each was produced by the engines described above
  — mostly ordered Knuth-Bendix completion with proof recording, run offline
  with a larger budget than a graded row affords — and then submitted to the
  official Lean judge; a certificate the judge did not accept is never stored.
  The majority are re-derivable live by the in-solver completion engine; the
  table exists to make the slowest solved rows O(1) at inference time. Ten of
  the 59 (named `inf_e*`) are the exceptions that no in-solver search
  reproduces: countermodels transcribed from constructions in the Equational
  Theories Project — infinite carriers over the naturals with a parity
  operation (proved by `omega`), and finite Cayley tables of orders 21, 24 and
  36 rendered as inlined `List.getD` lookups.
- **`FP_WITNESS_TABLES` — 113 Cayley tables of orders 3-11 (~12 KB).** Taken
  from the FinitePoly refutation database of the Equational Theories Project
  (https://github.com/teorth/equational_theories, Apache 2.0) and reduced to a
  minimal covering set: the full library was evaluated against 436 FALSE rows
  that the solver's own named tables and structured families do not refute, and
  greedy set-cover selected the 113 tables that cover 421 of them. Reproducible
  with `stage2/experiments/teorth_finitepoly_library.py` (extract the library
  from the ETP repository) followed by
  `stage2/experiments/select_witness_library.py` (the set-cover selection).
- **`WITNESS_TABLES` — 30 named Cayley tables of orders 2-9 (~2 KB).** Small
  countermodels found by this solver's own constraint-propagation and bounded
  enumeration searches over Equational Theories Project pairs, kept because
  re-finding them costs milliseconds to seconds per row; two of them (`S6B`,
  `S9A`) came from the ETP FinitePoly database instead, and are marked as such
  in the source.
- **An order-5 witness-table library.** A block of Cayley tables of order 5
  harvested offline by an SMT (z3) countermodel search over generated order-5
  equation pairs, then reduced by the same greedy set-cover procedure as
  `FP_WITNESS_TABLES` and tested in the same late portfolio slot. Reproducible
  with `stage2/experiments/z3_witness_search.py` (the search) and
  `stage2/experiments/witness_library_eval.py` (coverage evaluation and
  selection). Like every other witness, each table is re-checked against the
  hypothesis and the goal at solve time before any certificate is emitted, so
  the library is a cache of search results and never a source of truth.
- **`FORMULA_WITNESSES` / `WCG5`.** One order-32 magma — the twisted weak
  central groupoid on the field with two elements to the fifth power, from the
  Equational Theories Project blueprint. It is *computed by a closed form in
  the file*, not stored as a 1024-cell table, and rendered into the certificate
  as a bit formula (15 s of judge time against 262 s for the equivalent table).
- **Lemma library (`EGG_PRIORITY_LEMMAS` and the enumerated candidates).**
  Small candidate laws (projections, constancy, idempotence variants)
  enumerated by term size at run time; used as intermediate proof targets
  because proof-search cost scales with goal size. Nothing here is a search
  result: it is generated by enumeration.
- **`NARROW_GRIND_TRUE_SHAPES` — 9 equation pairs (~600 bytes).** A diagnostic
  holdover that gates one speculative tactic route. It is keyed on the parsed
  term structure with original variable names, so it matches only those exact
  spellings; under the no-reuse guarantee it cannot fire on an evaluation row
  and is disclosed here for completeness rather than as live coverage.

Third-party data: the Equational Theories Project
(https://github.com/teorth/equational_theories, Apache License 2.0) is used
both as a source of ground-truth labels for offline validation **and** as the
origin of embedded data — the 113 `FP_WITNESS_TABLES`, two of the named witness
tables, the `WCG5` construction, and the ten `inf_e*` certificates. All of it
is derived from that repository's published refutation database and blueprint
constructions.

## Determinism

The deterministic pass uses no randomness with unpinned seeds and no wall-time
dependence in its mathematics; wall-clock budgets only bound how long each
engine may run. LLM usage (if any) goes exclusively through the organizer
proxy with the organizer's pinned model configuration.
