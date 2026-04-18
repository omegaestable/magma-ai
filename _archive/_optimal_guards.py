"""Find the optimal guard assignments for T5B and NL1."""
import json, itertools

def parse_tree(s):
    s = s.strip()
    if not s: return s
    if s.startswith('('):
        depth = 0
        for i, c in enumerate(s):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            if depth == 0:
                if i == len(s) - 1: return parse_tree(s[1:-1])
                break
    depth = 0
    for i, c in enumerate(s):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '*' and depth == 0:
            return ('*', parse_tree(s[:i]), parse_tree(s[i+1:]))
    return s.strip()

def get_vars(tree):
    if isinstance(tree, str): return {tree}
    return get_vars(tree[1]) | get_vars(tree[2])

def eval_tree(tree, assign, table):
    if isinstance(tree, str): return assign[tree]
    l = eval_tree(tree[1], assign, table)
    r = eval_tree(tree[2], assign, table)
    return table[l][r]

T5B = [[0,2,1],[1,0,2],[2,1,0]]
NL1 = [[0,0,0],[1,1,0],[1,2,2]]

with open('data/hf_cache/hard.jsonl') as f:
    problems = [json.loads(l) for l in f]

true_p = [p for p in problems if p['answer']]

# For each TRUE problem, find which magma test falsely separates
# Then find which guard assignment would catch it
guards = {
    "all-0": lambda seen: {v:0 for v in seen},
    "all-1": lambda seen: {v:1 for v in seen},
    "all-2": lambda seen: {v:2 for v in seen},
    "01-alt": lambda seen: {v: i%2 for i,v in enumerate(seen)},
    "02-alt": lambda seen: {v: (i%2)*2 for i,v in enumerate(seen)},
    "12-alt": lambda seen: {v: 1+(i%2) for i,v in enumerate(seen)},
}

for mname, table in [("T5B", T5B), ("NL1", NL1)]:
    false_seps = []  # TRUE problems falsely separated by this magma
    
    for p in true_p:
        e1L_s, e1R_s = p['equation1'].split('=', 1)
        e2L_s, e2R_s = p['equation2'].split('=', 1)
        e1L = parse_tree(e1L_s.strip()); e1R = parse_tree(e1R_s.strip())
        e2L = parse_tree(e2L_s.strip()); e2R = parse_tree(e2R_s.strip())
        all_v = get_vars(e1L)|get_vars(e1R)|get_vars(e2L)|get_vars(e2R)
        n = len(all_v)
        if n >= 4: continue  # Skipped
        
        seen = []
        for c in p['equation1'] + p['equation2']:
            if c.isalpha() and c not in seen: seen.append(c)
        asgn = {v: i%3 for i,v in enumerate(seen)}
        
        try:
            if eval_tree(e1L, asgn, table) != eval_tree(e1R, asgn, table): continue
            if eval_tree(e2L, asgn, table) != eval_tree(e2R, asgn, table):
                # False separation! Check which guards would have caught it
                catching_guards = []
                for gname, gfn in guards.items():
                    g_asgn = gfn(seen)
                    try:
                        if eval_tree(e1L, g_asgn, table) != eval_tree(e1R, g_asgn, table):
                            catching_guards.append(gname)
                    except:
                        pass
                false_seps.append((p['id'], catching_guards))
        except: pass
    
    print(f"{mname}: {len(false_seps)} false separations on TRUE problems")
    for pid, cg in false_seps:
        print(f"  {pid}: caught by {cg if cg else 'NONE (need exhaustive)'}")
    
    # Summary: which guards catch the most
    guard_catches = {}
    for gname in guards:
        guard_catches[gname] = sum(1 for _, cg in false_seps if gname in cg)
    print(f"  Guard effectiveness: {dict(sorted(guard_catches.items(), key=lambda x:-x[1]))}")
    print()
