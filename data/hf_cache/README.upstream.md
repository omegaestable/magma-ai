---
configs:
- config_name: normal
  data_files:
  - split: train
    path: data/normal.jsonl
- config_name: hard
  data_files:
  - split: train
    path: data/hard.jsonl
- config_name: hard1
  data_files:
  - split: train
    path: data/hard1.jsonl
- config_name: hard2
  data_files:
  - split: train
    path: data/hard2.jsonl
- config_name: hard3
  data_files:
  - split: train
    path: data/hard3.jsonl
- config_name: evaluation_normal
  data_files:
  - split: train
    path: data/evaluation_normal.jsonl
- config_name: evaluation_hard
  data_files:
  - split: train
    path: data/evaluation_hard.jsonl
- config_name: evaluation_extra_hard
  data_files:
  - split: train
    path: data/evaluation_extra_hard.jsonl
- config_name: evaluation_order5
  data_files:
  - split: train
    path: data/evaluation_order5.jsonl
---

# Equational Theories Selected Problems

## Update (April 27, 2026)

This dataset was updated on April 27, 2026.

Main changes:
- added the released Stage 1 final evaluation subsets: `evaluation_normal`, `evaluation_hard`, `evaluation_extra_hard`, and `evaluation_order5`
- added metadata files for the new evaluation subsets
- updated the README and metadata to reflect the current released subsets

## Update (March 24, 2026)

This dataset was updated on March 24, 2026.

Main changes:
- added `eq1_id` and `eq2_id` to all released subsets
- added the `hard3` subset
- updated the README to reflect the current released subsets

This dataset contains selected problem subsets for the Mathematics Distillation Challenge: Equational Theories, including public training subsets and released Stage 1 evaluation subsets.

This dataset is intended for Stage 1 of the Mathematics Distillation Challenge: Equational Theories competition.

Competition page:

- [https://competition.sair.foundation/competitions/mathematics-distillation-challenge-equational-theories-stage1/overview](https://competition.sair.foundation/competitions/mathematics-distillation-challenge-equational-theories-stage1/overview)

The full raw implication dataset contains 4694 laws, which yields `4694 * (4694 - 1) = 22,028,942` ordered implications.

The full raw implications table can be downloaded from the Equational Theories Project implications page by selecting **Download raw implications table**:

- [https://teorth.github.io/equational_theories/implications/](https://teorth.github.io/equational_theories/implications/)

The full list of all 4694 equations is available here:

- [equations.txt](https://raw.githubusercontent.com/teorth/equational_theories/main/data/equations.txt)

Because the full raw dataset is very large, the competition organizers selected public subsets to make testing and experimentation more practical for participants.

## Subsets

- `normal`: 1000 selected problems, chosen programmatically, with 500 ground-truth `TRUE` labels and 500 ground-truth `FALSE` labels
- `hard`: 200 selected problems co-curated by human mathematicians and AI, with 74 ground-truth `TRUE` labels and 126 ground-truth `FALSE` labels
- `hard1`: a deduplicated version of the 200-problem `hard` subset, containing 69 unique problems total, with 24 ground-truth `TRUE` labels and 45 ground-truth `FALSE` labels
- `hard2`: 200 selected problems co-curated by human mathematicians and AI, with 100 ground-truth `TRUE` labels and 100 ground-truth `FALSE` labels
- `hard3`: 400 selected problems with 195 ground-truth `TRUE` labels and 205 ground-truth `FALSE` labels
- `evaluation_normal`: 200 Stage 1 final evaluation problems, with 100 ground-truth `TRUE` labels and 100 ground-truth `FALSE` labels
- `evaluation_hard`: 200 Stage 1 final evaluation problems, with 100 ground-truth `TRUE` labels and 100 ground-truth `FALSE` labels
- `evaluation_extra_hard`: 200 Stage 1 final evaluation problems, with 100 ground-truth `TRUE` labels and 100 ground-truth `FALSE` labels
- `evaluation_order5`: 200 order-5 evaluation problems, with 100 ground-truth `TRUE` labels and 100 ground-truth `FALSE` labels

All subsets are exposed as the `train` split in this repository. The `evaluation_*` subsets are released Stage 1 evaluation subsets.

## Data Schema

Each record has the following fields:

- `id`: stable identifier such as `normal_0001`, `hard_0001`, `hard3_0001`, or `evaluation_normal_0001`
- `index`: 1-based index within the subset
- `difficulty`: subset difficulty label such as `normal`, `hard`, `extra_hard`, or `order5_normal`
- `eq1_id`: 1-based equation identifier for `equation1`; for the order-4-and-below subsets, this refers to the full 4694-law equation list
- `eq2_id`: 1-based equation identifier for `equation2`; for the order-4-and-below subsets, this refers to the full 4694-law equation list
- `equation1`: Equation 1
- `equation2`: Equation 2
- `answer`: whether Equation 1 implies Equation 2 over all magmas

## Subset Metadata

Subset-level metadata for the official released subsets is stored under `metadata/`.

Each metadata file contains:

- `subset_name`: subset identifier
- `source`: release source, such as `official`
- `curators`: list of named curators, if provided
- `difficulty`: subset difficulty label
- `problem_count`: total number of problems in the subset
- `true_count`: number of ground-truth `TRUE` labels
- `false_count`: number of ground-truth `FALSE` labels
- `selection_method`: high-level selection method such as `programmatic`, `human`, or `human_ai`
- `derived_from`: parent subset name if the subset is derived from another subset
- `notes`: optional explanatory notes

Records in `hard1`, `hard2`, and `hard3` use subset-specific IDs and keep `difficulty: hard`.
Records in `evaluation_order5` use order-5 equation identifiers.

## Usage

```python
from datasets import load_dataset

normal = load_dataset(
    "SAIRfoundation/equational-theories-selected-problems",
    "normal",
    split="train",
)

hard = load_dataset(
    "SAIRfoundation/equational-theories-selected-problems",
    "hard",
    split="train",
)

hard1 = load_dataset(
    "SAIRfoundation/equational-theories-selected-problems",
    "hard1",
    split="train",
)

hard2 = load_dataset(
    "SAIRfoundation/equational-theories-selected-problems",
    "hard2",
    split="train",
)

hard3 = load_dataset(
    "SAIRfoundation/equational-theories-selected-problems",
    "hard3",
    split="train",
)

evaluation_normal = load_dataset(
    "SAIRfoundation/equational-theories-selected-problems",
    "evaluation_normal",
    split="train",
)

evaluation_hard = load_dataset(
    "SAIRfoundation/equational-theories-selected-problems",
    "evaluation_hard",
    split="train",
)

evaluation_extra_hard = load_dataset(
    "SAIRfoundation/equational-theories-selected-problems",
    "evaluation_extra_hard",
    split="train",
)

evaluation_order5 = load_dataset(
    "SAIRfoundation/equational-theories-selected-problems",
    "evaluation_order5",
    split="train",
)
```

## Files

- `data/normal.jsonl`
- `data/hard.jsonl`
- `data/hard1.jsonl`
- `data/hard2.jsonl`
- `data/hard3.jsonl`
- `data/evaluation_normal.jsonl`
- `data/evaluation_hard.jsonl`
- `data/evaluation_extra_hard.jsonl`
- `data/evaluation_order5.jsonl`
- `metadata/normal.json`
- `metadata/hard.json`
- `metadata/hard1.json`
- `metadata/hard2.json`
- `metadata/hard3.json`
- `metadata/evaluation_normal.json`
- `metadata/evaluation_hard.json`
- `metadata/evaluation_extra_hard.json`
- `metadata/evaluation_order5.json`
