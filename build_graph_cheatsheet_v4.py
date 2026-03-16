"""
Build graph cheatsheet v4: clean, functional, oversized (user will golf later).
Uses compact notation, equivalence classes, and transitive reduction.
"""
import sys
from collections import defaultdict

def load_equations(path):
    eqs = ['']
    with open(path, encoding='utf-8') as f:
        for line in f:
            eqs.append(line.strip().replace('\u25c7', '*'))
    return eqs

def normalize(eq):
    return eq.replace(' ', '')

def load_matrix(path, n):
    true_edges = set()
    with open(path, encoding='utf-8') as f:
        for row, line in enumerate(f, 1):
            if row > n: break
            for col, v in enumerate(line.strip().rstrip(',').split(','), 1):
                v = v.strip()
                if v in ('3', '4'):
                    true_edges.add((row, col))
            if row % 1000 == 0:
                print(f"  Row {row}...", file=sys.stderr)
    return true_edges

def find_classes(true_edges, n):
    parent = list(range(n + 1))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        if a != b: parent[b] = a
    for (i, j) in true_edges:
        if i != j and (j, i) in true_edges:
            union(i, j)
    classes = defaultdict(list)
    for i in range(1, n + 1):
        classes[find(i)].append(i)
    return {min(v): sorted(v) for v in classes.values()}

def compress_ints(nums):
    if not nums: return ''
    nums = sorted(nums)
    ranges = []
    s = e = nums[0]
    for n in nums[1:]:
        if n == e + 1: e = n
        else:
            ranges.append(f"{s}-{e}" if e > s + 1 else f"{s},{e}" if e > s else str(s))
            s = e = n
    ranges.append(f"{s}-{e}" if e > s + 1 else f"{s},{e}" if e > s else str(s))
    return ','.join(ranges)

def trans_reduce(adj, nodes):
    """Transitive reduction."""
    reduced = defaultdict(set)
    for u in nodes:
        if u not in adj: continue
        for v in adj[u]:
            visited = {u}
            queue = [w for w in adj[u] if w != v]
            visited.update(queue)
            found = False
            while queue and not found:
                c = queue.pop(0)
                if c == v:
                    found = True; break
                for w in adj.get(c, set()):
                    if w not in visited:
                        visited.add(w); queue.append(w)
            if not found:
                reduced[u].add(v)
    return reduced

def is_singleton_forcing(eq_text):
    """Check if equation forces singleton magma.
    A bare variable on one side that doesn't appear anywhere on the other side."""
    norm = eq_text.replace(' ', '')
    # Find the = sign at depth 0
    depth = 0
    eq_pos = -1
    for i, c in enumerate(norm):
        if c == '(': depth += 1
        elif c == ')': depth -= 1
        elif c == '=' and depth == 0:
            eq_pos = i; break
    if eq_pos < 0: return False
    lhs = norm[:eq_pos]
    rhs = norm[eq_pos+1:]
    
    # Check if LHS is a bare variable
    if len(lhs) == 1 and lhs.isalpha():
        # Check if that variable appears in RHS
        if lhs not in rhs:
            return True
    # Check if RHS is a bare variable
    if len(rhs) == 1 and rhs.isalpha():
        if rhs not in lhs:
            return True
    return False

def main():
    eqs = load_equations('data/exports/equations.txt')
    n = len(eqs) - 1
    print(f"Loaded {n} equations", file=sys.stderr)
    
    print("Loading matrix...", file=sys.stderr)
    true_edges = load_matrix('data/exports/export_raw_implications_14_3_2026.csv', n)
    print(f"{len(true_edges)} TRUE edges", file=sys.stderr)
    
    print("Finding classes...", file=sys.stderr)
    classes = find_classes(true_edges, n)
    eq_to_rep = {}
    for rep, members in classes.items():
        for m in members:
            eq_to_rep[m] = rep
    reps = sorted(classes.keys())
    
    # Inter-class edges
    inter = defaultdict(set)
    for (i, j) in true_edges:
        ri, rj = eq_to_rep[i], eq_to_rep[j]
        if ri != rj:
            inter[ri].add(rj)
    
    rep_1 = eq_to_rep[1]  # x=x
    rep_2 = eq_to_rep[2]  # x=y (singleton)
    
    # Simplify: remove edges to rep_1 and from rep_2
    simp = defaultdict(set)
    for u, vs in inter.items():
        if u == rep_2: continue
        for v in vs:
            if v == rep_1: continue
            simp[u].add(v)
    
    print("Transitive reduction...", file=sys.stderr)
    reduced = trans_reduce(simp, reps)
    red_count = sum(len(v) for v in reduced.values())
    print(f"Reduced edges: {red_count}", file=sys.stderr)
    
    # Count singleton-forcing equations
    singleton_eqs = [i for i in range(1, n+1) if is_singleton_forcing(eqs[i])]
    print(f"Singleton-forcing by rule: {len(singleton_eqs)}", file=sys.stderr)
    singleton_class = eq_to_rep[2]
    in_singleton_class = set(classes[singleton_class])
    print(f"In singleton class: {len(in_singleton_class)}", file=sys.stderr)
    
    # Identify equations where rules suffice vs need lookup
    # Singleton-forcing: handled by rule, no need to list
    # Non-singleton: need explicit class assignment
    
    non_singleton_eqs = [i for i in range(1, n+1) if i not in in_singleton_class]
    print(f"Non-singleton equations to list: {len(non_singleton_eqs)}", file=sys.stderr)
    
    # Build non-singleton classes
    ns_classes = {rep: members for rep, members in classes.items() if rep != singleton_class}
    
    # === BUILD OUTPUT ===
    out = []
    
    out.append("MAGMA IMPLICATION ORACLE")
    out.append("Task: Does equation E1 imply equation E2 over all magmas (sets with binary op *)?")
    out.append("")
    out.append("ALGORITHM:")
    out.append("1. Check RULES (fast structural tests)")
    out.append("2. Normalize E1,E2: remove all spaces")
    out.append("3. Find E1 in [MAP] to get its class C_a")
    out.append("4. Find E2 in [MAP] to get its class C_b")
    out.append("5. If C_a = C_b -> TRUE")
    out.append("6. Check [EDGES]: if path from C_a to C_b -> TRUE, else FALSE")
    out.append("NOTE: If equation not found in MAP, it is singleton-forcing (implies everything) -> TRUE")
    out.append("")
    
    # RULES
    out.append("[RULES]")
    out.append("R1 SINGLETON: If E1 has a bare variable on one side COMPLETELY ABSENT from the other side -> answer TRUE.")
    out.append("   Test: Look at each side. If one side is just a single letter (x,y,z,w,u) AND that letter does NOT appear ANYWHERE on the other side -> TRUE.")
    out.append("   YES: 'x = y * z' (x not on RHS). 'x = y * (z * w)'. 'x = (y * z) * w'. 'x = y * (y * z)' (x not on RHS).")
    out.append("   NO: 'x = x * y' (x on both sides). 'x = y * (x * z)' (x on both sides).")
    out.append("R2 IDENTITY: If E2 is 'x = x' -> TRUE (everything implies trivial identity).")
    out.append("R3 ABSORPTION LEFT: If E1 = 'x = x * EXPR' where EXPR has var(s) other than x -> E1's class implies x=x*y (class C4).")
    out.append("   Then if E2 = 'x = x * ANYTHING' -> TRUE.")
    out.append("R4 ABSORPTION RIGHT: If E1 = 'x = EXPR * x' where EXPR has var(s) other than x -> E1's class implies x=y*x (class C5).")
    out.append("   Then if E2 = 'x = ANYTHING * x' -> TRUE.")
    out.append("R5 BALANCE: Count * operators on LHS and RHS separately.")
    out.append("   If E1 has SAME count on both sides (balanced) but E2 has DIFFERENT counts (unbalanced),")
    out.append("   and E1 is NOT singleton-forcing -> FALSE.")
    out.append("R6 COUNTEREXAMPLE MAGMAS (any one satisfies E1 but violates E2 -> FALSE):")
    out.append("   LEFT_PROJ {0,1} a*b=a: Satisfies eq iff leftmost variable is same on both sides")
    out.append("   RIGHT_PROJ {0,1} a*b=b: Satisfies eq iff rightmost variable is same on both sides")
    out.append("   CONSTANT {0,1} a*b=0: Satisfies eq iff both sides have at least one *")
    out.append("R7 If E2 = 'x = y' (forces singleton) and E1 is NOT singleton-forcing -> FALSE.")
    out.append("")
    
    # MAP - list all non-singleton equations with class assignment
    out.append("[MAP]")
    out.append("Format: C<class_id>: eq1 | eq2 | ...")  
    out.append("Equations NOT listed here are singleton-forcing (use R1: answer TRUE for any E2).")
    out.append("To find an equation: remove spaces from the given equation text, search below.")
    
    for rep in sorted(ns_classes.keys()):
        members = ns_classes[rep]
        texts = [normalize(eqs[m]) for m in members]
        # Split into chunks if too long
        line = f"C{rep}: " + " | ".join(texts)
        out.append(line)
    
    out.append("")
    
    # EDGES - transitive reduction
    out.append("[EDGES]")
    out.append("Format: C<from> > C<to>, C<to>, ...")
    out.append("RULE: All classes imply C1 (x=x). Singleton class implies all classes.")  
    out.append("TRANSITIVITY: If C_a > C_b and C_b > C_c, then C_a implies C_c.")
    out.append("If NO path from C_a to C_b in the edges below -> FALSE.")
    
    for src in sorted(reduced.keys()):
        targets = sorted(reduced[src])
        if targets:
            out.append(f"C{src} > " + ", ".join(f"C{t}" for t in targets))
    
    # Also output FULL edges for top classes (most likely to be queried)
    # to help LLMs that struggle with transitivity
    out.append("")
    out.append("[FULL]")
    out.append("Full reachability for key classes (includes transitive). If C_a not listed, use EDGES+transitivity.")
    
    # Output full edges only for the most connected source classes
    # (those with most outgoing edges in the full graph)
    top_srcs = sorted(simp.keys(), key=lambda k: -len(simp[k]))[:100]  # top 100
    for src in sorted(top_srcs):
        targets = sorted(simp[src])
        if targets:
            out.append(f"C{src} > " + compress_ints(targets))
    
    full = '\n'.join(out)
    
    path = 'cheatsheets/graph_v4.txt'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(full)
    
    sz = len(full.encode('utf-8'))
    print(f"\nOutput: {path} ({sz:,} bytes = {sz/1024:.1f} KB)", file=sys.stderr)
    
    # Section breakdown
    in_section = False
    sec_name = "header"
    sec_start = 0
    section_info = []
    for i, line in enumerate(out):
        if line.startswith('[') and ']' in line:
            if in_section:
                sec_text = '\n'.join(out[sec_start:i])
                section_info.append((sec_name, len(sec_text)))
            sec_name = line
            sec_start = i
            in_section = True
    if in_section:
        sec_text = '\n'.join(out[sec_start:])
        section_info.append((sec_name, len(sec_text)))
    
    for name, sz in section_info:
        print(f"  {name}: {sz:,} bytes ({sz/1024:.1f} KB)", file=sys.stderr)
    
    # Quick validation: check some benchmark pairs
    import json
    eqs_norm = {}
    for i in range(1, n+1):
        eqs_norm[normalize(eqs[i])] = i
    
    correct = 0
    total = 0
    for fname in ['data/benchmark/hard.jsonl', 'data/benchmark/normal.jsonl']:
        with open(fname) as f:
            for line in f:
                d = json.loads(line)
                e1_idx = eqs_norm[normalize(d['equation1'])]
                e2_idx = eqs_norm[normalize(d['equation2'])]
                r1 = eq_to_rep[e1_idx]
                r2 = eq_to_rep[e2_idx]
                
                predicted = (r1 == r2) or (r2 in inter.get(r1, set())) or (r1 == singleton_class) or (r2 == rep_1)
                actual = d['answer']
                
                if predicted == actual:
                    correct += 1
                total += 1
    
    print(f"\nBenchmark validation (graph lookup only): {correct}/{total} = {correct/total*100:.1f}%", file=sys.stderr)

if __name__ == '__main__':
    main()
