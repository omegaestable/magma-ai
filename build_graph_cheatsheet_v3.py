"""
Build a compact graph-encoded cheatsheet for magma equation implications.
V3: Text-based matching, transitive reduction, maximally compressed.
"""
import sys
from collections import defaultdict

def load_equations(path):
    eqs = ['']  # 1-indexed
    with open(path, encoding='utf-8') as f:
        for line in f:
            eqs.append(line.strip().replace('\u25c7', '*'))
    return eqs

def normalize_eq(eq_text):
    """Normalize equation text: remove spaces, sort sides if needed."""
    return eq_text.replace(' ', '')

def load_implication_matrix(path, n):
    true_edges = set()
    with open(path, encoding='utf-8') as f:
        for row_idx, line in enumerate(f, 1):
            if row_idx > n:
                break
            vals = line.strip().rstrip(',').split(',')
            for col_idx, v in enumerate(vals, 1):
                v = v.strip()
                if not v:
                    continue
                try:
                    val = int(v)
                except ValueError:
                    continue
                if val in (3, 4):
                    true_edges.add((row_idx, col_idx))
            if row_idx % 1000 == 0:
                print(f"  Row {row_idx}/{n}...", file=sys.stderr)
    return true_edges

def find_equiv_classes(true_edges, n):
    parent = list(range(n + 1))
    
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    
    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[b] = a
    
    for (i, j) in true_edges:
        if i != j and (j, i) in true_edges:
            union(i, j)
    
    classes = defaultdict(set)
    for i in range(1, n + 1):
        classes[find(i)].add(i)
    
    result = {}
    for members in classes.values():
        rep = min(members)
        result[rep] = sorted(members)
    
    return result

def transitive_reduction(adj, nodes):
    """Compute transitive reduction of a DAG given adjacency dict."""
    # For each edge u->v, check if there's another path u->...->v
    reduced = defaultdict(set)
    
    # Precompute reachability for each node (BFS)
    # For efficiency, just check: remove edge u->v if any u->w->...->v exists
    # Simple O(V*E) method: for each edge (u,v), check if v is reachable from u 
    # via other neighbors
    
    for u in nodes:
        if u not in adj:
            continue
        targets = list(adj[u])
        for v in targets:
            # Check if v is reachable from u without direct edge u->v
            # BFS from u, excluding direct edge to v
            reachable = False
            visited = {u}
            queue = []
            for w in adj[u]:
                if w != v:
                    queue.append(w)
                    visited.add(w)
            while queue and not reachable:
                curr = queue.pop(0)
                if curr == v:
                    reachable = True
                    break
                for w in adj.get(curr, set()):
                    if w not in visited:
                        visited.add(w)
                        queue.append(w)
            
            if not reachable:
                reduced[u].add(v)
    
    return reduced

def compress_int_list(nums):
    if not nums:
        return ''
    nums = sorted(nums)
    ranges = []
    start = nums[0]
    end = nums[0]
    for n in nums[1:]:
        if n == end + 1:
            end = n
        else:
            if start == end:
                ranges.append(str(start))
            elif end == start + 1:
                ranges.append(f"{start},{end}")
            else:
                ranges.append(f"{start}-{end}")
            start = n
            end = n
    if start == end:
        ranges.append(str(start))
    elif end == start + 1:
        ranges.append(f"{start},{end}")
    else:
        ranges.append(f"{start}-{end}")
    return ','.join(ranges)

def main():
    eqs = load_equations('data/exports/equations.txt')
    n = len(eqs) - 1
    print(f"Loaded {n} equations", file=sys.stderr)
    
    print("Loading implication matrix...", file=sys.stderr)
    true_edges = load_implication_matrix(
        'data/exports/export_raw_implications_14_3_2026.csv', n
    )
    print(f"Loaded {len(true_edges)} TRUE edges", file=sys.stderr)
    
    print("Finding equivalence classes...", file=sys.stderr)
    equiv_classes = find_equiv_classes(true_edges, n)
    
    eq_to_rep = {}
    for rep, members in equiv_classes.items():
        for m in members:
            eq_to_rep[m] = rep
    
    reps = sorted(equiv_classes.keys())
    rep_set = set(reps)
    
    # Build inter-class edges (between reps)
    inter_adj = defaultdict(set)
    for (i, j) in true_edges:
        ri, rj = eq_to_rep[i], eq_to_rep[j]
        if ri != rj:
            inter_adj[ri].add(rj)
    
    total_inter = sum(len(v) for v in inter_adj.values())
    print(f"Inter-class edges: {total_inter}", file=sys.stderr)
    
    # Identify special classes
    # Class 1 (x=x): everything implies it
    # Class 2 (x=y): it implies everything (singleton-forcing)
    rep_1 = eq_to_rep[1]  # trivial identity
    rep_2 = eq_to_rep[2]  # singleton law
    print(f"Trivial class rep: {rep_1}, Singleton class rep: {rep_2}", file=sys.stderr)
    print(f"Singleton class size: {len(equiv_classes[rep_2])}", file=sys.stderr)
    
    # Remove trivial edges for compression
    # 1. Remove all edges to rep_1 (everything implies x=x)
    # 2. Remove all edges from rep_2 (singleton implies everything)
    simplified_adj = defaultdict(set)
    for u, targets in inter_adj.items():
        if u == rep_2:
            continue  # Skip all edges from singleton class
        for v in targets:
            if v == rep_1:
                continue  # Skip all edges to trivial class
            simplified_adj[u].add(v)
    
    simplified_total = sum(len(v) for v in simplified_adj.values())
    print(f"After removing trivial edges: {simplified_total}", file=sys.stderr)
    
    # Compute transitive reduction
    print("Computing transitive reduction...", file=sys.stderr)
    reduced_adj = transitive_reduction(simplified_adj, reps)
    reduced_total = sum(len(v) for v in reduced_adj.values())
    print(f"Transitive reduction edges: {reduced_total}", file=sys.stderr)
    
    # Now build the cheatsheet
    lines = []
    
    # === HEADER & ALGORITHM ===
    lines.append("MAGMA IMPLICATION ORACLE")
    lines.append("Given equations E1,E2: does E1 imply E2 over all magmas?")
    lines.append("Step 1: Apply RULES below.")
    lines.append("Step 2: Normalize E1,E2 text (remove spaces).")
    lines.append("Step 3: Find E1,E2 in MAP to get class IDs.")
    lines.append("Step 4: If same class->TRUE. Check EDGES for path from E1_class to E2_class.")
    lines.append("")
    
    # === RULES ===
    lines.append("[RULES]")
    lines.append("R1 SINGLETON: If E1 has a bare variable on one side totally absent from other side -> TRUE for any E2.")
    lines.append("  Examples: x=y*z, x=y*(z*w), x=(y*z)*w all have x absent from the other side -> TRUE.")
    lines.append("  Counter: x=x*y (x appears on both sides -> NOT singleton).")
    lines.append("R2 TRIVIAL: If E2 is x=x -> TRUE always.")
    lines.append("R3 SINGLETON_REQ: If E2 is x=y and E1 is not singleton-forcing -> FALSE.")
    lines.append("R4 ABSORPTION_LEFT: If E1 has form x=x*F where F has a var not x -> implies x=x*y(E4). E4 implies any x=x*G. So if E2 is x=x*G -> TRUE.")
    lines.append("R5 ABSORPTION_RIGHT: If E1 has form x=F*x where F has a var not x -> implies x=y*x(E5). E5 implies any x=G*x.")
    lines.append("R6 BALANCE: Count * on LHS vs RHS of E1 and E2. Balanced = same count each side. If E1 balanced, E2 unbalanced, E1 not singleton -> FALSE.")
    lines.append("R7 LEFT_PROJ: Check magma a*b=a on {0,1}. If E1 holds but E2 fails -> FALSE. E1 holds iff both sides have same leftmost variable.")
    lines.append("R8 RIGHT_PROJ: Check magma a*b=b on {0,1}. If E1 holds but E2 fails -> FALSE. E1 holds iff both sides have same rightmost variable.")
    lines.append("R9 CONSTANT: Check magma a*b=0 on {0,1}. Satisfies any eq where both sides have *. Fails if one side is bare variable.")
    lines.append("")
    
    # === EQUATION MAP ===
    lines.append("[MAP]")
    lines.append("Format: C<class_id>:<equation_text>|<equation_text>|...")
    lines.append("Equation text with spaces removed. Find your equation here to get class.")
    
    # For each class, list all member equation texts
    for rep in reps:
        members = equiv_classes[rep]
        member_texts = []
        for m in members:
            member_texts.append(normalize_eq(eqs[m]))
        # Output as class_rep:text1|text2|...
        lines.append(f"C{rep}:{' '.join(member_texts)}")
    
    lines.append("")
    
    # === SPECIAL RULES ===
    lines.append("[SPECIAL]")
    lines.append(f"C{rep_2} is the SINGLETON class. C{rep_2}->ANY: TRUE. ANY->C{rep_2}: only if E1 is also singleton-forcing.")
    lines.append(f"C{rep_1} is TRIVIAL (x=x). ANY->C{rep_1}: TRUE.")
    lines.append("")
    
    # === IMPLICATION EDGES (transitive reduction) ===
    lines.append("[EDGES]")
    lines.append("Format: C<from>>C<to>,C<to>,...")
    lines.append("Transitive: if C_A>C_B and C_B>C_C then C_A>C_C (TRUE).")
    lines.append("If no path exists from C_E1 to C_E2 -> FALSE.")
    
    for src in sorted(reduced_adj.keys()):
        targets = sorted(reduced_adj[src])
        if targets:
            target_str = ','.join(f"C{t}" for t in targets)
            lines.append(f"C{src}>{target_str}")
    
    # Also output the full adjacency for completeness (non-reduced)
    # since the LLM might not be great at transitive reasoning
    lines.append("")
    lines.append("[FULL_EDGES]")
    lines.append("Complete implication list (includes transitive). Use if unsure about transitivity.")
    
    for src in sorted(simplified_adj.keys()):
        targets = sorted(simplified_adj[src])
        if targets:
            lines.append(f"C{src}>{compress_int_list(targets)}")
    
    full = '\n'.join(lines)
    
    outpath = 'cheatsheets/graph_v1.txt'
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(full)
    
    size = len(full.encode('utf-8'))
    print(f"\nCheatsheet: {outpath}", file=sys.stderr)
    print(f"Size: {size:,} bytes ({size/1024:.1f} KB)", file=sys.stderr)
    
    # Section sizes
    current_section = ""
    section_sizes = {}
    current_text = []
    for line in lines:
        if line.startswith('[') and line.endswith(']'):
            if current_section:
                section_sizes[current_section] = len('\n'.join(current_text))
            current_section = line
            current_text = []
        current_text.append(line)
    if current_section:
        section_sizes[current_section] = len('\n'.join(current_text))
    
    for sec, sz in section_sizes.items():
        print(f"  {sec}: {sz:,} bytes ({sz/1024:.1f} KB)", file=sys.stderr)

if __name__ == '__main__':
    main()
