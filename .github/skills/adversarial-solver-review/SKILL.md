---
name: adversarial-solver-review
description: 'Use when: red-teaming a Stage 2 solver candidate for malformed I/O, forbidden imports, secret leakage, size limit, budget failure, Lean dependency policy, or official-config drift.'
argument-hint: 'Provide the candidate solver path or review scope.'
---

# Adversarial Solver Review

Use this workflow before any solver candidate is promoted.

## Review Checklist

1. Single-file `solver.py` is <= 500 KB.
2. No repo-local imports are required at official runtime.
3. No local API keys or unallowlisted environment variables are read.
4. Solo JSON request/response flow is valid.
5. Marathon manifest read and append-only output behavior are valid.
6. LLM escalation uses only official Solo/Marathon proxy paths; missing local upstream keys are classified separately from solver protocol failures.
7. Lean code avoids banned tokens and unsupported imports.
8. False certificates use valid finite magma tables.
9. True certificates compile in the official judge context.
10. Timeout and token-exhaustion behavior is graceful.
11. Results were produced with official reference config or documented local deviations.
12. Smoke-only evidence is not reported as a refreshed public benchmark total.

## Output

Return blockers first, then risks, then non-blocking improvements. Include explicit playground readiness status. Do not summarize a candidate as ready if any blocker remains.
