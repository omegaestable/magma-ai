# Risk Register

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | No automated test suite | Medium | Manual dry-run validation works; add tests before scaling |
| 2 | Dense matrix in repo enables accidental inference-time leakage | High | Code paths classified in `ARCHITECTURE.md`; guard with code review discipline |
| 3 | No cross-model local-model evaluation recorded | Medium | Run Qwen 3B, Qwen 7B, and Gemma evaluations before submission |
| 4 | Cheatsheet uses only 25% of byte budget | High | Fill with singleton membership, magma tables, coverage-ranked flowchart |
| 5 | External competition rules not archived locally | Low | Document what is verified vs unverified in `competition_alignment_memo.md` |