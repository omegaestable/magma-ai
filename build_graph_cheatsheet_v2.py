"""
Build a compact graph-encoded cheatsheet for magma equation implications.
The cheatsheet uses a compact tree notation and encodes the full implication graph.
"""
import json
import sys
from collections import defaultdict

def load_equations(path):
    """Load equations, return list indexed from 1."""
    eqs = ['']  # 1-indexed
    with open(path, encoding='utf-8') as f:
        for line in f:
            eqs.append(line.strip().replace('\u25c7', '*'))
    return eqs

def parse_tree(eq_text):
    """Parse equation text like 'x = x * (y * z)' into (lhs_tree, rhs_tree).
    Tree is either a string (variable) or tuple (left, right) for multiplication."""
    eq_text = eq_text.strip()
    # Split on top-level =
    # Need to find the = that's not inside parens
    depth = 0
    eq_pos = -1
    for i, c in enumerate(eq_text):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == '=' and depth == 0:
            eq_pos = i
            break
    
    lhs_text = eq_text[:eq_pos].strip()
    rhs_text = eq_text[eq_pos+1:].strip()
    
    return _parse_expr(lhs_text), _parse_expr(rhs_text)

def _parse_expr(s):
    """Parse an expression into a tree."""
    s = s.strip()
    if not s:
        return s
    
    # Find top-level * operator
    depth = 0
    for i, c in enumerate(s):
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == '*' and depth == 0:
            left = s[:i].strip()
            right = s[i+1:].strip()
            return (_parse_expr(left), _parse_expr(right))
    
    # No top-level *, might be parenthesized
    if s.startswith('(') and s.endswith(')'):
        # Check if outer parens match
        depth = 0
        for i, c in enumerate(s):
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
            if depth == 0 and i == len(s) - 1:
                return _parse_expr(s[1:-1])
            elif depth == 0:
                break
    
    return s  # variable

def tree_to_compact(tree):
    """Convert tree to compact notation.
    Variables: x->0, y->1, z->2, w->3, u->4
    Multiplication: (left right) with parens only when needed."""
    var_map = {'x': '0', 'y': '1', 'z': '2', 'w': '3', 'u': '4'}
    
    def _tc(t, top=True):
        if isinstance(t, str):
            return var_map.get(t, t)
        left, right = t
        l = _tc(left, False)
        r = _tc(right, False)
        s = l + '.' + r
        if not top:
            return '(' + s + ')'
        return s
    
    return _tc(tree)

def eq_to_compact(eq_text):
    """Convert full equation to compact notation."""
    lhs, rhs = parse_tree(eq_text)
    return tree_to_compact(lhs) + '=' + tree_to_compact(rhs)

def load_implication_matrix(path, n):
    """Load the implication matrix, return set of (i,j) TRUE edges."""
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
    """Union-find based equivalence classes."""
    parent = list(range(n + 1))
    rank = [0] * (n + 1)
    
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    
    def union(a, b):
        a, b = find(a), find(b)
        if a == b:
            return
        if rank[a] < rank[b]:
            a, b = b, a
        parent[b] = a
        if rank[a] == rank[b]:
            rank[a] += 1
    
    for (i, j) in true_edges:
        if i != j and (j, i) in true_edges:
            union(i, j)
    
    classes = defaultdict(set)
    for i in range(1, n + 1):
        classes[find(i)].add(i)
    
    # Use minimum member as representative
    result = {}
    for members in classes.values():
        rep = min(members)
        result[rep] = sorted(members)
    
    return result

def build_cheatsheet(eqs, true_edges, equiv_classes, n):
    """Build the cheatsheet text."""
    
    # Map each equation to its class representative
    eq_to_rep = {}
    for rep, members in equiv_classes.items():
        for m in members:
            eq_to_rep[m] = rep
    
    reps = sorted(equiv_classes.keys())
    rep_set = set(reps)
    
    # Build inter-class edges
    inter_edges = defaultdict(set)
    for (i, j) in true_edges:
        ri, rj = eq_to_rep[i], eq_to_rep[j]
        if ri != rj:
            inter_edges[ri].add(rj)
    
    lines = []
    
    # === HEADER ===
    lines.append("=MAGMA EQUATION IMPLICATION ORACLE=")
    lines.append("TASK: Given E1,E2 as equations, determine if E1 implies E2 over all magmas.")
    lines.append("ALGORITHM: 1)Apply RULES. 2)Find E1,E2 numbers in INDEX. 3)Find their class reps in CLASSES. 4)Check GRAPH for implication path.")
    lines.append("")
    
    # === QUICK RULES ===
    lines.append("==RULES(apply first)==")
    lines.append("R1:If E1 has a bare variable on one side not appearing on the other side->TRUE(singleton forcing)")
    lines.append("R2:If E2 is 'x=x'(identity)->TRUE")
    lines.append("R3:If E2 is 'x=y'(singleton law) and E1 is NOT singleton-forcing->FALSE")
    lines.append("R4:If E1 is 'x=x*EXPR' with EXPR containing fresh vars->E1 implies x=x*y(E4).Then E4 implies any x=x*F.Check if E2 has form x=x*F")
    lines.append("R5:If E1 is 'x=EXPR*x' with EXPR containing fresh vars->E1 implies x=y*x(E5).Then E5 implies any x=F*x")
    lines.append("R6:BALANCE:count * on each side of E1,E2. If E1 balanced(same count each side) and E2 unbalanced and E1 not singleton-forcing->FALSE")
    lines.append("R7:COUNTEREXAMPLES:Try left-projection(a*b=a),right-projection(a*b=b),constant(a*b=c).If any satisfies E1 but not E2->FALSE")
    lines.append("")
    
    # === EQUATION INDEX ===
    # Compact notation: number:compact_text
    lines.append("==INDEX(equation_number:compact_form)==")
    lines.append("Notation: 0=x 1=y 2=z 3=w 4=u .=binary_op")
    lines.append("Example: '0=0.(1.2)' means 'x = x * (y * z)'")
    
    # Build compact form for all equations
    compact_map = {}
    for i in range(1, n + 1):
        try:
            compact = eq_to_compact(eqs[i])
            compact_map[i] = compact
        except Exception as e:
            compact_map[i] = f"ERR:{eqs[i]}"
    
    # Group equations by compact form (they should all be unique)
    # Output as: number:compact
    batch = []
    for i in range(1, n + 1):
        batch.append(f"{i}:{compact_map[i]}")
        if len(batch) >= 10:
            lines.append(' '.join(batch))
            batch = []
    if batch:
        lines.append(' '.join(batch))
    
    lines.append("")
    
    # === EQUIVALENCE CLASSES ===
    lines.append("==CLASSES(rep~members)==")
    lines.append("All members of a class are equivalent (mutually implied)")
    
    for rep in reps:
        members = equiv_classes[rep]
        if len(members) == 1:
            continue  # Skip singletons to save space
        others = [m for m in members if m != rep]
        # Compress: use ranges where possible
        line = f"{rep}~" + compress_int_list(others)
        lines.append(line)
    
    lines.append("")
    
    # === IMPLICATION GRAPH ===
    lines.append("==GRAPH(from>to,to,...)==")
    lines.append("If rep_A > rep_B listed, then class A implies class B")
    lines.append("Use transitivity: if A>B and B>C then A>C")
    
    for src in sorted(inter_edges.keys()):
        targets = sorted(inter_edges[src])
        if targets:
            line = f"{src}>" + compress_int_list(targets)
            lines.append(line)
    
    full = '\n'.join(lines)
    return full

def compress_int_list(nums):
    """Compress a sorted list of integers using run-length encoding.
    E.g., [1,2,3,4,7,8,9,15] -> '1-4,7-9,15'"""
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
    n = len(eqs) - 1  # 1-indexed, so actual count
    print(f"Loaded {n} equations", file=sys.stderr)
    
    print("Loading implication matrix...", file=sys.stderr)
    true_edges = load_implication_matrix(
        'data/exports/export_raw_implications_14_3_2026.csv', n
    )
    print(f"Loaded {len(true_edges)} TRUE edges", file=sys.stderr)
    
    print("Finding equivalence classes...", file=sys.stderr)
    equiv_classes = find_equiv_classes(true_edges, n)
    
    nontrivial = sum(1 for v in equiv_classes.values() if len(v) > 1)
    print(f"Classes: {len(equiv_classes)} total, {nontrivial} non-trivial", file=sys.stderr)
    
    print("Building cheatsheet...", file=sys.stderr)
    cheatsheet = build_cheatsheet(eqs, true_edges, equiv_classes, n)
    
    outpath = 'cheatsheets/graph_v1.txt'
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(cheatsheet)
    
    size = len(cheatsheet.encode('utf-8'))
    print(f"\nCheatsheet: {outpath}", file=sys.stderr)
    print(f"Size: {size:,} bytes ({size/1024:.1f} KB)", file=sys.stderr)
    print(f"10KB limit: 10,240 bytes", file=sys.stderr)
    print(f"Over by: {max(0, size - 10240):,} bytes", file=sys.stderr)
    
    # Analyze sections
    sections = cheatsheet.split('\n\n')
    for s in sections:
        first_line = s.split('\n')[0] if s else ''
        print(f"  Section '{first_line[:40]}': {len(s):,} bytes", file=sys.stderr)

if __name__ == '__main__':
    main()
