---
name: marathon-triage
description: 'Use when: designing Stage 2 Marathon scheduling, token budgeting, problem ordering, cache reuse, deterministic-first solving, or shared-budget strategy.'
argument-hint: 'Describe the manifest, budget, candidate solver, or triage problem.'
---

# Marathon Triage

Use this workflow for competition-relevant multi-problem solving under a shared budget.

## Procedure

1. Read the manifest and extract problem ids, equation ids, and equation strings.
2. Rank deterministic wins first: reflexive, cached finite witness, cached proof motif, graph-known path with a validated template.
3. Estimate per-problem cost before spending LLM tokens.
4. Submit deterministic certificates before exploratory LLM calls.
5. Reuse proof attempts, witness tables, and error repairs across related equation families.
6. Track accepted count, wall-clock, token use, and failure class.

## Guardrails

- Never assume every problem can receive Solo-level budget.
- Do not let LLM repair loops starve deterministic solves.
- Append JSONL answers only in the official output shape.
