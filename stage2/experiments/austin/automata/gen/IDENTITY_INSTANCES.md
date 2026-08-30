# The failing instances of the semantically-broken laws

Produced by `python smallcheck.py <eq> 9 1` on the SEMANTIC free model (`freemodel.Free`) — the exhaustive
check over all 23 one-generator terms of size <= 9 in each of the law's three variables (12,167 assignments).
These instances are the INPUT to any quotient / tag / normal-form construction: each one says the free model
returns the wrong value, and the value it returns says what the law is forcing.

Raw per-law output is in `gen/_id_<eq>.txt` (6 smallest failures each, plus the JSON summary).

Read `#` as the magma operation. `g0` is the single generator.

## 12073  —  `x = y * (((y * x) * x) * (z * z))`   (23 failures)

```
FAIL {'y': 'g0', 'x': '(((g0*g0)*g0)*(g0*g0))', 'z': 'g0'} -> (g0*(g0*(g0*g0)))
FAIL {'y': 'g0', 'x': '(((g0*g0)*g0)*(g0*g0))', 'z': '(g0*g0)'} -> (g0*(g0*((g0*g0)*(g0*g0))))
FAIL {'y': 'g0', 'x': '(((g0*g0)*g0)*(g0*g0))', 'z': '(g0*(g0*g0))'} -> (g0*(g0*((g0*(g0*g0))*(g0*(g0*g0)))))
FAIL {'y': 'g0', 'x': '(((g0*g0)*g0)*(g0*g0))', 'z': '((g0*g0)*g0)'} -> (g0*(g0*(((g0*g0)*g0)*((g0*g0)*g0))))
FAIL {'y': 'g0', 'x': '(((g0*g0)*g0)*(g0*g0))', 'z': '(g0*(g0*(g0*g0)))'} -> (g0*(g0*((g0*(g0*(g0*g0)))*(g0*(g0*(g0*g0))))))
FAIL {'y': 'g0', 'x': '(((g0*g0)*g0)*(g0*g0))', 'z': '(g0*((g0*g0)*g0))'} -> (g0*(g0*((g0*((g0*g0)*g0))*(g0*((g0*g0)*g0)))))
```

## 27859  —  `x = ((y * (y * x)) * x) * (z * z)`   (13 failures)

```
FAIL {'y': '((g0*(g0*g0))*g0)', 'x': '((g0*(g0*g0))*g0)', 'z': 'g0'} -> ((g0*((g0*(g0*g0))*g0))*(g0*g0))
FAIL {'y': '((g0*(g0*g0))*g0)', 'x': '((g0*(g0*g0))*g0)', 'z': '(g0*g0)'} -> ((g0*((g0*(g0*g0))*g0))*((g0*g0)*(g0*g0)))
FAIL {'y': '((g0*(g0*g0))*g0)', 'x': '((g0*(g0*g0))*g0)', 'z': '(g0*(g0*g0))'} -> ((g0*((g0*(g0*g0))*g0))*((g0*(g0*g0))*(g0*(g0*g0))))
FAIL {'y': '((g0*(g0*g0))*g0)', 'x': '((g0*(g0*g0))*g0)', 'z': '((g0*g0)*g0)'} -> ((g0*((g0*(g0*g0))*g0))*(((g0*g0)*g0)*((g0*g0)*g0)))
FAIL {'y': '(g0*((g0*(g0*g0))*g0))', 'x': '(g0*((g0*(g0*g0))*g0))', 'z': 'g0'} -> ((((g0*(g0*g0))*g0)*(g0*((g0*(g0*g0))*g0)))*(g0*g0))
FAIL {'y': '(g0*((g0*(g0*g0))*g0))', 'x': '(g0*((g0*(g0*g0))*g0))', 'z': '(g0*g0)'} -> ((((g0*(g0*g0))*g0)*(g0*((g0*(g0*g0))*g0)))*((g0*g0)*(g0*g0)))
```

## 21865  —  `x = (y * (z * x)) * (x * (x * z))`   (68 failures)

```
FAIL {'y': 'g0', 'z': '((g0*(g0*g0))*g0)', 'x': '((g0*(g0*g0))*g0)'} -> ((g0*(g0*(g0*g0)))*(((g0*(g0*g0))*g0)*(g0*(g0*g0))))
FAIL {'y': '(g0*(g0*g0))', 'z': '(g0*g0)', 'x': '((g0*(g0*g0))*g0)'} -> (g0*(((g0*(g0*g0))*g0)*(((g0*(g0*g0))*g0)*(g0*g0))))
FAIL {'y': '(g0*(g0*g0))', 'z': '((g0*g0)*((g0*g0)*g0))', 'x': 'g0'} -> (((g0*g0)*((g0*g0)*g0))*(g0*(g0*g0)))
FAIL {'y': '(g0*g0)', 'z': '((g0*(g0*g0))*g0)', 'x': '((g0*(g0*g0))*g0)'} -> (((g0*g0)*(g0*(g0*g0)))*(((g0*(g0*g0))*g0)*(g0*(g0*g0))))
FAIL {'y': '(g0*g0)', 'z': '(g0*(g0*(g0*(g0*g0))))', 'x': '(g0*(g0*g0))'} -> ((g0*(g0*(g0*(g0*g0))))*((g0*(g0*g0))*g0))
FAIL {'y': '(g0*(g0*g0))', 'z': '((g0*g0)*g0)', 'x': '((g0*(g0*g0))*g0)'} -> (g0*(((g0*(g0*g0))*g0)*(((g0*(g0*g0))*g0)*((g0*g0)*g0))))
```

## 22591  —  `x = (y * (y * x)) * ((x * x) * z)`   (46 failures)

```
FAIL {'y': '(g0*(g0*g0))', 'x': '((g0*g0)*((g0*g0)*g0))', 'z': 'g0'} -> (((g0*(g0*g0))*g0)*(g0*g0))
FAIL {'y': '(g0*(g0*g0))', 'x': '((g0*g0)*((g0*g0)*g0))', 'z': '(g0*g0)'} -> (((g0*(g0*g0))*g0)*(g0*(g0*g0)))
FAIL {'y': '(g0*(g0*g0))', 'x': '((g0*g0)*((g0*g0)*g0))', 'z': '(g0*(g0*g0))'} -> (((g0*(g0*g0))*g0)*(g0*(g0*(g0*g0))))
FAIL {'y': '(g0*(g0*g0))', 'x': '((g0*g0)*((g0*g0)*g0))', 'z': '((g0*g0)*g0)'} -> (((g0*(g0*g0))*g0)*(g0*((g0*g0)*g0)))
FAIL {'y': '((g0*g0)*((g0*g0)*g0))', 'x': '((g0*g0)*((g0*g0)*g0))', 'z': 'g0'} -> ((((g0*g0)*((g0*g0)*g0))*g0)*(g0*g0))
FAIL {'y': '(g0*(g0*g0))', 'x': '((g0*g0)*((g0*g0)*g0))', 'z': '(g0*(g0*(g0*g0)))'} -> (((g0*(g0*g0))*g0)*(g0*(g0*(g0*(g0*g0)))))
```

## 9663  —  `x = y * ((z * y) * (x * (x * y)))`   (23 failures)

```
FAIL {'y': '(g0*(g0*g0))', 'z': '((g0*g0)*(g0*(g0*g0)))', 'x': 'g0'} -> ((g0*(g0*g0))*(g0*(g0*(g0*(g0*(g0*g0))))))
FAIL {'y': '(g0*(g0*g0))', 'z': '((g0*g0)*(g0*(g0*g0)))', 'x': '(g0*g0)'} -> ((g0*(g0*g0))*(g0*((g0*g0)*((g0*g0)*(g0*(g0*g0))))))
FAIL {'y': '(g0*(g0*g0))', 'z': '((g0*g0)*(g0*(g0*g0)))', 'x': '(g0*(g0*g0))'} -> ((g0*(g0*g0))*(g0*((g0*(g0*g0))*((g0*(g0*g0))*(g0*(g0*g0))))))
FAIL {'y': '(g0*(g0*g0))', 'z': '((g0*g0)*(g0*(g0*g0)))', 'x': '((g0*g0)*g0)'} -> ((g0*(g0*g0))*(g0*(((g0*g0)*g0)*(((g0*g0)*g0)*(g0*(g0*g0))))))
FAIL {'y': '(g0*(g0*g0))', 'z': '((g0*g0)*(g0*(g0*g0)))', 'x': '(g0*(g0*(g0*g0)))'} -> ((g0*(g0*g0))*(g0*((g0*(g0*(g0*g0)))*((g0*(g0*(g0*g0)))*(g0*(g0*g0))))))
FAIL {'y': '(g0*(g0*g0))', 'z': '((g0*g0)*(g0*(g0*g0)))', 'x': '(g0*((g0*g0)*g0))'} -> ((g0*(g0*g0))*(g0*((g0*((g0*g0)*g0))*((g0*((g0*g0)*g0))*(g0*(g0*g0))))))
```

## 10222  —  `x = y * ((x * y) * ((z * y) * y))`   (45 failures)

```
FAIL {'y': '(g0*g0)', 'x': 'g0', 'z': '((g0*g0)*((g0*g0)*g0))'} -> ((g0*g0)*((g0*(g0*g0))*(g0*(g0*g0))))
FAIL {'y': '(g0*g0)', 'x': '((g0*g0)*((g0*g0)*g0))', 'z': 'g0'} -> ((g0*g0)*(g0*((g0*(g0*g0))*(g0*g0))))
FAIL {'y': '(g0*g0)', 'x': '(g0*g0)', 'z': '((g0*g0)*((g0*g0)*g0))'} -> ((g0*g0)*(((g0*g0)*(g0*g0))*(g0*(g0*g0))))
FAIL {'y': '(g0*g0)', 'x': '((g0*g0)*((g0*g0)*g0))', 'z': '(g0*g0)'} -> ((g0*g0)*(g0*(((g0*g0)*(g0*g0))*(g0*g0))))
FAIL {'y': '(g0*g0)', 'x': '(g0*(g0*g0))', 'z': '((g0*g0)*((g0*g0)*g0))'} -> ((g0*g0)*(((g0*(g0*g0))*(g0*g0))*(g0*(g0*g0))))
FAIL {'y': '(g0*g0)', 'x': '((g0*g0)*g0)', 'z': '((g0*g0)*((g0*g0)*g0))'} -> ((g0*g0)*((((g0*g0)*g0)*(g0*g0))*(g0*(g0*g0))))
```

## 12294  —  `x = y * (((z * y) * x) * (x * y))`   (22 failures)

```
FAIL {'y': '((g0*g0)*g0)', 'z': '(((g0*g0)*g0)*(g0*g0))', 'x': 'g0'} -> (((g0*g0)*g0)*((g0*g0)*(g0*((g0*g0)*g0))))
FAIL {'y': '((g0*g0)*g0)', 'z': '(((g0*g0)*g0)*(g0*g0))', 'x': '(g0*g0)'} -> (((g0*g0)*g0)*((g0*(g0*g0))*((g0*g0)*((g0*g0)*g0))))
FAIL {'y': '((g0*g0)*g0)', 'z': '(((g0*g0)*g0)*(g0*g0))', 'x': '(g0*(g0*g0))'} -> (((g0*g0)*g0)*((g0*(g0*(g0*g0)))*((g0*(g0*g0))*((g0*g0)*g0))))
FAIL {'y': '((g0*g0)*g0)', 'z': '(((g0*g0)*g0)*(g0*g0))', 'x': '((g0*g0)*g0)'} -> (((g0*g0)*g0)*((g0*((g0*g0)*g0))*(((g0*g0)*g0)*((g0*g0)*g0))))
FAIL {'y': '((g0*g0)*g0)', 'z': '(((g0*g0)*g0)*(g0*g0))', 'x': '(g0*(g0*(g0*g0)))'} -> (((g0*g0)*g0)*((g0*(g0*(g0*(g0*g0))))*((g0*(g0*(g0*g0)))*((g0*g0)*g0))))
FAIL {'y': '((g0*g0)*g0)', 'z': '(((g0*g0)*g0)*(g0*g0))', 'x': '(g0*((g0*g0)*g0))'} -> (((g0*g0)*g0)*((g0*(g0*((g0*g0)*g0)))*((g0*((g0*g0)*g0))*((g0*g0)*g0))))
```

## 21864  —  `x = (y * (z * x)) * (x * (x * y))`   (5 failures)

```
FAIL {'y': '(g0*(g0*g0))', 'z': 'g0', 'x': '(g0*((g0*(g0*g0))*g0))'} -> (g0*((g0*((g0*(g0*g0))*g0))*g0))
FAIL {'y': '(g0*(g0*g0))', 'z': '((g0*(g0*g0))*g0)', 'x': '((g0*(g0*g0))*g0)'} -> (g0*(((g0*(g0*g0))*g0)*(((g0*(g0*g0))*g0)*(g0*(g0*g0)))))
FAIL {'y': '(g0*((g0*g0)*g0))', 'z': '((g0*(g0*g0))*g0)', 'x': '((g0*(g0*g0))*g0)'} -> (g0*(((g0*(g0*g0))*g0)*(((g0*(g0*g0))*g0)*(g0*((g0*g0)*g0)))))
FAIL {'y': '(g0*((g0*(g0*g0))*g0))', 'z': '((g0*(g0*g0))*g0)', 'x': '((g0*(g0*g0))*g0)'} -> (g0*(((g0*(g0*g0))*g0)*(((g0*(g0*g0))*g0)*(g0*((g0*(g0*g0))*g0)))))
FAIL {'y': '(g0*(((g0*g0)*g0)*g0))', 'z': '((g0*(g0*g0))*g0)', 'x': '((g0*(g0*g0))*g0)'} -> (g0*(((g0*(g0*g0))*g0)*(((g0*(g0*g0))*g0)*(g0*(((g0*g0)*g0)*g0)))))
```

## 24199  —  `x = ((y * x) * x) * ((x * z) * y)`   (230 failures)

```
FAIL {'y': 'g0', 'x': '((g0*g0)*g0)', 'z': '((g0*g0)*g0)'} -> (((g0*((g0*g0)*g0))*((g0*g0)*g0))*(g0*g0))
FAIL {'y': 'g0', 'x': '((g0*g0)*g0)', 'z': '((g0*(g0*g0))*g0)'} -> (((g0*((g0*g0)*g0))*((g0*g0)*g0))*(g0*g0))
FAIL {'y': '(g0*g0)', 'x': '((g0*g0)*g0)', 'z': '((g0*g0)*g0)'} -> ((((g0*g0)*((g0*g0)*g0))*((g0*g0)*g0))*(g0*(g0*g0)))
FAIL {'y': 'g0', 'x': '((g0*g0)*g0)', 'z': '((g0*(g0*(g0*g0)))*g0)'} -> (((g0*((g0*g0)*g0))*((g0*g0)*g0))*(g0*g0))
FAIL {'y': 'g0', 'x': '((g0*g0)*g0)', 'z': '((g0*((g0*g0)*g0))*g0)'} -> (((g0*((g0*g0)*g0))*((g0*g0)*g0))*(g0*g0))
FAIL {'y': 'g0', 'x': '(((g0*g0)*g0)*g0)', 'z': '((g0*g0)*(g0*g0))'} -> (((g0*(((g0*g0)*g0)*g0))*(((g0*g0)*g0)*g0))*(g0*g0))
```

## What to notice

* In every case the failing assignment gives one of the variables a value that is **itself of the shape the
  encoding builds** — for 12073 the smallest failure is `x = ((a#a)#a)#(a#a)`, which is exactly the
  law's own encoding `((y#x)#x)#(z#z)` at `y = z = a`. The free model cannot tell a payload from an
  encoding of a payload, and the law forces the two readings to agree.
* The `--values` restriction is a dead end at this size: the one-generator pool of terms of size <= 9 has
  23 elements and every one of them is a value, so `smallcheck --values` changes nothing. Measured.
* 21864 (22 failures) vs its dual 24199 (23 by the same measurement, 230 in the earlier sweep at a
  different orientation) — work the 21864 side.
* The three design agents of this session converged independently on the same conclusion for 12073: the
  construction must identify **all squares with a single element**. Two of them built carriers on that
  basis (a normal-form carrier `M ::= g n | K | E t | J a b` and a tag carrier `M ::= g n | E | J u v`),
  and the third derived it as a theorem: with `S_z = z#z`, `psi_y(x) = (y#x)#x` and `E(y,z) = psi_y(y)#S_z`,
  the substitutions `x := y` and `x := E(y,z')` give `psi_y(E) = y`, hence `E(y,z') = y#(y#S_z)` — so `E` does
  not depend on `z'`. See gen/PLAYBOOK_QUOTIENT.md.
