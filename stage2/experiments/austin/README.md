# Austin research set — construction experiments (2026-08-28)

Diagnosis tooling for `data/hf_cache/research_order5_hard.jsonl` (100 rows,
every `eq2` a confirmed Austin law, every `eq1` a Table-2/3 order-5 law with
no finite model; ground truth null). Nothing here is a solver route yet.
Results and the construction map:
`stage2/results/2026-08-28-assessment-deterministic-austin-tidy.md` §2.

| Script | What it tries | Result on the 69 hypotheses |
| --- | --- | --- |
| `austin_z3.py prove` | z3 with a ∀-axiom + skolemised ¬goal, 120 s/row | 169/169 `unknown` |
| `austin_z3.py finite N T table3` | z3 finite-domain model search for the 14 Table-3 laws | stopped by decision (Table 2 provably has none) |
| `austin_z3.py linear` | affine `x◇y = a·x + b·y + c` over ℚ (sympy, exact) | 0/69 (controls pass) |
| `pwl_search.py` | ℤ piecewise-linear `if COND then L1 else L2` models, omega-provable | 0/69, control 40/40 |
| `term_model.py` | term algebra with root-reduction only (model R) and innermost normal forms (model N) + critical pairs | R passes random tests on 23 laws but is refuted by a hand-built overlap assignment; N fails everywhere (non-confluent) |
| `tagged_model.py`, `repair_model.py` | partial (junk-truncated) term models, structural tags, iterated critical-pair repair | repairs regress over deeper shapes (completion divergence in disguise) |
| `tag_automaton.py` | Kisielewicz-style tag automaton: only spine subterms get tags, off-spine products are junk, rules keyed on tags with equality guards, priority orders, projection-based repairs | reproduces a model of **28770 with 0 repairs on a depth-2 universe** — and that model is **wrong at depth 4** (`y = s0(a, s0(a', s0(a'', s0(p, q))))` returns `q`); square-first priority cuts deep violations 13 % → 1 %, i.e. his extra clause `2^{3^y} ◇ z = 3^y` is the missing repair |
| `tag_lean.py` | render a tag automaton as a Lean certificate (inductive carrier, `Option` rule chain, no-fixpoint lemmas, `cases`/`simp`/`split`) | compiles up to the main proof; a bounded `cases` proof is not enough — guards need an inductive argument (a size function + `omega`), and the model itself must first be correct |

Run everything from the repo root with the venv interpreter, e.g.
`python stage2/experiments/austin/tag_automaton.py rows.jsonl out.json`
(`rows.jsonl` has `id`, `equation1`, `equation2`, optional `eq1_id`).

**Lesson (rail 37 in CLAUDE.md):** a depth-bounded "exhaustive" universe is not
exhaustive for models with unbounded payload nesting; add deep random
assignments (depth ≥ 5) and critical-pair-derived assignments to every model
check before believing it.

Next step if this is resumed: fix the checker (deep random + CP-derived), then
search priority orders + repairs on 28770 until 0/20,000 deep violations, make
the Lean proof inductive (size function; no term equals a proper superterm of
itself), judge it — and only then try the 69.
