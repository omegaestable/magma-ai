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

The submitted artifact contains **one compressed data blob and no binary
executables**. In the submitted `solver.py`, the fifteen packed values are
`DISTILLED_CERTS`,
`FP_WITNESS_TABLES`, `O5_WITNESS_TABLES`, `WITNESS_TABLES`,
`_ANCHORED_RIGHT_PROJECTION_BLOCKS`, `_ANCHORED_LEFT_PROJECTION_BLOCKS`,
`_PRODUCT_CONSTANT_BLOCKS_3565`, `_PRODUCT_CONSTANT_BLOCKS_3967`,
`PROTOCOL_FALSE_FIRST`, `_PRODUCT_CONSTANT_BLOCKS_3983`,
`_PRODUCT_CONSTANT_BLOCKS_3577`, `_RIGHT_SPINE_CROSSED_BLOCKS`,
`MINED_LEMMA_LIBRARY_TEXT`, `PROTOCOL_DERIVATION_EXCLUSION`, and
`PROTOCOL_TERMS` are carried together in a single string, produced by
serialising the plain Python literals (each table as
JSON, or as its own `repr` where the literal's tuple/list types must survive
exactly), compressing the result with LZMA (`preset=9 | lzma.PRESET_EXTREME`) and
encoding it with base85 (`base64.b85encode`). A helper at the top of
the data section (`_unpack_all`) reverses exactly that at import time using only
the standard library, and each table is then a plain dictionary lookup. Nothing
else in the file is compressed or encoded.

The packing is a pure size measure against the 500 KB cap and is applied by the build
script `stage2/solver/minify_submission.py`, which decodes every blob again and
compares it to the source literal, and compares the artifact's parse tree to the
source's, before writing the artifact. One shared blob is used rather than one
per table because the tables share vocabulary and a separate LZMA stream
restarts the dictionary each time. The readable literals live in the source tree
(`stage2/solver/solver.py`) in plain Python/Lean text. `PROMPT` is deliberately
not packed: the official proxy extracts it as a top-level string constant, and
packing it would silently give the Solo LLM lane an empty prompt. Every payload below is
reproducible from the sources named. Sizes are of the unpacked text, measured
2026-08-29.

- **`DISTILLED_CERTS` — 119 complete Lean certificates.** They are keyed by
  the renaming-invariant canonical text of the hypothesis/goal equation pair,
  never by a problem id. Every stored certificate has official judge evidence;
  some are live-rederivable and some preserve search-resistant finite or
  infinite constructions. The 60 Austin research certificates added in session
  8 came from `stage2/experiments/austin/automata/` and were independently
  re-judged before being stored.
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
- **`O5_WITNESS_TABLES` — 18 order-5 witness tables.** A block of Cayley tables
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
both as a source of ground-truth labels for offline validation and as the origin
of the FinitePoly tables, two named witness tables, the `WCG5` construction, and
published construction material used for distilled certificates. All embedded
data is rechecked locally before emission, and every stored certificate has
official judge evidence.

## Determinism

The deterministic pass uses no randomness with unpinned seeds and no wall-time
dependence in its mathematics; wall-clock budgets only bound how long each
engine may run. LLM usage (if any) goes exclusively through the organizer
proxy with the organizer's pinned model configuration.
