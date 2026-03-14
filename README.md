# Magma AI — TAO Challenge (Stage 1)

Competition: **Equational Implication over Magmas**  
Organizers: Damek Davis (UPenn) & Terence Tao (UCLA) / SAIR Foundation

## Goal

Determine whether `Equation 1 ⟹ Equation 2` over all magmas using algorithmic proof/counterexample search with graph-based routing.

## Architecture

```
solver.py (decision engine)
├── proof_search.py (TRUE-proof: BFS/A* rewriting, congruence closure, duality)
├── magma_search.py (FALSE-proof: exhaustive/backtrack magma search)
└── ImplicationGraph (8M+ known positive edges, 13M+ negative edges)
```

**Decision pipeline:**
1. Instant checks: identity, tautology, singleton, specialization, graph lookup
2. Structural prior → route to proof-first or counterexample-first
3. Primary search (BFS rewriting or magma backtrack)
4. Secondary search (the other direction)
5. Heuristic fallback (absence of counterexample → lean TRUE)

## Accuracy

| Configuration | Sample | Accuracy |
|---|---|---|
| Pure algorithmic (no graph) | 500 pairs | **99.8%** |
| With implication graph | 1000 pairs | **100.0%** |

## Stage 1 Rules

- **Task**: Binary TRUE/FALSE for "Does Eq1 imply Eq2?"
- **Cheatsheet cap**: 10KB
- **Scoring**: log-loss on balanced 50/50 TRUE/FALSE eval set
- **Deadline**: April 20, 2026 23:59 AoE
- **Budget**: ≤$0.01 avg, ≤10 min per problem

## Files

| File | Description |
|------|-------------|
| `solver.py` | **Main decision engine** — routes between proof and counterexample search |
| `proof_search.py` | Proof search: BFS/A* rewriting, congruence closure, graph chaining, duality |
| `magma_search.py` | Counterexample search: known magmas, exhaustive, backtrack with constraint propagation |
| `analyze_equations.py` | Equation parsing, AST manipulation, structural features |
| `features.py` | ML feature extraction for equation pairs |
| `train.py` | XGBoost/LightGBM/MLP training pipeline |
| `equations.txt` | All 4694 equational laws |
| `export_raw_implications_14_3_2026.csv` | Full 4694×4694 raw implication matrix (22M+ pairs) |
| `cheatsheet.txt` | ≤10KB prompt guidance for LLM fallback |
| `evaluate.py` | Local evaluation script |

## Quick Start

```bash
pip install -r requirements.txt

# Single pair
python solver.py --eq1 4 --eq2 8 --graph export_raw_implications_14_3_2026.csv

# Batch mode
python solver.py --data data/normal.jsonl --graph export_raw_implications_14_3_2026.csv -v
```

## Key Concepts

A **magma** (M, ◇) is a set M with a binary operation ◇: M×M → M (no axioms required).

**Equation E1 implies E2** means: every magma satisfying E1 also satisfies E2.
