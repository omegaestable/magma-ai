"""Verify structural witness results for the 10 benchmark problems to compare against LLM answers."""
import json, re, sys
sys.path.insert(0, '.')
from v21_verify_structural_rules import rule_LP, rule_RP, rule_C0, rule_XOR, rule_XNOR, rule_AND, rule_OR, rule_Z3A

def split_eq(eq_str):
    """Split equation on = and return (LHS, RHS)."""
    parts = eq_str.split('=', 1)
    return parts[0].strip(), parts[1].strip()

data = json.load(open('results/sim_meta-llama_llama-3.3-70b-instruct_normal_balanced10_true5_false5_seed0_v21_structural_20260330_202300.json'))

tests = [
    ("LP", rule_LP),
    ("RP", rule_RP),
    ("C0", rule_C0),
    ("XOR", rule_XOR),
    ("XNOR", rule_XNOR),
    ("AND", rule_AND),
    ("OR", rule_OR),
    ("Z3A", rule_Z3A),
]

for i, r in enumerate(data['results']):
    mark = 'OK' if r['ground_truth'] == r['predicted'] else 'ERR'
    print(f"=== [{i+1}] {r['id']} | GT={r['ground_truth']} Pred={r['predicted']} {mark} ===")
    e1 = r['equation1']
    e2 = r['equation2']
    print(f"  E1: {e1}")
    print(f"  E2: {e2}")
    
    e1_lhs, e1_rhs = split_eq(e1)
    e2_lhs, e2_rhs = split_eq(e2)
    
    separating = []
    for name, rule_fn in tests:
        e1_holds = rule_fn(e1_lhs, e1_rhs)
        e2_holds = rule_fn(e2_lhs, e2_rhs)
        status = ""
        if e1_holds and not e2_holds:
            status = " <<< SEPARATES"
            separating.append(name)
        print(f"  {name:5s}: E1={'HOLD' if e1_holds else 'FAIL'}  E2={'HOLD' if e2_holds else 'FAIL'}{status}")
    
    if separating:
        print(f"  => Should be FALSE (separated by: {', '.join(separating)})")
    else:
        print(f"  => Should be TRUE (no witness separates)")
    
    # Show what the LLM claimed
    lines = r['raw_response'].strip().split('\n')
    print(f"  LLM: {lines[0]}")
    if len(lines) > 1:
        print(f"       {lines[1]}")
    print()
