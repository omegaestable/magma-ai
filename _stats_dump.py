"""Quick stats dump for all rotation0002 results."""
import json
from pathlib import Path

for f in sorted(Path("results").glob("sim_*rotation0002*.json")):
    data = json.loads(f.read_text(encoding="utf-8"))
    s = data["summary"]
    print(f"{f.name}:")
    print(f"  N={s['total']} acc={s['accuracy']} f1={s['f1_score']}")
    print(f"  tp={s['tp']} fp={s['fp']} fn={s['fn']} tn={s['tn']} unp={s['unparsed']}")
    print(f"  true_acc={s['true_accuracy']} false_acc={s['false_accuracy']} parse={s['parse_success_rate']}")
    
    # Count execution errors: cases where the 4 tests SHOULD separate but model got wrong
    from v21_verify_structural_rules import rule_LP, rule_RP, rule_C0, rule_AND
    exec_err = 0
    for r in data["results"]:
        if r["correct"]:
            continue
        if r["ground_truth"] is not True:  # only look at FALSE pairs
            eq1, eq2 = r["equation1"], r["equation2"]
            l1, r1 = eq1.split(" = ", 1)
            l2, r2 = eq2.split(" = ", 1)
            for name, fn in [("LP", rule_LP), ("RP", rule_RP), ("C0", rule_C0), ("VARS", rule_AND)]:
                if fn(l1, r1) and not fn(l2, r2):
                    exec_err += 1
                    print(f"  EXECUTION_ERROR: {r['id']} has {name} separator but model said {r['predicted']}")
                    break
    
    # Show unparsed
    for r in data["results"]:
        if r["predicted"] is None:
            print(f"  UNPARSED: {r['id']} gt={r['ground_truth']}")
    print()
