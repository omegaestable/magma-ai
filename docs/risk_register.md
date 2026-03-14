# Risk Register

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | HF dataset URLs stale (404) | Medium | Use local generation from dense matrix; set `SAIR_STAGE1_*_URL` env vars when organizer provides new URLs |
| 2 | No automated test suite | Medium | Manual dry-run validation works; add tests before scaling |
| 3 | Dense matrix in repo enables accidental inference-time leakage | High | Code paths classified in `ARCHITECTURE.md`; guard with code review discipline |
| 4 | No cross-model LLM evaluation recorded | Medium | Run GPT-4o-mini + Claude evaluations before submission |
| 5 | Cheatsheet uses only 25% of byte budget | High | Fill with singleton membership, magma tables, coverage-ranked flowchart |
| 6 | External competition rules not archived locally | Low | Document what is verified vs unverified in `competition_alignment_memo.md` |