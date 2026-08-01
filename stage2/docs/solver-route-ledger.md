# Solver Route Ledger

Updated: 2026-07-29 (header note only; the tables below still date from 2026-05-30
and predate every engine added since — `derived_cp_closure`, `universal_identity`,
`projection_bootstrap`, `lemma_bootstrap`, `lemma_chain`, `egg_closure`).

This ledger is the review map for `stage2/solver/solver.py`. It records what each route is allowed to claim, why the method is mathematically sound, what local evidence exists, and what must be rechecked before promotion.

**Source of truth for dispatch order is the `TRUE_ROUTES` table in
`stage2/solver/solver.py`**, not this document. `solve_problem` was refactored
from ~380 lines of copy-pasted dispatch into that table on 2026-07-29; the order
was verified mechanically unchanged.

Two ledger entries below are out of date on evidence, worth knowing while reading:

- `true:right_projection_collapse:left_pair_tail` no longer contains a `grind`
  step or a `maxHeartbeats` bump — the lemma it needed is now derived. All emitted
  certificates are checked against the banned-tactic list
  (`oracles.check_no_banned_tactics`); only `true:narrow_grind` and the Solo
  `fallback:unsolved_grind` may use a search tactic.
- The 34 routes whose certificates the proof kernel cannot check (`other` shape)
  now carry **real Lean judge evidence**: 34/34 `accepted`, pinned in
  `stage2/fixtures/judge_verified_certs.jsonl`. Where an "Evidence / checks"
  cell below says a route "should get a route fixture", check that file first.

## Status Labels

- `active`: enabled in default packaged solver runs.
- `opt-in`: present but disabled unless an environment flag enables it.
- `llm`: reachable only through official Solo or Marathon proxy paths.
- `needs-card`: route has working code but still needs deeper theory notes or route fixtures.

## TRUE Routes

| Route | Key functions | Status | Trigger | Certificate shape | Theory justification | Evidence / checks | Review notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `true:reflexive` | `is_reflexive_problem`, `reflexive_true_certificate` | active | `eq1_id == eq2_id` | `exact h` | A hypothesis implies itself. | Official sample/public runs; hardcoded proof. | Keep tiny and first in `solve_problem`. |
| `true:singleton` | `singleton_route`, `singleton_true_certificate` | active | Hypothesis has a variable alone on one side and absent from the other side. | Builds `hall : forall a b, a = b`; solves goal by collapse. | A singleton law collapses every carrier element to one equivalence class by two substitutions of `h`. | Public TRUE certificates in previous historical runs; should get a route fixture. | High-value motif card. Do not widen trigger without semantic proof. |
| `true:rewrite`, `true:rewrite:symm` | `direct_substitution_route`, `match_term`, `substitution_true_certificate` | active | Goal sides are direct instances of the two hypothesis sides. | Direct call to `h` or `.symm`. | Equational logic substitution: any instance of a law holds under variable substitution. | Covered by `smoke_llm_dsl.py` style parsing and official runner evidence. | Conservative and safe; keep before more expensive routes. |
| `true:bridge:*` | `bridge_route`, `completed_bridge_route`, `goal_term_pool` | active | Two instances of the hypothesis share a middle term, optionally with filled variables. | `(h ...).trans (h ...).symm` variants. | Transitivity over two substitution instances of the same law. | Public/hard smoke evidence; needs compact fixture list. | Max-trial bounds are empirical; document before tuning. |
| `true:projection:*` | `projection_law_route`, `projection_true_route`, `projection_term_proof` | active | Hypothesis states a projection/boundary law, and both goal sides reduce to same boundary variable. | Recursive `.trans` proof reducing each term to a variable. | Projection laws orient every composite to a boundary variable; congruence preserves equality through subterms. | Active deterministic route. | Needs route fixture and motif card. |
| `true:left_row_constancy` | `left_row_constancy_source`, `left_row_constancy_route`, `left_row_constancy_term_proof` | active | Hypothesis has shape `r = ((r ◇ p) ◇ (p ◇ q)) ◇ s`; goal sides have the same recursive left-row skeleton. | Derives `hrow : ∀ a b c, a ◇ b = a ◇ c`, then recursively rewrites row arguments by congruence. | From `h (a◇b) (b◇a) a c` and `h a b a ((b◇a)◇a)`, the shared middle proves right-argument constancy for every row. | Official Marathon accepted `hard3_0284` and `hard3_0285` (`2/2`), full selected public TRUE fixture improved to `2/17`, and `normal_100` stayed `74/100` in historical validation. | Narrow four-variable trigger; public corpus scan found only those two hard3 hits and no normal hits. |
| `true:rewrite_chain:*` | `find_rewrite_chain`, `rewrite_steps`, `proof_between_terms` | active | Short bounded chain connects goal lhs to rhs. | `.trans` chain of explicit hypothesis rewrites. | Finite equational derivation by repeated substitution and congruence. | Depth-limited; covered indirectly by accepted certificates. | Keep bounded. Increasing depth needs fixture evidence. |
| `true:self_square_absorption` | `self_square_absorption_source`, `self_square_absorption_route` | active | Hypothesis has shape `r = (p ◇ r) ◇ (p ◇ r)` and goal has shape `r = A ◇ (B ◇ r)`. | Three-call `calc` proof using `h r B`, `congrArg (fun t => t ◇ t) (h (B ◇ r) A)`, and `(h C C).symm`. | From `r = (p◇r)^2`, first rewrite `r` to `B^2`; prove `B = C^2`; then collapse `(C^2)^2` back to `C`. | Judge-accepted direct certificate for `hard1_0052`; public30 historical sample improved `15/30` to `16/30` with route count `1`. | Narrow trigger. Corpus scan found one public hard hit; keep before expensive closure and do not broaden without another accepted template. |
| `true:repeat_tail_absorption` | `repeat_tail_absorption_source`, `repeat_tail_absorption_route` | active | Hypothesis has shape `r = p ◇ (q ◇ (q ◇ r))` and goal has shape `r = (r ◇ r) ◇ (r ◇ (A ◇ r))`. | Three hypothesis calls joined by transitivity, with one `congrArg` over `(r ◇ r) ◇ (r ◇ t)`. | Rewrite `r` to `A ◇ (A ◇ (A ◇ r))`, rewrite that middle term to `(r ◇ r) ◇ (r ◇ r)`, then use the hypothesis under congruence to replace `A ◇ r` by `r`. | Shadow closure found `hard3_0020`; extracted certificate accepted by runner-equivalent `verify_answer(_to_judge_problem(...), raw_answer)`; study150 profile moved `hard3_0020` from `skip:none` to this route in `0.0015s`; corpus scan found one official hard hit. | Narrow trigger promoted instead of widening global equational closure, whose misses cost roughly `1.5s` in the shadow probe. |
| `true:absorption_closure:*` | `absorption_hypothesis`, `absorption_closure_route`, `filled_absorption_steps`, `combine_meeting_proofs` | active, needs-card | Absorption-like hypothesis; bounded bidirectional closure meets. | Proof chain joined at meeting term. | Bounded search in the congruence closure generated by the hypothesis. | Hard TRUE wins in May summaries; 2026-05-20 `normal_100` speed cap evidence. | Route is sound because every edge carries a proof. Bounds are empirical; regular closure now has a `0.05s` wall cap and needs hard TRUE no-loss fixtures before further tuning. |
| `true:absorption_closure:deep` | `deep_absorption_closure_route` | active, needs-card | Same as absorption closure after cheaper routes fail. | Same as absorption closure with deeper/time-bounded config. | Same as above. | Hard-route regression evidence needed before tuning. | Keep time cap; order with equational closure is sensitive. |
| `true:equational_closure:*` | `equational_closure_route`, `filled_absorption_steps`, `combine_meeting_proofs` | active, needs-card | General bounded bidirectional closure, not only absorption. | Explicit proof chain from generated equality edges. | Bounded equational reasoning under substitution and congruence. | Accepted hard TRUE certificates; no broad proof-engine guarantee. | Do not merge with absorption code until fixtures are stable. |
| `true:egg_closure` | `_EggProver`, `egg_saturate_prove`, `egg_closure_route` | active | Last TRUE engine; unresolved rows only. | `exact_expr`: balanced `.trans` chain of `h`-instances under `congrArg` contexts. | Ground equality saturation (e-graph + congruence closure) over goal-variable terms — the MagmaEgg mechanism; proof forest explanation, cycle-cut + greedy bridge shortening, and a full syntactic REPLAY of every step before emission (fail-closed). | 2026-07-23: 21–23/67 frontier TRUE rows kernel-verified; 9/9 shippable certs accepted by the local Lean judge; 0/25 ETP-FALSE negative controls. | Cert byte cap 49.5 KB (real judge cap is 50 KB, not the solver's 100 KB constant). Wall-clock/candidate-order nondeterministic like the other closure engines. |
| `true:grind` | removed from active solver | retired | Historical short heuristic shape only. | Lean `grind` under heartbeat cap. | Tactic automation, not solver-owned proof search. | Historical `34` accepted / `433` incorrect; failed playground error discipline. | Do not re-enable as default or playground evidence. |

## FALSE Routes

| Route | Key functions | Status | Trigger | Certificate shape | Theory justification | Evidence / checks | Review notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `false:witness:*` | `WITNESS_TABLES`, `find_counterexample`, `witness_check` | active | Named table satisfies hypothesis and refutes goal. | `Fin n` magma plus `decideFin!`. | A finite countermodel refutes universal implication. | Compact witness fixture; public FALSE wins; `S9A` real-judge accepted 5/5 (2026-07-23). | Each table is checked before emission. **Every table is tried on every problem** — the old `LARGE_WITNESS_SHAPE_KEYS` gate pinned `S9A` to one goal and cost 30 HF rows for 0.021 ms/problem of savings. Never gate a sound witness on an equation-pair shape. Keep provenance card. |
| `false:semilattice:*`, `false:spine:*`, `false:central:*`, `false:rectband:*` | `structured_family_tables` | active | Generated finite family separates pair. | Same finite-countermodel certificate. | Standard finite algebra families instantiate small magmas. | Checked by `table_is_counterexample` before certificate. | Family generation is runtime local, no cache dependency. |
| `false:linear:*`, `false:affine:*` | `affine_family_tables` | active | Modular affine operation separates pair. | Same finite-countermodel certificate. | Operations over `Z_n` are finite magmas; brute semantic check proves separation. | Hard-mix witness evidence. | Sizes are empirical. Document before expanding. |
| `false:linear:z11..z25` | `large_linear_family_tables` | active | Linear model `ax + by (mod n)` over `Z_n`, `n` in 11..25, separates pair. | `List.getD` table plus `decideFin!` — the `finOpTable` digit parser cannot render these orders. | Same finite-countermodel reasoning; the only new thing is the rendering. | `hard2_0051` judge-accepted end-to-end in 5.6 s (2026-07-31), the row the retired order-10 ceiling had made unreachable. | Linear only (`c = 0`): the affine sweep is O(n³) tables, 15,625 at order 25. Placed late in the FALSE dispatch so solved rows never pay. Bounded by `witness_decide_is_affordable`, not by the size tuple. |
| `false:quadratic_*` | `quadratic_family_tables` | active | Modular quadratic/bilinear operation separates pair. | Same finite-countermodel certificate. | Same finite model reasoning. | Useful for compact hard FALSE wins. | Keep dedupe; watch runtime. |
| `false:enum_fin*` | `enumerate_tables` | active | Exhaustive table search up to `ENUMERATION_MAX_N`. | Exhaustive finite model search. | Local semantic verifier before Lean. | Bound 3 keeps runtime sane. Do not raise broadly. |
| `false:dual:*` | `dual_equation`, `transpose_table`, recursive `find_counterexample` | active | Countermodel found for dual pair; transpose refutes original. | Same finite-countermodel certificate. | Duality swaps argument order; transposed magma transports countermodels. | Checked after transpose by normal certificate emission path. | Keep; verify transpose involution in route fixture. |

## LLM Routes

| Route | Key functions | Status | Trigger | Validation | Evidence / checks | Review notes |
| --- | --- | --- | --- | --- | --- | --- |
| Solo proxy LLM | `send_proxy_call`, `judge_via_solo_proxy`, `run_solo` | llm | Deterministic route absent or rejected. | Official proxy mediates model and judge. | Positive-token parity required. | Solver never sees real upstream key. |
| Marathon proxy LLM | `load_marathon_llm`, `render_marathon_prompt`, `run_marathon` | llm | Positive token budget and unresolved problem. | Official helper enforces budget and proxy. | `tokens_used > 0` required for LLM evidence; 2026-05-30 analysis-only TRUE100 spent `179936` tokens, TRUE red-flags spent `22764`, and official `normal_100` spent `47419` through the official proxy. | Full-reference token budgets now allow up to one LLM call per manifest row; compressed/default budgets keep the conservative cap. |
| `llm:true:rewrite_chain`, `llm:true:guided_chain` | `candidate_from_llm_text`, `parse_llm_chain_terms_with_reason`, `chain_certificate_from_terms`, `guided_chain_certificate_from_terms` | llm | LLM returns TRUE JSON chain. | Chain terms must use only goal variables; every adjacent step must be proved by solver-owned rewrite or bounded guided-closure logic. | `smoke_llm_dsl.py`; 2026-05-30 analysis-only TRUE100 showed 67 checked LLM proposals and 0 accepted LLM certificates. | Preferred TRUE LLM shape. Current dominant reject is unsupported chain edges, not parser loss. |
| `llm:true:raw_code` | `sanitize_lean_code` | llm, Solo/debug only | LLM returns a complete Lean file outside the Marathon TRUE lane. | Allowed imports, banned tokens, size, and `submission` checked before judge. Marathon calls `candidate_from_llm_text_with_reason(..., allow_raw_true=False)`. | `smoke_llm_dsl.py`; judged targeted evidence still required. | Raw Lean may include helper declarations above `submission`, but Marathon TRUE submissions must remain solver-owned rewrite or guided chains. |
| `llm:false:table` | `normalize_table`, `table_is_counterexample`, `make_false_answer` | llm | LLM returns finite table. | Table shape and semantic counterexample verified before Lean. | Targeted LLM fixture. | Best FALSE LLM shape because solver verifies it locally. |

## Cross-Cutting Invariants

1. Submitted judge answers contain exactly `verdict` and `code`; route metadata stays in stderr or result summaries.
2. Solver runtime must not import repo-local modules, read caches, scrape Teorth, or require local secrets.
3. Every deterministic certificate is either syntactic equality reasoning or a locally checked finite countermodel before Lean emission.
4. `tmp_stage2_smoke/` is scratch; promotion evidence belongs in dated summaries under `stage2/results/`.
5. Historical grind-inclusive totals must be caveated; active packaged solver no longer exposes grind.
6. Active Marathon validation must use a positive token budget; `--budget-tokens 0` is not a promotion or guardrail lane.

## Route Fixture Backlog

- Singleton/collapse fixture: one direct public accepted case and one negative non-trigger.
- Direct substitution/bridge fixture: direct, symmetric, two-instance bridge, completed constancy.
- Projection fixture: left projection and right projection examples.
- Closure fixture: accepted absorption, deep absorption, and equational closure examples from hard summaries.
- FALSE fixture: compact named witnesses plus one structured/affine/quadratic/dual witness.
- LLM fixture: mixed official rows by default, or targeted unresolved TRUE rows with `run_playground_parity_llm.py --fixture-mode unresolved-true`.
