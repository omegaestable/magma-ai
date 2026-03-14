# %% [markdown]
# # Cheat-Sheet ICL Research — Equational Implication over Magmas
#
# Notebook for exploring the TAO Challenge domain and running
# Honda et al. (2025) cheat-sheet distillation experiments.
#
# **Sections:**
# 1. Data exploration (equations, implications)
# 2. Cheatsheet distillation (single run)
# 3. Evaluation against ground truth
# 4. Ablation comparison
# 5. Error analysis

# %% [markdown]
# ## 1. Setup & Data Exploration

# %%
import json
import random
import math
from pathlib import Path
from collections import Counter

from config import ExperimentConfig, MODELS, DATA_DIR, RESULTS_DIR, CHEATSHEETS_DIR
from analyze_equations import load_equations, parse_equation, get_vars, count_ops, get_depth

equations = load_equations()
print(f"Loaded {len(equations)} equations")
print(f"Example eq[0]: {equations[0]}")
print(f"Example eq[100]: {equations[100]}")

# %% [markdown]
# ### Equation statistics

# %%
stats = {"n_vars": [], "n_ops": [], "depth": []}
for eq_str in equations:
    try:
        lhs, rhs = parse_equation(eq_str)
        vs = get_vars(lhs) | get_vars(rhs)
        ops = count_ops(lhs) + count_ops(rhs)
        d = max(get_depth(lhs), get_depth(rhs))
        stats["n_vars"].append(len(vs))
        stats["n_ops"].append(ops)
        stats["depth"].append(d)
    except Exception:
        stats["n_vars"].append(0)
        stats["n_ops"].append(0)
        stats["depth"].append(0)

for k, v in stats.items():
    print(f"{k}: min={min(v)}, max={max(v)}, mean={sum(v)/len(v):.1f}, median={sorted(v)[len(v)//2]}")

# %% [markdown]
# ### Explorer CSV summary

# %%
import csv
explorer_path = Path("export_explorer_14_3_2026.csv")
if explorer_path.exists():
    with open(explorer_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"Explorer CSV: {len(rows)} rows")
    if rows:
        print(f"Columns: {list(rows[0].keys())}")
        # Distribution of implications counts
        implies_counts = [int(r.get('implies', r.get('Implies', 0))) for r in rows if r.get('implies', r.get('Implies', ''))]
        if implies_counts:
            print(f"Implies count: min={min(implies_counts)}, max={max(implies_counts)}, mean={sum(implies_counts)/len(implies_counts):.1f}")
else:
    print("Explorer CSV not found")

# %% [markdown]
# ### Training data inspection

# %%
# Check if training data has been downloaded
data_dir = DATA_DIR
normal_path = data_dir / "normal.jsonl"
hard_path = data_dir / "hard.jsonl"

for path in [normal_path, hard_path]:
    if path.exists():
        with open(path, 'r') as f:
            lines = f.readlines()
        print(f"{path.name}: {len(lines)} problems")
        if lines:
            sample = json.loads(lines[0])
            print(f"  Fields: {list(sample.keys())}")
            print(f"  Sample: {sample}")
            labels = [json.loads(l).get('implies', json.loads(l).get('label')) for l in lines[:1000]]
            true_count = sum(1 for l in labels if l)
            print(f"  Label balance (first 1000): {true_count} TRUE, {len(labels)-true_count} FALSE")
    else:
        print(f"{path.name}: NOT FOUND — run `python download_data.py` first")

# %% [markdown]
# ## 2. Single Cheatsheet Distillation

# %%
# Uncomment and run after setting API keys and downloading data
#
# from distill import run_pipeline
#
# config = ExperimentConfig(
#     name="test_run",
#     distill_model="gpt-4.1",
#     n_shots=50,  # start small
#     use_rationale_augmentation=False,  # skip for quick test
# )
#
# cheatsheet = run_pipeline(
#     training_data=str(normal_path),
#     config=config,
#     prompt_variant="default",
# )
# print(f"Generated cheatsheet: {len(cheatsheet.encode('utf-8'))} bytes")
# print(cheatsheet[:500])

# %% [markdown]
# ## 3. Evaluate a Cheatsheet

# %%
# from run_eval import run_evaluation
#
# results = run_evaluation(
#     cheatsheet_path="cheatsheet.txt",  # or generated one
#     eval_data_path=str(normal_path),
#     config=ExperimentConfig(
#         name="baseline_eval",
#         eval_model="gpt-4o-mini",
#         n_eval=50,  # start small
#     ),
# )
# print(f"Accuracy: {results['accuracy']:.3f}")
# print(f"Log-loss: {results['log_loss']:.4f}")
# print(f"Cost: ${results['total_cost']:.4f}")

# %% [markdown]
# ## 4. Compare Ablation Results

# %%
def load_results(pattern="eval_*.json"):
    results = []
    if RESULTS_DIR.exists():
        for path in sorted(RESULTS_DIR.glob(pattern)):
            with open(path) as f:
                r = json.load(f)
            r["file"] = path.name
            results.append(r)
    return results

results = load_results()
if results:
    print(f"{'Name':<35} {'Acc':>6} {'LogLoss':>8} {'Cost':>8} {'N':>5}")
    print("-" * 65)
    for r in results:
        name = r.get("experiment_name", r.get("file", "?"))
        print(f"{name:<35} {r['accuracy']:>6.3f} {r['log_loss']:>8.4f} ${r['total_cost']:>7.4f} {r['n_eval']:>5}")
else:
    print("No results yet. Run experiments first.")

# %% [markdown]
# ## 5. Error Analysis

# %%
def analyze_errors(result_file: str):
    """Analyze errors from a single evaluation run."""
    with open(result_file) as f:
        data = json.load(f)

    details = data.get("details", [])
    errors = [d for d in details if not d["correct"]]
    print(f"Errors: {len(errors)}/{len(details)} ({len(errors)/len(details)*100:.1f}%)")

    # Error breakdown by label
    fp = [d for d in errors if d["label"] == False]  # predicted TRUE, was FALSE
    fn = [d for d in errors if d["label"] == True]   # predicted FALSE, was TRUE
    print(f"  False positives (pred TRUE, label FALSE): {len(fp)}")
    print(f"  False negatives (pred FALSE, label TRUE): {len(fn)}")

    # Show some errors
    for d in errors[:5]:
        eq1_str = equations[d["eq1_idx"]-1] if d["eq1_idx"] <= len(equations) else "?"
        eq2_str = equations[d["eq2_idx"]-1] if d["eq2_idx"] <= len(equations) else "?"
        print(f"\n  Eq{d['eq1_idx']} → Eq{d['eq2_idx']}: label={d['label']}, pred_prob={d['predicted_prob']:.2f}")
        print(f"    {eq1_str}")
        print(f"    {eq2_str}")

# Uncomment after running an evaluation:
# analyze_errors(str(RESULTS_DIR / "eval_default.json"))

# %% [markdown]
# ## 6. Cheatsheet Comparison

# %%
def compare_cheatsheets():
    """Compare all generated cheatsheets."""
    if not CHEATSHEETS_DIR.exists():
        print("No cheatsheets directory yet.")
        return

    for path in sorted(CHEATSHEETS_DIR.glob("*.txt")):
        with open(path, 'r') as f:
            text = f.read()
        size = len(text.encode('utf-8'))
        lines = text.count('\n')
        print(f"{path.name}: {size} bytes, {lines} lines")

compare_cheatsheets()

# Also check the main cheatsheet
main_cs = Path("cheatsheet.txt")
if main_cs.exists():
    with open(main_cs, 'r') as f:
        text = f.read()
    size = len(text.encode('utf-8'))
    print(f"\nMain cheatsheet.txt: {size}/10240 bytes ({size*100/10240:.1f}%)")
