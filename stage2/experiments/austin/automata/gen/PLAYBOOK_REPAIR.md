# PLAYBOOK: repairing a FALSE generated model

Wave 1 measured that **7 of 10 generated skeletons were FALSE** and that **4 were repaired by hand and then
judge-ACCEPTED**. About half the laws still open are in that state: the free model exists, the extractor found
*most* of it, and one accessor path is wrong in one case. This file is the procedure, so that the next agent
does not rediscover it.

Read `AGENT_BRIEF.md` (proof method) and `WAVE2_PROMPT.md` (validation standard + banned tokens) first.
This file sits between them: **skeleton is false → validated repaired rule set**. It stops where the Lean
proof starts.

Everything below was re-run on 2026-08-29 while writing it. The reproduction is §10.

---

## 1. Load a law and its rules — three lines, and the `dualized` trap

```python
import closedform as cf, revalidate as rv, smallcheck as sc, leangen
from freemodel import normalise, catalog; from laws import parse_eq
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig   # the law the skeleton's `op` models
rules = <rule list>
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)       # [] = validated
```

To get `rules` out of a generated package, take **only the `rules = [...]` literal**, never the module:

```python
src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
```

**Why the `dualized` dance.** `normalise` puts the bare variable on the left. A law is one of three shapes:

| shape | example | `Extractor.lform` / `rform` |
| --- | --- | --- |
| L-form `x = y ◇ B` | 9667 `x = y*((z*y)*(x*(y*y)))` | lform |
| R-form `x = A ◇ y` | 38249 `x = ((y*((x*x)*z))*y)*y` | rform |
| both-compound `x = A ◇ B` | 24200 `x = ((y*x)*x)*((x*z)*z)` | neither |

An **R-form law is served by the model of its dual L-form law with the operation flipped**: `leangen.emit`
writes `def inst : Magma M := { op := fun a b => op b a }` and states `theorem law` for the dual pattern.
So the rules, the Lean `op`, and every test must run on `('x', leangen.dual_pat(orig[1]))`. Testing an
R-form law against `orig` prints 3000/3000 spurious fails and has already cost agents hours.

**`gen/chk<eq>.py` still gets this wrong** (verified 2026-08-29: `chk40057.py`, `chk38316.py` — both dualized
laws — each open with `law = normalise(parse_eq(catalog()[eq]))`). `leangen.emit` writes that line
unconditionally. Take the `rules` literal from the chk file and **rebuild `law` yourself**, always.
`trace.py`, `revalidate.py` and `smallcheck.py` all build it correctly.

**`gen/rules<eq>.txt`'s header lies too.** Its second line always reads `deep tests: all rules 0/3000 fails`
— that is `leangen.emit`'s own weak 3,000-test check, printed even for packages `revalidate.py` classified
FAIL (e.g. `gen/rules6912.txt`, a known-false package, reads `0/3000`). Never take that line as validation.

---

## 2. The rule DSL, exactly (`closedform.py`)

A rule is `(conds, result_expr, tag)`.

**Expressions** — `('U',)` `('V',)` = the two arguments of `op u v`; `('A1', e)` `('A2', e)` = the children of
a `J`-node; `('OP', a, b)` = a *recursive call* `op a b`; `('J', a, b)` = the free product; `('F', k)` = an
unresolved placeholder (only inside the extractor; a placeholder surviving into a condition raises
`Infeasible`).

**Conditions** —

| form | meaning | `Closed.ev`/`check` |
| --- | --- | --- |
| `('TG', e)` | `e` is a `J`-node | `ev(e)` must be non-None with `[0] == 'J'` |
| `('EQ', e1, e2)` | the two terms are identical | both must evaluate, and be equal |
| `('OPEQ', e_op, e_w)` | the evaluated `op`-term equals the target | same, `e_op` contains an `OP` |

**`Closed.ev`** returns `None` — which makes the condition FAIL and the rule not fire — in exactly three
situations: an `A1`/`A2` applied to a non-`J`; a sub-expression that already returned `None`; and an `OP`
whose pair fails the recursion gate `gate_ok`.

**`Closed.check`** sorts conditions so structural ones (`TG`/`EQ` with no nested `op`) run first and the
`OPEQ`/nested ones last. That is a cost ordering only; it does not change which rules fire.

**`Closed.op(u, v)`** walks `self.rules` **in list order** and takes the first rule for which
`check(conds) and ev(result) is not None`; otherwise the result is `('J', u, v)` (the free product).
Results are memoised. A re-entrant pair (`key in self.inprog`) returns `J u v` and bumps `self.cycles`
— a nonzero `cycles` in a validate report means some guard is asking about the product it is inside;
that is legal but is where non-obvious behaviour lives, so look at it before trusting the package.

**The gate.** `msr(a, b) = max(|a|,|b|)² + |a| + |b|`; `gate_ok(a,b,u,v)` is `msr a b < msr u v`. It is the
well-founded measure of the emitted Lean (`termination_by msr u v`, `let p_k := if hs_k : msr .. < msr u v
then op .. else J u v`). A guard that needs a pair not below the gate cannot be expressed as an `OP`.

**The Lean mirror.** `leangen.emit` turns rule *k* into a branch `if P_k u v ∧ <gates> ∧ <op-conditions>
then <result>`, chained in the same order, `else J u v`. So Python order == Lean order, and the gates are
part of the branch condition (a cut gate falls through to the next rule in both). One place they can
*diverge*: Lean's `a1`/`a2` are total (`a1 t = t` on a generator) whereas Python's `ev` returns `None`.
Measured: with rule `[EQ(a1 u, v)] -> a2 u` and `u = v = g0`, Python `check` is `False` and `op(g0,g0) =
J g0 g0`; the Lean branch condition `a1 u = v` would be *true*. **Invariant to preserve in every hand-written
rule: every accessor chain you use is J-guarded by a `TG` on each of its prefixes, in the same rule.**
The generator does this; keep doing it.

---

## 3. Reading `trace.py`

```
python trace.py <eq>            # first failing instance of gen/chk<eq>.py, explained
python trace.py <eq> --n 400    # smaller deep-test budget
```

It finds the smallest failing instance, then prints, for **each product of the law's pattern, bottom-up**,
the value and the rule that produced it. Authentic output (9667, generated rule set, via `gen/_pb_trace9667.py`):

```
  ('z', 'y')                      = (((g1*g2)*(g0*(g2*g2)))*((g1*g2)*(g0*(g2*g2))))   [R2 B0l]
  ('y', 'y')                      = <size 83>   [free]
  ('x', ('y', 'y'))               = <size 85>   [free]
  (('z', 'y'), ('x', ('y', 'y'))) = <size 105>  [free]
  FINAL op(A,B) = <size 147>  expected x = g1  [free]
  rules whose structural conditions hold at the final pair: [] []
```

How to read it:

* **`[free]`** = no rule fired, the product is the free `J`. **`[Rk tag]`** = rule *k* fired.
* **A product that says `[Rk ...]` where the rules downstream assumed it free is the hole.** Here
  `('z','y')` decoded; every later rule expected `y.1` to be the free `J`-shape left by an *undecoded*
  `op z y`, so nothing matched at the top.
* **`FINAL ... [free]` with `expected x = ...`** is the failure: the top product should have decoded to `x`.
* **`rules whose structural conditions hold at the final pair: []`** (guards ignored) — this is the
  classifier. **Empty ⇒ a missing mode** (no rule is even the right *shape*): write a new rule. **Non-empty
  ⇒ the shape is right and an op-guard failed**: either the guard reads the wrong occurrence (§4a–c) or it
  was cut by the gate.
* **`GATE CUT: op(...) at pair sizes (a,b) vs (u,v) sizes (p,q)`** — a genuine reading whose nested guard
  needs a pair that is not `msr`-below `(u,v)`. Not a missing rule; see §9.
* The last line, **`SEMANTIC model: law HOLDS` / `law FAILS too`**, is the go/no-go for repair at all (§9).

After the repair the same script prints, on the same instance:

```
  ('z', 'y') = (((g1*g2)*(g0*(g2*g2)))*((g1*g2)*(g0*(g2*g2))))   [R2 B0l2]
  FINAL op(A,B) = g1  expected x = g1  [R2]
  rules whose structural conditions hold at the final pair: [2] ['B0l2']
```

`trace.py` reads `gen/chk<eq>.py`. To trace a *different* rule set (a candidate repair, or the pre-repair
`chk<eq>_gen0.py`), copy `gen/_pb_trace9667.py` — it reuses `trace.Tracing` and `trace.struct_ok` verbatim
and just takes the rules file as an argument. Do not edit `trace.py`.

---

## 4. Catalogue of holes, and the rule shape that fixes each

The master recipe under all four: **write down the case table of "which products of the law's evaluation
chain fired", and check there is a rule for every cell.** The generator emits one rule per *single* decoded
node; the holes are the cells it never enumerated. `gen/rep6878.py` and `gen/fix33020.py` both open with
that table written out in the docstring — copy that habit, it is what makes the repair provable later.

The invariant that makes every repair possible: **a fired product tells you where its arguments are.**
If `op(p,q)` decoded, then `q` has the encoding shape around `p`, so `p` is recoverable from `q` by a fixed
accessor path — through an occurrence that is *provably free*.

### (a) A decoder reachable only through an occurrence that is itself decoded (level 2 / 3)

* **Symptom.** An inner product of the chain shows `[Rk]` where a later rule's `OPEQ` guard reads its
  argument out of the *free* shape that product would have had. `rules whose structural conditions hold` is
  empty at the final pair.
* **Guard to replace.** Re-locate the decoder to an occurrence that every firing rule guarantees. Keep the
  same `OPEQ` target, move the first argument, and add the `TG` guards for the new path.
* **Worked instance — 9667, `x = y ◇ ((z ◇ y) ◇ (x ◇ (y ◇ y)))`** (`gen/hole9667.py`, `gen/repair9667.py`):

  ```
  generated R2 : J?v & J?v.2 & J?v.2.2 & u = v.2.2.1 & u = v.2.2.2 &
                 J?u & J?u.1 & op(u.1.2, u) == v.1                      -> v.2.1
  repaired  R2 : J?v & J?v.2 & J?v.2.2 & u = v.2.2.1 & u = v.2.2.2 &
                 J?u & J?u.2 & J?u.2.2 & op(u.2.2.1, u) == v.1          -> v.2.1
  ```

  The generated rule recovers `z` at `u.1.2`, i.e. through the R1 `J`-shape of `op z u`. When `op q z`
  itself fired, `u.1` is not that free `J`. But *every* rule carries `u = v.2.2.1`, so after `op z y` fires,
  `y = J _ (J _ (J z z))` and `z = y.2.2.1` — a provably free occurrence. One accessor path changed;
  nothing else.
* **Extractor name.** This is the `level2` mode (`Extractor.decoder_of` with an `('L2',)+path` sub-mode
  vector); its rules carry the tag suffix `l2` / `|<path>:<modes>`. `X.rules(level2=True, cap2=N)` enumerates
  them — raise `cap2` before hand-writing, and hand-write when the combination explodes.

### (b) The outer product of the encoding is itself decoded (the `v = u` case)

* **Symptom.** The failing instance has `u == v` at the final pair (or `v` a proper subterm of `u`), and no
  rule holds structurally — every generated rule's first condition is `J?v` plus an `EQ` locating `u` inside
  `v`, which cannot hold when `v` *is* `u`.
* **Guard to add.** A rule keyed on `('EQ', ('V',), ('U',))` that reads the payload out of `u`'s own
  structure, with the sub-products verified by `OPEQ` rather than assumed free.
* **Worked instance — 5837, `x = y ◇ (x ◇ (y ◇ ((z ◇ y) ◇ y)))`** (`gen/emit5837.py`, the R4 family). Their
  shared prefix is literally

  ```python
  q = A1(U); x = A1(q)
  common = [EQ(V, U), TG(U), TG(A2(U)), EQ(A1(U), A1(A2(U))), OPEQ(OP(A1(U), U), A1(U)), TG(q)]
  R4a = (common + [TG(A2(q)), TG(A1(A2(q))), EQ(x, A2(A1(A2(q)))), EQ(x, A2(A2(q)))], x, 'R4a')
  ```

  four variants (`R4a/R4b/R4bp/R4c`) covering the free/decoded sub-cases underneath the `v = u` case —
  i.e. the case table of §4 applied inside a single hole.

### (c) A decoded product inside a struct-decoded root

* **Symptom.** The chain shows **two or more** `[Rk]` products, and there is a rule for each one alone but
  none for the combination. Very often the trace's structural-hold list is non-empty but the `OPEQ` guard
  of that rule reads a `J`-shape that is now a decoded value.
* **Guard to add.** Replace the `J`-shape (`TG` + `EQ`) guard of the existing rule by the *other* rule's
  `OPEQ` guard — the conjunction rule. When several products can decode independently, verify **the whole
  chain** with one `OPEQ` per product instead of assuming any of them free.
* **Worked instances.**
  * **7701, `x = y ◇ (y ◇ ((x ◇ (z ◇ x)) ◇ y))`** (`gen/rules7701fix.py`): R2 covers "`z◇x` decoded",
    R3 covers "`(x◇(z◇x))◇y` decoded", neither covers both, so the top product fell through to `J y (J y p)`.
    R4 = R3 with the `J`-shape guard on `q2.2` replaced by R2's op-guard `q2.2 == op(x.1, x)`. Four rules,
    accepted (`certs/research_order5_hard_0094.lean`).
  * **40057, dual L-form `x = y◇(y◇(x◇((z◇x)◇y)))`** (`gen/rep40057.py`, `gen/rules6_40057.py`): the
    generated R1–R4 assume `E = op x P1` free; when `P1 = op P0 y` is itself a decoded payload of shape
    `J x (...)`, `E` decodes again and `x` is no longer at `a1 (a2 v)`. Repair = two rules that read
    `v = J u E`, `u = J P0 (J P1 u3)`, `P1 = J x _` and check `op x P1 = E`, `op P0 u = P1`, `P0 = op z x`.
  * **33020 / 12883** (`gen/fix33020.py`): each generated rule verifies only the one product it assumes
    fired and takes the rest free by shape — that is the hole. `R2full`/`R3full`/`R4full` verify `s1..s4`
    of the chain with an `OPEQ` each.
  * **6878, `x = y◇(y◇((z◇x)◇(x◇y)))`** (`gen/rep6878.py`): the six mutually exclusive cases of
    (`a = z◇x` free/decoded) × (`b = x◇y` free/decoded) × (`c = a◇b` decoded), three of which the generator
    never emitted.

### (d) A decoded inner product of the encoding on the root-pattern side (both-compound laws)

* **Where.** Laws with neither side a bare variable (24200 `x = ((y◇x)◇x)◇((x◇z)◇z)`, 23357, 23653, 21864,
  24199). For these `Extractor` has `lform = rform = False`, its mode list collapses to `['free','struct']`,
  and the decoded *root-side* nodes come from a separate choice, `choices[('RD',)]` — see
  `Extractor.unify_expr`'s `self.rdec` branch and `resolve_rdefer`. `rules()` enumerates `rdsets` = at most
  **two** root-side internal nodes at a time; tags carry `|rd:<paths>`.
* **Symptom.** The failing instance has the *encoding* built with an inner product that decoded — e.g.
  24200's `x = J(op(w, z'), z')`. Structural-hold list empty; the chain shows a decoded product on the side
  the extractor read structurally.
* **Guard to add.** An `OPEQ` on the root-side inner product instead of the `TG`/`EQ` structural reading —
  i.e. what `('RD',)` generates. First try widening the extractor's own enumeration (three RD nodes, or
  `level2` on top of RD); hand-write the rule only if that does not terminate.
* **Warning specific to this class.** Both-compound rule sets are large (24200: 15 rules; 13764: 82) and
  **must not be minimised by firing counts** — see §6. 24200 went 0 → 21 fails that way.

### Not a rule hole

`(e)` gate-cut readings and `(f)` quotient laws — §9.

---

## 5. Rule ORDER, and rules whose result is a nested `op`

* **`Closed.op` fires the FIRST matching rule**, and `leangen` emits the branches in the same order. So a
  repair rule placed too early can steal a pair from a rule that was already right. Two consequences:
  * **Append, then check.** Add new rules at the END, validate, reorder only if one needs priority — and
    then prefer making the *earlier* rule's guard stricter (an `OPEQ` instead of a `TG`) to moving the new
    one up: mutually exclusive guards are what the Lean proof needs anyway (each rule lemma has to refute
    the earlier branches).
  * **Keep the `free` rule first.** Every generated set starts with the purely structural R1 tagged `free`;
    `revalidate.py`'s minimiser refuses to drop it (`if r[2] == 'free': continue`). Leave it in place.
* **A rule may return a nested `op`.** `('OP', a, b)` is legal as a *result* expression, not only in guards
  (the payload is "whatever `op a B` decodes to" — the chain descent of 18137's model,
  `gen/rec18137b.lean`). `leangen` `let`-binds it like any other nested call and adds its gate to the
  branch condition, so it must satisfy the same rule: **gate it** — the pair `(a, b)` must be `msr`-below
  `(u, v)` on every real reading, or the branch falls through.
* **Every accessor must be `TG`-guarded** in the same rule (§2, the Lean-divergence note).
* **Keep sets small.** ≤ 8 rules is the working target for an L-form repair; each rule becomes a `P_k`, a
  branch, a rule lemma and a no-fire obligation in the proof. Both-compound laws are the exception.

---

## 6. Minimisation: validated removal only

**Never drop a rule because it "fired on one seed".** `closedform.minimise` keeps the rules that fired on a
single deep-test seed and re-checks once; that is how 24200 went from 0 fails to 21, and how 28626 lost a
rule that fires on 2 of 20,000 tests. **For both-compound laws (§4d) do not minimise at all — keep the full
set.**

The only sound procedure is *validated removal*: drop one rule, re-run the **full** validator, keep the drop
only if it still passes. Copy-pasteable (this is the loop `revalidate.py` uses, extracted so you can run it
on a hand-written set; verified on 9667, which correctly refuses to drop its recursive rule):

```python
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = <eq>
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
rules = <your rule list>

C = cf.Closed(law, rules)                       # firing counts, least-fired dropped first
cf.deep_tests(C, law, 1500, 120, 991)
order = sorted(range(len(rules)), key=lambda i: C.fired.get(i, 0))
keep = list(rules); dropped = []
for i in order:
    r = rules[i]
    if r[2] == 'free':
        continue
    trial = [q for q in keep if q is not r]
    if not trial:
        continue
    if rv.run_tests(law, trial, [3, 4, 5], 3000, 12000):      # non-empty = it broke something
        print('  KEEP  %-8s (fired %d)' % (r[2], C.fired.get(i, 0)))
        continue
    keep = trial; dropped.append(r[2])
    print('  DROP  %-8s (fired %d) -> %d rules' % (r[2], C.fired.get(i, 0), len(keep)))
print('minimised %d -> %d rules, dropped %s' % (len(rules), len(keep), dropped))
assert not rv.run_tests(law, keep, [77, 78], 3000, 12000), 'FRESH-SEED VALIDATION FAILED'
print('final validation on fresh seeds: 0 fails')
```

The final assert on **fresh seeds** is not optional: a set minimised against seeds `[3,4,5]` has been
selected on those seeds. `revalidate.py` falls back to the full set when this check fails; so should you.

---

## 7. The validation standard — verbatim, before any proof work starts

> 1. `rv.run_tests(law, rules, [3,4,5], 3000, 12000)` = 0 fails **and** `cf.deep_tests` 20,000 on two more
>    seeds = 0 fails, on the *dualised* law for R-form laws.

(`DEEP_SESSION_6_AUSTIN_HANDOVER.md`, "Testing protocol", item 1. Items 2–5 — compile against the row's
`JudgeProblem`, `squeeze.py`, one `judge1.py` call, `dualcert.py` — are proof-stage and out of scope here.)

What `rv.run_tests` actually runs, per call: exhaustive assignments over all terms of size ≤ 9 on one
generator and size ≤ 5 on two generators (`smallcheck.exhaustive`, limit 25 fails), then for each seed
`cf.deep_tests` (nested random triples), `fuzz.fuzz` (rule-shaped instances: each rule's own `u`/`v`
skeleton, `EQ` conditions imposed by copying, `OPEQ` guards satisfied by *computing* `op(P,Q)` and writing
it at the target — this is what manufactures derailment coincidences), `fuzz.closure_fuzz` (pool closed
under evaluations of the law's subpatterns and products) and `fuzz.critical_fuzz` (a variable rebuilt as an
encoding of the other variables' values, nested once or twice). It returns a list of
`(assignment, got, kind, seed)`; `got == 'recursion'` is evaluator depth, **not** a counterexample — filter
those out before concluding.

Also run, and report:

* your own coincidence-targeted instances (x/y/z built from the model's own encodings of each other) —
  every hole found so far has been of that shape. `gen/repair38249.py`'s `hand_instances()`/`targeted()` and
  `gen/rep6878.py`'s `hand_instances()` are the pattern to copy: name the case, build it, assert.
* `python smallcheck.py <eq> 9 1 --closed` and `<eq> 5 2 --closed` if you want the exhaustive part alone.

Do **not** use `gen/chk<eq>.py 3000` as evidence. It is one seed of `cf.deep_tests` on a possibly wrong law.

Cost, measured on 9667 (2 rules): `rv.run_tests(law, rules, [3,4,5], 3000, 12000)` = **6.1 s**;
`cf.deep_tests(..., 20000, 900, seed)` = **1.4 s**. Bigger sets are minutes, not hours (24200's full
`revalidate.py` pass is 122 s); 36524/10222's 2,400 s timeouts are extraction, not validation.

---

## 8. Emitting the repaired skeleton

From a **tiny script in `gen/`**. Never edit `leangen.py`, `closedform.py` or `fuzz.py`.

```python
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import revalidate as rv, leangen
# ... law, dualized, rules as in §1 ...
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
print('run_tests fails', len(fails))
if not fails:
    out = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rep%d' % EQ
    print(leangen.emit(EQ, out, rules_override=rules))
```

`gen/build38316.py` is the model of this script (it also prints `cf.show_rule` for each rule before
validating — do that, the rendered rule is what you will be proving about).

* Use an **absolute** `outdir` and a **fresh directory** (`gen/rep<eq>/`): `emit` writes `rec<eq>.lean`,
  `rules<eq>.txt` and `chk<eq>.py` into it, and pointing it at `gen/` would clobber the generated skeleton
  you may still want to diff against. Convention in this tree: emit to `gen/rep<eq>/`, then copy
  `gen/rep<eq>/rec<eq>.lean` up to `gen/rep<eq>.lean` for the proof work.
* `emit` returns `{'eq', 'dualized', 'nrules', 'fails_all', 'fails_kept', 'refuted', 'rows'}`. Check
  `refuted` is non-empty — it lists the goal ids for which `emit` found a refuting triple and wrote the
  `rhs` block. An empty `refuted` means the skeleton has no refutation and is not a certificate yet.
* Keep the original: `gen/rules9667_gen0.txt` / `gen/chk9667_gen0.py` is the convention for "the generator
  output that was refuted", and `gen/rules9667.txt` carries a one-line header saying so. Do the same, and
  name the script that refuted it.
* Verified round trip (2026-08-29): `leangen.emit(9667, '<abs>/gen/_pbrep9667', rules_override=keep)` →
  `['chk9667.py', 'rec9667.lean', 'rules9667.txt']`, `{'nrules': 2, 'fails_all': 0, 'fails_kept': 0,
  'refuted': [25964], 'rows': ['research_order5_hard_0071']}`.

Then the proof: `AGENT_BRIEF.md`. Report the repaired rule set **verbatim** under HOLES in the wave format.

---

## 9. When it is NOT repairable by a rule

Two dispositions, both decided by evidence, not by effort spent.

**Quotient law — the free magma is not a model at all.** Decisive signal: `trace.py`'s last line,
`SEMANTIC model: law FAILS too (got ...)`, or `python smallcheck.py <eq> 9 1` (the **semantic** free model,
no `--closed`) failing on small one-generator terms. Then the law derives an identity between distinct free
terms — 12073 derives `y◇(y◇(z◇z)) = ((y◇y)◇y)◇(z'◇z')` and then `K(S) = S` for squares — and **no rule set
can fix it**, because the rules only decide `op`, not the carrier. Signature in a `revalidate` report: fails
concentrated in `value:exh9/1` / `value:exh5/2` (e.g. 27859 `{'exh9/1': 23, ...}`, 22591 `{'exh9/1': 25,
'deep': 5, ...}`, 21865 with both exhaustive buckets saturated). Known members: 12073, 27859, 21865, 21866,
22591. These go to **Track C** (quotient carrier with tag constructors); stop and hand over with the
identified instances.

**Gate-cut law — a genuine reading below no admissible pair.** Signal: `trace.py` prints
`GATE CUT: op(...) at pair sizes (a,b) vs (u,v) sizes (p,q)` at the final product, *and*
`rules whose structural conditions hold` is non-empty (the shape is right; only the recursive guard is
unusable). Two moves before giving up:
1. **Express the guard structurally** — state the shape the encoding must have instead of asking `op`.
   That is exactly what the extractor's `~` (softdrop) variants are: `Extractor.rules(softdrop=True)` emits,
   *last in the order*, each struct-mode rule without its redundant evaluation guard, because the guard is
   implied by the structure whenever the inner products are free. Try those rules first.
2. **One level of structural expansion** buys one level of nesting; it does not close a family.

If the reading needs a *negative* constraint ("this pair is NOT a reading"), the DSL cannot express it —
6912's self-squaring family and 8485 are in this class. Stop and report the instance and the cut pair sizes.

**Extraction timeout is not a verdict.** 36524 and 10222 time out in `revalbatch` at 2,400 s during
*extraction* (the `level2` combination product). Cap `cap2` / the RD sets and re-extract; that is a Track B
task, not a repair.

---

## 10. Worked reproduction (do this once before trusting yourself on a new law)

Law **9667**, `x = y ◇ ((z ◇ y) ◇ (x ◇ (y ◇ y)))`, L-form. Both rule sets are on disk: the generated one in
`gen/chk9667_gen0.py`, the accepted repair in `gen/chk9667.py`. Scripts written for this playbook:
`gen/_pb_repro9667.py` (steps 1–3), `gen/_pb_trace9667.py` (the trace of §3), `gen/_pb_minemit9667.py`
(the §6 loop and the §8 emit).

```
$ python gen/_pb_repro9667.py step1
GENERATED      nrules=2  run_tests fails=1 (value fails=1) {"value:deep": 1}  6.1s
   FAIL[deep seed 3] {'y': '(g0*((((g1*g2)*(g0*(g2*g2)))*...', 'z': '((g1*g2)*(g0*(g2*g2)))', 'x': '(g2*g2)'}

$ python gen/_pb_repro9667.py step2
step2: op(z,y) = (((g1*g2)*(g0*(g2*g2)))*((g1*g2)*(g0*(g2*g2))))  (decoded, so y.1 = op(q,z) is NOT free)
step2: law under GENERATED rules holds? False
step2: law under REPAIRED  rules holds? True

$ python gen/_pb_repro9667.py step3
REPAIRED       nrules=2  run_tests fails=0 (value fails=0) {}  6.2s
REPAIRED  cf.deep_tests 20000 tested, 0 fails, 1.4s
```

Note the size of the signal: **one value fail out of 3 seeds × (3,000 deep + 3 × 12,000 fuzz) plus the
exhaustive pass.** That is why the standard in §7 is what it is, and why `chk<eq>.py 3000` proves nothing.

`gen/_pb_minemit9667.py` then runs the §6 loop (`KEEP B0l2 (fired 28) — removal breaks the validator`,
2 → 2 rules, fresh-seed validation 0 fails) and the §8 emit.

---

## 11. Checklist

1. Rebuild `law` yourself with the `dualized` test; take only `rules` from `chk<eq>.py`. (§1)
2. `rv.run_tests(law, rules, [3,4,5], 3000, 12000)` — confirm it really fails, and on `value:*`, not
   `recursion:*`. (§7)
3. `python trace.py <eq>` — read the chain, the structural-hold list, the GATE CUT lines and the SEMANTIC
   line. (§3)
4. Quotient or gate-cut? Stop and hand over. (§9)
5. Otherwise write the case table of "which products fired", find the missing cell, classify it (a)–(d),
   add or re-aim the guard through a provably free occurrence. (§4)
6. Append the rule; keep every accessor `TG`-guarded; gate every nested `op`, results included. (§2, §5)
7. Re-validate to the §7 standard on 3 seeds, plus your own coincidence instances. (§7)
8. Minimise by validated removal only, never for both-compound laws, with a fresh-seed assert. (§6)
9. `leangen.emit(EQ, '<abs>/gen/rep<eq>', rules_override=rules)` from a tiny script in `gen/`; check
   `refuted` is non-empty. (§8)
10. Report the repaired rule set verbatim, with the instance that refuted the generated one and the
    one-sentence statement of what the old guard read and what the new one reads.

---

## 12. ORCHESTRATOR ADDENDUM (added mid-session, read this)

`gen/SEMANTIC_TABLE.md` now holds the measured semantic-vs-extracted table for EVERY open law, plus the
correction that the `revalidate.py` timeouts are a validation cost, not an extraction blow-up
(extraction is 0.2-0.3 s; the rule sets are 83-218 rules). Read it before you decide your law's track.
Notable reclassifications: 9663/36487, 10222/35836 and 12294 fail SEMANTICALLY and cannot be fixed by any
rule set; 32281, 33020/12883 and 34889 are the opposite — clean semantically, so they are extractor holes.
