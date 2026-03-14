# Magma AI — TAO Challenge (Stage 1)

Competition: **Equational Implication over Magmas**  
Organizers: Damek Davis (UPenn) & Terence Tao (UCLA) / SAIR Foundation

## Goal

Submit a **cheatsheet** (≤10KB plain text) that helps an LLM determine whether `Equation 1 ⟹ Equation 2` over all magmas.

## Stage 1 Rules

- **Task**: Binary TRUE/FALSE for "Does Eq1 imply Eq2?"
- **Cheatsheet cap**: 10KB
- **Scoring**: correctness only (log-loss on balanced 50/50 TRUE/FALSE eval set)
- **Deadline**: April 20, 2026 23:59 AoE
- **Budget**: ≤$0.01 avg, ≤10 min per problem

## Training Data

- **Normal** (1000 problems): [HuggingFace normal.jsonl](https://huggingface.co/datasets/...)
- **Hard** (200 problems): [HuggingFace hard.jsonl](https://huggingface.co/datasets/...)
- **Full raw dataset**: 4694 laws × 4693 = 22M+ implications from [Equational Theories Project](https://teorth.github.io/equational_theories/implications/)

## Files

| File | Description |
|------|-------------|
| `equations.txt` | All 4694 equational laws (line number = equation index) |
| `export_explorer_14_3_2026.csv` | Explorer summary: implies/implied-by counts per equation |
| `export_raw_implications_14_3_2026.csv` | Full 4694×4694 raw implication matrix |
| `cheatsheet.txt` | **THE SUBMISSION** — ≤10KB prompt guidance |
| `evaluate.py` | Local evaluation script |
| `analyze_equations.py` | Equation parsing & structural feature extraction |
| `data/` | Training data (normal.jsonl, hard.jsonl) |

## Evaluation Prompt (Jinja2)

```
You are a mathematician specializing in equational theories of magmas.
Your task is to determine whether Equation 1 ({{ equation1 }}) implies Equation 2 ({{ equation2 }}) over all magmas.
{% if cheatsheet is defined and cheatsheet %}
{{ cheatsheet }}
{% endif %}
Output format (use exact headers without any additional text or formatting):
VERDICT: must be exactly TRUE or FALSE (in the same line).
REASONING: must be non-empty.
PROOF: required if VERDICT is TRUE, empty otherwise.
COUNTEREXAMPLE: required if VERDICT is FALSE, empty otherwise.
```

## Key Concepts

A **magma** (M, ◇) is a set M with a binary operation ◇: M×M → M (no axioms required).

**Equation E1 implies E2** means: every magma satisfying E1 also satisfies E2.

## Quick Start

```bash
pip install -r requirements.txt
python evaluate.py --cheatsheet cheatsheet.txt --data data/normal.jsonl
```
