# Comparison: graph_v4_revised vs no_cheatsheet (qwen2.5:3b, balanced-120, seed17)

## Run configuration

| Setting           | graph_v4_revised                                     | no_cheatsheet                                        |
|-------------------|------------------------------------------------------|------------------------------------------------------|
| Model             | qwen2.5:3b                                           | qwen2.5:3b                                           |
| Cheatsheet        | cheatsheets/graph_v4.txt                             | none                                                 |
| Benchmark         | control_balanced_normal100_hard20_seed17 (120 items) | control_balanced_normal100_hard20_seed17 (120 items) |
| Date              | 2026-03-16                                           | 2026-03-16                                           |

## Headline metrics

| Metric            | graph_v4_revised | no_cheatsheet | Delta (v4 − NC) |
|-------------------|-----------------|---------------|-----------------|
| Accuracy          | 52.5 %          | 49.2 %        | **+3.3 pp**     |
| F1                | 0.095           | 0.116         | −0.021          |
| Precision (TRUE)  | 1.000           | 0.444         | **+0.556**      |
| Recall (TRUE)     | 0.050           | 0.067         | −0.017          |
| TRUE accuracy     | 5.0 %  (3/60)   | 6.7 % (4/60)  | −1.7 pp         |
| FALSE accuracy    | 100.0 % (60/60) | 91.7 % (55/60)| **+8.3 pp**     |
| Avg time / item   | 4.45 s          | 9.31 s        | **−52 % faster**|
| Unparsed          | 0               | 0             | 0               |

## Case-level flip analysis (cases that changed between runs)

**v4 ✓, NC ✗ — cheatsheet helped (8 cases)**

| Category      | Count |
|---------------|-------|
| Gained TRUE   | 3     |
| Gained FALSE  | 5     |

**v4 ✗, NC ✓ — cheatsheet hurt (4 cases)**

| Category      | Count |
|---------------|-------|
| Lost TRUE     | 4     |
| Lost FALSE    | 0     |

Net: the cheatsheet adds +4 net correct answers (+3 TRUE, +5 FALSE gained, −4 TRUE lost, −0 FALSE lost).
It converts 5 NC false-positives (predicted TRUE, actually FALSE) into correct TRUE predictions, at the cost
of 4 NC true-positives it now misses.

## Detailed miss breakdown for graph_v4_revised (57 misses)

Of the 57 total misses, **all 57 are TRUE cases predicted as FALSE** (zero FALSE cases mispredicted).

| Miss category                         | Count | Root cause                                                |
|---------------------------------------|-------|-----------------------------------------------------------|
| SINGLETON (E1: x = EXPR, x ∉ RHS)    | 23    | Singleton rule not recognised or not trusted by model     |
| LEFT-PROJ (E1: x = x ∗ EXPR, x ∉ EXPR) | 7  | Generic/graph-backed left-proj examples not applied       |
| RIGHT-PROJ (E1: x = EXPR ∗ x)        | 2     | Listed graph-backed shapes missed (hard_0121, hard_0115)  |
| COMPLEX (x on both sides, no family) | 25    | No current proof lane covers these                        |

### SINGLETON misses (23 — all should be immediate TRUE)

These cases have E1 of the form `x = EXPR` where x does NOT appear anywhere in EXPR.
The singleton rule (§2 of cheatsheet) covers them directly; the model failed to apply it.

Sample cases:
```
normal_0873: x = (((y * y) * y) * y) * y          =>  x * (y * z) = (y * w) * u
normal_0772: x = (y * (y * (z * z))) * w           =>  x = (y * y) * (x * y)
normal_0911: x = y * ((y * (z * z)) * y)           =>  x = (y * (z * y)) * w
normal_0160: x = y * (z * (w * (z * z)))           =>  x = (y * (z * w)) * x
normal_0319: x = ((y * (y * y)) * z) * w           =>  x = (y * (z * (w * w))) * z
normal_0194: x = (y * (z * w)) * (z * w)           =>  x = x * (((x * y) * y) * z)
normal_0486: x = ((y * y) * (z * z)) * y           =>  x * y = (z * (w * y)) * x
normal_0662: x = y * ((y * (z * w)) * w)           =>  x = y * ((z * (w * w)) * x)
normal_0646: x = (y * (z * w)) * (u * v)           =>  x = (y * (z * (w * x))) * z
normal_0277: x = ((y * (z * w)) * u) * v           =>  x = y * (z * (x * x))
```

### LEFT-PROJ misses (7)

All have E1 = `x = x * EXPR` with x NOT inside EXPR. All have same leftmost variable on
both sides of E2. Per the cheatsheet rule these should be TRUE.

```
hard_0065:  x = x * (y * (z * y))          =>  x = (x * (x * (x * y))) * x
hard_0117:  x = x * (y * (z * y))          =>  x = (x * (x * (x * y))) * x
hard_0191:  x = x * ((y * z) * (w * u))    =>  x = (x * (x * (y * x))) * x
hard_0196:  x = x * ((y * (z * w)) * w)    =>  x * y = (x * (z * w)) * u
normal_0973: x = x * (y * ((z * w) * u))  =>  (x * x) * y = (x * y) * z
hard_0183:  x = x * (y * (x * z))          =>  x = ((x * y) * (z * w)) * u  [x in EXPR]
hard_0113:  x = x * (y * (z * (x * y)))    =>  x = x * (((y * x) * z) * w)  [x in EXPR]
```

Note: hard_0183 and hard_0113 have x inside EXPR — these may belong to a deeper sub-family
not coverable by the generic left-proj rule.

### RIGHT-PROJ misses (2)

Both shapes are explicitly listed in the cheatsheet graph-backed right-proj list:
```
hard_0121:  x = ((y * y) * z) * x   =>  x = y * (y * (z * (w * x)))    [listed shape]
hard_0115:  x = ((y * z) * w) * x   =>  x = y * ((z * (w * u)) * x)    [listed shape]
```

The model failed to apply the rule despite an exact shape match.

## Key insights for v5 cheatsheet

1. **Singleton is the #1 fix target.** 23/57 misses are pure singleton failures.
   The fix is not adding new rules — it's making the singleton scan unmissable.
   Safety: zero FALSE cases have E1 with x absent from RHS. Adding emphasis costs nothing.

2. **Left-proj generic rule needs better safeguarding.**
   All 4 FALSE left-proj cases have x INSIDE EXPR. The fix: explicitly state
   "x must not appear anywhere inside EXPR after the leading x*."
   Adding graph-backed examples for hard_0065/0117/0191/0196/normal_0973 shapes recovers 5+ cases.

3. **Right-proj shape matching fails on listed examples.** Reinforcing the listed shapes
   and adding a direct check helps without risk (0 FALSE right-proj cases with x ∉ EXPR and
   non-general shape — except 2 that the generic rule would misclassify).

4. **24 COMPLEX misses are not easily recoverable** from cheatsheet edits alone.
   They require proof techniques beyond projection/singleton. The constant-product family
   has 7 FALSE collision cases in the "both sides have products" pattern, preventing broad rules.
   These are candidates for a future deeper graph-embedding approach.

5. The cheatsheet doubles speed (4.45 s vs 9.31 s) while holding perfect FALSE precision.
   The v5 goal: recover TRUE recall while preserving FALSE precision = 1.0.
