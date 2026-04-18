#!/usr/bin/env python3
"""Compute step-by-step evaluations for MA1 and MA2 examples."""
from distill import parse_equation_tree, eval_tree

MA1 = [[2,1,2],[2,2,2],[2,2,2]]
MA2 = [[0,2,1],[0,1,2],[0,1,2]]

def ma1_eval(a, b):
    return MA1[a][b]

def ma2_eval(a, b):
    return MA2[a][b]

# MA1 example: hard3_0359
# E1: x * x = y * ((y * x) * z)     E2: x * y = (y * y) * (z * z)
# Assignment: x=0, y=1, z=2
print("=== MA1 Example (hard3_0359) ===")
print("E1: x * x = y * ((y * x) * z)")
print("E2: x * y = (y * y) * (z * z)")
print("Variables: x=0, y=1, z=2")
print()
print("MA1 rule: a*b = 2, EXCEPT 0*1 = 1")
print()
print("E1 LHS: 0 * 0 → MA1[0][0] = 2")
print("E1 RHS: 1 * ((1 * 0) * 2)")
print("  1*0 → MA1[1][0] = 2")
print("  2*2 → MA1[2][2] = 2")
print("  1*2 → MA1[1][2] = 2")
print("E1: 2 = 2 ✓")
print()
print("E2 LHS: 0 * 1 → MA1[0][1] = 1")
print("E2 RHS: (1 * 1) * (2 * 2)")
print("  1*1 → MA1[1][1] = 2")
print("  2*2 → MA1[2][2] = 2")
print("  2*2 → MA1[2][2] = 2")
print("E2: 1 ≠ 2 → MA1 SEPARATION")

# Verify
lhs, rhs = parse_equation_tree("x * x = y * ((y * x) * z)")
a = {'x':0, 'y':1, 'z':2}
print(f"\nVerify E1: LHS={eval_tree(lhs, a, MA1)}, RHS={eval_tree(rhs, a, MA1)}")
lhs, rhs = parse_equation_tree("x * y = (y * y) * (z * z)")
print(f"Verify E2: LHS={eval_tree(lhs, a, MA1)}, RHS={eval_tree(rhs, a, MA1)}")

print("\n=== MA2 Example (hard3_0195) ===")
print("E1: x = (y * z) * ((x * z) * x)")
print("E2: x * y = ((x * z) * y) * y")
print("Variables: x=0, y=1, z=2")
print()
print("MA2 table: M[0]={0,2,1} M[1]={0,1,2} M[2]={0,1,2}")
print()
a = {'x':0, 'y':1, 'z':2}
print("E1 LHS: x → 0")
print("E1 RHS: (1 * 2) * ((0 * 2) * 0)")
print(f"  1*2 → M[1][2] = {MA2[1][2]}")
print(f"  0*2 → M[0][2] = {MA2[0][2]}")
print(f"  {MA2[0][2]}*0 → M[{MA2[0][2]}][0] = {MA2[MA2[0][2]][0]}")
print(f"  {MA2[1][2]}*{MA2[MA2[0][2]][0]} → M[{MA2[1][2]}][{MA2[MA2[0][2]][0]}] = {MA2[MA2[1][2]][MA2[MA2[0][2]][0]]}")
lhs, rhs = parse_equation_tree("x = (y * z) * ((x * z) * x)")
print(f"Verify E1: LHS={eval_tree(lhs, a, MA2)}, RHS={eval_tree(rhs, a, MA2)}")

print()
print("E2 LHS: 0 * 1")
print(f"  0*1 → M[0][1] = {MA2[0][1]}")
print("E2 RHS: ((0 * 2) * 1) * 1")
print(f"  0*2 → M[0][2] = {MA2[0][2]}")
print(f"  {MA2[0][2]}*1 → M[{MA2[0][2]}][1] = {MA2[MA2[0][2]][1]}")
v = MA2[MA2[0][2]][1]
print(f"  {v}*1 → M[{v}][1] = {MA2[v][1]}")
lhs, rhs = parse_equation_tree("x * y = ((x * z) * y) * y")
print(f"Verify E2: LHS={eval_tree(lhs, a, MA2)}, RHS={eval_tree(rhs, a, MA2)}")
