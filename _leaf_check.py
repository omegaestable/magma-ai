import json, re

def leftmost(expr):
    vars = re.findall(r'\b[a-z]\b', expr)
    return vars[0] if vars else None

def rightmost(expr):
    vars = re.findall(r'\b[a-z]\b', expr)
    return vars[-1] if vars else None

with open('data/benchmark/control_hard20_seed17.jsonl') as f:
    rows = [json.loads(l) for l in f]

for label, answer in [('FALSE', False), ('TRUE', True)]:
    print(f'== {label} cases ==')
    for r in rows:
        if r['answer'] != answer:
            continue
        e1 = r['equation1']
        e2 = r['equation2']
        if '=' in e1:
            parts = e1.split('=', 1)
            lhs = parts[0].strip()
            rhs = parts[1].strip()
            lm1 = leftmost(rhs); rm1 = rightmost(rhs)
            lm2 = leftmost(e2.split('=',1)[1].strip()) if '=' in e2 else '?'
            rm2 = rightmost(e2.split('=',1)[1].strip()) if '=' in e2 else '?'
            lp_e1 = lm1 == 'x'; rp_e1 = rm1 == 'x'
            lp_e2 = lm2 == 'x'; rp_e2 = rm2 == 'x'
            print(f"  {r['id']}: E1={e1}")
            print(f"         E2={e2}")
            print(f"    E1: LP-leaf={lm1}({'HOLDS' if lp_e1 else 'FAILS'}) RP-leaf={rm1}({'HOLDS' if rp_e1 else 'FAILS'})")
            print(f"    E2: LP-leaf={lm2}({'HOLDS' if lp_e2 else 'FAILS'}) RP-leaf={rm2}({'HOLDS' if rp_e2 else 'FAILS'})")
            if lp_e1 and not lp_e2:
                print("    *** LP: E1 HOLDS, E2 FAILS -> LP is valid CE -> FALSE ***")
            elif lp_e1 and lp_e2:
                print("    --- LP: both HOLD -> LP not CE; check others")
            if rp_e1 and not rp_e2:
                print("    *** RP: E1 HOLDS, E2 FAILS -> RP is valid CE -> FALSE ***")
            elif rp_e1 and rp_e2:
                print("    --- RP: both HOLD -> RP not CE; check others")
        else:
            print(f"  {r['id']}: {e1}  [non-standard form]")
    print()
