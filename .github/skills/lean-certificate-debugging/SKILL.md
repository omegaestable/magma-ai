---
name: lean-certificate-debugging
description: 'Use when: generating, debugging, or reviewing Lean 4 certificates for Stage 2 true implications, false finite magma witnesses, judge statuses, or dependency-policy failures.'
argument-hint: 'Provide the problem, verdict, Lean code, judge status, or stderr excerpt.'
---

# Lean Certificate Debugging

Use this workflow when a certificate fails or when adding a new proof template.

## Procedure

1. Identify the intended verdict: `true` implication proof or `false` finite magma witness.
2. Confirm the submitted code imports only official allowed modules such as `JudgeProblem`, `JudgeDecide.DecideBang`, and `JudgeFinOp.MemoFinOp`.
3. Check for banned proof tokens and disallowed imports before running the judge.
4. Run through the official judge or runner in `vendor/stage2-official/`.
5. Classify failure status: `unparsed`, `malformed`, `incomplete_proof`, or `incorrect`.
6. For true proofs, verify that the proof is standalone and does not assume Teorth theorem names.
7. For false proofs, verify the magma table and equation evaluation before blaming Lean syntax.
8. For direct harness checks, use the official runner or convert with `_to_judge_problem(problem)` before `verify_answer`; direct `verify_answer(problem, ...)` is not runner-equivalent.

## Guardrails

- No template is promoted without `accepted` evidence.
- Do not use `sorry`, `admit`, generated axioms, or unsafe initialization tricks.
- Preserve stderr excerpts in `stage2/results/` when they teach a reusable fix.
- Larger finite witnesses can need `set_option maxRecDepth 20000` before `decideFin!`; validate the emitted certificate through the runner.
