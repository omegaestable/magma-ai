# SAIR Equational Theories — Stage 1 Ruleset

**Competition:** Mathematics Distillation Challenge — Equational Theories  


---

## 1. Core Task

Given two equations over magmas (sets with a single binary operation ◇),  
determine: **Does Equation 1 imply Equation 2 over all magmas?**

Answer: **TRUE** or **FALSE**.

A *magma* is a set M with a binary operation ◇ : M × M → M, with no axioms
(no associativity, commutativity, etc.) assumed.

"E1 implies E2" means: for every magma (M, ◇), if E1 holds universally in M,
then E2 also holds universally in M.

---

## 2. Cheatsheet Rules

| Constraint          | Value                                    |
|---------------------|------------------------------------------|
| Format              | Plain text                               |
| Max size            | **10 KB** (10,240 bytes)                 |
| Injection point     | Inserted into system prompt before query |
| Content             | Any reasoning guidance, heuristics, examples, decision trees |

The cheatsheet is the **only** submission artifact. No code, no model weights.

---

## 3. Evaluation Protocol


### 3.2 Parsing

- VERDICT line is extracted; must contain exactly `TRUE` or `FALSE`.
- If unparseable → counts as **incorrect**.

### 3.3 Evaluation Setting

- **No-tools:** No browser, web search, or internet access during evaluation.
- **Offline:** Organizer runs evaluation after submission deadline.
- **Evaluation set:** Different from the 1200 public training problems.
- **Balance:** 50% TRUE, 50% FALSE in evaluation set.
- **Multiple models:** Final model list TBD by April 10, 2026; likely includes
  open-source (Llama, GPT-OSS, Qwen) and proprietary (Gemini Flash, GPT-nano).

### 3.4 Cost & Time Budget

- Recommended avg cost: ≤ **$0.01/problem**
- Recommended solve time: ≤ **10 min/problem**
- Exceeding limits may negatively affect final ranking.

---

## 4. Scoring

### 4.1 Primary Metric: Correctness

Stage 1 scoring is **correctness only** (right/wrong on the TRUE/FALSE verdict).

Key metrics to track locally:
- **Accuracy** = correct / total
- **True Accuracy** = correct TRUE verdicts / total TRUE problems
- **False Accuracy** = correct FALSE verdicts / total FALSE problems  
- **F1** = harmonic mean of precision and recall for TRUE class
- **Unparsed rate** = fraction of responses that fail VERDICT extraction

### 4.2 Baseline Reference (Public Benchmark, 200 Hard Problems)

| Model                        | Accuracy | F1    | Notes                  |
|------------------------------|----------|-------|------------------------|
| gemini-3.1-pro-preview       | 69.2%    | 58.6% | Best overall           |
| qwen3.5-397b-a17b            | 64.0%    | 56.1% | Best open-weights      |
| gpt-5.4                      | 64.0%    | 16.9% | Low TRUE recall        |
| llama-4-maverick              | 63.7%    | 12.8% | Near-zero TRUE recall  |
| claude-haiku-4-5             | 62.2%    | 27.5% |                        |
| No-cheatsheet baseline       | ~60-63%  | ~0-15%| Most models guess FALSE|

**Key insight:** Most models without guidance achieve ~63% by defaulting to FALSE
(since hard problems skew FALSE). TRUE recall is the differentiator.

---

## 5. Training Data

### 5.1 Public Problems (from SAIR HuggingFace)

| Dataset       | Count | Source |
|---------------|-------|--------|
| normal.jsonl  | 1000  | Programmatically selected from full dataset |
| hard.jsonl    | 200   | Hand-selected by mathematicians |

Format per line:
```json
{"id": "hard_0001", "index": 1, "difficulty": "hard",
 "equation1": "x = y * (y * ((x * y) * x))",
 "equation2": "x * y = ((z * x) * w) * y",
 "answer": false}
```

### 5.2 Full Raw Dataset

- 4694 equations → 22,028,942 ordered pairs
- Dense matrix: `data/exports/export_raw_implications_14_3_2026.csv`
- Matrix encoding: 3=TRUE(known), 4=TRUE(needed proof), -3=FALSE(known), -4=FALSE(needed counterexample)
- Base rate: 37.12% TRUE, 62.88% FALSE
- Equations list: `data/exports/equations.txt`

### 5.3 Additional Resources

- Equational Theories Project: https://teorth.github.io/equational_theories/
- Implications graph: https://teorth.github.io/equational_theories/implications/
- 524 finite magmas (size ≤ 4) refute 96.3% of all false implications

---

## 6. Key Dates

| Date | Event |
|------|-------|
| March 14, 2026 | Stage 1 starts |
| April 10, 2026 | Final evaluation model list announced |
| April 20, 2026 23:59 AoE | **Stage 1 submission deadline** |
| ≤ April 30, 2026 | Stage 1 leaderboard release |
| May 1, 2026 | Stage 2 starts |

---

## 7. Anti-Cheating & Team Policy

- One team per individual/organization.
- Members and sponsors must be registered in advance.
- Sockpuppet teams → disqualification of all related teams.
- Stage 1 cheatsheets may be made public after Stage 1 ends.

---

## 8. Stage 2 Preview

- Harder benchmark, larger cheatsheets allowed.
- May require: explicit counterexamples, Lean proofs, or calibrated probabilities.
- ≤ 1000 teams advance from Stage 1.

---

## 9. Strategy Notes (from repo analysis)

### What works
- Finite magma counterexample search (covers 96.3% of FALSE cases)
- Singleton-equivalence detection (E2 = "x = y" equivalence class has 1496 members)
- Variable-occurrence heuristics (multiplicity analysis)
- Canonizer-based term rewriting

### What's hard
- TRUE implications requiring deep algebraic reasoning
- Hard problems where structural heuristics fail
- Achieving TRUE recall — most LLMs default to FALSE

### Cheatsheet budget
- 10 KB = 10,240 bytes (measured on disk, CRLF-aware on Windows)
- Current baseline: ~2568 bytes used → ~7672 bytes available
