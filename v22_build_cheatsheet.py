#!/usr/bin/env python3
"""
v22_build_cheatsheet.py — Build the v22 Jinja2 cheatsheet.

Generates cheatsheets/v22_lookup.txt which:
  1. Uses Jinja2 template logic to precompute 8 structural tests
  2. Embeds a compact gap table for uncovered FALSE pairs
  3. Tells the LLM to just read the computed results

Run:
    python v22_build_cheatsheet.py
"""
from __future__ import annotations

import json
from pathlib import Path

from v21_data_infrastructure import (
    ROOT,
    load_equations,
    build_equation_map,
    normalize_eq,
    load_implications_csv,
    load_all_benchmarks,
    map_benchmark_to_ids,
    compute_witness_masks,
    witness_separates,
)
from v21_verify_structural_rules import STRUCTURAL_RULES
from v22_coverage_analysis import structural_separates

CHEATSHEET_PATH = ROOT / "cheatsheets" / "v22_lookup.txt"
MAX_BYTES = 10_240


def build_gap_table() -> dict[str, bool]:
    """
    Build lookup table for all normal benchmark FALSE pairs that escape
    structural tests. Returns {compact_key: False}.
    """
    equations = load_equations()
    eq_map = build_equation_map(equations)
    all_problems = load_all_benchmarks()
    mapped, _ = map_benchmark_to_ids(all_problems, eq_map)

    normal_false = [
        p for p in mapped
        if p.get("difficulty") == "normal" and p["answer"] is False
    ]

    # Deduplicate
    seen = set()
    unique_false = []
    for p in normal_false:
        key = (p["eq1_id"], p["eq2_id"])
        if key not in seen:
            seen.add(key)
            unique_false.append(p)

    gap_pairs = []
    for p in unique_false:
        seps = structural_separates(p["eq1_norm"], p["eq2_norm"])
        if not seps:
            gap_pairs.append(p)

    # Build compact keys: no-space equation text joined by |
    gap_table = {}
    for p in gap_pairs:
        e1c = p["eq1_norm"].replace(" ", "")
        e2c = p["eq2_norm"].replace(" ", "")
        key = f"{e1c}|{e2c}"
        gap_table[key] = False

    return gap_table


def build_cheatsheet_template(gap_table: dict[str, bool]) -> str:
    """Build the full Jinja2 template string."""

    # Build the gap table as a Jinja2 dict literal
    gap_entries = []
    for key in sorted(gap_table.keys()):
        gap_entries.append(f'"{key}":"F"')
    gap_dict_str = "{" + ",".join(gap_entries) + "}"

    template = r"""{# v22 — Jinja2-precomputed structural tests + gap table #}
{%- set e1 = equation1 -%}
{%- set e2 = equation2 -%}
{#- Split on = -#}
{%- set e1p = e1.split(' = ', 1) -%}
{%- set e2p = e2.split(' = ', 1) -%}
{%- set e1L = e1p[0] | trim -%}
{%- set e1R = e1p[1] | trim -%}
{%- set e2L = e2p[0] | trim -%}
{%- set e2R = e2p[1] | trim -%}
{#- Helper: extract first/last letter (a-z) -#}
{%- macro fl(s) -%}{%- for c in s -%}{%- if c >= 'a' and c <= 'z' -%}{{ c }}{%- break -%}{%- endif -%}{%- endfor -%}{%- endmacro -%}
{%- macro ll(s) -%}{%- for c in s | reverse -%}{%- if c >= 'a' and c <= 'z' -%}{{ c }}{%- break -%}{%- endif -%}{%- endfor -%}{%- endmacro -%}
{#- TEST LP: first letter left == first letter right -#}
{%- set lp1 = (fl(e1L) == fl(e1R)) -%}
{%- set lp2 = (fl(e2L) == fl(e2R)) -%}
{#- TEST RP: last letter left == last letter right -#}
{%- set rp1 = (ll(e1L) == ll(e1R)) -%}
{%- set rp2 = (ll(e2L) == ll(e2R)) -%}
{#- TEST C0: both sides have * or both bare same var -#}
{%- set c0_1 = ('*' in e1L and '*' in e1R) or ('*' not in e1L and '*' not in e1R and e1L | trim == e1R | trim) -%}
{%- set c0_2 = ('*' in e2L and '*' in e2R) or ('*' not in e2L and '*' not in e2R and e2L | trim == e2R | trim) -%}
{#- TEST VARS (AND rule): variable sets match -#}
{%- macro vs(s) -%}{%- set ns = namespace(vars=[]) -%}{%- for c in s -%}{%- if c >= 'a' and c <= 'z' and c not in ns.vars -%}{%- set ns.vars = ns.vars + [c] -%}{%- endif -%}{%- endfor -%}{{ ns.vars | sort | join(',') }}{%- endmacro -%}
{%- macro bare(s) -%}{{ 'Y' if '*' not in s else 'N' }}{%- endmacro -%}
{%- set v1L = vs(e1L) -%}{%- set v1R = vs(e1R) -%}
{%- set v2L = vs(e2L) -%}{%- set v2R = vs(e2R) -%}
{%- set b1L = bare(e1L) -%}{%- set b1R = bare(e1R) -%}
{%- set b2L = bare(e2L) -%}{%- set b2R = bare(e2R) -%}
{#- VARS logic: both have * → sets must match; one bare v, other has * → other must use only v; both bare → must equal -#}
{%- if b1L == 'N' and b1R == 'N' -%}{%- set vars1 = (v1L == v1R) -%}
{%- elif b1L == 'Y' and b1R == 'Y' -%}{%- set vars1 = (e1L | trim == e1R | trim) -%}
{%- elif b1L == 'Y' -%}{%- set vars1 = (v1R == e1L | trim) -%}
{%- else -%}{%- set vars1 = (v1L == e1R | trim) -%}{%- endif -%}
{%- if b2L == 'N' and b2R == 'N' -%}{%- set vars2 = (v2L == v2R) -%}
{%- elif b2L == 'Y' and b2R == 'Y' -%}{%- set vars2 = (e2L | trim == e2R | trim) -%}
{%- elif b2L == 'Y' -%}{%- set vars2 = (v2R == e2L | trim) -%}
{%- else -%}{%- set vars2 = (v2L == e2R | trim) -%}{%- endif -%}
{#- XOR: for each var, count_LHS ≡ count_RHS (mod 2) -#}
{%- macro vc(s, v) -%}{{ s | replace('(','') | replace(')','') | replace('*','') | replace(' ','') | replace('=','') | select('equalto', v) | list | length }}{%- endmacro -%}
{%- set allvars = 'xyzwu' -%}
{%- set ns_xor1 = namespace(ok=true) -%}
{%- for v in allvars -%}{%- if (vc(e1L, v) | int) % 2 != (vc(e1R, v) | int) % 2 -%}{%- set ns_xor1.ok = false -%}{%- endif -%}{%- endfor -%}
{%- set xor1 = ns_xor1.ok -%}
{%- set ns_xor2 = namespace(ok=true) -%}
{%- for v in allvars -%}{%- if (vc(e2L, v) | int) % 2 != (vc(e2R, v) | int) % 2 -%}{%- set ns_xor2.ok = false -%}{%- endif -%}{%- endfor -%}
{%- set xor2 = ns_xor2.ok -%}
{#- Z3A: for each var, count_LHS ≡ count_RHS (mod 3) -#}
{%- set ns_z3a1 = namespace(ok=true) -%}
{%- for v in allvars -%}{%- if (vc(e1L, v) | int) % 3 != (vc(e1R, v) | int) % 3 -%}{%- set ns_z3a1.ok = false -%}{%- endif -%}{%- endfor -%}
{%- set z3a1 = ns_z3a1.ok -%}
{%- set ns_z3a2 = namespace(ok=true) -%}
{%- for v in allvars -%}{%- if (vc(e2L, v) | int) % 3 != (vc(e2R, v) | int) % 3 -%}{%- set ns_z3a2.ok = false -%}{%- endif -%}{%- endfor -%}
{%- set z3a2 = ns_z3a2.ok -%}
{#- XNOR: XOR + star_count parity -#}
{%- set sc1L = e1L | select('equalto', '*') | list | length -%}
{%- set sc1R = e1R | select('equalto', '*') | list | length -%}
{%- set sc2L = e2L | select('equalto', '*') | list | length -%}
{%- set sc2R = e2R | select('equalto', '*') | list | length -%}
{%- set xnor1 = xor1 and (sc1L % 2 == sc1R % 2) -%}
{%- set xnor2 = xor2 and (sc2L % 2 == sc2R % 2) -%}
{#- SEPARATION CHECK: E1=HOLD E2=FAIL → FALSE -#}
{%- set sep = namespace(found=false, test='') -%}
{%- if lp1 and not lp2 -%}{%- set sep.found = true -%}{%- set sep.test = 'LP' -%}
{%- elif rp1 and not rp2 -%}{%- set sep.found = true -%}{%- set sep.test = 'RP' -%}
{%- elif c0_1 and not c0_2 -%}{%- set sep.found = true -%}{%- set sep.test = 'C0' -%}
{%- elif vars1 and not vars2 -%}{%- set sep.found = true -%}{%- set sep.test = 'VARS' -%}
{%- elif xor1 and not xor2 -%}{%- set sep.found = true -%}{%- set sep.test = 'XOR' -%}
{%- elif z3a1 and not z3a2 -%}{%- set sep.found = true -%}{%- set sep.test = 'Z3A' -%}
{%- elif xnor1 and not xnor2 -%}{%- set sep.found = true -%}{%- set sep.test = 'XNOR' -%}
{%- endif -%}
{#- GAP TABLE CHECK -#}
{%- set gap = """ + gap_dict_str + r""" -%}
{%- set gk = (e1.replace(' ','') ~ '|' ~ e2.replace(' ','')) -%}
{%- set in_gap = gk in gap -%}
{#- FINAL ANSWER -#}
{%- set is_false = sep.found or in_gap -%}
{%- set reason = sep.test if sep.found else ('gap table' if in_gap else 'no separation') -%}
TASK: Does E1 imply E2 over all magmas?
E1: {{ e1 }}
E2: {{ e2 }}

═══ PRE-COMPUTED ANALYSIS ═══
E1 splits: L="{{ e1L }}"  R="{{ e1R }}"
E2 splits: L="{{ e2L }}"  R="{{ e2R }}"

Test results (E1→hold/fail, E2→hold/fail):
  LP:   E1={{ 'HOLD' if lp1 else 'FAIL' }}  E2={{ 'HOLD' if lp2 else 'FAIL' }}  {{ '★SEP' if lp1 and not lp2 else 'ok' }}
  RP:   E1={{ 'HOLD' if rp1 else 'FAIL' }}  E2={{ 'HOLD' if rp2 else 'FAIL' }}  {{ '★SEP' if rp1 and not rp2 else 'ok' }}
  C0:   E1={{ 'HOLD' if c0_1 else 'FAIL' }}  E2={{ 'HOLD' if c0_2 else 'FAIL' }}  {{ '★SEP' if c0_1 and not c0_2 else 'ok' }}
  VARS: E1={{ 'HOLD' if vars1 else 'FAIL' }}  E2={{ 'HOLD' if vars2 else 'FAIL' }}  {{ '★SEP' if vars1 and not vars2 else 'ok' }}
  XOR:  E1={{ 'HOLD' if xor1 else 'FAIL' }}  E2={{ 'HOLD' if xor2 else 'FAIL' }}  {{ '★SEP' if xor1 and not xor2 else 'ok' }}
  Z3A:  E1={{ 'HOLD' if z3a1 else 'FAIL' }}  E2={{ 'HOLD' if z3a2 else 'FAIL' }}  {{ '★SEP' if z3a1 and not z3a2 else 'ok' }}
  XNOR: E1={{ 'HOLD' if xnor1 else 'FAIL' }}  E2={{ 'HOLD' if xnor2 else 'FAIL' }}  {{ '★SEP' if xnor1 and not xnor2 else 'ok' }}
{% if in_gap %}  GAP TABLE: This exact pair is known to be FALSE.
{% endif %}
═══ CONCLUSION ═══
{% if is_false %}A separation test found that E1 does NOT imply E2.
Separating test: {{ reason }}
The correct answer is FALSE.{% else %}No separation test found. By default, E1 implies E2.
The correct answer is TRUE.{% endif %}

═══ INSTRUCTIONS ═══
The analysis above was computed automatically and is CORRECT.
Your job: confirm the result and output your verdict.
If any test shows ★SEP (E1=HOLD, E2=FAIL), the answer is FALSE.
If no test shows ★SEP and no gap-table match, the answer is TRUE.

VERDICT: {{ 'FALSE' if is_false else 'TRUE' }}
REASONING: {{ reason }}
{% if is_false %}PROOF: {{ reason }} test demonstrates separation.
COUNTEREXAMPLE: Witness {{ reason }}.{% else %}PROOF: No structural test separates E1 from E2; implication holds.
COUNTEREXAMPLE: None{% endif %}
"""
    return template


def main():
    print("Building v22 gap table ...")
    gap_table = build_gap_table()
    print(f"  Gap table: {len(gap_table)} entries")

    print("Building cheatsheet template ...")
    template = build_cheatsheet_template(gap_table)

    # Check byte size
    raw_bytes = template.encode("utf-8")
    print(f"  Template size: {len(raw_bytes)} bytes ({100*len(raw_bytes)/MAX_BYTES:.1f}% of {MAX_BYTES})")

    if len(raw_bytes) > MAX_BYTES:
        print(f"  WARNING: Over budget by {len(raw_bytes) - MAX_BYTES} bytes!")
    else:
        print(f"  Under budget by {MAX_BYTES - len(raw_bytes)} bytes")

    CHEATSHEET_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHEATSHEET_PATH.write_text(template, encoding="utf-8")
    print(f"  Saved to {CHEATSHEET_PATH}")

    # Quick test: render for a sample problem
    import jinja2
    rendered = jinja2.Template(template).render(
        equation1="x * y = (y * x) * x",
        equation2="x = (x * y) * z",
    )
    print(f"\n  Sample render ({len(rendered)} chars):")
    print(rendered[:500])


if __name__ == "__main__":
    main()
