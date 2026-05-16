# 2026-05-15 Theory Diagnosis After Deep Absorption

This note is a cold-start bridge for the next Stage 2 solver session. It records what the
mathematics says about the current hard gap, where this session underperformed, and the
highest-value next route.

## Current Hard State

Latest local runner-equivalent hard-only evidence after the deep absorption patch:

- `hard1`: `25/69`
- `hard2`: `70/200`
- `hard3`: `219/400`
- combined hard-only: `314/669`
- solved by expected answer: `42 TRUE`, `272 FALSE`
- remaining misses: `277 TRUE`, `78 FALSE`

New local ledgers, ignored by git unless force-added:

- `stage2/results/2026-05-15-post-deep-hard-misses.jsonl`: all `355` hard misses
- `stage2/results/2026-05-15-post-deep-hard-true-misses.jsonl`: the `277` TRUE misses
- `stage2/results/2026-05-15-post-deep-hard-true-misses-teorth.jsonl`: Teorth graph labels for those TRUE misses

Index caution: official Stage 2 rows use display equation ids. Local `equations.txt` and
Teorth graph tooling are zero-based internally. For proof-page / `full_entries` paths,
subtract one from `eq*_id` before looking up matrix positions; display it again as
`Equation(n+1)` in notes.

## What The Read Says

The right abstraction is the word problem of the one-law equational theory on the free
magma. The blueprint rewriting chapter makes the missing algorithmic shape explicit:
rewrite systems are closed under substitutions and congruence; if a system is
normalizing and Church-Rosser, equality is decided by reducing both terms to a unique
normal form. Knuth-Bendix-style critical pairs are the computable local obstruction to
confluence; even when full completion is too much, partial / unfailing completion is a
semi-decision procedure for equality.

The Teorth blueprint also says the same thing empirically: tens of thousands of positive
edges came from generated simple rewrites, `nth_rewrite` scripts, e-graph/ATP proofs, and
trivial rewrite combinations. Our solver has only the smallest direct version of that
machinery: direct substitution, short BFS rewrite chains, and a bounded absorption
closure.

The invariant chapters explain the FALSE side. Projection, variable-multiset, parity,
mod-3, constant, and free-magma invariants are not vague heuristics; they are canonical
free-object tests. The local structural-rule tools already verify LP/RP/C0/XOR/XNOR/
AND/OR/Z3A-style witnesses against all equations. The hard FALSE residue is therefore
more likely to need stronger finite families, lifting / modified magmas, central
groupoid-style constructions, or infinite/partial-extension ideas than another generic
TRUE fallback.

## Post-Deep TRUE Shape

The remaining hard TRUE misses are not random:

- `100`: variable-side absorption-like, boundary-changing
- `81`: same, with many hypothesis variables
- `39`: same, with many goal variables
- `13`: same, with many hypothesis and goal variables
- `44`: product/product boundary-changing laws with no bare variable side

The priority cues currently mislead us: `212/277` TRUE misses fall under
`false:projection_cue`, and `62/277` under `true:absorption`. Boundary change is no longer
a reliable FALSE cue once the hypothesis itself is strong enough to collapse boundaries.

Teorth graph status for the TRUE misses:

- `277/277`: `implicit_proof_true`
- `0/277`: direct `full_entries` source record

Short explicit-edge probe using proven non-finite `full_entries` edges, with correct
index conversion:

- `43/277` TRUE misses have an explicit proven path of length <= 5.
- path lengths: `6` of length 2, `3` of length 3, `12` of length 4, `22` of length 5.
- the path edges are mostly generated families: `SimpleRewrites`, `TrivialBruteforce`,
  `NthRewrites`, `RewriteHypothesis`, `RewriteGoal`, `MagmaEgg`, and `VampireProven`.
- `234/277` have no path of length <= 5 through only these direct source records.

Representative short-path targets:

- `hard1_0018`: display path `2105 -> 1264 -> 1229`
- `hard1_0046`: display path `3550 -> 41 -> 3381 -> 3423 -> 3282`
- `hard2_0003`: display path `3348 -> 395 -> 4243 -> 4040 -> 3972`
- `hard3_0168`: display path `1506 -> 1491 -> 359`
- `hard3_0192`: display path `1695 -> 1932 -> 680`

These paths are not solver policy and cannot be imported in certificates. They are
motif signals: the solver needs to synthesize the corresponding local proof terms from
the single hypothesis `h`.

## Shortcomings Of This Session

1. The patch widened one existing motif instead of adding a new proof calculus. The
   `true:absorption_closure:deep` route is useful and validated, but it is still a bounded
   term-growth BFS.

2. Larger absorption bounds are not the answer. Probes with depth `5`, pool `18`,
   frontier `2000`, fills `500`, slack `16`, and `20s` budgets still failed on
   representative misses such as `hard2_0106`, `hard2_0117`, and `hard1_0007`.

3. The solver has no local theorem-chaining layer. Teorth paths show many TRUE misses
   factor through intermediate equations. A submitted proof cannot import those theorems,
   but the solver can create local `have` facts if it can synthesize each edge from `h`.

4. The solver has no target-guided rewrite script generator. Generated Teorth proofs use
   `nth_rewrite`-style sequences and rewrite under hypothesis/goal contexts. Our BFS only
   explores a small pool and does not intentionally solve unification goals created by
   the target term shape.

5. The solver has no completion/e-graph route. It does not build a congruence closure
   over a generated term universe, add critical-pair joins, or extract proof paths from
   equivalence classes.

6. The product/product TRUE lane is underdeveloped. `44` remaining TRUE misses have no
   bare variable-side hypothesis, so absorption-specific code will not reach them.

7. FALSE was not improved in this session. The remaining `78` FALSE misses should be
   mined later, but the current bottleneck is still TRUE.

8. `normal` was not rerun, so canonical public totals must not be updated.

9. Local LLM plumbing was not validated with a rotated key. Keep the solver secret-free
   and use only official proxy calls.

## Next Solver Route

Build `true:equational_closure` before spending more time on LLM prompts.

Core idea: a small proof-producing congruence engine over free-magma terms.

1. Generate a term universe from:
   - all goal terms and subterms
   - all variables in the goal
   - bounded products of these terms
   - target-guided holes created by matching hypothesis sides against goal subterms
   - self-overlap / critical-pair candidates from the hypothesis law

2. Add equality edges:
   - instantiated hypothesis edges in both directions
   - congruence edges: if `a = b`, then `C[a] = C[b]`
   - local critical-pair joins when two one-step rewrites overlap
   - optional shrink-oriented rewrite edges to keep the graph finite

3. Extract proof paths:
   - every graph edge stores the Lean proof expression
   - subterm edges render with `congrArg`
   - final paths compose with `.trans` / `.symm`
   - intermediate law facts can be emitted as local `have` declarations, not imports

4. Add a generated rewrite-script lane:
   - enumerate bounded `nth_rewrite`-like position sequences against the goal
   - solve missing substitutions by unifying with the target term, not by blind pool fill
   - support rewriting the hypothesis-derived intermediate laws, not just the final goal

5. Keep the route bounded and silent on failure:
   - per-route deadline
   - term count cap
   - proof length cap
   - route label only in stderr

## First Focus Fixtures

Start with short-path TRUE misses, not the whole hard set:

```powershell
# already generated by this session
Get-Content stage2/results/2026-05-15-post-deep-hard-true-misses.jsonl
Get-Content stage2/results/2026-05-15-post-deep-hard-true-misses-teorth.jsonl
```

Recommended first official fixture:

- `hard1_0018`
- `hard1_0046`
- `hard2_0003`
- `hard3_0168`
- `hard3_0192`

Acceptance target: at least one of these becomes a deterministic accepted certificate
without regressing the existing `15/15` deep absorption fixture.

## Validation Ladder

1. Unit smoke:

```powershell
.\.venv\Scripts\python.exe -m py_compile stage2\solver\solver.py stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe theory\tools\smoke_problem_sets.py
.\stage2\solver\package_solver.ps1
```

2. Focused TRUE fixture with the five ids above.
3. Existing deep absorption `15/15` fixture.
4. Required smokes: `sample_20`, `sample_200`, Marathon `normal_100` with zero tokens.
5. Hard mix seed `20260514`.
6. Full hard-only `hard1|hard2|hard3`.
7. Full promotion only after rerunning `normal` too.

## LLM Note

Do not write secrets into the solver or repo. Configure local LLM tests only through the
official proxy with session environment variables. Use a currently unresolved TRUE row
from `2026-05-15-post-deep-hard-true-misses.jsonl`; success for plumbing means the proxy
does not report `OPENAI_API_KEY or OPENROUTER_API_KEY not set`.
