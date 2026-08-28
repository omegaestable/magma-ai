# 2026-08-28 — Three assessments: full-deterministic?, the Austin set, repo tidiness

Companion to `2026-08-28-deterministic-pass-perf-and-bytes.md` (same day).
Every number is measured unless marked *estimate*.

## 1. Should the solver go fully deterministic?

**Recommendation: keep the LLM lane, exactly where it is (after every
deterministic engine and after the deterministic second pass), and do not
spend another session on it.** Dropping it buys simplicity and nothing
measurable; keeping it costs nothing measurable and has a small, real,
judge-verified upside. Details:

What the lane can and cannot do, per the organizers' docs re-read today:

- Solo (`docs/solo_mode.md` L82): the solver *may* issue `llm` requests; it is
  not required to. Marathon: the lane is gated on `budget_tokens != 0 and
  JUDGE_MARATHON_LIB_DIR` (`run_marathon`, solver.py ~L13148) and simply does
  not start otherwise. A fully deterministic run is therefore already what
  happens whenever the proxy is absent, and it is what every real Solo/Marathon
  verification run this week measured (7/7 Solo, 199/200 sandbox Marathon,
  both "deterministic-only — the key had expired").

What it has ever produced (all real-judge numbers, from `CLAUDE.md`):

| Period | Result |
| --- | --- |
| 2026-07 to 2026-08-26 | **0 / 433** accepted TRUE certificates from the lemma/chain protocols; the only accepted LLM rows were `llm:false:table` |
| 2026-08-27 (ladder protocol, `gpt-oss-120b`, low reasoning) | **3 / 37** hard-sample rows settled, 5 distinct `llm:true:ladder:goal` certs judge-accepted, 2 of them inside a real 20-row Marathon |
| Order-5 collapse bucket, 6 protocols x 20 rows | **0 / 120** |
| Token utilisation | 11.4 % of the Marathon token budget (was 1.3 % / 0.03 %) |

Expected value on the private set (*estimate*): the deterministic pass misses
~0.04 % of order-4 and ~1–2 % of order-5 rows; the lane settles ~8 % of hard
misses (3/37). That is on the order of **+0.1 % of the order-5 quarter of the
score**, i.e. a fraction of a row per 400. Small, but the sign is positive and
the evidence is judge-accepted certificates, not offline oracles.

What it costs:

- **Clock**: `MARATHON_LLM_TIME_RESERVE_SHARE = 0.2` (min 1200 s) is held back
  from the deterministic *second pass*. Marathon has never used more than ~2 %
  of its wall clock (rail 29; 5,048 of 300,000 s on the 1000-row hard run), so
  the reserve has never bound a row. If it ever does, the fix is to lower the
  reserve, not to delete the lane.
- **Bytes**: ~40 KB of source (`run_marathon`'s LLM half, `run_solo`'s LLM
  half, the three candidate parsers, `PROMPT`, `LLM_CONFIG`), ~28 KB in the
  artifact (*estimate*). Bytes stopped binding today (126 KB headroom).
- **Risk**: every LLM candidate is kernel-checked before it is emitted; the lane
  cannot produce a wrong verdict, only spend tokens. The failure modes seen
  (stale key, 300 s HTTP timeouts, provider fields dropped by the proxy — rails
  31, 3b-iv) all degrade to "no LLM row", never to a rejected certificate.
  Each row's LLM work is wrapped in `try/except` (rail 11).

Why competitors may be switching, and why that does not transfer: a lane whose
accept rate is 0/433 is pure cost, and that *was* our number until the ladder
protocol on 2026-08-27. The decision should follow the accept rate, and ours
is now non-zero. (I could not verify the claim itself: the competition
repository has no Discussions and its five Issues do not mention it; the
forum is outside what this session can reach.)

The one thing worth doing if a future session wants to simplify: remove
`NARROW_GRIND_TRUE_SHAPES` (rail 32, dead by construction) — not the LLM lane.

## 2. The Austin research set (`research_order5_hard`, 100 rows)

What the set is (from `2026-08-27-austin-order5-hard-research-set.md` and the
blueprint chapter `paper/blueprint_source/chapter/order_5.tex`, re-read today):
every `eq2` is one of teorth's **10 confirmed Austin laws** (infinite models
exist, no nontrivial finite ones); every `eq1` is one of 55 **Table-2** laws
(no nontrivial finite model, infinite-model status *open*) or 14 **Table-3**
laws (even finite-model existence *unknown*). The blueprint states: "Vampire
did not establish any implications between equations in this set. **No
effort was made to build infinite models for these equations.**" Ground truth
is `null` on all 100 rows; the organizers exclude the set from evaluation.

So each row is one of two open questions:

- **TRUE** needs `eq1 ⇒ eq2` in equational logic, which a complete
  superposition prover (Vampire) did not find inside its time limit;
- **FALSE** needs an *infinite* model of `eq1` violating `eq2` (for Table-2
  `eq1` no finite one exists; for Table-3 none is known), and the blueprint's
  Lefschetz remark rules out every linear-over-a-field model for Table-2
  hypotheses outright — a linear counterexample would reduce mod p to a finite
  model that provably does not exist.

Automated attempts made today (nothing here touches the solver):

| # | Attempt | Result |
| --- | --- | --- |
| 1 | Affine templates `x◇y = a·x + b·y + c` over ℚ (sympy, exact), all 69 `eq1` | **0 solutions** (positive controls pass) — dead for Table 3 as well as Table 2 |
| 2 | z3 (uninterpreted sort, ∀-axiom + skolemised ¬goal, 120 s each): all 100 implications and all 69 `eq1 ⇒ x = y` | **169 / 169 `unknown`** — z3 4.16 neither proved nor refuted a single implication or collapse in 120 s (14 workers, ~25 min wall). Consistent with Vampire's null result; a real superposition prover with hours per row is item 3 below |
| 3 | z3 finite-domain model search for the 14 Table-3 `eq1`, orders 2–12, 120 s per order (one model refutes every row sharing that `eq1`) | **stopped by decision** after the proof phase: the user capped brute-force table search on this set (diminishing returns — for the 55 Table-2 hypotheses it provably cannot succeed, and for Table 3 the 2026-08-27 harvest already reached order 9). Switched to constructions (below) |
| 4 | (2026-08-27) the solver at `fast`/`standard`/`deep`, unbounded clock; completion with the 25 s escalation cap removed and 10x budget | 0/100, 0/69, 0/14 — none even saturated |

### What the blueprint's constructions can and cannot do here (read 2026-08-28)

| Construction (blueprint chapter) | Carrier | Applies to the Austin set? | Applies to our order-4 FALSE survivors (`481`, `2162`, `2531`)? |
| --- | --- | --- | --- |
| Linear magmas `x◇y = a·x + b·y` over a field (`infinite_models.tex`, Austin's finite-model theorem; `counterexamples.tex`) | finite or ℚ | **No** — Lefschetz: a field-linear model reduces mod p to a finite model, which Table-2 laws do not have; measured 0/69 over ℚ today | Only if a finite model exists; teorth's refutations are `finite: false`, so no |
| Cohomological extensions `(x,s)◇(y,t) = (x◇y, as + bt + f(x,y))` (`cohomology.tex`) — an `E`-cocycle over a finite base `G` and linear `M`, computed by linear algebra | finite (`|G|·|M|`) | **No** — every model it builds is finite | No, same reason; it is a lever for *finite* countermodels above the search ceiling and is worth an experiment on the order-5 held-out FALSE misses (219/353 still uncovered), not here |
| Translation-invariant `y◇x = x + f(x − y)` over ℤ with `f` built greedily (`infinite_magma_constructions.tex` §1–2) | ℤ | **Yes in principle** — the only technique that produced Austin models; every one of the 69 hypotheses reduces to a *two-variable* functional equation (derived today, below), harder than the univariate Asterix/Dupont cases | Yes in principle (teorth: "a variation of the translation-invariant construction shows 1661 ⇏ 1657") |
| Kisielewicz-style case tables on ℕ with injective encodings (`2^y`, `3^y·5^x`) (`infinite_models.tex` §Austin laws) | ℕ | **Yes** — this is how the confirmed Austin laws 374794 and 28770 got their models; per-law hand construction, Lean proof by cases on the encoding | Yes in principle |
| Free magma modulo a confluent rewrite system (`rewriting.tex`, `Confluence*.lean`) | terms | Yes in principle — needs a terminating confluent completion of `eq1`, which our completion engine does not reach on these | **Yes — this is exactly what refutes `481`/`2531` in teorth** (`rw481.Facts`, `Confluence3.lean:66`); no Lean source in the repo, no network in the sandbox (rail F8) |
| Piecewise-linear / parity formulas on ℕ or ℤ discharged by `omega` (the accepted `hard2_0027` shape; blueprint's `3994 ⇏ 3588` XOR/parity model) | ℕ, ℤ | Untested before today — searched below | Untested before today — searched below |

The last row is the one that is *searchable*: a grammar `op(x,y) = if COND then
a₁x + b₁y + c₁ else a₂x + b₂y + c₂` with 16 omega-friendly conditions and
small coefficients (~123k formulas), checked on a window and then provable in
Lean by `unfold; split <;> omega`. Result (window ±4, 14 workers, 0.1 s per
hypothesis): **0 models of any of the 69 Austin hypotheses and 0 of the 3
order-4 survivor hypotheses**, against 40 models (10 refuting the goal) for
the positive control `hard2_0027`. The grammar is right for parity-style rows
and wrong for these: the laws force every model to have no nontrivial finite
quotient, and the constructions that achieve that (Kisielewicz's `2^y`/`3^y`
encodings, greedy `f` on ℤ) mint *fresh* values per pattern — not something a
two-piece linear formula can express. Stopped here by the same
diminishing-returns rule.

### "Math mode" attempt (same day): term models and tag automata

Tooling preserved in `stage2/experiments/austin/` (README has the per-script table).
Chain of results, each a measured negative except the partial last one:

1. **Root-reduce term model** (carrier = all terms, `op` reduces only a root
   instance of `T`): passes 3,000 random + adversarial tests on 23/69 laws
   and refutes 33 rows — but a hand-built overlap assignment (`v_x` shaped
   like `T` with its `y`-part equal to `v_y`) breaks 12073, exactly at the
   critical pair the theory predicts. Random tests miss coincidences.
2. **Normal-form model** (innermost rewriting): fails on all 69 — the one-rule
   systems are not confluent.
3. **Junk-truncated partial term models with iterated critical-pair repair**
   (structural tags, then realisability-filtered repairs): repairs regress
   over ever-deeper shapes on every law tried, including the control — the
   completion divergence in another costume.
4. **Tag automaton** (only the root-to-`x` spine subterms get tags, off-spine
   products are junk, rules keyed on tags with equality guards, priority by
   specificity, projection-based repairs): reproduces a model of Kisielewicz's
   **28770 with zero repairs on a depth-2 universe** — and 0/69 on the research
   laws, where every derailment loses the payload the root needs (the
   projection step fails). Then the check itself failed: the 28770 model is
   **wrong at depth 4** (2,629/20,000 deep random violations; square-first
   priority 205/20,000 — his `2^{3^y} ◇ z = 3^y` clause is precisely the
   missing repair). The Lean renderer for such models compiles up to the main
   proof, where a bounded `cases` argument cannot close the guards; an
   inductive size argument is needed.

Net: the construction that fits the literature is identified and partially
built, the checker is now known to need deep random + critical-pair-derived
assignments, and the research laws lose information at their derailments —
so they are exactly as open as the blueprint says. Rail 37.

Plan to actually move rows, ranked by cost:

1. **Translation-invariant models by greedy construction** (blueprint
   `infinite_magma_constructions.tex` §Translation-invariant, §Greedy). Carrier
   ℤ, `x◇y = x + f(y − x)`; `eq1` becomes a univariate functional equation in
   `f`, and the blueprint's partial-solution/extension lemmas build `f`
   greedily. This is how the ETP settled Asterix (65) and Dupont (63) and it
   is the only method in the literature that produced Austin models at all.
   Cost: per-`eq1` mathematics (deriving the functional equation is
   mechanical — a script can emit it for all 69; proving an extension lemma is
   not), then a Lean formalisation *per model* of the kind
   `equational_theories/Eq63.Greedy` is (hundreds of lines, Mathlib-heavy).
   Judge feasibility: rail 25 (non-transitive allowlist) means everything can
   sit behind `def submission.<name>` and use any tactic, and the 100 KB cap is
   ample; the `hard2_0027` parity model (Nat carrier, `omega`) is the accepted
   template. Realistic yield: a handful of the 69 `eq1`, each settling every
   row that shares it — *if* the functional equation admits a greedy solution,
   which is exactly what nobody has checked.
2. **Non-abelian / free constructions** (blueprint §"modified
   translation-invariant" and the confluence/rewriting chapter): build the free
   `eq1`-magma on generators and show `eq2` fails on it via a confluent rewrite
   system. This is what `Confluence3.lean`-style refutations do (the same
   family our four order-4 FALSE survivors need, rail F8). Cost: a terminating
   confluent completion of `eq1` — our `_KBCompletion` reports these as
   non-saturating even at 10x budget, so a much faster core (term interning +
   discrimination trees, the O5-6 item) is a prerequisite.
3. **TRUE side**: a real ATP (Vampire/E) offline with hours per row on the 100
   goals and the 69 collapse goals. Teorth ran Vampire once with a time limit
   and "did not establish" — not "disproved". If any proof is found, our
   completion engine's proof-recording can be pointed at the same lemma
   ladder to reproduce it as a kernel-checkable chain. Cost: installing an ATP
   (not available in this environment today), compute time.
4. **Table-3 finite models at orders 13–20** with the bit-vector/SAT
   encoding rather than z3's integer one — the 2026-08-27 harvest found
   order-9 witnesses z3 missed at the integer encoding. Cheap to run
   overnight; low prior.

First step of item 1, done today for all 69 hypotheses (script in the session
scratchpad; sympy, `y◇x = x + f(x − y)`, `x := 0` by translation invariance).
The three most-shared hypotheses reduce to:

```
22591  x = (y◇(y◇x))◇((x◇x)◇z)      -> [20034, 28770, 41082]
   0 = z + f(z − f(0)) + f(z − f(−y) − f(−y + f(−y)) + f(z − f(0)))
11116  x = y◇((x◇(z◇x))◇(y◇y))      -> [22455, 22818, 28770]
   0 = y + f(0) + f(f(0) + f(y + f(0) − f(−z) − f(f(−z)))) + f(y + f(0) − f(−z) − f(f(−z)))
24200  x = ((y◇x)◇x)◇((x◇z)◇z)      -> [22455, 30591]
   0 = z + f(z − f(−f(−y)) + f(−f(z))) + f(−f(z))
```

Every one of the 69 is a **two-variable** functional equation (all Table-2/3
laws have three variables), not the univariate shape the blueprint's Asterix
and Dupont greedy constructions solve — so the partial-solution/extension
lemmas would have to be written for a two-parameter family, which is why
this is a research item and not a script. Note also the `f(0)` terms: setting
`f(0) = 0` (the blueprint's axiom (c)) is available, and `z + f(...) + f(...) = 0`
with `f` finite-range is impossible for large `z`, so any solution has
unbounded `f` — consistent with "no finite quotient", as it must be.

Honest summary: these are teorth's open research frontier handed over as a
"problem set"; the organizers say so and score none of it. Items 1–2 are
research projects with a Lean formalisation each, not solver changes. A
session should attempt item 1 on the *two or three* `eq1` that appear most
often (`22818` is the goal in 20 rows; `11116`, `22591`, `32281`, `34889`,
`36713` each pair with three Austin laws) and stop as soon as the functional
equation resists a greedy solution.

### Stress test

`stage2_stress_test_200.jsonl` (the organizers' 200-row set: 50 order-4
normal / hard / extra-hard + 50 order-5 normal, 100 TRUE / 100 FALSE) was
sitting under the gitignored `stage2/results/*.jsonl`. Audited today:
**200 / 200, 0 oracle failures, every label matched, 12.7 s** (slowest row
`order4_hard_0036` 11.7 s via `derived_cp_closure`). Moved to
`data/stage2_official_problems/stress_test_200.jsonl` and added to
`audit_corpus.py`'s official `SETS` as `stress_test_200`, so `--all` covers
it; the first full pass on the extended battery read **2089/2089 solved, 0 oracle failures, 73.5 s solver time (hard1 69/69 1.3s; hard2 200/200 24.6s; hard3 400/400 11.6s; normal 1000/1000 14.0s; sample_20 20/20 1.9s; sample_200 200/200 7.4s; stress_test_200 200/200 12.7s)**. The research set is registered separately as `RESEARCH_SETS` /
`--set research_order5_hard` and deliberately kept out of `--all` and `--hf`:
its labels are null and every row runs the whole engine chain to exhaustion
(~460 s/row), which would add ~45 min to every standing audit for no label
evidence.

## 3. Repo size and tidiness

Measured today:

| What | Size | Tracked? |
| --- | --- | --- |
| `.git` object store | **58.8 MiB** (4,013 loose objects, no packs — never `gc`'d) | — |
| All 1,399 tracked files, working copies | **173 MB** | yes |
| of which `data/` | 119 MB: `exports/export_raw_implications_14_3_2026.csv` 55 MB, `exports/general_implications_closure.json.gz` 23 MB, `teorth_cache/outcome_matrix.bin` 21 MB, `teorth_cache/graph.json` 8.7 MB, `teorth_cache/full_entries.json` 3.9 MB, `stage2_official_problems/eq_size5.txt` 2 MB | yes |
| of which `stage1/` | 23.6 MB (16.7 MB is one `results/v26_recovery/magma_audit_locked.json`) — a finished archive | yes |
| of which `paper/` + `docs/paper/` | 11.5 MB + duplicates: `paper/main.pdf`, `docs/paper/source/main.pdf`, `docs/paper/paper.pdf` (3.4 MB each), `paper-source.tar` 3.3 MB, two arXiv PDFs + full arXiv source trees | yes |
| `vendor/stage2-official/.lake` | **7.10 GB, 143,317 files** — Lean + Mathlib build cache | no (ignored) |
| `.venv` + `.venv311` | 0.42 GB + 0.11 GB (23.5k files) | no |
| `stage2/results/` (665 files, the audit JSONs) | **0.45 GB** | no (`*.json`/`*.jsonl`/`*.log` ignored; the `.md` evidence is tracked and small) |
| `tmp_stage2_smoke/` | 0.11 GB, **21,242 files** | no (ignored) |

So a fresh clone is ~180 MB and the other ~8.4 GB on this machine is local
build/runtime state (7.1 GB of it the Lean cache; Python walk, 19.7 s). Two different problems, two different fixes:

**A. Make the clone lean (what "lots of people" will see).**

1. Move the six big data files (115 MB) to **Git LFS** (`git-lfs 3.7.1` is
   installed). `git lfs migrate import --include="data/exports/*.csv,
   data/exports/*.gz,data/teorth_cache/*.bin,data/teorth_cache/graph.json,
   data/teorth_cache/full_entries.json,stage1/results/v26_recovery/*.json"`
   rewrites history, so it is a **force-push and every collaborator re-clones**
   — do it once, announced, not as a side effect. Alternative with no history
   rewrite: keep the files, add `.gitattributes` LFS rules for *future*
   versions only; the clone stays 173 MB.
2. De-duplicate `paper/`: keep one PDF, drop `paper-source.tar` and
   `docs/paper/source/` (the arXiv `.src` tarballs are re-downloadable), or
   move the whole `paper/` reference material to LFS with item 1.
3. Freeze `stage1/` as a tag (`stage1-final`) and delete the tree from `main`
   — CLAUDE.md already says "finished archive, do not start work there".
4. Run `git gc --aggressive` once (58.8 MiB of loose objects will pack to a
   fraction of that).
5. Delete the stray untracked top-level files (`chain.log`,
   `stop_after_b08.log`) and keep `tmp*/` out of the tree — already ignored,
   but 17 scripts reference `tmp_stage2_smoke/`, so either promote what they
   need into `stage2/experiments/` or accept that those scripts only run on
   this machine (rail 3b-iv named this exact problem once).

**B. Move the local bulk off the repo path (this machine).**

1. `vendor/stage2-official/.lake` must stay *at that path* for `lake`, but it
   can be a **directory junction** to a local drive location:
   `Move-Item vendor\stage2-official\.lake D:\magma-local\lake; New-Item
   -ItemType Junction -Path vendor\stage2-official\.lake -Target
   D:\magma-local\lake`. Nothing in the repo changes; `elan`/`lake` follow
   junctions. Re-validate with the three-cert judge-parity smoke (rail 14)
   afterwards.
2. The two venvs can be recreated anywhere; point `.venv` at a junction the
   same way, or just leave them — they are ignored and not part of the clone.
3. `stage2/results/*.json` (the audit outputs) and `tmp_stage2_smoke/` are
   ignored already; archive them to the local drive at session end
   (`stage2/results/*.md` stay — they are the evidence, and are small).
4. Add one env var, `MAGMA_DATA_DIR`, read by the 15 scripts that hard-code
   `data/exports`, `data/teorth_cache`, `data/hf_cache` (5 + 4 + 6 files),
   defaulting to the in-repo path, so the big data can live outside the tree
   on a machine that has it and be fetched by `theory/tools/fetch_problem_sets.py`
   on one that does not. That is a mechanical change; it was **not** made
   today because the user asked for a plan, and because item A.1 (LFS) makes
   it unnecessary if taken.

None of A is done in this session: A.1 and A.3 rewrite or delete shared
history and are the user's call; A.2/A.4/A.5 are safe but were held with them
so the tidy lands as one announced change.
