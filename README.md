# Magma AI

Magma AI is a submission-focused research repository for Stage 1 of the SAIR Mathematics Distillation Challenge on equational implication over magmas. The repository has two jobs:

1. Produce a strong plain-text cheatsheet under 10 KB.
2. Preserve the mathematical and experimental tooling used to build that cheatsheet without confusing research-time assistance with submission-time behavior.

The current competition-oriented source of truth is [docs/MASTER_SUBMISSION_AGENT_PROMPT.md](docs/MASTER_SUBMISSION_AGENT_PROMPT.md). If a rule claim is not grounded there or in archived primary competition material, it should be treated as unverified.

## What This Repository Is About

The underlying mathematics comes from the Equational Theories Project, which studied implication between the 4694 simplest equational laws on magmas. A magma is just a set with one binary operation and no further axioms assumed. Given two laws $E_1$ and $E_2$, the central question is whether every magma satisfying $E_1$ must also satisfy $E_2$.

The LaTeX paper in [docs/paper/source](docs/paper/source) gives the larger context. The most important facts for this repository are:

- There are 4694 laws in scope, listed in `equations.txt`.
- This yields 22,028,942 non-reflexive implication questions.
- The full implication graph was resolved in the broader project through a combination of rewriting, duality, finite counterexamples, linear models, automated theorem proving, and formal verification in Lean.
- In this repo, that full graph is research data. The Stage 1 submission artifact is not the graph; it is the cheatsheet.

Concrete landmark equations used throughout the code and docs include:

- Eq1: `x = x`, the trivial top law.
- Eq2: `x = y`, the singleton law that implies every law.
- Eq43: `x ◇ y = y ◇ x`, commutativity.
- Eq4512: `x ◇ (y ◇ z) = (x ◇ y) ◇ z`, associativity.

## Submission Boundary

The only intended submission artifact is [cheatsheet.txt](cheatsheet.txt).

Submission-valid behavior:

- Prompting an evaluation model with the cheatsheet alone.
- Optionally using separate, non-evaluation examples purely for output formatting.

Research-only behavior:

- Looking up answers in the dense implication matrix.
- Using graph reachability, solver shortcuts, proof search, counterexample search, or ML models at inference time.
- Feeding evaluation labels back into the prompt context.

If a workflow touches the matrix or graph during inference, it is useful for research but not a valid Stage 1 submission path.

## Repository Layout

Top-level files are now limited to the working code and primary artifact. Supporting assets live under `data/` and `docs/`.

| Path | Purpose |
|---|---|
| `cheatsheet.txt` | Current submission candidate |
| `equations.txt` | Canonical list of the 4694 equations |
| `run_eval.py` | LLM-based cheatsheet evaluation harness |
| `evaluate.py` | Local heuristic benchmark and prompt export |
| `distill.py` | Offline cheatsheet distillation pipeline |
| `solver.py` | Research-only implication engine |
| `data/local_benchmark.jsonl` | Small offline benchmark that requires no external host |
| `data/exports/` | Dense implication matrix and explorer export |
| `docs/guides/tutorial.md` | End-to-end usage tutorial |
| `docs/guides/math-background.md` | Mathematical background distilled from the paper |
| `docs/ARCHITECTURE.md` | Repo structure and data-flow guide |
| `docs/paper/` | PDF copies and LaTeX source for the project paper |

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run an offline sanity check

This path uses only local files already present in the repo.

```bash
python evaluate.py --mode heuristic --data data/local_benchmark.jsonl
```

### 3. Generate a fresh local benchmark

```bash
python download_data.py --generate-local --n 200 --seed 42
```

This samples a balanced JSONL benchmark from `data/exports/export_raw_implications_14_3_2026.csv`.

### 4. Validate the LLM evaluation pipeline without making API calls

```bash
python run_eval.py --data data/local_benchmark.jsonl --dry-run
```

### 5. Run a live cheatsheet evaluation

```bash
python run_eval.py --cheatsheet cheatsheet.txt --data data/local_benchmark.jsonl --eval-model gpt-4o-mini --name local_eval
```

The safe default is now `--n-format 0`. If you want format examples, supply a separate labeled file explicitly with `--format-data`.

## Tutorial Workflow

The recommended workflow for contributors is:

1. Read [docs/guides/math-background.md](docs/guides/math-background.md) for the algebraic setup.
2. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand which scripts are submission-support versus research-only.
3. Use [docs/guides/tutorial.md](docs/guides/tutorial.md) for the step-by-step command flow.
4. Iterate on `cheatsheet.txt` or distill a new candidate with `distill.py`.
5. Evaluate with `run_eval.py` and keep the validity metadata with the result.

## Mathematical Approach Used In This Repo

The paper shows that no single method is enough to understand the implication graph. The practical approach in this repository follows the same lesson.

Positive implications are often discovered or checked using:

- direct specialization;
- rewriting under a single law;
- duality and transitivity;
- ATP-assisted proof search.

Negative implications are often discovered or checked using:

- explicit small finite magmas;
- linear and translation-invariant constructions;
- syntactic invariants;
- greedy counterexample search.

The heuristic and ML code in this repo can exploit structural signals such as variable support, operation count, depth, symmetry, and easy counterexamples. Those signals are useful for research prioritization, but they are not themselves proofs.

## Data And Reproducibility Notes

- `data/local_benchmark.jsonl` is the supported no-network evaluation fallback.
- `data/exports/export_raw_implications_14_3_2026.csv` is the dense 4694 x 4694 implication matrix used for offline research and benchmark generation.
- `data/exports/export_explorer_14_3_2026.csv` is an auxiliary explorer export used for analysis notebooks and reporting.
- The old hardcoded Hugging Face dataset path still appears stale as of 2026-03-14. Treat remote download as best-effort only until an official path is restored.

## Documentation Index

- [docs/guides/tutorial.md](docs/guides/tutorial.md)
- [docs/guides/math-background.md](docs/guides/math-background.md)
- [docs/guides/competition-readiness-report.md](docs/guides/competition-readiness-report.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/competition_alignment_memo.md](docs/competition_alignment_memo.md)
- [docs/benchmark_integrity_memo.md](docs/benchmark_integrity_memo.md)
- [docs/mathematical_notes.md](docs/mathematical_notes.md)
- [docs/risk_register.md](docs/risk_register.md)

## Current Cleanup Highlights

- Publication assets and paper materials were moved out of the repository root.
- Data exports now live under `data/exports/`.
- Generated LaTeX intermediates and archive clutter were removed.
- Script defaults were updated to the new layout.
- `run_eval.py` now defaults to zero format examples, matching the intended benchmark-safety policy.
