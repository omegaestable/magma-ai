# Proof Atlas

## Summary

- Equations indexed: 4,694
- Explicit atlas families: 16
- Raw theorem/facts entries compressed: 12,326
- Hard-case bucket entries: 17
- Cheatsheet bytes: 2,472 / 10,240

## Benchmark Alignment

- Aggregated manual-distill patterns: 68
- Aggregated witness hits: 66
- Current cheatsheet sizes: {'v19_noncollapse': 7171, 'v13_proof_required': 10857}

## Canonizers/Free-Magma Arguments

### canonizer_confluence:false:general

- Title: Canonizer / Confluence
- Polarity / Scope / Closure: false / general / facts
- Description: Confluence and canonizer arguments preserve matching invariants and certify many FALSE implications without small finite witnesses.
- Entry count: 44
- Pair count: 156
- Macro pair capacity: 156
- Trigger features: Confluence provenance, matching invariant or canonizer signal, free-magma / normal-form asymmetry
- Known blockers: do not use this lane unless the invariant is stated concretely, avoid vague claims about normal forms or confluence
- Paper refs: paper/metatheorems.tex, paper/intro.tex
- Benchmark relevance: score=1 signals=['heuristic:important when finite witnesses fail']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation467"], "refuted": ["Equation2847"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/Confluence/ManuallySampled.lean", "line": 7}, {"kind": "facts", "satisfied": ["Equation477"], "refuted": ["Equation1426"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/Confluence/ManuallySampled.lean", "line": 10}]
- Supporting theorems: [{"name": "Confluence.Equation467_not_implies_Equation2847", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/Confluence/ManuallySampled.lean", "line": 7}, {"name": "Confluence.Equation477_not_implies_Equation1426", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/Confluence/ManuallySampled.lean", "line": 10}, {"name": "Confluence.Equation477_not_implies_Equation1519", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/Confluence/ManuallySampled.lean", "line": 13}]

## Closure/Index Layer

### closure_dual

- Title: Duality Closure
- Polarity / Scope / Closure: true / general / dual
- Description: Duality transports proven implications across the opposite operation by reversing both sides of the laws.
- Entry count: 0
- Pair count: 0
- Trigger features: dual(lhs) -> dual(rhs) is explicit or transitively derivable
- Known blockers: duality is exact structural symmetry, not loose resemblance
- Paper refs: paper/foundations.tex, paper/intro.tex
- Benchmark relevance: score=0 signals=[]

### closure_transitive

- Title: Transitive Closure
- Polarity / Scope / Closure: true / general / transitive
- Description: Many TRUE pairs in the full matrix are derived by chaining explicit backbone implications.
- Entry count: 0
- Pair count: 0
- Trigger features: pair is TRUE in the outcomes matrix, pair is not itself an explicit theorem edge, a path exists through explicit theorem edges
- Known blockers: do not pretend the derived pair has its own standalone proof file
- Paper refs: paper/foundations.tex, paper/data.tex
- Benchmark relevance: score=0 signals=[]

## Exceptional Hard Cases

### exceptional_hard:false:general

- Title: Exceptional / Hard Cases
- Polarity / Scope / Closure: false / general / facts
- Description: Named constructions and residual hard files capture the pairs that resist easy rewrite and tiny finite-witness compression.
- Entry count: 91
- Pair count: 126
- Macro pair capacity: 126
- Trigger features: Asterix/Austin/InfModel or equation-specific provenance, immune or hard-case behavior
- Known blockers: do not overgeneralize from one named hard construction, prefer conservative fallback when the family trigger is unclear
- Paper refs: paper/intro.tex, paper/conclusions.tex, paper/project.tex
- Benchmark relevance: score=9 signals=['pattern:generic_fp=9']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation65"], "refuted": ["Equation4065", "Equation3862", "Equation1426", "Equation817", "Equation614"], "finite": false, "macro_pair_capacity": 5, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Asterix.lean", "line": 532}, {"kind": "facts", "satisfied": ["Equation374794"], "refuted": ["Equation2"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/InfModel.lean", "line": 39}]
- Supporting theorems: [{"name": "Asterix.Equation65_facts", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Asterix.lean", "line": 532}, {"name": "InfModel.Equation374794_not_implies_Equation2", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/InfModel.lean", "line": 39}, {"name": "InfModel.Equation28770_not_implies_Equation2", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/InfModel.lean", "line": 135}]

### hard_case:false:general

- Title: Unclassified Hard Bucket
- Polarity / Scope / Closure: false / general / facts
- Description: Fallback bucket for explicit entries that remain low-support or weakly classified after provenance analysis.
- Entry count: 11
- Pair count: 21
- Macro pair capacity: 21
- Trigger features: unmatched theorem provenance, low-support family assignment
- Known blockers: this bucket exists to avoid false compression confidence
- Paper refs: paper/conclusions.tex
- Benchmark relevance: score=0 signals=['heuristic:conservative residual family']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation63"], "refuted": ["Equation1692"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/ManuallyProved/Equation63.lean", "line": 312}, {"kind": "facts", "satisfied": ["Equation73"], "refuted": ["Equation4380", "Equation99"], "finite": false, "macro_pair_capacity": 2, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/ManuallyProved/Equation73.lean", "line": 269}]
- Supporting theorems: [{"name": "Eq63.Equation63_not_implies_Equation1692", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/ManuallyProved/Equation63.lean", "line": 312}, {"name": "Eq73.not_99_4380", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/ManuallyProved/Equation73.lean", "line": 269}, {"name": "Eq73.not_203", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/ManuallyProved/Equation73.lean", "line": 296}]

### hard_case:false:finite

- Title: Unclassified Hard Bucket
- Polarity / Scope / Closure: false / finite / facts
- Description: Fallback bucket for explicit entries that remain low-support or weakly classified after provenance analysis.
- Entry count: 6
- Pair count: 1,819
- Macro pair capacity: 91,260
- Trigger features: unmatched theorem provenance, low-support family assignment
- Known blockers: this bucket exists to avoid false compression confidence
- Paper refs: paper/conclusions.tex
- Benchmark relevance: score=0 signals=['heuristic:conservative residual family']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation4673", "Equation4591", "Equation4343", "Equation2939", "Equation2937"], "refuted": ["Equation4658", "Equation4636", "Equation4635", "Equation4629", "Equation4608"], "finite": true, "macro_pair_capacity": 2166, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/FinSearch/theorems/Refutation0.lean", "line": 20}, {"kind": "facts", "satisfied": ["Equation4608", "Equation4470", "Equation4343", "Equation3140", "Equation2873"], "refuted": ["Equation4658", "Equation4636", "Equation4629", "Equation4606", "Equation4605"], "finite": true, "macro_pair_capacity": 2136, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/FinSearch/theorems/Refutation1.lean", "line": 20}]
- Supporting theorems: [{"name": "\u00abFacts from FinSearch [[1,3,2,4,0], [4,2,0,3,1], [0,4,3,1,2], [2,1,4,0,3], [3,0,1,2,4]]\u00bb", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/FinSearch/theorems/Refutation0.lean", "line": 20}, {"name": "\u00abFacts from FinSearch [[4,2,0,3,1], [2,0,3,1,4], [0,3,1,4,2], [3,1,4,2,0], [1,4,2,0,3]]\u00bb", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/FinSearch/theorems/Refutation1.lean", "line": 20}, {"name": "\u00abFacts from FinSearch [[0,4,3,2,1], [2,1,0,4,3], [4,3,2,1,0], [1,0,4,3,2], [3,2,1,0,4]]\u00bb", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/FinSearch/theorems/Refutation2.lean", "line": 20}]

## Linear/Translation-Invariant Constructions

### linear_translation:false:finite

- Title: Linear / Translation-Invariant Countermodels
- Polarity / Scope / Closure: false / finite / facts
- Description: Linear and translation-invariant constructions explain finite refutations that are resistant to tiny table witnesses.
- Entry count: 31
- Pair count: 652
- Macro pair capacity: 962
- Trigger features: LinearOps provenance, affine or translation-invariant construction, finite-only countermodel scope
- Known blockers: finite-only constructions must not be promoted to general implications, this is not the first refutation lane for easy pairs
- Paper refs: paper/constructions.tex, paper/intro.tex
- Benchmark relevance: score=1 signals=['heuristic:used for harder finite-only refutations']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation1286", "Equation1279"], "refuted": ["Equation4470", "Equation4435", "Equation4380", "Equation4118", "Equation4065"], "finite": true, "macro_pair_capacity": 82, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/LinearOps.lean", "line": 45}, {"kind": "facts", "satisfied": ["Equation2301", "Equation2328"], "refuted": ["Equation4470", "Equation4435", "Equation4380", "Equation4118", "Equation4065"], "finite": true, "macro_pair_capacity": 82, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/LinearOps.lean", "line": 50}]
- Supporting theorems: [{"name": "LinearOps.Equation1286_not_implies_Equation3", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/LinearOps.lean", "line": 45}, {"name": "LinearOps.Equation2301_not_implies_Equation3", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/LinearOps.lean", "line": 50}, {"name": "LinearOps.Equation3116_not_implies_Equation513", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/LinearOps.lean", "line": 54}]

## Modified/Enlarged/Extended Magma Constructions

### modified_lifted_magma:false:general

- Title: Modified / Lifted Magma Families
- Polarity / Scope / Closure: false / general / facts
- Description: Lifting, extension, and modification families package many refutations into macro counterexample objects.
- Entry count: 242
- Pair count: 242
- Macro pair capacity: 242
- Trigger features: instLiftingMagmaFamily provenance, base magma modified or extended to refute many targets
- Known blockers: compress as reusable witness families, not pair-by-pair anecdotes
- Paper refs: paper/intro.tex, paper/constructions.tex
- Benchmark relevance: score=1 signals=['heuristic:facts macros compress many false pairs at once']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation936498"], "refuted": ["Equation26302"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/InvariantMetatheoremNonimplications/instLiftingMagmaFamilyList_counterexamples.lean", "line": 5}, {"kind": "facts", "satisfied": ["Equation936498"], "refuted": ["Equation345169"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/InvariantMetatheoremNonimplications/instLiftingMagmaFamilyList_counterexamples.lean", "line": 9}]
- Supporting theorems: [{"name": "Equation936498_not_implies_Equation26302", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/InvariantMetatheoremNonimplications/instLiftingMagmaFamilyList_counterexamples.lean", "line": 5}, {"name": "Equation936498_not_implies_Equation345169", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/InvariantMetatheoremNonimplications/instLiftingMagmaFamilyList_counterexamples.lean", "line": 9}, {"name": "Equation1_not_implies_Equation26302", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/InvariantMetatheoremNonimplications/instLiftingMagmaFamilyList_counterexamples.lean", "line": 13}]

## Projection/Absorption Families

### projection_family_counterexamples:false:general

- Title: Projection / Absorption Counterexamples
- Polarity / Scope / Closure: false / general / facts
- Description: Projection-style witnesses and leaf-anchoring asymmetries are the highest-yield FALSE families on the current benchmark trail.
- Entry count: 52
- Pair count: 52
- Macro pair capacity: 52
- Trigger features: LP/RP obstruction, leftmost or rightmost leaf mismatch, fresh variables in E2
- Known blockers: FALSE still requires a named witness and concrete check, projection cues are search priorities, not standalone proofs
- Paper refs: paper/spectrum.tex, paper/intro.tex
- Benchmark relevance: score=55 signals=['pattern:fp_new_variable_trap=16', 'pattern:fp_lp_obstruction_missed=4', 'pattern:fp_rp_obstruction_missed=14', 'pattern:fp_both_projections_missed=1', 'witness:LP=5', 'witness:RP=15']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation4656"], "refuted": ["Equation26302"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/InvariantMetatheoremNonimplications/instLiftingMagmaFamilyLeftProj_counterexamples.lean", "line": 5}, {"kind": "facts", "satisfied": ["Equation4656"], "refuted": ["Equation345169"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/InvariantMetatheoremNonimplications/instLiftingMagmaFamilyLeftProj_counterexamples.lean", "line": 9}]
- Supporting theorems: [{"name": "Equation4656_not_implies_Equation26302", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/InvariantMetatheoremNonimplications/instLiftingMagmaFamilyLeftProj_counterexamples.lean", "line": 5}, {"name": "Equation4656_not_implies_Equation345169", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/InvariantMetatheoremNonimplications/instLiftingMagmaFamilyLeftProj_counterexamples.lean", "line": 9}, {"name": "Equation4065_not_implies_Equation26302", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/InvariantMetatheoremNonimplications/instLiftingMagmaFamilyLeftProj_counterexamples.lean", "line": 13}]

## Rewrite/Metatheorem Families

### rewrite_metatheorem:true:general

- Title: Rewrite / Metatheorem
- Polarity / Scope / Closure: true / general / explicit
- Description: Direct substitution and trivial rewrite schemas cover a large fraction of explicit positive implications.
- Entry count: 8,126
- Pair count: 8,126
- Trigger features: syntactic weakening of E1 into E2, single-step or bounded-step rewrite files, trivial-bruteforce theorem provenance
- Known blockers: do not call a rewrite valid unless the concrete chain is visible, structural resemblance alone is not a proof
- Paper refs: paper/intro.tex, paper/metatheorems.tex
- Benchmark relevance: score=24 signals=['pattern:fn_no_projection_handle=24']
- Canonical exemplars: [{"kind": "implication", "lhs": "Equation150", "rhs": "Equation149", "finite": false, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/SimpleRewrites/theorems/Rewrite_uw.lean", "line": 9}, {"kind": "implication", "lhs": "Equation254", "rhs": "Equation253", "finite": false, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/SimpleRewrites/theorems/Rewrite_uw.lean", "line": 11}]
- Supporting theorems: [{"name": "SimpleRewrites.Equation150_implies_Equation149", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/SimpleRewrites/theorems/Rewrite_uw.lean", "line": 9}, {"name": "SimpleRewrites.Equation254_implies_Equation253", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/SimpleRewrites/theorems/Rewrite_uw.lean", "line": 11}, {"name": "SimpleRewrites.Equation536_implies_Equation535", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/SimpleRewrites/theorems/Rewrite_uw.lean", "line": 13}]

### rewrite_metatheorem:false:general

- Title: Rewrite / Metatheorem
- Polarity / Scope / Closure: false / general / facts
- Description: Direct substitution and trivial rewrite schemas cover a large fraction of explicit positive implications.
- Entry count: 22
- Pair count: 65
- Macro pair capacity: 65
- Trigger features: syntactic weakening of E1 into E2, single-step or bounded-step rewrite files, trivial-bruteforce theorem provenance
- Known blockers: do not call a rewrite valid unless the concrete chain is visible, structural resemblance alone is not a proof
- Paper refs: paper/intro.tex, paper/metatheorems.tex
- Benchmark relevance: score=24 signals=['pattern:fn_no_projection_handle=24']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation1117"], "refuted": ["Equation2441"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/ManuallyProved/Equation1117.lean", "line": 8}, {"kind": "facts", "satisfied": ["Equation1289"], "refuted": ["Equation4435", "Equation3116"], "finite": false, "macro_pair_capacity": 2, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/ManuallyProved/Equation1289.lean", "line": 397}]
- Supporting theorems: [{"name": "Equation1117_not_implies_Equation2441", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/ManuallyProved/Equation1117.lean", "line": 8}, {"name": "Eq1289.not_3116_4435", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/ManuallyProved/Equation1289.lean", "line": 397}, {"name": "Eq1323.Equation1323_not_implies_Equation2744", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/ManuallyProved/Equation1323.lean", "line": 668}]

### automated_reasoner:true:general

- Title: Automated Equational Reasoner
- Polarity / Scope / Closure: true / general / explicit
- Description: ATP and e-graph generated proofs contribute a sizable explicit theorem backbone even when the human summary should stay compact.
- Entry count: 2,339
- Pair count: 2,339
- Trigger features: VampireProven or MagmaEgg provenance, syntactic or automated equational closure
- Known blockers: the cheatsheet should compress these into reusable patterns, not cite solver names as proof
- Paper refs: paper/automated.tex, paper/intro.tex
- Benchmark relevance: score=1 signals=['heuristic:useful provenance, low direct prompt value']
- Canonical exemplars: [{"kind": "implication", "lhs": "Equation102", "rhs": "Equation1029", "finite": false, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/VampireProven/Proofs1.lean", "line": 6}, {"kind": "implication", "lhs": "Equation102", "rhs": "Equation1226", "finite": false, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/VampireProven/Proofs1.lean", "line": 19}]
- Supporting theorems: [{"name": "Equation102_implies_Equation1029", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/VampireProven/Proofs1.lean", "line": 6}, {"name": "Equation102_implies_Equation1226", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/VampireProven/Proofs1.lean", "line": 19}, {"name": "Equation1021_implies_Equation47", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/VampireProven/Proofs1.lean", "line": 32}]

### singleton_rewrite:true:general

- Title: Singleton Rewrite
- Polarity / Scope / Closure: true / general / explicit
- Description: Singleton-strength equations collapse the model immediately and are high-confidence TRUE sources.
- Entry count: 106
- Pair count: 106
- Trigger features: E1 literally has the form x = term, x does not occur on the RHS of E1, often lands in the large singleton equivalence class
- Known blockers: do not use when x still appears in the RHS, do not promote approximate similarity into singleton strength
- Paper refs: paper/intro.tex, paper/metatheorems.tex
- Benchmark relevance: score=1 signals=['heuristic:high-value TRUE eliminator']
- Canonical exemplars: [{"kind": "implication", "lhs": "Equation89", "rhs": "Equation2", "finite": false, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/Singleton.lean", "line": 9}, {"kind": "implication", "lhs": "Equation144", "rhs": "Equation2", "finite": false, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/Singleton.lean", "line": 13}]
- Supporting theorems: [{"name": "Singleton.Equation89_implies_Equation2", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/Singleton.lean", "line": 9}, {"name": "Singleton.Equation144_implies_Equation2", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/Singleton.lean", "line": 13}, {"name": "Singleton.Equation147_implies_Equation2", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/Singleton.lean", "line": 17}]

### subgraph_seed:true:general

- Title: Subgraph Seed Implications
- Polarity / Scope / Closure: true / general / explicit
- Description: Seed implications anchor the closure graph and often act as short canonical witnesses for broad regions of the graph.
- Entry count: 104
- Pair count: 104
- Trigger features: explicit subgraph theorem provenance, basic backbone edges reused by transitive closure
- Known blockers: many downstream truths are closure facts, not standalone seed theorems
- Paper refs: paper/foundations.tex, paper/data.tex
- Benchmark relevance: score=1 signals=['heuristic:backbone closure family']
- Canonical exemplars: [{"kind": "implication", "lhs": "Equation2", "rhs": "Equation3", "finite": false, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Subgraph.lean", "line": 23}, {"kind": "implication", "lhs": "Equation2", "rhs": "Equation4", "finite": false, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Subgraph.lean", "line": 27}]
- Supporting theorems: [{"name": "Subgraph.Equation2_implies_Equation3", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Subgraph.lean", "line": 23}, {"name": "Subgraph.Equation2_implies_Equation4", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Subgraph.lean", "line": 27}, {"name": "Subgraph.Equation2_implies_Equation5", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Subgraph.lean", "line": 31}]

### subgraph_seed:false:general

- Title: Subgraph Seed Implications
- Polarity / Scope / Closure: false / general / facts
- Description: Seed implications anchor the closure graph and often act as short canonical witnesses for broad regions of the graph.
- Entry count: 64
- Pair count: 66
- Macro pair capacity: 66
- Trigger features: explicit subgraph theorem provenance, basic backbone edges reused by transitive closure
- Known blockers: many downstream truths are closure facts, not standalone seed theorems
- Paper refs: paper/foundations.tex, paper/data.tex
- Benchmark relevance: score=1 signals=['heuristic:backbone closure family']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation3"], "refuted": ["Equation39"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Subgraph.lean", "line": 571}, {"kind": "facts", "satisfied": ["Equation3"], "refuted": ["Equation42"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Subgraph.lean", "line": 575}]
- Supporting theorems: [{"name": "Subgraph.Equation3_not_implies_Equation39", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Subgraph.lean", "line": 571}, {"name": "Subgraph.Equation3_not_implies_Equation42", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Subgraph.lean", "line": 575}, {"name": "Subgraph.Equation3_not_implies_Equation4512", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Subgraph.lean", "line": 579}]

## Small Finite Magma Families

### small_finite_magma:false:finite

- Title: Small Finite Magma Counterexamples
- Polarity / Scope / Closure: false / finite / facts
- Description: Explicit small magmas and compact witness tables cover most false implications and dominate current benchmark failures.
- Entry count: 142
- Pair count: 32,785
- Macro pair capacity: 1,016,252
- Trigger features: small Cayley-table witness, XOR/XNOR/C0/AND/OR style counterexamples, manually sampled or Z3-assisted finite refutations
- Known blockers: the witness must show E1 holds and E2 fails on a concrete assignment, do not report a family without the actual check
- Paper refs: paper/constructions.tex, paper/intro.tex, RULESET.md
- Benchmark relevance: score=46 signals=['witness:C0=12', 'witness:XOR=12', 'witness:XNOR=12', 'witness:AND=5', 'witness:OR=5', 'shared-pattern:fp_new_variable_trap=16']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation4155", "Equation4070", "Equation3674", "Equation3461", "Equation3306"], "refuted": ["Equation4658", "Equation4636", "Equation4635", "Equation4629", "Equation4608"], "finite": true, "macro_pair_capacity": 6216, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/FinitePoly/Refutation6.lean", "line": 21}, {"kind": "facts", "satisfied": ["Equation5"], "refuted": ["Equation4658", "Equation4636", "Equation4629", "Equation4608", "Equation4605"], "finite": true, "macro_pair_capacity": 339, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/FinitePoly/Refutation8.lean", "line": 21}]
- Supporting theorems: [{"name": "\u00abFacts from FinitePoly 2 * x\u00b2 + x + y + 2 * x * y % 3\u00bb", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/FinitePoly/Refutation6.lean", "line": 21}, {"name": "\u00abFacts from FinitePoly x\u00b2 + x + y % 2\u00bb", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/FinitePoly/Refutation8.lean", "line": 21}, {"name": "\u00abFacts from FinitePoly x + 2 * y % 4\u00bb", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/FinitePoly/Refutation14.lean", "line": 21}]

### all4x4_table_counterexamples:false:finite

- Title: All4x4 Table Counterexamples
- Polarity / Scope / Closure: false / finite / facts
- Description: Brute-force small-table counterexamples compress large banks of finite refutations that are especially valuable for FALSE coverage.
- Entry count: 940
- Pair count: 22,270
- Macro pair capacity: 149,006
- Trigger features: All4x4Tables provenance, explicit finite table macro refutations, many refuted targets packed into one witness family
- Known blockers: finite-only tables must not be promoted to general claims, keep this family as a witness source, not as free-form prose
- Paper refs: paper/constructions.tex, paper/intro.tex, RULESET.md
- Benchmark relevance: score=0 signals=['heuristic:conservative residual family']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation4081", "Equation3140", "Equation2900", "Equation2460", "Equation2301"], "refuted": ["Equation4635", "Equation4590", "Equation4585", "Equation4482", "Equation4442"], "finite": true, "macro_pair_capacity": 2296, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/All4x4Tables/Refutation0.lean", "line": 20}, {"kind": "facts", "satisfied": ["Equation3269", "Equation2301", "Equation1516", "Equation1286", "Equation1112"], "refuted": ["Equation4658", "Equation4636", "Equation4635", "Equation4629", "Equation4608"], "finite": true, "macro_pair_capacity": 3465, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/All4x4Tables/Refutation1.lean", "line": 20}]
- Supporting theorems: [{"name": "\u00abFacts from All4x4Tables [[0,2,1,4,3,6,5],[3,1,5,0,6,2,4],[4,6,2,5,0,3,1],[6,5,4,3,2,1,0],[5,3,6,1,4,0,2],[2,4,0,6,1,5,3],[1,0,3,2,5,4,6]]\u00bb", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/All4x4Tables/Refutation0.lean", "line": 20}, {"name": "\u00abFacts from All4x4Tables [[0,2,3,1,5,6,4],[4,1,6,0,3,2,5],[5,0,2,4,6,1,3],[6,5,0,3,1,4,2],[1,6,5,2,4,3,0],[2,3,4,6,0,5,1],[3,4,1,5,2,0,6]]\u00bb", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/All4x4Tables/Refutation1.lean", "line": 20}, {"name": "\u00abFacts from All4x4Tables [[0,2,3,4,5,6,1],[6,1,0,5,2,4,3],[1,4,2,0,6,3,5],[2,6,5,3,0,1,4],[3,5,1,6,4,0,2],[4,3,6,2,1,5,0],[5,0,4,1,3,2,6]]\u00bb", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/Generated/All4x4Tables/Refutation2.lean", "line": 20}]

### central_groupoid_counterexamples:false:general

- Title: Central Groupoid Counterexamples
- Polarity / Scope / Closure: false / general / facts
- Description: Central-groupoid style finite constructions capture structured hard FALSE regions that are not well described by the smallest canned witnesses alone.
- Entry count: 6
- Pair count: 38
- Macro pair capacity: 422
- Trigger features: CentralGroupoids or ThreeC2 provenance, structured finite witness family beyond tiny canned tables
- Known blockers: treat as finite-only witness families, do not compress these into vague algebraic jargon in the prompt
- Paper refs: paper/constructions.tex, paper/conclusions.tex
- Benchmark relevance: score=0 signals=['heuristic:conservative residual family']
- Canonical exemplars: [{"kind": "facts", "satisfied": ["Equation1485"], "refuted": ["Equation3457"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/WeakCentralGroupoids.lean", "line": 281}, {"kind": "facts", "satisfied": ["Equation1485"], "refuted": ["Equation3511"], "finite": false, "macro_pair_capacity": 1, "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/WeakCentralGroupoids.lean", "line": 302}]
- Supporting theorems: [{"name": "Refutation_1485.not_3457", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/WeakCentralGroupoids.lean", "line": 281}, {"name": "Refutation_1485.not_3511", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/WeakCentralGroupoids.lean", "line": 302}, {"name": "Refutation_1485.not_2087_2124", "file": "/home/runner/work/equational_theories/equational_theories/equational_theories/WeakCentralGroupoids.lean", "line": 323}]
