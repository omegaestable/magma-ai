# %% [markdown]
# # Exploratory Analysis — Equational Implication over Magmas
#
# Notebook-style script (run with `jupytext` or cell-by-cell in VS Code).

# %% [markdown]
# ## 1. Setup & Data Exploration

# %%
import json
from pathlib import Path
from collections import Counter

from config import CHEATSHEET_FILE, EXPLORER_CSV, ExperimentConfig, MODELS, DATA_DIR, RESULTS_DIR, CHEATSHEETS_DIR
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
explorer_path = EXPLORER_CSV
if explorer_path.exists():
    with open(explorer_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"Explorer CSV: {len(rows)} rows")
    if rows:
        print(f"Columns: {list(rows[0].keys())}")
else:
    print("Explorer CSV not found")

# %% [markdown]
# ## 2. Compare Evaluation Results

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
# ## 3. Cheatsheet Comparison

# %%
def compare_cheatsheets():
    """Compare all generated cheatsheets."""
    if not CHEATSHEETS_DIR.exists():
        print("No cheatsheets directory yet.")
        return
    for path in sorted(CHEATSHEETS_DIR.glob("*.txt")):
        size = path.stat().st_size
        lines = path.read_text(encoding='utf-8').count('\n')
        print(f"{path.name}: {size} bytes, {lines} lines")

compare_cheatsheets()

main_cs = CHEATSHEET_FILE
if main_cs.exists():
    size = main_cs.stat().st_size
    print(f"\nMain cheatsheet.txt: {size}/10240 bytes ({size*100/10240:.1f}%)")

