# 2026-08-28 — Deterministic pass: 4x faster, 96 KB lighter, 0 rows moved

Session goal: make the deterministic pass lighter and faster, recover artifact
bytes for future TRUE/FALSE work, and re-check alignment with the rules. No LLM
calls anywhere in this session. Every coverage number is a **row-id diff**
against the 2026-08-27 improvement-pass-2 audits (rail 2).

## Headline

| Metric | Before (2026-08-27 pass 2) | After | Evidence |
| --- | --- | --- | --- |
| Official sets (`normal`+`hard1`+`hard2`+`hard3`+samples), `fast`, 16 workers, isolated | 1869/1869 distinct rows, **1,105.9 s** solver time | 1869/1869, **262.6 s** (−76%) | `audit-2026-08-28-perf.json` vs `audit-2026-08-27-final-official.json`: **0 lost / 0 gained / 0 flips / 0 oracle failures**, 184 route changes |
| Rows over 1 s (official) | 201 (961 s) | **10** (84 s) | same files |
| HF mirror sets (800 rows) | 800/800, 479.9 s | 800/800, **135.1 s** (−72%) | `audit-2026-08-28-perf-hf.json`: 0 lost / 0 gained / 0 flips / 0 oracle failures, 70 route changes |
| Packaged artifact | 469,348 B (30.6 KB headroom) | **373,997 B (126.0 KB headroom, 25.2%)** | `minify_submission.py` now packs four data tables (below) |
| Offline gate | 458 passed / 2 skipped | **474 passed / 1 skipped** (packager run, `-n auto`, 8 min 50 s; the one skip is "no spot-check failures pinned yet"). The first post-change run read 452 / 9 — see "Gate skips" below | `pytest stage2/tests -q -n auto` |
| Real Lean judge (4.33.1, deployed caps) on the rows that changed route | — | **29 / 29 accepted**: 14 sampled route-changed official rows (6 `completion:collapse`, 4 `:join`, 4 `:bridge`) + the 15 fixture pins whose route drifted, all re-pinned (fixture 159 → 173 entries) | `judge_rows.py --ids ... --append-fixture` |
| Upstream snapshot | `817a4653` | unchanged — `gh api compare` reads 0 ahead / 0 behind | rail 14 |
| Spotcheck (standing loop, run after packaging) | 90/90 | **90 / 90, 100% accuracy, 0 mistakes** | `spotcheck.py` |

## Where the time went (diagnosis)

`engine_time_profile.py` over the 197 official rows slower than 1 s in the
baseline audit (859 s of the corpus's 1,136 s):

| Engine | calls | seconds | share | on rows ending |
| --- | --- | --- | --- | --- |
| `egg_probe_route` | 195 | **616.2** | 71.7% | TRUE |
| `find_counterexample` | 197 | 117.7 | 13.7% | TRUE (115 s) |
| `constraint_countermodel` (cheap tier) | 13 | 57.1 | 6.6% | TRUE |
| `lemma_chain_bootstrap_route` | 3 | 20.6 | 2.4% | TRUE |
| `local_model_counterexample` (probe) | 13 | 19.5 | 2.3% | TRUE |
| `completion_probe_route` | 110 | **4.7** | 0.5% | TRUE |

The tell was in the route histogram before any profiling: 61 of the 75
`true:completion:collapse` rows sat at exactly ~6.5 s. `EGG_PROBE_COLLAPSE_BUDGET`
is 6.0 s, the egg probe ran first, and on a collapse row it spends the whole
slice before the completion probe closes the same row in ~0.3 s.

The second cost, `find_counterexample` on TRUE rows, was traced with a
stage-labelled `witness_check` over 12 TRUE rows: **affine family 4.09 s /
43,392 checks**, `Fin 3` enumeration 1.39 s / 475,944 checks, quadratic 0.12 s,
structured 0.02 s, named 0.01 s. Affine tables satisfy eq1, and on a TRUE row
eq2 then holds too, so *both* equations were evaluated over all `n ** k`
assignments through the dict-environment `eval_term` interpreter at ~94 µs a
check.

## The three solver changes

1. **Completion probe before egg probe** (`solve_problem_pass`). A/B on the
   197 slow rows with `verify_reorder_ab.py`: 932 s → 229.5 s, 0 lost / 0
   flips / 0 oracle failures, 71 route changes — all from
   `egg_collapse`/`egg_bootstrap:*` into `completion:collapse|join|bridge`
   (judge-pinned families; the golden gate already treats both as
   `true:general_closure`).
2. **`equational_closure` and `deep_absorption_closure` ahead of the cheap
   constraint tier.** No official or HF row is served by the constraint,
   local-model or large-linear tiers, so every row reaching them is TRUE and
   paid 7 × 0.8 s + 1.5 s before `equational_closure` closed it in < 1 s (13
   calls, 0.81 s total). Loss cost measured over 68 official FALSE rows:
   0.65 s mean / 2.07 s max, 0 FALSE rows claimed. `derived_cp_closure` stays
   below the tier — its loss is 8 s. Relative order of the two closures is
   preserved (absorption hypotheses still get `deep_absorption` first).
3. **Compiled `equation_holds`.** A per-equation lambda built once
   (`lambda t, v0, v1, v2: t[t[v0][v1]][v2] == ...`), cached on the equation
   dict's identity with term-identity checks, cleared by
   `clear_term_caches()`. Same assignment order, same first-failure
   short-circuit, so `note_hypothesis_model` bookkeeping is unchanged.
   Equivalence: 117,780 (equation, table) checks against the old
   implementation, 0 mismatches. Speed: 0.55 → 0.08 ms per full 9³ check
   (7x); 37 → 15 ms over all 19,683 `Fin 3` tables (2.5x). `find_counterexample`
   on the 12 TRUE rows: 6.52 → 1.84 s.

Combined on the official corpus: 1,105.9 → 262.6 s. What is left above 5 s
(six rows, 73 s) is the cheap constraint tier (27 s) and the local-model probe
(9 s) on rows that still reach the general engines, plus `lemma_chain_bootstrap`
(21 s over 3 calls). Both FALSE tiers win order-5 sweep rows the corpus does
not contain, so they stay; 4.6 s on a rare row is worth less than order-5
FALSE coverage.

## The byte change: packed data tables

`stage2/solver/minify_submission.py` now runs a second pass after the
comment/docstring strip: the four largest literals are serialised to JSON,
zlib-compressed (level 9), base85-encoded, and rebuilt at import time by a
six-line `_unpack_table` helper (local `import base64, json, zlib`; all stdlib in
`python:3.11-slim`; 0.11 s import measured under the 3.11 interpreter).

| Table | source bytes | packed bytes |
| --- | --- | --- |
| `DISTILLED_CERTS` (59 certs) | 99,672 | 14,633 |
| `FP_WITNESS_TABLES` (113) | 11,787 | 2,379 |
| `O5_WITNESS_TABLES` (18) | 7,650 | 1,162 |
| `WITNESS_TABLES` (30) | 2,370 | 517 |

Artifact 470,433 (stripped) → **373,997 B**. No certificate or table was
removed, so every judge-pinned byte in `judge_verified_certs.jsonl` is still
shipped. Safety: the packer decodes each blob and compares it to the source
literal with `==` and a type check (tuple-vs-list is enforced at every level)
before writing; `test_artifact.py` repeats the comparison from the shipped
file through the shipped helper, and asserts the artifact really is packed.
The source stays readable — `distill_certs.py`'s paste-in workflow is
unchanged.

Rules alignment (re-read 2026-08-28, `vendor/stage2-official/rules/`):
`evaluation.md` L23 — "a solver that includes compressed data or binary blobs
must disclose them in a submission note: what they contain, and the methodology
used to generate them". `SUBMISSION_NOTE.md` now says exactly what is packed,
how, and where the plain text lives; the per-table methodology paragraphs were
already there. `overview.md` "Human-Interpretable Artifacts" permits
non-human-readable data sets with such a note and bars only compiled binaries
without source — a zlib'd JSON of Lean text with its generator in the repo is
the sanctioned case, not the barred one. Whole-file compression was
considered and rejected on the same page: the strategy has to be
interpretable, and the code is the strategy.

## Measured and rejected this session

- Moving `derived_cp_closure` ahead of the constraint tier: 8 s loss on any
  FALSE row that reaches it, more than the 5.6 s tier it would displace.
- Reordering inside the FALSE portfolio: order only decides which witness a
  FALSE row gets; a TRUE row runs every stage regardless, so speed had to
  come from the evaluator, not the order (and reordering would move
  byte-pinned `enum_fin3` certificates for nothing).
- Trimming `DISTILLED_CERTS` to recover bytes (`NEXT_SESSION_BRIEF` §3.3's
  "120 KB of slack"): unnecessary now — packing recovered 96 KB with every
  pinned certificate intact.

## Gate skips and the re-pin

The first post-change gate read 452 passed / **9 skipped** against a baseline of
2 skipped. Rail 16 says compare the skip count, and the reasons were exactly the
reorder: `test_judge_verified.py` skips a pin whose live route no longer matches
("route drifted true:egg_collapse -> true:completion:collapse; nothing to
compare"), so seven byte-pinned rows had silently stopped being tests. All 15
pins whose route could drift (every `egg_collapse`, `egg_bootstrap`,
`egg_ladder` and `completion:bridge` entry) were re-judged live together with
the 14-row sample: 29/29 accepted, and `--append-fixture` replaced the stale
entries by id. Two of the 15 (`etp_3983_3800`, `etp_3983_4296`) had drifted
between `egg_ladder:*:h1` and `:h2` before this session — a genuine timing race
the re-pin does not remove, only refreshes.
