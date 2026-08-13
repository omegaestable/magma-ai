# magma-ai

A lab for the **SAIR Mathematics Distillation Challenge, Equational Theories
Stage 2** (organized by Damek Davis and Terence Tao, SAIR Foundation).

The task is equational implication over magmas: given equation 1 and equation 2
over a single binary operation, decide whether equation 1 implies equation 2 —
and **prove it**, with a Lean 4 certificate a deterministic judge accepts. No
partial credit, no probabilistic scoring.

Deadline: **2026-08-31 23:59 AoE**.

`stage1/` is a finished archive of the Stage 1 prompt-cheatsheet work. New work
happens in `stage2/`.

---

## The deliverable

One file: `stage2/submissions/solver.py`.

| Constraint | Value |
| --- | --- |
| Size | ≤ 500,000 bytes |
| Dependencies | Python standard library only — no third-party packages, no repo-local imports |
| Network | none directly (the organizer proxy is the only channel) |
| Secrets | none inherited |

It emits two kinds of certificate:

- **TRUE** — a Lean 4 proof that `equation1 ⇒ equation2`.
- **FALSE** — a magma satisfying `equation1` but not `equation2`. The goal shape
  is `∃ (G : Type) (_ : Magma G), EquationLHS G ∧ ¬ EquationRHS G`, with **no**
  `Finite`/`Fintype` constraint. We ship finite witnesses (a Cayley table plus
  `decideFin!`) almost everywhere; infinite carriers are legal and used once.

The artifact is a build output (`stage2/submissions/*.py` is gitignored). Build
it with `stage2/solver/package_solver.ps1`, which runs the offline gate first and
refuses to package on failure.

---

## Official evaluation spec

Authoritative source: `vendor/stage2-official/pipeline/config.json` (the values
the harness actually passes to the judge) and `vendor/stage2-official/rules/`.
The snapshot vendored here is commit `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.

### Sandbox, per submission

`python:3.11-slim` · 2 vCPU · 2048 MB RAM · 64 PIDs · `/tmp` a 64 MB tmpfs ·
read-only filesystem · all capabilities dropped · env allowlist
`PATH`/`HOME`/`LANG`/`PYTHONDONTWRITEBYTECODE`.

The 2048 MB ceiling is load-bearing, not decorative: deep-tier closure engines
have been measured at 5–17 GB RSS and were OOM-killed in the sandbox before a
memory guard was added.

### Tracks

| Track | Workload per process | Budget | I/O |
| --- | --- | --- | --- |
| **Solo** | one problem per solver subprocess | fixed per problem | stdin problem JSON / stdout answer JSON |
| **Marathon** | N problems per subprocess (reference N=100) | one shared global budget; SIGTERM at the budget and the output JSONL is frozen at that moment | manifest JSONL in / append-only JSONL out |

One source file serves both. Marathon **cannot call the judge** —
`marathon_runner.py` spawns the solver with `stdin=subprocess.DEVNULL` and
`marathon_proxy.py` serves only `/v1/chat/completions`. Solo keeps its judge
channel.

### Budgets and judge limits

| Resource | Value | Source |
| --- | --- | --- |
| Solver wall clock, per problem | 3600 s | `config.json` `solver.timeout_seconds` |
| Marathon, per problem on average | ~300 s (5 min) | organizer clarification 2026-07-31; `scripts/run_marathon.py` uses a 600 s reference → 30,000 s at N=100 |
| Lean judge, per call | **300 s** | `config.json` `judge.lean_timeout_seconds` |
| Lean code, per call | **100,000 bytes** | `config.json` `judge.max_code_length` |
| FALSE certificate, per call | **20,000 bytes** | `config.json` `judge.max_false_cert_bytes` |
| LLM max output tokens, per call | 65,536 | `config.json` `llm.max_output_tokens` |

The proxy clamps the judge timeout to `min(config cap, wall-clock remaining)`,
so a certificate gets the promised 300 s only when 300 s are left.

LLM lane: `openai/gpt-oss-120b` and `google/gemma-4-31b-it`, OpenRouter pinned to
DeepInfra, provider fallback disabled, `temperature = 0.0`, `seed = 0`. The model
is selectable through the organizers' `JUDGE_MARATHON_MODEL` environment
variable.

### Judge statuses and proof policy

`accepted` · `unparsed` · `malformed` · `incomplete_proof` · `incorrect`. A
problem is solved when the judge returns `accepted`.

Allowed trusted axioms: `propext`, `Quot.sound`, `Classical.choice`. Proofs using
`sorry`, `admit`, or disallowed axioms/declarations come back `incomplete_proof`.
Declarations are checked against a per-problem allowlist.

### Where the vendored rules text is stale

Two places, both verified against the snapshot rather than assumed:

1. **Marathon budget.** `rules/evaluation.md` still derives a global budget from
   `compression_ratio × N × 3600 s` (180,000 s at N=100). `compression_ratio`
   was **withdrawn as misleading** in the 2026-07-31 organizer clarification;
   the CLI has always used a 600 s reference. Treat the rules file as stale here.
2. **Judge limits.** `judge/verify.py` carries 50,000 / 10,000 / 120 s as
   *fallback* defaults for direct invocation with no config. Those are not the
   deployed limits — see below.

`rules/evaluation.md` still marks **Scoring** as TBD. We have not tried to
predict it; the working assumption is the stated baseline intent, that higher
accepted counts are better.

### The judge-limit correction (settled by experiment, 2026-08-13)

For two weeks this repo enforced 50,000-byte certificates, 10,000-byte FALSE
certificates and a 120 s Lean timeout. All three were wrong — they were
`verify.py`'s no-config fallbacks, not the deployed configuration. The original
"evidence" for halving the caps was a measurement taken through
`stage2/experiments/judge_rows.py`, which called `verify_answer()` with no
config and therefore measured the fallback against itself.

One certificate, judged twice, with only the configured cap varying:

| Certificate size | Cap 50,000 | Cap 100,000 |
| --- | --- | --- |
| 48,003 bytes | accepted | accepted |
| 60,015 bytes | `malformed` / `CODE_TOO_LONG` | **accepted** |
| 90,023 bytes | `malformed` / `CODE_TOO_LONG` | **accepted** |

The cap is configuration, not a property of the judge. The solver constants,
the offline oracles and `judge_rows.py` now all match `config.json`, and CI
asserts that they still do, so this drift cannot recur silently.

The generalizable lesson — this was the third instance of it — is in `CLAUDE.md`
rail 3b: **check whether a "judge limit" is actually the judge's before building
a rail on it**, and vary an experiment once before writing an impossibility
down.

---

## Architecture

`stage2/solver/solver.py` — 10,308 lines (2026-08-13), single file by contract.

**Route ordering is load-bearing.** `solve_problem()` dispatches through a fixed
cheap-to-expensive order, so rows that a syntactic route can claim never pay for
the hungry search engines. Everything after the cheap tiers runs only on rows
nothing earlier claimed.

- **Recognised law families are data, not code.** A family is one
  `law_matcher(pattern, args, ...)` table row; the law text in the row is the
  same string the certificate emits, so the two cannot drift. This replaced 37
  bespoke matchers, proved equivalent over the entire real input domain first.
- **TRUE engines**, in order: `egg_probe`, `equational_closure`,
  `deep_absorption_closure`, `derived_cp_closure`, `projection_bootstrap`,
  `lemma_bootstrap`, `lemma_chain_bootstrap`, `egg_closure`, `egg_collapse`,
  `egg_priority_bootstrap`, `egg_bootstrap`, `egg_ladder`, then a demoted
  `narrow_grind`. `egg_ladder` is the only one that reasons with more than one
  law at a time: it derives a small law from eq1, binds it with `have`, and
  saturates again with that law in scope.
- **FALSE search**: named compact witnesses → structured/affine/quadratic
  families → bounded `Fin 2..3` enumeration → a cheap Mace4-style constraint
  propagation tier → [TRUE engines] → randomized `Fin 4..6` repair search → a
  wide constraint tier. Witness order is bounded by rendered bytes and `decide`
  cost (`n ** variables`), not by carrier size as such.
- **`DISTILLED_CERTS`** maps *canonical equation text* — renaming-invariant, so
  one entry covers the official row, its `*`-notation mirror, and any future
  sample of the same implication — to a judge-accepted certificate. It is keyed
  by mathematical content, never by benchmark row id, and every entry is
  byte-pinned in `stage2/fixtures/judge_verified_certs.jsonl`.
- **`EFFORT_TIERS`** scale time and search caps together. Solo and Marathon pick
  a tier from their real budget. `solve_problem` walks the tier ladder cheapest
  first rather than jumping to the top tier — more budget applied naively made
  the solver measurably *worse*, because early engines ate the per-row clock
  before a late engine was reached.
- **`_engine_gate()`** is checked before every engine and enforces the global
  hard deadline plus the memory guard.

The single most productive idea in the whole project: **proof-search cost scales
with goal size, so a small law that implies the goal can be reachable when the
goal is not.**

---

## How correctness is enforced

Two layers, because the cheap one is only an upper bound.

**Offline (`stage2/tests/`, no Lean needed).** These tests deliberately **share
no code with `solver.py`**, so a bug in a solver primitive cannot hide itself in
the oracle.

- A `ProofKernel` independently evaluates the restricted Lean grammar the
  builders emit (`h t1..tk`, `.symm`, `.trans`, `congrArg`, `rfl`) down to the
  equation it actually proves. A TRUE certificate passes only if it proves
  *exactly* `eq2.lhs = eq2.rhs`.
- A finite-model oracle builds magmas satisfying eq1 and refutes any unsound
  TRUE verdict. Known limit: the trivial one-element magma satisfies every
  equation, so `nontrivial_model_count()` is the number that matters, and laws
  that force a singleton can only be proof-checked.
- `check_no_banned_tactics()` rejects `grind`/`simp`/`aesop` in emitted
  certificates.
- `test_golden.py` pins real rows to the route family that solved them, catching
  coverage loss, engine drift and soundness loss.
- `spotcheck.py` draws randomized balanced batches across 8 benchmark sets plus
  the ETP outcome matrix (~22M labelled pairs the solver was never tuned on) and
  auto-pins any mistake into the gate forever.

**The real Lean judge** is ground truth, and the only thing that is not an upper
bound. It runs locally on Windows via `elan` — despite the official docs saying
WSL/Linux only:

```powershell
.\.venv\Scripts\python.exe stage2/experiments/judge_rows.py --ids hard2_0080,normal_0747
```

Roughly 3–8 s per row warm. Touch a certificate builder and you owe this run: a
locally-sound witness is not automatically a *renderable* one, and every offline
check reads the parsed Python table, blind to the emitted text.

---

## The four commands

```powershell
# 1. Correctness gate. Run before AND after any solver change.
.\.venv\Scripts\python.exe -m pytest stage2/tests -q -n auto

# 2. Full corpus audit (official sets; add --hf for the HF mirrors).
#    Run it once per session, never two at once — concurrent sweeps starve each
#    other's wall-clock-budgeted engines and produce spurious "losses".
#    Add --row-budget when measuring a tier you actually deploy: Solo and
#    Marathon always bound a row, the audit does not unless told to.
.\.venv\Scripts\python.exe stage2/experiments/audit_corpus.py --all --out stage2/results/audit-<date>.json

# 3. The standing accuracy loop. Run it every session; fix whatever it pins.
.\.venv\Scripts\python.exe stage2/experiments/spotcheck.py

# 4. Package (re-runs the gate and refuses to package on failure).
.\stage2\solver\package_solver.ps1
```

---

## Current measured state

Every number carries its date. Coverage figures are from a **fresh isolated
audit** at `fast` tier; see the caveat below before quoting any wall clock.

| Metric | Value | Measured |
| --- | --- | --- |
| Official sets (`normal`+`hard1`+`hard2`+`hard3`) | **1669 / 1669** | 2026-08-12 |
| Official TRUE / FALSE | **819 / 819** and **850 / 850** | 2026-08-12 |
| HF mirror sets | **800 / 800** | 2026-08-12 |
| `sample_200` (an ETP sample disjoint from `normal`) | **200 / 200** | 2026-08-12 |
| Distinct rows solved | **2669** | 2026-08-12 |
| Oracle failures / crashes / label mismatches | **0 / 0 / 0** | 2026-08-12 |
| Offline gate | 252 passed, 2 skipped, ~24 s (`-n auto`) | 2026-08-12 |
| Packaged artifact | **445,640 of 500,000 bytes** (54,360 free, 10.9%) | 2026-08-13 |
| Solver source | 10,308 lines | 2026-08-13 |

State the corpus as its constituent sets — official 1669/1669, HF mirrors
800/800, `sample_200` 200/200, **2669 distinct rows**. An earlier headline in
this repo reported 2689: that sum also counted `sample_20`, whose 20 rows are a
strict subset of `normal` and so are already inside the official 1669. The HF
mirrors do not overlap the official sets at all (intersection 0). Corrected
2026-08-13.

**Real-judge evidence** — the only evidence that is not an upper bound:

| Run | Result | Date |
| --- | --- | --- |
| Certificates byte-pinned in `stage2/fixtures/judge_verified_certs.jsonl`, all re-checked by the gate | 99 | 2026-08-12 |
| Real Marathon on `hard3.jsonl` | 400/400 accepted, 0 rejected, 0 `not_attempted`, 0 LLM calls against a 200,000-token budget | 2026-08-12 |
| Real Marathon on 200 fresh ETP rows (seed `20260812`, benchmark ids excluded) | 200/200 accepted, 0 rejected, 0 tokens | 2026-08-12 |
| Earlier broad campaign across all 4 official + 5 HF sets + a 200-row ETP sample | 2863/2894 accepted, **0 rejected anywhere** | 2026-08-01/03 |
| Standing spotcheck loop, 108 rows across 9 sources | 100% accuracy, 100% coverage, 0 mistakes | 2026-08-12 |

**Timing caveat.** Part of the 2026-08-12 measurement ran against heavy
unrelated CPU load on the same machine. The *coverage* numbers are unaffected —
0 mismatches over thousands of rows does not come and go with load — but the
speedup figures from that session are **lower bounds, not precise
measurements**. Check what else is running on the box before quoting a wall
clock.

**Known gap.** Solo has no end-to-end real-runner evidence for the current tier
ladder. It runs `deep`, which is three passes, and nothing has exercised that
path end to end since the ladder landed (2026-08-12).

---

## Repository layout

| Path | Contents |
| --- | --- |
| `stage2/solver/` | the solver source, minifier and packager |
| `stage2/tests/` | the offline correctness gate (shares no code with the solver) |
| `stage2/experiments/` | audit, spotcheck, judging and discovery tooling |
| `stage2/results/` | dated session evidence — measurements, not narrative |
| `stage2/docs/` | route ledger, motif cards, handoffs, preflight |
| `stage2/fixtures/` | judge-verified certificates and regression pins |
| `vendor/stage2-official/` | vendored official judge, pipeline, docs and Lean package |
| `theory/` | Teorth data/proof/witness tooling and workflow notes |
| `data/exports/` | implication matrix and equation exports |
| `data/teorth_cache/` | Teorth graph, proof-page cache, witness/provenance data |
| `paper/` | math papers, TeX sources, reading material |
| `stage1/` | complete Stage 1 archive — reference only |

**Note on repo size.** The working tree is ~7.4 GB / 154k files;
`vendor/stage2-official/.lake` alone is 7.06 GB / 117,609 files of Lean and
Mathlib build cache. It is needed — but `du`/`find` at the repo root will hang.
Scope every search to a subdirectory.

---

## Quick start

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Printing `◇` crashes with `UnicodeEncodeError` on Windows cp1252 — prefix ad-hoc
scripts with `PYTHONIOENCODING=utf-8`, or run them through the repo's own
entrypoints, which set it.

LLM credentials are for **local experiments only**; the official solver
subprocess inherits no such variables and must not assume they exist.

```powershell
.\stage2\experiments\set_openrouter_repo_env.ps1   # -FromClipboard if terminal input is unreliable
```

The official harness setup script targets Linux/WSL:

```bash
cd vendor/stage2-official
bash scripts/setup.sh
source .env.judge
python3 scripts/run_harness.py
python3 scripts/run_marathon_harness.py
```

The local Lean judge itself does not need WSL — see the correctness section
above.

---

## Going deeper

| Need | Read |
| --- | --- |
| **Current numbers, the four commands, and the rails** | **`CLAUDE.md`** — the authoritative doc; if another doc disagrees with it, the other doc gets fixed |
| Latest session detail and ranked next levers | `stage2/docs/LATEST_HANDOFF.md` |
| Next session plan | `stage2/docs/NEXT_SESSION_BRIEF.md` |
| Operational truth, effort tiers, open rows | `CURRENT_STATE.md` |
| Route inventory | `stage2/docs/solver-route-ledger.md`, `stage2/docs/motif-cards/` |
| Offline gate design | `stage2/tests/README.md` |
| Spot-check design | `stage2/docs/spotcheck.md` |
| Before any upload | `stage2/docs/playground-preflight.md` |
| Official harness and runners | `vendor/stage2-official/`, `EVAL_WORKFLOW.md` |
| Teorth theory mining | `theory/TEORTH_WORKFLOW.md` |
| Agent role playbooks | `AGENTS.md` |

`CLAUDE.md`'s rails section is the highest-value read in the repo: each entry is
a mistake that cost measurable points, written down so it costs them once. The
most transferable ones are that a node cap alongside a time deadline is
redundant when harmless and wrong when it fires first (it bit four times), that
a deadline polled once per outer loop is not a deadline, that one shared clock
across a cheap-to-expensive portfolio starves whatever runs last, and that a
failed countermodel search is not evidence of TRUE.

---

## Open questions

- **There is no `LICENSE` file in this repository.** Nothing here states the
  terms under which the code may be used, and this section is not a licence.
  Before publication, a licence needs to be chosen and added — noting that
  `vendor/` and `stage1/` carry third-party material with their own terms.
- Upstream **scoring rules** are still marked TBD in the vendored rules
  snapshot.
- Solo end-to-end evidence on the current tier ladder is outstanding (above).

---

## External resources

- Stage 2 overview: <https://competition.sair.foundation/competitions/mathematics-distillation-challenge-equational-theories-stage2/overview>
- Stage 2 evaluation setup: <https://competition.sair.foundation/competitions/mathematics-distillation-challenge-equational-theories-stage2/evaluation-setup>
- Official Stage 2 repository: <https://github.com/SAIRcompetition/equational-theories-lean-stage2>
- Teorth Equational Theories Project: <https://teorth.github.io/equational_theories/>
- Teorth implication explorer: <https://teorth.github.io/equational_theories/implications/>
