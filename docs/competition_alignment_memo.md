# Competition Alignment Memo

Source basis for this memo:

- [MASTER_SUBMISSION_AGENT_PROMPT.md](MASTER_SUBMISSION_AGENT_PROMPT.md)
- Repository code and data available locally on 2026-03-14

External organizer rules page is not archived in this repo, so any claim not present in the prompt above is marked unverified.

## Claims Audit

| Repo claim | Status | Notes |
|---|---|---|
| Final artifact is a plain-text cheatsheet under 10 KB | Verified | Explicit in [MASTER_SUBMISSION_AGENT_PROMPT.md](MASTER_SUBMISSION_AGENT_PROMPT.md). |
| Stage 1 should be optimized for binary TRUE/FALSE correctness | Verified | Explicit in [MASTER_SUBMISSION_AGENT_PROMPT.md](MASTER_SUBMISSION_AGENT_PROMPT.md). |
| Solver, graph, proof search, and ML may be used offline | Verified | Explicit in [MASTER_SUBMISSION_AGENT_PROMPT.md](MASTER_SUBMISSION_AGENT_PROMPT.md). |
| Matrix-backed solver behavior is the Stage 1 submission path | Rejected | Conflicts with the prompt’s submission-artifact boundary. |
| README accuracy numbers 99.8% and 100.0% are established | Unsupported | No reproducible artifact in the repo currently backs these figures. |
| README statement that Stage 1 scoring is on a balanced 50/50 set | Unverified | Present in old README, not backed by an archived primary rules source in the repo. |
| README deadline and budget statements are authoritative | Unverified | Not backed by an archived primary rules source in the repo. |

## Invalid Assumptions Removed Or Flagged

1. Treating `solver.py` plus matrix or graph lookup as if it were the submission artifact.
2. Using evaluation-set labeled examples as prompt-format demonstrations in `run_eval.py`.
3. Presenting single global accuracy without trivial/nontrivial split or bucket breakdown.
4. Stating unsupported base-rate and accuracy numbers in top-level docs or cheatsheet text.

## Clean Statement Of The Submitted Artifact

The intended Stage 1 artifact for this repo is a single plain-text cheatsheet, represented by [cheatsheet.txt](cheatsheet.txt). Any solver, matrix lookup, proof search, counterexample search, or ML system is offline support only and must not be treated as hidden inference-time behavior.