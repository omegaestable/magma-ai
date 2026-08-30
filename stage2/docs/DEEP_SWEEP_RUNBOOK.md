# Deep sweep runbook

Written 2026-08-27, at the end of improvement pass 2. This is the **operational**
handover for the remaining deep sweeps: exact commands, in the order you run
them, with the traps that have already cost sessions. The *why* is in
`CLAUDE.md` (rails) and `stage2/docs/DEEP_SWEEP_ROADMAP.md` (design and cost
model); the *what to measure next* is in `stage2/docs/NEXT_SESSION_BRIEF.md`.

Every command below was run with `--help` on 2026-08-27 and the flags are as
printed. Paths are repo-relative; run from the repo root with
`PYTHONIOENCODING=utf-8` set (`◇` crashes on Windows cp1252).

```powershell
$env:PYTHONIOENCODING = "utf-8"
$PY = ".\.venv311\Scripts\python.exe"
```

---

## 0. Before you start anything

1. **Confirm nothing else is running.** `Get-Process python*` must be empty.
   Rail 5e (never two audits at once), rail 15 (killing a sweep does not kill
   its worker pool), rail 22 (your own parallel agents count). A ledger audit
   read **60/218 under load and 167/218 isolated with the same code**.
2. **Diff the vendored harness against upstream** (rail 14):
   `gh api repos/<upstream>/compare/<UPSTREAM.md snapshot>...HEAD`. A stale
   snapshot fails nothing while invalidating everything. After any sync, re-run
   the judge-parity smoke (a TRUE cert, a table FALSE cert, the infinite-ℕ cert)
   and re-verify the local Windows patches in
   `vendor/stage2-official/UPSTREAM.md`.
3. **Record the worker count and the machine load next to every wall clock**
   (rail 19). Coverage numbers survive load; timing numbers do not.

### The kill-everything recipe (rail 15)

```powershell
# 1. the chain shell (it can relaunch a batch before it dies)
Get-CimInstance Win32_Process | Where-Object {
  $_.CommandLine -like '*sweep_chain.sh*' -and $_.Name -eq 'bash.exe'
} | ForEach-Object { taskkill /F /T /PID $_.ProcessId }
# 2. any audit worker pool
Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Where-Object {
  $_.CommandLine -like '*audit_corpus*'
} | ForEach-Object { taskkill /F /T /PID $_.ProcessId }
# 3. THEN confirm
Get-Process python*   # must print nothing
```

---

## 1. Sampling a batch

### Order-4 (the full ETP outcome matrix, 22,028,942 labelled pairs)

```powershell
& $PY stage2/experiments/sample_etp_matrix.py `
    --count 10000 --seed 20260828 `
    --exclude stage2/results/etp-sample-*.jsonl `
    --out stage2/results/etp-sample-20260828-b01.jsonl
```

`--exclude` takes any number of prior batch jsonl/json files and drops their
`(eq1_id, eq2_id)` pairs, so batches stay disjoint. **Always pass every prior
batch** — an unseen-row measurement that quietly re-draws seen rows is not one.
The exclusion set is maintained incrementally (rail 17): 100,000 rows takes
~5.5 s, and the O(n²) version this replaced had not finished 100,000 in 10 min.

Rows carry ground-truth labels from the matrix, so an order-4 sweep measures
**label mismatches** as well as coverage. Nothing else does.

### Order-5 (generated pairs from the vendored catalog, no labels)

```powershell
# the ≤3-variable population every prior sweep used
& $PY stage2/experiments/sample_order5_pairs.py `
    --count 20000 --max-variables 3 --seed 20260828 `
    --exclude stage2/results/order5-sweep-*.jsonl `
    --out stage2/results/order5-20260828-le3var.jsonl

# THE UNMEASURED HALF: ≥4 variables (rail 33)
& $PY stage2/experiments/sample_order5_pairs.py `
    --count 2000 --min-variables 4 --max-variables 7 --seed 20260828 `
    --out stage2/results/order5-20260828-ge4var.jsonl
```

`--min-variables` is new on 2026-08-27 and exists because **every order-5 sweep
on record ran at `--max-variables 3`, while 56.9% of `eq_size5.txt`'s 62,576
laws have ≥ 4 variables** (counts 1..7 = 97 / 4,937 / 21,956 / 24,547 / 9,565 /
1,408 / 66) and the only local proxy for the private Order-5 category,
`data/hf_cache/evaluation_order5.jsonl`, is 50% ≥ 4 variables and exactly
100 TRUE / 100 FALSE. So the 98.24% order-5 figure describes one stratum.
A 250-row batch is already generated at
`stage2/experiments/order5-ge4var-250-2026-08-27.jsonl` (seed 20260827, both
sides drawn from the 35,586 catalog laws with ≥ 4 variables) — audit that first,
it is the cheapest read on the question. **Label every number from it
`stratified: variables >= 4`** (rails 18, 33).

Other flags that matter: `--catalog` / `--goal-catalog` (draw eq2 from a
*smaller* catalog — same-catalog draws at high order are almost pure FALSE),
`--id-prefix` (e.g. `order6`), `--goal-max-variables` / `--goal-min-variables`.

### Order-6 and any high-order batch: stratify, do not draw uniformly

```powershell
& $PY stage2/experiments/generate_eq_catalog.py --ops 6 --max-variables 3 --out <order6.txt>
& $PY stage2/experiments/sample_order5_pairs.py --catalog <order6.txt> --id-prefix order6 ...
& $PY stage2/experiments/filter_hard_region.py `
    --in  stage2/results/order6-raw.jsonl `
    --out stage2/results/order6-hard.jsonl `
    --target 500 --workers 3
```

`filter_hard_region.py` keeps the pairs an **independent** small-model search
cannot refute (~14.2% survive at order 6). Two 200-row uniform order-6 (≤2 var)
pilots came back **200/200 FALSE with a p50 of 8 ms** — a uniform draw there
measures the named-witness table and nothing else (rail 18). Report the result
as **stratified**; its solve rate is not comparable to a uniform sweep's.

---

## 2. Auditing a batch

```powershell
& $PY stage2/experiments/audit_corpus.py `
    --file stage2/results/etp-sample-20260828-b01.jsonl `
    --effort fast --row-budget 60 --workers 3 `
    --out stage2/results/audit-etp-sample-20260828-b01.json
```

- `--file` takes an arbitrary jsonl/json problem file (`--set` / `--all` /
  `--hf` are for the built-in corpora).
- **`--row-budget` is not optional when you are measuring a deployed tier**
  (rail 12). Solo and Marathon always bound a row; the audit does not unless
  told to, so `--effort standard/deep` without it measures a solver no runner
  will ever be. Marathon ≈ `--effort standard --row-budget 540` (the borrow
  ceiling around a ~300 s fair share); Solo ≈ `--effort deep --row-budget 1980`.
- `--workers`: **cap at 3 while other agents share the box** (rail 22). The
  sweep chain used 16 (~100% sustained) and then 20 (~88%) of 32 logical CPUs
  on an otherwise idle machine; never average wall clocks across worker counts
  (rail 19).
- One audit at a time (rail 5e). `stage2/experiments/sweeps/sweep_chain.sh`
  runs a sequence *sequentially* and resumes rather than redoes; its header
  carries the kill recipe.

Reproduce any surprising single-row result standalone, three clean repeats, same
route, before calling it a regression.

---

## 3. Reporting

```powershell
& $PY stage2/experiments/sweep_report.py `
    --audit stage2/results/audit-etp-sample-20260828-b0*.json `
    --batch stage2/results/etp-sample-20260828-b0*.jsonl `
    --baseline stage2/results/audit-2026-08-27-final.json `
    --out-prefix stage2/results/sweep-20260828
```

Several `--audit` reports merge into one measurement (that is how a 10 × 10k
sweep is read). `--batch` supplies equation text and ground-truth labels.
`--baseline` diffs **by row id** (rail 2) — never compare totals, which carry a
±7 noise band.

Add `--diagnose` to re-run every failed row with per-engine timing
(`--diagnose-budget`, `--diagnose-effort`, `--diagnose-limit`). That profile is
how the "wide countermodel search is 37–76% of an unsolved row's clock" number
was measured; it is the right first move on any new frontier.

---

## 4. Real Marathon on a batch

```powershell
$K = (Select-String -Path .env -Pattern '^OPENROUTER_API_KEY=').Line -replace '^OPENROUTER_API_KEY=',''
$env:OPENROUTER_API_KEY = $K; $env:OPENAI_API_KEY = $K
& $PY stage2/experiments/run_marathon_batch.py `
    --manifest stage2/results/etp-hardtest-20260828.jsonl `
    --output-dir stage2/results/marathon-20260828
```

Now tracked in the repo (it lived only in gitignored `tmp_stage2_smoke/` until
2026-08-27; the originals are still there). It imports `local_runner_env`, whose
`judge_cap_env()` **reads the deployed caps out of `pipeline/config.json`**
rather than copying them — without it `judge/verify.py` falls back to
50,000 / 10,000 / 120 and you score against a phantom judge (rail 3b-iv: an
88,539-byte certificate came back `malformed` at 50,000 and `accepted` at
100,000, turning a real 200/200 into a reported 199/200). It asserts
`MAX_CODE_LENGTH` is present and fails loudly if not, and it prepends
`~\.elan\bin` to `PATH`, which a detached process does not inherit.

Flags: `--budget-tokens`, `--budget-seconds`, `--score-only`, `--no-score`.
A Marathon launched from an agent session **dies with that session's console**
(exit `0x40010004`); `answers.jsonl` is append-only, so recover with
`--score-only` and run the unanswered rows as a second manifest — **never
re-solve what is already on disk**. Solo equivalent:

```powershell
& $PY stage2/experiments/run_solo_batch.py --problems <jsonl> --output <jsonl> [--limit N]
```

Never quote a `--budget-tokens 0` run as validation evidence (rail 7).

### Modelling the sandbox

```powershell
& $PY stage2/experiments/sandbox_limits_wrapper.py --cpus 2 --memory-mb 2048 -- <command...>
```

The graded sandbox is 2 vCPU / 2048 MB; deep-tier closures have been measured at
5–17 GB RSS and were OOM-killed there. Use the wrapper before believing a
timing or memory number taken on the 32-core box.

**Budget context**: the 1000-row hard Marathon spent **5,048 s of 300,000 s**
and 10.8k of 32.8M tokens (rail 29). Wall clock has never been Marathon's
binding constraint; the per-row budget is.

---

## 5. Judging the misses

```powershell
# rows the solver solves live (needs vendor/stage2-official/.lake -- main tree only)
& $PY stage2/experiments/judge_rows.py --ids etp_1234_5678,order5_1_2 `
    --problems stage2/results/etp-sample-20260828-b01.jsonl
# certificate text you already have (works from a worktree with no Lean build)
& $PY stage2/experiments/judge_cert_text.py --in certs.jsonl --out judged.jsonl
```

`judge_rows.py --problems` is what resolves ids from a *generated* batch — the
built-in catalog only knows the official and HF sets. `--from-audit` +
`--per-route N` + `--shape other` is the pattern that pins one certificate per
route family, which is how the 10 families with no offline *and* no judge
evidence were closed 10/10.

`judge_cert_text.py` takes rows
`{id, equation1, equation2, eq1_id, eq2_id, verdict, code}`, applies the
deployed caps (100,000 / 20,000 / 300 s) and prints `accepted N/M`. **One judge
process at a time**; each call is 3–40 s.

Pinning: `--append-fixture`, never `--write-fixture` (which REPLACES the file —
rail 16). Fixture rows must carry their own `equation1`/`equation2`/eq ids, or
they resolve to nothing and the test **skips** instead of failing. After any
fixture change, **compare the gate's SKIP count, not just its pass count**.

---

## 6. The z3 witness harvest loop (the productive FALSE lever)

```powershell
# 1. hunt countermodels for the misses
& $PY stage2/experiments/z3_witness_search.py `
    --rows stage2/results/order5-misses.jsonl `
    --orders 5,6,7,8,9 --timeout 45 --procs 3 `
    --out stage2/results/z3-witnesses-20260828.jsonl
# 2. greedy set-cover: which few tables cover the most rows
& $PY stage2/experiments/witness_library_eval.py `
    --witnesses stage2/results/z3-witnesses-20260828.jsonl `
    --library stage2/results/teorth-finitepoly-library.jsonl `
    --targets stage2/results/order5-misses.jsonl `
    --out stage2/results/witness-library-20260828.json
# 3. ship the selection into O5_WITNESS_TABLES / FP_WITNESS_TABLES, judge a
#    sample of the rendered certs (section 5), pin the accepted ones.
```

Measured 2026-08-27: 13 z3 tables / **2,091 bytes** cover **122 of 398 (30.7%)**
order-5 misses, cross-validated on a *disjoint* sample (3 tables / 513 B cover
57/351, spanning 42 distinct eq1 ids), 122/122 re-verified by
`stage2/tests/oracles.py` `equation_holds` (which shares no code with the
solver), and 3/3 rendered certs real-judge accepted at 426–462 bytes. Scanning
costs ~3 µs per (row, table), so a 300-table library is ~1 ms per row. **Not
saturated**: z3 over 100 further held-out misses these tables miss found 17 more
FALSE, all at order 9.

Two sources that are **spent** — do not re-run them (numbers in `CLAUDE.md`'s
dead-ends table): the rest of teorth's 1,048-table FinitePoly library (worth 2
rows of 351 for order 5; `select_witness_library.py` is the set-cover over it,
fed by `teorth_finitepoly_library.py`, which extracts the tables), and random
Latin squares (800 of orders 8–9 satisfy **0** of 280 order-5 hypotheses).

---

## 7. The mined-law loop

```powershell
# 1. probe protocols against real LLM calls, harvesting every law the SOLVER can prove
& $PY stage2/experiments/llm_protocol_probe.py `
    --file stage2/results/order4-residual.jsonl --protocols A2 `
    --model openai/gpt-oss-120b --reasoning low --workers 3 `
    --out stage2/results/llm-probe-20260828.json
# 2. scan the harvested laws over the open rows, deterministically
& $PY stage2/experiments/mined_law_scan.py `
    --rows stage2/results/order4-residual.jsonl `
    --laws stage2/results/mined-laws.json --budget 2.0 --workers 3 `
    --out stage2/results/mined-law-scan-20260828.json
# 3. ship the winners into MINED_LEMMA_LIBRARY_TEXT; judge one cert per law family.
```

Measured 2026-08-27: 31 mined laws (of 33 harvested, 31 outside
`full_lemma_library()`'s 601 entries) close **19 of 51** order-4 residual rows
the full solver misses at 420 s/row, 0 oracle failures, ~6 s/row on 4 workers;
3/3 real-judge accepted. One law — `x ◇ y = (z ◇ (x ◇ z)) ◇ y` — closes all 17
residual eq1-`3983` rows. Two of the three best are outside
`enumerated_lemma_library()`'s grammar entirely (it only emits laws whose LHS is
`a` or `a ◇ b`), which is why the ladder could never find them.

**Do not point this loop at order-5.** 6 protocols × 20 collapse-bucket rows =
120 calls, 0 settled; the 31 mined laws over 80 order-5 misses = **0/80** in
1199 s, at ~60 s CPU/row (vs ~6 s on order-4) because `lemma_survives_models`
rejects nothing when eq1 has no small non-trivial model.

LLM caveats when you spend real calls: the key in `.env` expires — check it
first; keep `--reasoning low` (medium is 2.8× tokens, 7× wall, same rows); and
the model's **verdict follows the prompt framing, not the mathematics**
(148/148 TRUE under TRUE-framed prompts, 24/24 FALSE under a FALSE-framed one,
0 valid tables either way — rail 30). Choose the direction from solver evidence.

---

## Per-batch checklist

Copy this into the results doc for each batch.

- [ ] `Get-Process python*` empty before launch; nothing else scheduled on the box
- [ ] batch drawn with every prior batch in `--exclude`; seed recorded
- [ ] stratum recorded (`uniform`, `variables >= 4`, `hard-region filtered`, …)
- [ ] `--effort` and `--row-budget` recorded, and they model a real runner (rail 12)
- [ ] **worker count and machine load recorded next to every wall clock** (rails 19, 22)
- [ ] audit diffed **by row id** against a named baseline (rail 2): lost / gained / flips
- [ ] oracle failures, crashes, label mismatches all reported (0 is a result, not a silence)
- [ ] any surprising loss reproduced standalone, 3 clean repeats, same route (rail 5e)
- [ ] misses classified (family? variable count? operations?) before proposing a lever
- [ ] new certificate shapes real-judge checked and `--append-fixture` pinned (rails 3c, 16)
- [ ] gate re-run: pass count **and skip count** compared (rail 16)
