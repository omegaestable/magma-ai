# 2026-08-13 — QA pass: the judge caps were half the deployed ones, and CI was red

A QA/publish-readiness session, not a coverage session. The corpus was already
100% solved locally, so every change here is about **generalization to held-out
rows, robustness under the real runners, and repo health**. Coverage was held
constant and proved constant.

## Headline: the solver enforced half its real certificate budget

`stage2/solver/solver.py` carried `JUDGE_MAX_CODE_LENGTH = 50_000` and
`JUDGE_MAX_FALSE_CERT_BYTES = 10_000`, and its `decide` cost model was anchored
to a 120 s Lean timeout. The deployed values live in
`vendor/stage2-official/pipeline/config.json` (`judge` block) and are passed
straight into the judge by `pipeline/proxy.py` (~L1004-1012):

| | solver had | deployed |
| --- | --- | --- |
| `max_code_length` | 50,000 | **100,000** |
| `max_false_cert_bytes` | 10,000 | **20,000** |
| `lean_timeout_seconds` | 120 | **300** |

The 50,000 / 10,000 / 120 in `judge/verify.py` are module defaults, used only
when the verifier is called with no config. The deployed pipeline always passes
its own.

### The evidence for halving them was self-inflicted

The caps were *lowered* from 100,000/20,000 on 2026-07-29, citing a 2026-07-23
measurement — "a 59,820-byte cert was rejected `malformed`". That measurement
ran through `stage2/experiments/judge_rows.py`, which called `verify_answer()`
with **no config** and therefore measured `verify.py`'s fallback against itself.
The result was circular, and it was written down as a property of the judge.

### Settled by experiment, per rail 3b

One certificate, judged twice, with only the configured cap varying:

| bytes | cap = 50,000 | cap = 100,000 |
| --- | --- | --- |
| 48,003 | accepted | accepted |
| 60,015 | `malformed / CODE_TOO_LONG` | **accepted** |
| 90,023 | `malformed / CODE_TOO_LONG` | **accepted** |

The cap is configuration. This is the third instance of the rail-3b error class
(a hard limit inferred from one insufficient experiment), and the most
expensive: the largest certificate the corpus ships is 45,288 bytes
(`evaluation_order5_0076`, `true:egg_collapse`) — 91.5% of the old 49,500-byte
working cap. The generative engines were pressed against a ceiling that was half
real, and every rejection was *silent*, because all these gates fail closed and
discard the certificate before the row is recorded.

`judge_rows.py` now sets the production values, so local ground truth is
configured like the ground.

## Changes

### Solver

| constant | was | now | why |
| --- | --- | --- | --- |
| `JUDGE_MAX_CODE_LENGTH` | 50,000 | 100,000 | config.json |
| `JUDGE_MAX_FALSE_CERT_BYTES` | 10,000 | 20,000 | config.json |
| `EGG_MAX_PROOF_BYTES` | 46,000 | 96,000 | derived from the above |
| `MAX_WITNESS_DECIDE_APPLICATIONS` | 20,000 | 50,000 | re-derived against 300 s |
| `LLM_HTTP_TIMEOUT_SECONDS` | 75 | 300 | see below |
| `SOLO_FALLBACK_RESERVE_SECONDS` | 90 | 310 | one 300 s judge call + margin |
| `SOLO_LLM_ROUND_MIN_SECONDS` | 150 | 620 | one LLM + one judge call + margin |

Plus four behavioural fixes:

- **`LLM_HTTP_TIMEOUT_SECONDS = 75` aborted 225 of the 446 real gpt-oss-120b
  calls logged in `stage2/results/`** — the median call in the one raised-cap
  run was 87.3 s. An abort is worse than a slow call: the solver drops the
  socket but the proxy stays inside `forward_upstream` (600 s), finishes the
  generation and settles the usage, so the tokens are spent, the row is lost
  permanently, and nothing is logged. A plausible contributor to several
  sessions of "the LLM lane gets zero accepts".
- **Rail 10 was re-armed one function later.** `reset_memory_reclaims()` was
  called per row in the deterministic loop but never in the Marathon LLM lane,
  so the lane inherited whatever the last deterministic row left behind — which
  can be zero. With no reclaims left, `deadline_expired()` short-circuits on the
  memory guard and every engine bails on entry, logging
  `guided_chain_unproved_or_bad_endpoints` instead of the real cause. This is
  verbatim the shape that scored 287/1000 in the 08-01 campaign, and equally
  invisible to `audit_corpus.py`, which never arms the guard.
- **`constraint_countermodel_wide_domain` searched orders it could never use.**
  On a 3-variable goal, orders 40/50/60 cost 64,000 / 125,000 / 216,000 decide
  applications and are vetoed by `witness_decide_is_affordable` *after*
  `_cp_search` has spent its full per-order budget building a table. Up to
  1,760 s per row at `deep`, on the last-resort path, taken directly out of
  other rows under Marathon's per-row budget. The cost gate now runs before the
  search. Exhaustion-neutral, so it cannot license a speculative TRUE.
- **`LLM_CONFIG["model"]` was hardcoded**, and the official helper's precedence
  is `cfg.get("model") or os.environ["JUDGE_MARATHON_MODEL"]` — so the
  organizers' documented knob was unreachable. The published spec lists a second
  model (`google/gemma-4-31b-it`); requesting the wrong one is billed at the
  full token reservation even when rejected.

And two robustness fixes: `main()` had no top-level handler (garbage on stdin
gave a traceback and exit 1 with no answer at all — rail 11's failure class one
level up the stack), and one `DISTILLED_CERTS` entry carried verdict
`"false_code"`, reaching the wire correctly only via a coercing else-branch.

### Build and CI — both steps were red

- `ruff check .` exited 1 with **443 errors**, all from `.git/logs/errorsaug.py`
  — a pasted playground error log saved with a `.py` extension inside `.git`.
  Root cause: `ruff.toml` used `exclude`, which **replaces** ruff's built-in
  defaults (including `.git`) rather than adding to them. Now `extend-exclude`;
  the stray file was removed.
- The size gate asserted the 500 KB cap on `stage2/solver/solver.py`. That is
  the **source** (529,700 bytes at HEAD) and is legitimately over the cap since
  it carries the comments; the deliverable is the minified artifact. CI now
  *builds* the artifact and checks that, which also exercises the packaging path
  on every push. It runs Python **3.11** to match the `python:3.11-slim`
  sandbox (was 3.12 — nothing had ever run the solver on the interpreter that
  grades it), and a new step pins the solver's judge constants to config.json so
  this drift cannot recur silently.
- `package_solver.ps1` wiped `stage2/submissions/` *before* running the
  minifier, so any failure left no artifact — and none in git either, since it
  is gitignored. It also left an oversized artifact in place while throwing
  "refusing to package". Now builds to a temp file and swaps in only after the
  size check passes, then asserts the directory holds only `solver.py` (the
  official Solo runner rejects extras, and `__pycache__` appears there easily).
- `minify_submission.py` applied its two line transforms **inside multi-line
  string literals**, rewriting their content. `DISTILLED_CERTS` stores every
  certificate as triple-quoted Lean, so one cert carrying a trailing space or a
  three-blank-line gap would have failed the parse-tree check and bricked
  packaging. Now string-aware, and `check()` names the first differing top-level
  statement instead of a bare message.

### Gate coverage

Two new tests. `DISTILLED_CERTS` — 65 entries, the largest block of emitted Lean
in the file — had **no direct test**: the static banned-tactic scan skips any
line without a literal `\n`, which excludes every triple-quoted certificate
body. The new test checks every entry for banned tactics, size caps and a valid
verdict, and caught the `false_code` bug immediately. The second test pins the
solver's judge caps to the vendored config.

## Verification

| check | result |
| --- | --- |
| offline gate | **254 passed, 2 skipped** (was 252) |
| isolated audit, row-id diff vs `audit-2026-08-12-final.json` | **1869/1869 identical — 0 lost, 0 gained**, TRUE 919, FALSE 950, 0 oracle failures, 0 crashes |
| official Solo runner + real Lean judge, `sample_20` | **20/20 solved, 0 failed**, every row accepted on its first judge call, 0 LLM calls, 112.8 s |
| Marathon, packaged artifact, 12-row manifest | 12/12 answered, payload exactly `{id, verdict, code}`, 6 route kinds |
| spotcheck, 9 sources | **90/90, 100% accuracy, 100% coverage, 0 mistakes** |
| ruff | clean |

The audit's only movement was **5 route changes**, all TRUE closure-engine
reshuffles (`hard2_0168`, `hard3_0208`, `normal_0404`, `normal_0692`,
`normal_0926`) — the budget-marginal noise rail 2 describes. **No FALSE witness
changed**, which is where the raised caps could have churned.

Audit written to `stage2/results/audit-2026-08-13-limits.json`.

## Corpus total: 2689 was a double-count

`2689 = 1669 + 800 + 200 + 20` adds `sample_20` on top of the sets it is drawn
from. Measured: **`sample_20` is a strict subset of `normal`** (all 20 rows, by
`(eq1_id, eq2_id)`), and `sample_20 ∩ sample_200 = 0`. Separately, official ∩ HF
`evaluation_*` is **0** by id and by canonical content — the mirrors do not
overlap the official sets, which is a different thing and worth not conflating.
The distinct total is **2669**.

## Ordered completion is now in version control

CLAUDE.md called it "the durable result worth carrying forward" and told the
next session to run it first on any fresh corpus. It had **0 files tracked**
(`.gitignore` excludes `tmp*/`), and its `render.py` had an absolute path baked
in pointing at a *different session's* OS temp directory — reproducible on one
machine, by luck. Now at `stage2/experiments/completion/`, with the repo root
derived from the file's own location. Verified: `normal_0491` → 1,321-byte
`lemma_chain` certificate, **KERNEL OK**, matching the judge-accepted artifact.

Its known defect is documented and reproducible in one command: a derived
collapse (`x = y`, two distinct variables) gets no orientation from
`Eq.__init__`, so it never becomes a rewrite rule and `joinable()` — which works
by normalization — can never use it. On `hard2_0073` the collapse falls out in
0.0 s as `E12` and is then discarded. That is the blocker on 5 of the final
nine. Not fixed here: it is an algorithmic change and belongs with its own judge
verification, not a QA pass.

## Left undone, deliberately

- **Rail 6 is violated in the shipped Marathon LLM lane.** CPU-bound
  certificate construction (`solver_analysis`, `candidate_from_llm_text_with_reason`,
  which runs `guided_chain_certificate_from_terms` — the function whose comment
  records 21.5 GB RSS) runs inside the same 8-worker `ThreadPoolExecutor` as the
  network calls, on a 2-vCPU sandbox. The fix is the two-phase split rail 6
  already prescribes; it is a restructuring, not a constant.
- Nothing has been re-measured *against* the corrected caps. Every coverage and
  route-attribution number in the docs still describes a solver that discarded
  certificates over 49.5 KB. The audit above proves nothing was lost; it does not
  probe what the extra headroom now buys.
- `MAX_WITNESS_ORDER` is still 25 while both real bounds now sit well above it
  (~82 on bytes, 36 on decide for a 3-variable goal). Raising it needs
  real-judge evidence per rail 3c.
- The repo has **no LICENSE file**.
