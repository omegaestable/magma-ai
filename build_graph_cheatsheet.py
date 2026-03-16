"""
Build a compact graph-based cheatsheet from the implication CSV.
Encodes: equation text, equivalence classes, and known implications.
"""
import csv
import sys
from collections import defaultdict

def parse_equations(path):
    """Return dict mapping 1-indexed equation number to its text."""
    eqs = {}
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            # Convert ◇ to * for matching benchmark format
            eqs[i] = line.strip().replace('◇', '*')
    return eqs

def parse_implication_matrix(path, n):
    """
    Parse the CSV matrix. Values:
      3 or 4  -> TRUE (implies)
      -3 or -4 -> FALSE (does not imply)
    Returns dict: (i, j) -> True/False
    But that's too large. Instead, return sets of TRUE edges.
    """
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
            if row_idx % 500 == 0:
                print(f"  Parsed row {row_idx}/{n}...", file=sys.stderr)
    return true_edges

def find_equivalence_classes(true_edges, n):
    """Find equivalence classes: i ~ j iff i->j AND j->i."""
    # Build adjacency for quick lookup
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
    
    # Check mutual implications
    for (i, j) in true_edges:
        if i != j and (j, i) in true_edges:
            union(i, j)
    
    # Build classes
    classes = defaultdict(set)
    for i in range(1, n + 1):
        classes[find(i)].add(i)
    
    return classes

def build_transitive_reduction(true_edges, eq_classes, n):
    """
    Build the transitive reduction of the implication graph
    between equivalence class representatives.
    """
    # Map each equation to its representative
    repr_map = {}
    for rep, members in eq_classes.items():
        for m in members:
            repr_map[m] = rep
    
    # Get unique representatives
    reps = sorted(set(repr_map.values()))
    rep_set = set(reps)
    
    # Build edges between representatives (excluding self-loops)
    rep_edges = set()
    for (i, j) in true_edges:
        ri, rj = repr_map[i], repr_map[j]
        if ri != rj:
            rep_edges.add((ri, rj))
    
    # Transitive reduction: remove edge (a,b) if there exists c such that a->c->b
    # For efficiency, build adjacency lists
    adj = defaultdict(set)
    for (a, b) in rep_edges:
        adj[a].add(b)
    
    # For each edge, check if it can be reached via an intermediate
    reduced = set()
    for (a, b) in rep_edges:
        # Check if there's a path a -> ... -> b not using direct edge
        # Simple: check if any neighbor c of a (c != b) has b reachable
        reachable_via_other = False
        for c in adj[a]:
            if c != b and b in adj[c]:
                reachable_via_other = True
                break
        if not reachable_via_other:
            reduced.add((a, b))
    
    return reduced, repr_map

def compact_eq_text(eq_text):
    """Compress equation text for the cheatsheet."""
    # Remove spaces, use . for *
    return eq_text.replace(' ', '').replace('*', '.')

def main():
    eqs = parse_equations('data/exports/equations.txt')
    n = len(eqs)
    print(f"Loaded {n} equations", file=sys.stderr)
    
    print("Parsing implication matrix...", file=sys.stderr)
    true_edges = parse_implication_matrix(
        'data/exports/export_raw_implications_14_3_2026.csv', n
    )
    print(f"Found {len(true_edges)} true implications", file=sys.stderr)
    
    print("Finding equivalence classes...", file=sys.stderr)
    eq_classes = find_equivalence_classes(true_edges, n)
    
    # Filter to non-trivial classes (size > 1)
    nontrivial = {k: v for k, v in eq_classes.items() if len(v) > 1}
    singletons = {k: v for k, v in eq_classes.items() if len(v) == 1}
    print(f"Found {len(nontrivial)} equivalence classes with >1 member", file=sys.stderr)
    print(f"Found {len(singletons)} singleton classes", file=sys.stderr)
    total_in_classes = sum(len(v) for v in nontrivial.values())
    print(f"Total equations in non-trivial classes: {total_in_classes}", file=sys.stderr)
    
    # Get the top equivalence classes by size
    sorted_classes = sorted(nontrivial.items(), key=lambda x: -len(x[1]))
    print("\nTop 10 equivalence classes:", file=sys.stderr)
    for rep, members in sorted_classes[:10]:
        print(f"  E{rep} ({len(members)} members): {eqs[rep]}", file=sys.stderr)
    
    # Build edges between class representatives
    print("\nBuilding inter-class edges...", file=sys.stderr)
    repr_map = {}
    for rep, members in eq_classes.items():
        for m in members:
            repr_map[m] = rep
    
    reps = sorted(set(repr_map.values()))
    
    # Count inter-class TRUE edges
    inter_edges = set()
    for (i, j) in true_edges:
        ri, rj = repr_map[i], repr_map[j]
        if ri != rj:
            inter_edges.add((ri, rj))
    
    print(f"Inter-class edges: {len(inter_edges)}", file=sys.stderr)
    
    # Now output the cheatsheet
    # Part 1: Equivalence classes (most compression)
    # Part 2: Key implications between classes
    # Part 3: Quick reasoning rules
    
    output = []
    
    # ===== HEADER =====
    output.append("=MAGMA IMPLICATION ORACLE=")
    output.append("Notation: .=binary op, E<n>=equation number")
    output.append("LOOKUP: Match E1,E2 below. If E1->E2 listed: TRUE. If E2->E1 but not E1->E2: FALSE.")
    output.append("")
    
    # ===== EQUIVALENCE CLASSES =====
    output.append("==EQUIV CLASSES (mutual implication)==")
    output.append("Format: {rep}~{members}")
    
    # Output all non-trivial equivalence classes
    for rep, members in sorted_classes:
        if len(members) <= 1:
            continue
        member_list = sorted(members)
        # Use rep as first, list others
        others = [m for m in member_list if m != rep]
        if len(others) <= 20:
            output.append(f"{rep}~{','.join(str(m) for m in others)}")
        else:
            # For very large classes, just list count and some members
            output.append(f"{rep}~[{len(others)+1}eq]:{','.join(str(m) for m in others[:30])}...")

    output.append("")
    
    # ===== IMPLICATION EDGES =====
    output.append("==IMPLICATIONS (E_from => E_to)==")
    output.append("Format: from>to,to,to")
    
    # Group edges by source
    edges_by_src = defaultdict(set)
    for (a, b) in inter_edges:
        edges_by_src[a].add(b)
    
    for src in sorted(edges_by_src.keys()):
        targets = sorted(edges_by_src[src])
        output.append(f"{src}>{','.join(str(t) for t in targets)}")
    
    output.append("")
    
    # ===== EQUATION DEFINITIONS =====
    output.append("==EQUATIONS (number:text)==")
    # Only output equations that are class representatives
    for rep in sorted(reps):
        output.append(f"{rep}:{compact_eq_text(eqs[rep])}")
    
    output.append("")
    
    # ===== REASONING RULES =====
    output.append("==RULES==")
    output.append("R1:SINGLETON.If E1 has bare var on one side absent from other->E1 forces |M|=1->TRUE for any E2")
    output.append("R2:TRIVIAL.E1=E2(up to var rename)->TRUE.'x=x'implied by all->TRUE")
    output.append("R3:ABSORPTION.x=x.f(x,y,..)=>x=x.y(E4).x=f(x,y,..).x=>x=y.x(E5).E4=>x=x.g for any g.E5=>x=g.x for any g")
    output.append("R4:BALANCE.Count ops each side.Balanced E1+unbalanced E2+E1 not singleton->FALSE")
    output.append("R5:VARCHECK.E1 all vars same count both sides,E2 not->FALSE")  
    output.append("R6:MAGMA_L(a.b=a):satisfies x=x.f,x.y=x.g.Fails x=y.x,x.y=y.x")
    output.append("R7:MAGMA_R(a.b=b):satisfies x=f.x,x.y=g.y.Fails x=x.y,x.y=y.x")
    output.append("R8:MAGMA_C(a.b=0):satisfies any eq with ops both sides.Fails x=x.y where bare x on one side")
    output.append("R9:If E1 class contains E2 class(lookup above)->TRUE")
    output.append("R10:If E1_rep>E2_rep in IMPLICATIONS->TRUE")
    output.append("R11:TRANSITIVITY.If E1_rep>X and X>E2_rep->TRUE")
    output.append("R12:If no path E1_rep to E2_rep->FALSE")
    
    full_text = '\n'.join(output)
    
    # Write output
    with open('cheatsheets/graph_v1.txt', 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print(f"\nCheatsheet written: {len(full_text)} bytes", file=sys.stderr)
    print(f"10KB limit: {10240} bytes", file=sys.stderr)
    print(f"Over by: {max(0, len(full_text) - 10240)} bytes", file=sys.stderr)

if __name__ == '__main__':
    main()
