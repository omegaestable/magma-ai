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
   tables checked by `decide`/`decideFin!`, plus one infinite carrier (`Nat`
   with a parity operation, proved with `omega`).
6. **LLM lane** (optional, via the organizer proxy only) — the model proposes
   candidate lemmas or rewrite chains; the solver derives and kernel-checks
   them itself. Nothing the model says is trusted or emitted unverified.

## Generated data payloads (disclosure)

The solver contains no compressed data and no binary blobs. All embedded data
is plain Python/Lean text:

- **`DISTILLED_CERTS`** — 65 complete Lean certificates, keyed by the
  renaming-invariant canonical text of the (hypothesis, goal) equation pair.
  Methodology: each certificate was produced by the engines above (most by
  ordered Knuth–Bendix completion with proof recording, run offline on hard
  rows), then verified against the official judge before inclusion; a
  certificate the judge did not accept is never stored. 48 of the 65 are
  re-derivable live by the in-solver completion engine; the table exists to
  make the slowest solved rows O(1) at inference time.
- **Named witness tables** — small Cayley tables (orders 2–9) found by
  countermodel search over Equational Theories Project data and by the
  constraint-propagation engine.
- **Lemma library** — ~600 small candidate laws (projections, constancy,
  idempotence variants) enumerated by term size; used as intermediate proof
  targets.

To reproduce any of these: run the corresponding search (completion,
saturation, or constraint search) on the equation pair; the tables are caches
of search results, not hand-crafted or opaque data. The Equational Theories
Project (https://github.com/teorth/equational_theories, Apache 2.0) was used
during development as a source of ground-truth labels and finite-model data
for validation.

## Determinism

The deterministic pass uses no randomness with unpinned seeds and no wall-time
dependence in its mathematics; wall-clock budgets only bound how long each
engine may run. LLM usage (if any) goes exclusively through the organizer
proxy with the organizer's pinned model configuration.
