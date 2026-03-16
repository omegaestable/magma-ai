#!/usr/bin/env python3
"""Light golf of graph_v1.txt — compress prose and syntax, keep ALL data."""

import re

def golf():
    with open("cheatsheets/graph_v1.txt", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")

    # Find section starts
    map_start = next(i for i, l in enumerate(lines) if l == "[MAP]")
    edges_start = next(i for i, l in enumerate(lines) if l == "[EDGES]")
    full_start = next(i for i, l in enumerate(lines) if l == "[FULL]")

    # ── HEADER (replace entirely) ──
    header = (
        "MAGMA IMPLICATION GRAPH\n"
        "E1 implies E2 over all magmas?\n"
        "1.Check rules 2.Strip spaces from E1,E2 3.Find E1 in MAP->class a 4.Find E2->class b\n"
        "5.a=b->TRUE 6.Path a>b in EDGES->TRUE else FALSE\n"
        "Eq not in MAP=singleton-forcing(one side is bare var absent from other)->TRUE for any E2\n"
    )

    # ── RULES (compress heavily) ──
    rules = (
        "RULES\n"
        "R1 SINGLETON:side is lone var not in other side->TRUE. x=y*z YES. x=x*y NO.\n"
        "R2 E2='x=x'->TRUE\n"
        "R3 E1='x=x*EXPR'(EXPR has other vars)->implies x=x*y class 4\n"
        "R4 E1='x=EXPR*x'(EXPR has other vars)->implies x=y*x class 5\n"
        "R5 E1 balanced(*count same both sides),E2 unbalanced,E1 not singleton->FALSE\n"
        "R6 COUNTEREX:LEFT_PROJ a*b=a satisfies iff leftmost var same;RIGHT_PROJ a*b=b iff rightmost same;CONST a*b=0 iff both sides have *\n"
        "R7 E2='x=y' and E1 not singleton->FALSE\n"
    )

    # ── MAP: strip "C" prefix, colon no space, pipe no space ──
    map_lines = []
    for i in range(map_start, edges_start):
        l = lines[i]
        if l.startswith("C"):
            # C4: eq1 | eq2 -> 4:eq1|eq2
            l = l[1:]  # drop C
            l = l.replace(" | ", "|")
            l = l.replace(": ", ":")
            map_lines.append(l)

    # ── EDGES: strip "C" prefix ──
    edge_lines = []
    for i in range(edges_start, full_start):
        l = lines[i]
        if l.startswith("C") and " > " in l:
            # C3 > C8, C23 -> 3>8,23
            parts = l.split(" > ", 1)
            src = parts[0][1:]  # drop C
            targets = parts[1].replace("C", "")
            # Also remove spaces after commas
            targets = targets.replace(", ", ",")
            edge_lines.append(f"{src}>{targets}")

    # ── FULL: strip "C" prefix ──
    full_lines = []
    for i in range(full_start, len(lines)):
        l = lines[i]
        if l.startswith("C") and " > " in l:
            parts = l.split(" > ", 1)
            src = parts[0][1:]
            targets = parts[1]
            full_lines.append(f"{src}>{targets}")

    # ── Assemble ──
    out = header
    out += rules
    out += "MAP\n"
    out += "\n".join(map_lines) + "\n"
    out += "EDGES\n"
    out += "All classes imply 1(x=x).Singleton implies all.Transitive:a>b,b>c then a>c.No path->FALSE.\n"
    out += "\n".join(edge_lines) + "\n"
    out += "FULL\n"
    out += "\n".join(full_lines) + "\n"

    outpath = "cheatsheets/graph_v2.txt"
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(out)

    orig = len(text.encode("utf-8"))
    new = len(out.encode("utf-8"))
    print(f"Original: {orig:,} bytes")
    print(f"Golfed:   {new:,} bytes")
    print(f"Saved:    {orig - new:,} bytes ({100*(orig-new)/orig:.1f}%)")

    # Measure sections
    parts = out.split("MAP\n", 1)
    header_size = len(parts[0].encode("utf-8"))
    rest = parts[1]
    parts2 = rest.split("EDGES\n", 1)
    map_size = len(parts2[0].encode("utf-8"))
    rest2 = parts2[1]
    parts3 = rest2.split("FULL\n", 1)
    edges_size = len(parts3[0].encode("utf-8"))
    full_size = len(parts3[1].encode("utf-8"))
    print(f"\nSection sizes:")
    print(f"  Header+Rules: {header_size:,}")
    print(f"  MAP:          {map_size:,}")
    print(f"  EDGES:        {edges_size:,}")
    print(f"  FULL:         {full_size:,}")

if __name__ == "__main__":
    golf()
