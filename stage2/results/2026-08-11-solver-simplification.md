# 2026-08-11 — solver simplification pass (no behaviour change)

Goal: make `stage2/solver/solver.py` smaller and simpler without moving a single
certificate byte. No coverage work, no new mathematics.

## Result

| | before | after |
| --- | --- | --- |
| Solver source | 10,388 lines | **9,043** (−1,345) |
| Solver bytes (LF) | 480,115 | 430,925 |
| **Packaged submission** | **480,115 B (4.0% headroom)** | **355,879 B (28.8% headroom)** |
| Offline gate | 201 passed, 2 skipped | 201 passed, 2 skipped |

Two independent levers. **Neither deleted a route** — `TRUE_ROUTES` is identical
entry for entry, in order, with the same function names.

1. **37 bespoke `*_source` pattern matchers → one `law_matcher` + a table row
   each** (−51 KB of source). A family is now a pattern string, the Lean argument
   each pattern variable becomes, and two flags. `collapse_family_route` and
   `projection_collapse_route` turn whole routes into table rows;
   `submission_certificate` / `law_have` render the one skeleton they share.
2. **Comments and docstrings stripped from the artifact only** (−74 KB), by the
   new `stage2/solver/minify_submission.py`, called from `package_solver.ps1`.
   Comments stay in the working tree — most record a measurement that cost a
   session — and are worth nothing to the judge. The stripper proves the artifact
   parses to the same tree as the source before writing.

## Evidence that behaviour did not change

- **Route differential, byte-exact.** Frozen pre-refactor module vs working tree,
  every cheap syntactic route, over the whole real input domain (4,694 ETP
  equations + every equation in every benchmark set = 5,090 distinct) crossed
  with a spread of eq2 shapes plus all 4,138 real benchmark pairs. **0
  differences**, re-run after every batch of edits.
- **Row-id snapshot diff over 2,469 rows** (official + HF), verdict + route +
  SHA-256 of the certificate: **2,446 identical, 0 verdict flips, 0 route
  changes, 0 certificate-byte changes, 0 crashes**. 18 apparent losses, all on
  wall-clock-bounded engines, **all 18 reproduced 3/3 on both modules with the
  same route** — CPU contention, not regression (rail 5e).
- **Offline gate**: 201 passed, 2 skipped — on the source *and* on the stripped
  artifact itself.
- **Spotcheck**: 90/90, 100% accuracy, 0 mistakes across all 9 sources including
  the never-tuned-on ETP matrix.
- **Corpus audit** (`audit-2026-08-11-simplification.json`): official
  **1660/1669, 0 oracle failures, 0 crashes, 0 label mismatches**; `normal`
  1000/1000 and `hard1` 69/69 complete. See the caveat below.
- **Adversarial review**, 9 agents each trying to refute equivalence with their
  own harnesses. Headline numbers they ran independently: 26.6M matcher calls
  over ETP × injective renamings × both orientations (0 acceptance differences on
  all 37 families), 14.8M fuzz calls outside ETP (0), and 1,261,120 comparisons
  over every binary tree with ≤5 leaves on 4 variables — a domain that is
  *complete* for matching, because `law_matcher` rejects any pattern variable
  bound to a compound term, which forces leaf-count equality with the pattern.

Three findings survived, all acted on:

- `lemma_certificate` delegating to `lemma_chain_certificate` changed the intro
  guard from the joined binder string to the binder list. Unreachable
  (`parse_equation` cannot produce an empty variable name) but real. Rewritten to
  keep the joined-string guard; verified over 26,400 comparisons including the
  degenerate `[""]` case.
- `nested_left_projection_route` evaluated the eq2 gate before the eq1 match.
  Output identical, but the driver now matches eq1 first and builds the eq2 proof
  only on a hit — strictly less work than either the baseline or the first
  rewrite. Re-verified: 0 route differences.
- `_closure_route_impl`'s `**kwargs` could have let a future caller silently pick
  up `_closure_proof_expr_impl`'s `seed_terms` default. Explicit parameters
  restored.

## Caveat on the audit's coverage number

The documented isolated baseline is 1666/1669; this audit read 1660 while eight
review agents were still running. The six-row gap is **not** a regression. Every
one was reproduced standalone on both the frozen baseline and the current solver,
back to back under identical conditions, and all six come out the same:

| row | baseline | current |
| --- | --- | --- |
| `hard2_0005` | `true:lemma_chain:direct_goal` 17.4 s | same route, 18.2 s |
| `hard2_0079` | `true:egg_collapse` 77.7 s | same route, 77.2 s |
| `hard2_0082` | `true:egg_bootstrap:product_c` 50.3 s | solved **faster**, `true:lemma_chain:enum319` 16.5 s |
| `hard2_0098` | `true:egg_collapse` 84.1 s | same route, 83.4 s |
| `hard2_0125` | `false:constraint_fin6` 202.5 s | same route, 202.3 s |
| `hard2_0162` | `true:egg_ladder:collapse:h1` 174.7 s | same route, 175.4 s |

These are 17-to-202-second rows a contended 16-worker sweep cannot finish;
`hard2_0082`'s route difference is the documented race between general engines
(CLAUDE.md already records it as budget-marginal at 74 s standalone), and it
landed sooner here, not later. **The soundness numbers in that audit are
load-independent and clean.** An isolated re-run is still owed for a publishable
coverage headline.

## Also changed

- `stage2/tests/test_golden.py`: the escape hatch for "a bespoke route lost its
  wall-clock race to a general engine" listed only the three closure engines and
  was never extended to the egg engines added later, so `evaluation_hard_0028`
  (an 0.08 s budget, 22 ms of work on an idle machine) failed the pre-package
  gate on a coin flip. `narrow_grind` stays excluded on purpose.
- `stage2/experiments/probe_dead_routes.py`: it instruments after import, so the
  18 `*_block` builders now evaluated at import time read as unreachable dead
  code. It recovers them statically and reports them separately — rail 1 depends
  on this tool being right about what is safe to delete.
