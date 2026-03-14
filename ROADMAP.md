# Roadmap: Boosting Repo Effectiveness for SAIR Stage 1

This document synthesizes insights from the foundational paper ("The Equational Theories Project," Tao et al., Dec 2025) and a thorough audit of the current repo, then maps them to concrete actions organized by the six Master Prompt workstreams.

---

## I. Paper Synthesis — Key Mathematical Facts Not Yet Exploited

### 1. Corrected Base Rate (FIXED)

| Claim | Old cheatsheet | Paper / CSV ground truth |
|---|---|---|
| TRUE rate | ~6% | **37.12%** (8,178,279 / 22,033,636) |
| FALSE rate | ~94% | **62.88%** (13,855,357 / 22,033,636) |

The cheatsheet has been corrected. All heuristic priors, default verdicts, and scoring calibration must reflect ~37% TRUE.

### 2. Equivalence Class Structure

- 4694 equations collapse into **1,415 equivalence classes**.
- The largest class has **1,496 equations** all equivalent to the singleton law E2 (x = y). Any equation whose two sides have disjoint variable sets and at least one ◇ operation falls here.
- The second-largest class has only 59 members.
- 819 classes are singletons (one equation each).
- **Cheatsheet leverage**: Correctly identifying the ~1496 singleton-equivalent laws instantly resolves 1496 × 4693 ≈ 7M implication questions (all TRUE when such a law is Eq1).

### 3. Counterexample Arsenal (Paper Ch. 3–4)

| Method | Coverage | Repo status |
|---|---|---|
| Finite magmas size ≤ 4 (524 magmas) | **96.3%** of all false implications | `magma_search.py` searches up to size 5 ✓ |
| Linear magmas x◇y = ax+by (mod p) | Covers most remaining false cases | `magma_search.py` `linear_magma_search_primes()` ✓ |
| Translation-invariant models (Cayley-table twists on groups) | Resolves many "medium-hard" cases | `magma_search.py` `translation_invariant_search()` ✓ |
| Twisting semigroups (binary encoding of a functorial invariant) | Structural distinguisher | `magma_search.py` `twisted_magma_search()` ✓ |
| Greedy constructions (inherently infinite, free-algebra extensions) | 820 implications that differ finite vs infinite | `magma_search.py` `greedy_construction_search()` ✓ |
| Affine "magma cohomology" extensions | Systematic model construction from base models | **Not implemented** |
| ATP (Vampire, Prover9/Mace4, egg/MagmaEgg) | Complements exhaustive search | `proof_search.py` `atp_prove()` / `atp_refute()` ✓ (if binaries available) |

**Key paper fact**: Only 524 explicit magmas (all size ≤ 4) suffice to refute 96.3% of all 13.8M false implications. The remaining 3.7% required more sophisticated constructions.

### 4. Proof Method Arsenal (Paper Ch. 3, 6)

| Method | What it does | Repo status |
|---|---|---|
| Specialization (variable substitution) | Most common proof method | `proof_search.py` ✓ |
| BFS/A* rewriting | Find proof chains | `proof_search.py` ✓ |
| Transitivity + duality closure | Chain known implications | `proof_search.py` partial ✓ |
| Matching invariants (variable multiplicities) | Syntactic refutation: if Eq2 requires more "weight" than Eq1 provides, FALSE | `solver.py` `_multiplicity_refutes()` ✓ |
| Canonizer / normal forms | Some laws induce canonical forms on terms; if Eq2's normal form differs, FALSE | `proof_search.py` `canonizer_refutes()` ✓ |
| Unique factorization (left-absorptive laws) | For depth-≤1 LHS, the free magma factors uniquely | Included in canonizer (oriented rules) ✓ |
| ATP integration | Automated theorem proving for harder cases | `proof_search.py` `atp_prove()` ✓ (requires Vampire/eprover on PATH) |

**Key insight from paper**: Only **10,657** positive implications (0.13% of TRUE) needed a direct proof that wasn't reducible to transitivity/duality/self-evidence. Most TRUE implications follow by combining a small set of "seed" proofs with transitivity and duality.

### 5. Duality Symmetry

If E1 ⊨ E2, then E1* ⊨ E2* (where * swaps arguments of ◇). This halves the search space. The cheatsheet mentions duality but doesn't exploit it systematically (e.g., "if you've decided E1→E2, the dual pair has the same answer").

### 6. Spectrum Analysis

- **65%** of equations have "full spectrum" (satisfied by magmas of every finite size).
- **35%** don't (including the 1496 ≡ E2, which force |M|=1).
- The set of possible spectra is highly constrained and determines much of the implication order.
- Cheatsheet could encode spectrum-based reasoning: "if E1 allows all sizes but E2 doesn't, FALSE."

### 7. Finite vs. Infinite Distinction

- **820 implications** differ between finite and infinite magmas.
- These are all TRUE for finite magmas but FALSE for infinite.
- Relevant for edge cases; the competition almost certainly tests on standard (all magma) semantics.

### 8. CNN Results (Paper Ch. 7)

- A 1.34MB CNN achieved **99.7% accuracy** on implication prediction using only equation structure as input.
- On a 5/5/90 train/val/test split, still **99.6%** accuracy.
- The bit table of the full implication graph compresses to ~40KB.
- This proves the structure is highly compressible — meaning a 10KB cheatsheet should be able to capture most of it if we encode the right invariants.

---

## II. Repo Audit — Gaps and Strengths

### Strengths
1. **Architecture is sound**: Separate solver, proof search, counterexample search, distillation, evaluation.
2. **solver.py** already has correct base rate (0.37).
3. **magma_search.py** has good constraint-propagation backtracking up to size 5.
4. **proof_search.py** has BFS, A*, congruence closure, graph chaining.
5. **features.py** extracts meaningful structural features.
6. **train.py** supports XGBoost/LightGBM/MLP with calibration.
7. **Evaluation pipeline** (evaluate.py, run_eval.py) is functional.

### Critical Gaps
1. **Cheatsheet base rate was wrong** (now fixed to 37%).
3. **No linear magma counterexample method** — ~~the highest-leverage algorithmic addition.~~ ✅ IMPLEMENTED (`linear_magma_search_primes`)
4. **No matching invariant / multiplicities check** — ~~a fast syntactic refutation method.~~ ✅ IMPLEMENTED (`_multiplicity_refutes`)
5. **No systematic exploitation of the 1496 singleton-class** — ~~instant TRUE for 7M pairs.~~ ✅ IMPLEMENTED (`_is_singleton_equivalent`)
5. **No ATP integration** — ~~for proof search.~~ ✅ IMPLEMENTED (`atp_prove`, `atp_refute` — requires Vampire/eprover/Mace4 on PATH)
6. **No spectrum-based reasoning** in cheatsheet or solver.
7. **Evaluation has potential leakage risks** — sampling from the same matrix used for training features.
8. **Cheatsheet wastes bytes** on content an LLM already knows (e.g., what a magma is, basic proof methodology) instead of encoding high-value decision data.

---

## III. Prioritized Action Plan by Workstream

### Workstream A: Competition Alignment Audit

| # | Action | Priority | Effort |
|---|---|---|---|
| A1 | Document exactly what the final artifact is (plain-text ≤ 10KB cheatsheet, nothing else) | HIGH | Low |
| A2 | Audit and label every code path as "submission-support" or "research-only" | HIGH | Medium |
| A3 | Verify scoring: is it accuracy? log-loss? Both? Document and align eval metrics. | HIGH | Low |
| A4 | Ensure no inference-time lookup of the implication matrix — currently evaluate.py samples from the matrix, which is fine for benchmarking but must not leak into the cheatsheet | HIGH | Low |

### Workstream B: Benchmark Hygiene

| # | Action | Priority | Effort |
|---|---|---|---|
| B1 | Create a **no-leak benchmark**: hold out N random equation indices entirely from feature extraction and cheatsheet content | CRITICAL | Medium |
| B2 | Report per-bucket accuracy (trivial, specialization, counterexample-easy, ambiguous, landmark, hard) | HIGH | Medium |
| B3 | Report trivial-case share to prevent inflation | HIGH | Low |
| B4 | Build a "hardest 500" benchmark from pairs where structural heuristics are misleading | HIGH | Medium |
| B5 | Download the official training data (normal.jsonl, hard.jsonl) and benchmark against it if available | HIGH | Low |

### Workstream C: Mathematical Understanding Extraction

| # | Action | Priority | Effort |  
|---|---|---|---|
| C1 | **Build singleton-class detector**: Implement a function that identifies equations equivalent to E2 (x=y) using the disjoint-variables criterion from the paper. Encode the full list in a compressed format. | CRITICAL | ✅ DONE |
| C2 | **Implement matching invariant refutation**: Compute variable multiplicity vectors for both sides of each equation. If Eq2 requires a multiplicity pattern that Eq1 doesn't constrain, output FALSE. | HIGH | ✅ DONE |
| C3 | **Build equation taxonomy**: Classify all 4694 equations into families (singleton, projection, idempotent, commutative, associative, constant, self-dual, etc.) using paper's analysis. | HIGH | Medium |
| C4 | **Mine the 524 critical magmas**: From the paper/data, identify which small magmas (size ≤ 4) resolve the most false implications. Rank them by "refutation coverage" and embed the top N in the cheatsheet. | CRITICAL | High |
| C5 | **Implement linear magma search**: x◇y = ax+by (mod p) for primes p ≤ 7. Check if Eq1 is satisfied and Eq2 is violated. This covers cases that exhaustive size-4 search misses. | HIGH | ✅ DONE |
| C9 | **Translation-invariant model search**: x◇y = x + f(y−x) on ℤ/nℤ. Covers medium-hard cases from §3.3. | HIGH | ✅ DONE |
| C10 | **Twisting semigroup search**: Construct M^k with cyclic shifts on base magmas. Functorial invariant from §3.4. | HIGH | ✅ DONE |
| C11 | **Greedy construction framework**: Partial-magma greedy fill for inherently-infinite counterexamples. §3.5. | HIGH | ✅ DONE |
| C12 | **Canonizer / normal-form refutation**: Orient equations as rewrite rules, check if normal forms of Eq2 sides differ. §5.3. | HIGH | ✅ DONE |
| C13 | **ATP integration**: TPTP generation + Vampire/eprover/Mace4 subprocess wrappers. §6. | HIGH | ✅ DONE |
| C6 | **Extract high-hub equations**: From the implication graph, identify equations with many outgoing/incoming implications (high in-degree or out-degree). These are the most important for the cheatsheet to handle correctly. | MEDIUM | Low |
| C7 | **Catalog duality pairs**: For each equation, compute its dual. Group equations by duality relationship and use this to halve the decision space. | MEDIUM | Low |
| C8 | **Spectrum-based rules**: Encode which equations force finite spectrum restrictions (e.g., only allow |M|=1) vs. which allow all sizes. | MEDIUM | Medium |

### Workstream D: Cheatsheet Optimization

| # | Action | Priority | Effort |
|---|---|---|---|
| D1 | **Remove bytes wasted on LLM-obvious content**: The model already knows what a magma is, how to construct proofs, etc. Cut the "what is a magma" preamble and basic proof tips. Replace with more decision data. | HIGH | Low |
| D2 | **Add singleton-class membership data**: Encode a compact representation of which equation numbers are ≡ E2 (e.g., a bitfield, range list, or inclusion criterion). This alone could resolve ~7M pairs. | CRITICAL | Medium |
| D3 | **Add top-coverage counterexample magmas**: Include the ~20 most refutation-powerful magmas as compact tables with annotations of which equation families they refute. | HIGH | Medium |
| D4 | **Add matching-invariant rules**: Encode the variable multiplicity test as a concise algorithm step. | HIGH | Low |
| D5 | **Restructure flowchart by coverage**: Reorder the decision procedure so the highest-coverage steps come first (singleton check → specialization → size-2 magma check → linear magma check → structural heuristics). | HIGH | Medium |
| D6 | **Test algorithm-first vs. data-first cheatsheet variants**: Compare a cheatsheet that leads with compact decision rules vs. one that leads with lookup tables of critical equation data. | MEDIUM | Medium |
| D7 | **Run A/B test across GPT-4o-mini and Claude Sonnet**: Ensure the champion cheatsheet is robust across at least two models. | HIGH | Medium |
| D8 | **Byte budget analysis**: Measure current cheatsheet bytes vs. 10KB cap. Allocate remaining budget to highest-leverage additions. | HIGH | Low |

### Workstream E: ML and Algorithmic Support

| # | Action | Priority | Effort |
|---|---|---|---|
| E1 | **Train XGBoost on full feature set to identify hardest pairs**: Use the ML pipeline to find which pairs the structural features can't resolve, then target those for cheatsheet improvement. | HIGH | Medium |
| E2 | **Cluster equations by implication behavior**: Use the implication graph to cluster equations and identify which clusters the cheatsheet handles poorly. | MEDIUM | Medium |
| E3 | **Feature importance analysis**: Identify which structural features are most predictive of implication, then ensure those features are reflected in the cheatsheet's decision procedure. | MEDIUM | Low |
| E4 | **Mine recurring proof patterns**: From the 10,657 "direct proof" implications, extract common proof templates (e.g., "substitute y=x then simplify") and encode the top patterns as cheatsheet rules. | HIGH | High |
| E5 | **Mine recurring counterexample patterns**: From the 586,925 "hard false" (value -4) implications, identify which counterexample methods work and encode patterns as cheatsheet content. | HIGH | High |
| E6 | **Redundancy detection**: Use ML to identify which cheatsheet content has zero marginal value (the model already gets those cases right without it). Remove or compress. | MEDIUM | Medium |

### Workstream F: Adversarial Evaluation

| # | Action | Priority | Effort |
|---|---|---|---|
| F1 | **Evaluate with trivial cases removed**: Re-score after removing all pairs involving E1 (tautology), E2 (singleton), and pairs where both equations are in the singleton class. | CRITICAL | Low |
| F2 | **Dual-swap test**: For each test pair (E_a, E_b), also test (E_a*, E_b*) and verify consistent answers. | HIGH | Low |
| F3 | **Extra-variable adversarial set**: Build a test set of pairs where Eq2 has variables not in Eq1 (which the paper shows are usually FALSE but not always). | MEDIUM | Low |
| F4 | **Wording sensitivity test**: Make small formatting changes to the cheatsheet and verify performance doesn't collapse. | MEDIUM | Low |
| F5 | **Byte-limit stress test**: Test cheatsheet at 5KB, 8KB, 9.5KB, and 10KB to find the efficiency frontier. | MEDIUM | Low |
| F6 | **Per-landmark accuracy**: Report accuracy specifically for pairs involving E3, E4, E5, E43, E4512, and other landmarks from the paper. | HIGH | Low |

---

## IV. Recommended Execution Order

### Phase 1: Foundation Fixes (Immediate)
1. ~~Fix base rate in cheatsheet~~ ✅ DONE
2. ~~**C1**: Build singleton-class detector~~ ✅ DONE (`solver.py:_is_singleton_equivalent`, `features.py:is_singleton_equivalent`)
3. **D2**: Encode singleton-class data into cheatsheet
4. **D1**: Cut LLM-obvious preamble, free up byte budget
5. **B1**: Create no-leak benchmark
6. **D8**: Byte budget audit

### Phase 2: Core Mathematical Enrichment
7. **C4**: Mine and rank top-coverage counterexample magmas
8. **D3**: Add top counterexample magmas to cheatsheet
9. ~~**C2**: Implement matching invariant refutation~~ ✅ DONE (`solver.py:_multiplicity_refutes`)
10. **D4**: Add matching invariant to cheatsheet flowchart
11. **D5**: Restructure flowchart by coverage order
12. **A1–A4**: Complete alignment audit

### Phase 3: Algorithmic Deepening
13. ~~**C5**: Implement linear magma search~~ ✅ DONE (`magma_search.py:linear_magma_search_primes`)
14. **E4**: Mine recurring proof patterns  
15. **E5**: Mine recurring counterexample patterns
16. **D6**: Test cheatsheet structural variants
17. **D7**: Cross-model A/B testing

### Phase 4: Hardening
18. **B2–B4**: Full bucket-level benchmarking
19. **E1–E3**: ML feature analysis on hard cases
20. **F1–F6**: Full adversarial evaluation suite
21. **E6**: Redundancy detection and compression
22. **Final champion cheatsheet selection**

---

## V. Expected Impact Estimates

| Action | Est. pairs resolved | % of total |
|---|---|---|
| Correct base rate (done) | Affects all heuristic decisions | — |
| Singleton-class detection | ~7,000,000 TRUE | ~32% |
| Top-20 counterexample magmas | ~13,300,000 FALSE (96.3% × 13.8M) | ~60% |
| Matching invariants | Many "structural FALSE" cases | ~5–10% |
| Linear magma search | Remaining ~500K hard FALSE | ~2–3% |
| Proof pattern templates | ~10,000 non-trivial TRUE | ~0.1% |
| **Combined** | **~95+% of all pairs** | |

The key insight: the problem is far more tractable than it appears. The paper proved that a very small number of counterexample magmas and proof methods resolve nearly everything. The cheatsheet's job is to compress this resolution power into ≤10KB of text that an LLM can follow.

---

## VI. Critical Anti-Patterns to Avoid

1. **Don't optimize prompts without fixing math**: Prompt engineering on a cheatsheet with wrong base rates is wasted effort.
2. **Don't treat this as generic classification**: The problem has deep mathematical structure that generic ML ignores.
3. **Don't leak matrix labels into the cheatsheet**: The cheatsheet must encode *methods* and *patterns*, not memorized answers.
4. **Don't bloat the cheatsheet with explanations**: Every byte explaining what a magma is displaces a byte that could encode a critical counterexample magma table.
5. **Don't benchmark only on easy cases**: Trivial cases (involving E1, E2) inflate accuracy. Always report nontrivial accuracy separately.
6. **Don't ignore duality**: Every insight about (E_a, E_b) automatically applies to (E_a*, E_b*). Build this into the pipeline.
