# EXTRACTOR NOTES — `gen/closedform2.py`, a strictly better `closedform.Extractor`

Written 2026-08-29 by the EXTRACTOR agent. **`closedform.py` is untouched.** Everything below lives in
**`gen/closedform2.py`**, a drop-in replacement for `closedform` *for extraction*; the evaluator (`Closed`,
`deep_tests`, `msr`, `gate_ok`, the whole rule DSL) is byte-identical to `closedform.py`, so a rule set
extracted here goes into `leangen.emit`, `revalidate.run_tests`, `fuzz`, `trace.py` and the Lean generator
unchanged.

**Headline.** Four defects found and fixed, all generic (no per-law hacks):

1. the decoder variable was **hardcoded as the literal name `'y'`** — wrong for every law whose bare side is
   not called `y`, i.e. 32281, 34889, 40037;
2. the rule list was never **subsumption-pruned** — rule counts roughly halve, and it is the rule count, not
   `cap2`, that causes `revalidate.py`'s 2,400 s timeouts;
3. the **decoder occurrence** in the encoding was always the first one — the generic form of the hand repair
   `PLAYBOOK_REPAIR.md` §4(a) does per law;
4. the **`softdrop` (`~`) rules are not always sound**; a soundness filter against the semantic free model
   removes the bad ones.

Concrete effect measured with the full validator (`revalidate.run_tests`, 3 seeds, deep 3000, fuzz 12000,
plus the exhaustive one- and two-generator sweeps): **32281 goes 42 value fails → 0** and **33020 goes 1 → 0**,
both with fewer rules; **34889's 8 wrong small pairs → 0**; nothing regresses.
`gen/xrep32281/` is an emitted, fully-validated package for 32281 (3 rows).

---

## How to use it (one line)

```python
import sys; sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform2 as cf2
rules, info = cf2.extract(law)          # rules() + the soundness filter; info tells you what was dropped
# or, without the filter:               rules = cf2.Extractor(law).rules()
```

`law` is built exactly as in `PLAYBOOK_REPAIR.md` §1 (the `dualized` dance — unchanged).

* `revalidate.run_tests(law, rules, [3,4,5], 3000, 12000)` already takes `rules` as an argument, so it needs
  no change. If you want `revalidate`'s *whole* pipeline on the new extractor, set `rv.cf = cf2` after
  importing it.
* `leangen.emit(EQ, '<abs>/gen/rep<eq>', rules_override=rules)` needs **no change at all** — it only uses
  `Closed`, which is identical.
* The rule DSL, the gate, rule order semantics and the Lean mirror are all exactly as `PLAYBOOK_REPAIR.md`
  §2 and §5 describe. Nothing you know changes.

Helper scripts, all in `gen/`, all safe to copy:

| script | what it does |
| --- | --- |
| `_xt_opdiff.py <eq> --maxsize 7 --gens 2` | **the sharp measurement**: enumerate every pair `(u,v)` of free-magma terms up to a size and print where the SEMANTIC free model and the EXTRACTED rule system disagree. Names the missing mode without going through a law failure — this is how both holes below were found, in seconds |
| `_xt_diag.py <eq>` | full validator on a package, then replay the smallest failing instance's evaluation chain in both models side by side; the first `<<< DISAGREE` is the hole |
| `_xt_class.py <eq>` | same, but splits failures into SEMANTIC (the free model fails too — quotient law, unfixable by rules) and HOLE (extractor) |
| `_xt_bench.py <eqs> --mods closedform,closedform2,closedform2+sound` | before/after: extract fresh with each module and run the full validator |
| `_xt_prunecheck.py <eqs>` | differential test that the subsumption step is behaviour-preserving |
| `_xt_sweep.py <eqs>` | cheap deterministic op-diff count per law for old / new / new+sound, split into WRONG (a rule fired and returned the wrong value) and HOLE (no rule fired) |
| `_xt_cost.py`, `_xt_cost2.py` | extraction cost vs `cap2`; validation cost vs rule count |
| `_xt_ship.py <eq>` | validate to the FULL handover standard and, if it passes, `leangen.emit` into `gen/xrep<eq>/` |

---

## FIX 1 — the decoder variable was hardcoded as the literal name `'y'`

`closedform.decoder_expr` reads

```python
pat = self.B if self.lform else self.A
path = self.path_to('y', pat)          # <- the literal string 'y'
```

and `decoder_of` ends with `return r.get('y')`. The decoder is the variable on the **bare side** of the law
(`self.A` for an L-form law, `self.B` for an R-form one), and after `normalise` + `leangen.dual_pat` that
variable is **not always called `y`**. Measured over 36 laws of the research set it is `'z'` for exactly
**32281, 34889 and 40037** — all three dualised. For those three, every lazy-decode rule looked for the
decoder at the position of an unrelated variable.

`closedform2` records `self.decvar = self.A if self.lform else (self.B if self.rform else None)` and uses it
in both places; when the decoder does not occur in the encoding at all, `decoder_expr` raises `Infeasible`
instead of crashing on `path = None`.

**Worked instance (32281).** L-form (dualised) law `x = z ◇ ((z ◇ ((x ◇ y) ◇ y)) ◇ y)`, so `decvar = 'z'` at
encoding path `(0,0)`, while `path_to('y', B) = (0,1,0,1)`. `python gen/_xt_diag.py 32281`:

```
{"eq": 32281, "nrules": 26, "fails": 134, "kinds": {"deep":21,"fuzz":13,"closure":39,"critical":61}}
SMALLEST FAIL critical {'z': 'g2', 'x': 'g3', 'y': '((g3*((g3*g1)*g1))*g1)'}
  ('x','y')                closed=g3            free=g3            OK
  (('x','y'),'y')          closed=g3            free=g3            OK
  ('z',(('x','y'),'y'))    closed=(g2*g3)       free=(g2*g3)       OK
  ((...),'y')              closed=((g2*g3)*..)  free=((g2*g3)*..)  OK
  ('ROOT',)                closed=(g2*((g2*g3)*..))  free=g3       <<< DISAGREE
```

The root pair needs `op(z', op(u, x')) = w` with the decoder `z'` read out of `v`'s own structure; with the
`'y'` path the rule looks in the wrong subterm. Under `closedform2` the same instance evaluates to `g3`.

## FIX 2 — subsumption pruning of the emitted rule list (`prune`)

`closedform.rules()` ends with a dedup keyed on `(tuple(conds), result)` — order-sensitive, and blind to
rules that can never fire. `closedform2.prune` does

1. exact dedup on the condition **set** (`Closed.check` sorts the conditions, so their order is not
   semantics), then
2. **subsumption**: drop rule *j* when an **earlier** rule *i* has `conds_i ⊆ conds_j` and the **same result
   expression**. Every pair satisfying *j* satisfies *i*; `Closed.op` tries *i* first; `ev` is a pure
   function of the expression and the pair, so the same result expression evaluates identically (including
   to `None`). *j* is therefore unreachable.

Behaviour-preserving by that argument and by differential test (`gen/_xt_prunecheck.py`, dedup-only vs
dedup+subsumption, compared on every pair of terms of size ≤ 7 over 2 generators plus the rule-shaped fuzz
pairs of the full set): **0 differences** on every law tried, e.g. 10222 292 → 152, 12294 282 → 132,
6878 118 → 44, 39163 142 → 60, all with 0 differences over 1,500 pairs each.

Rule counts (`Extractor.rules()` only, no soundness filter), before → after:

| law | before | after | | law | before | after |
| --- | --- | --- | --- | --- | --- | --- |
| 10222 | 168 | 88 | | 12234 | 169 | 84 |
| 12294 | 218 | 141 | | 39163 | 100 | 26 |
| 10218 | 140 | 79 | | 6878 | 98 | 30 |
| 35836 | 168 | 88 | | 9667 | 87 | 50 |
| 36524 | 97 | 60 | | 8485 | 83 | 55 |
| 13764 | 82 | 67 | | 5837 | 32 | 15 |
| 32294 | 82 | 67 | | 38565 | 30 | 12 |
| 9663 | 82 | 47 | | 11081 | 32 | 26 |

(Those are with `decocc=False`; with FIX 3 on, the counts sit between — see the final table below.)
Both-compound laws (24200, 23354, 28626, 17286, 18137, 23357, 21864, 24199) are unchanged.

This matters twice: `revalidate.py`'s minimiser is **quadratic in the rule count** (FIX 5 below), and every
rule is a `P_k`, a branch, a rule lemma and a no-fire obligation in the Lean proof.

## FIX 3 — the decoder occurrence is a choice, not always the first one

`decoder_expr` walked `path_to(decvar, encoding)`, i.e. the **first** (deepest-left) occurrence. A law can
have the decoder variable at several positions in its encoding, and the first is very often the one *inside*
a node that itself decodes — exactly the hand repair `PLAYBOOK_REPAIR.md` §4(a) documents for 9667 and
40057 ("re-locate the decoder to an occurrence that every firing rule guarantees").

`closedform2` computes `self.decpaths` and makes the occurrence a choice dimension
`choices[('DECOCC',) + path] = index`, enumerated by `rules()` over the (at most two) nodes that used a lazy
decode. Tags carry `|dec:<indices>`. Turn it off with `X.rules(decocc=False)`.

**Ordering is deliberate: candidate 0 is `closedform.py`'s legacy `path_to('y', ...)` position whenever
that is a real position**, so occurrence 0 reproduces the old extractor exactly and nothing that worked
before can be lost; the true decoder occurrences are the `|dec:k` alternatives. That matters — with the
decvar occurrence as candidate 0, **40037 regressed** from 0 value fails to 1 (its closed form then follows
the semantic free model, which itself fails on that one instance). A wrong decoder position only makes a
rule fire *less* often (the `OPEQ` guard still certifies the reading), so extra candidates are safe.

**Worked instance (33020).** L-form (dualised) law `x = y ◇ ((x ◇ (z ◇ (y ◇ x))) ◇ y)`; `decvar = 'y'` occurs
at `(0,1,1,0)` (inside the decoded node) and at `(1,)` (the shallow, provably free one). `closedform.py` only
ever emits the first — the `op(u, v.1.1).1.2.2.1` accessor of the shipped package's R3. On
`{y=(g0*g0), x=z=(g0*(g0*(g0*g0)))}` the root product needs the decoder at `op(u, v.1.1).2`; no rule has that
shape, the closed form leaves the root free and the semantic model reads `x`. `closedform2` emits the
`|dec:1` variant and the instance passes.

Occurrence counts: 1 for 12087; 2 for 32281, 33020, 12883, 34889, 40037, 8485, 10218, 11081, 12234, 12294,
6878; 3 for 13764, 10222, 36524, 5837, 9667, 39163; 0 for the both-compound laws.

## FIX 4 — the `softdrop` (`~`) rules are not always sound; filter them

`rules(softdrop=True)` emits, last in the order, each struct-mode rule **without** its evaluation guard, on
the stated theory that "the guard is implied by the structure whenever the inner products are free". That is
false in general. Measured on **34889** (`x = ((y◇y)◇((x◇z)◇x))◇z`, dualised, L-form dual
`x = z ◇ ((x ◇ (z ◇ x)) ◇ (y ◇ y))`): the rule

```
[B0l~] J?v & J?v.2 & v.2.1 = v.2.2 & J?u & v.1 = u.1 & J?u.2 & v.1 = u.2.2 & J?u.2.1 & u.2.1.1 = u.2.1.2 -> u.2.1
```

fires on `u = (g0*((g0*g0)*g0))`, `v = (g0*(g0*g0))` and returns `(g0*g0)` where the free model has the free
product — **8 such pairs among terms of size ≤ 7 over ≤ 2 generators**. Its guarded twin `B0l` (which adds
`op(u.2.1, op(u, u.2.1)) == v.1`) is the correct rule and is tried first, so the `~` variant only ever fires
where the guard *failed*, i.e. exactly where it must not fire.

`closedform2.drop_unsound(law, rules)` (used by `cf2.extract`) evaluates the rule system against
`freemodel.Free` on every pair of terms of size ≤ 7 over 2 generators and greedily drops the rule that fires
wrongest, re-checking after each drop. It only ever drops a rule that **fires and returns the wrong value**;
a pair where *no* rule fires and the free model reads a value is a missing mode, not an unsound rule, and is
reported separately as `small_pair_holes`. Softdrop rules exist to recover gate-cut readings (6912), so they
stay on by default and are filtered here rather than switched off.

On 34889: `{"nrules0": 4, "nrules": 3, "dropped": ["B0l~"], "small_pair_holes": 0}`, and the op-diff count
goes 8 → 0. No other law in the set loses a rule.

## FIX 5 — where the 2,400 s `revalidate.py` timeout actually goes

**The handover's diagnosis was wrong.** `PLAYBOOK_REPAIR.md` §9 and the Track-B note say the 10222 / 36524
timeouts are *extraction* and that `cap2` / the RD sets are the combinatorics to cap. Measured
(`gen/_xt_cost2.py 10222`; the box was under heavy multi-agent load, so read ratios, not absolutes):

| module | `cap2` | rules | extract |
| --- | --- | --- | --- |
| closedform | 1 | 61 | 0.46 s |
| closedform | 8 | 112 | 0.49 s |
| closedform | 64 | 168 | 0.79 s |
| closedform | 256 | 219 | 1.05 s |
| closedform | 1024 | 219 | 1.40 s |
| closedform2 | 1 … 1024 | **152 (flat)** | 0.61 … 1.76 s |

Extraction of the worst law in the set is **under two seconds at any `cap2`**, and with subsumption the rule
count stops depending on `cap2` altogether (every extra level-2 rule is subsumed). **`cap2` is not the knob;
capping it buys nothing and loses rules.**

The cost is `revalidate.py`'s validate-then-minimise loop: `run_tests` is ~linear in the rule count (every
`Closed.op` call walks the rule list) and the minimiser calls `run_tests` **once per rule**, so the pass is
**quadratic in the rule count**. Measured on 10222 at a deliberately small budget (1 seed, deep 400,
fuzz 1200 — the real `revalidate.py` default is 3 seeds × deep 3000 × fuzz 12000, ~25× more):

| rules | `run_tests` | minimiser ≈ rules × run_tests |
| --- | --- | --- |
| 10 | 14.5 s | ~145 s |
| 20 | 32.7 s | ~654 s |
| 40 | 60.4 s | ~2,415 s |
| 80 | 131.4 s | ~10,515 s |
| 168 | 269.6 s | **~45,290 s** |

168 rules is 10222's `closedform` count, and ~45,000 s at 1/25 of the real budget is why it never returns.
**The fix for the timeout is fewer rules, which is FIX 2** — and `X.rules(decocc=False)` if you want only the
cost win: 10222 168 → 88, 36524 97 → 60.

---

## Before / after table

Full validator = `revalidate.run_tests` (exhaustive terms ≤ 9 over 1 generator and ≤ 5 over 2, then deep +
rule-shaped fuzz + closure fuzz + critical fuzz per seed). `value fails` excludes `recursion`.
Budget for this table: 1 seed, deep 1000, fuzz 3000 (32281's and 33020's rows re-measured at 2 seeds /
deep 2000 / fuzz 6000 and at the full 3 seeds / 3000 / 12000 — see below). Box under heavy multi-agent load,
so seconds are indicative only.

| law | `closedform` rules → value fails | `closedform2` rules → value fails | verdict |
| --- | --- | --- | --- |
| **32281** | 36 → **42** | 18 → **0** (25 with legacy-first ordering) | **FIXED** (FIX 1) |
| **33020** | 31 → **1** | 19 → **0** | **FIXED** (FIX 3) |
| **12883** (dual of 33020) | 31 | 19 | same model, same fix |
| **34889** | 4 → 33 | 4 → 33; **3 → still fails** with FIX 4 | small-pair op-diffs 8 → **0**; the residue is SEMANTIC (see below) |
| **40037** | 6 → 0 | 6 → 0 | unchanged (legacy-first ordering keeps it) |
| 12087 | 13 → 0 | 11 → 0 | no regression, 2 fewer rules |
| 11081 | 32 → 0 | 22 → 0 | no regression, 10 fewer rules |
| 24200 (both-compound) | 15 → 0 | 15 → 0 | untouched by design |
| 8485 | 83 → 0 | 38 → 0 | no regression, 45 fewer rules |
| 10218 | 140 → 0 | 63 → 0 | no regression, 77 fewer rules |

Full-standard runs (handover testing protocol item 1 — `run_tests` on seeds [3,4,5] with deep 3000 /
fuzz 12000, then `deep_tests` 20,000 on two further seeds):

* **32281, 18 rules: 0 value fails, 20,000/0 and 20,000/0 → PASS.** Emitted to
  **`gen/xrep32281/`** (kept also as `gen/xrep32281_18rules/`), `refuted = [41082, 15535, 17522]`,
  rows **research_order5_hard_0006, _0032, _0068**. This package is ready for a proof agent.

The cheap op-diff sweep (`gen/_xt_sweep.log`, every pair of terms of size ≤ 7 over 2 generators, per law:
WRONG = a rule fired and returned the wrong value, HOLE = no rule fired where the free model reads a value)
is the fastest regression check for any future extractor change.

## What is still missing (measured, for the next agent)

* **34889 is a Track-C law, not a Track-B one.** After FIX 4 the rule set has **0** disagreements with the
  semantic free model on all pairs of terms of size ≤ 7 over 2 generators, and of the 25 smallest remaining
  validator failures **every single one is also a failure of the semantic free model** (`gen/_xt_class.py`
  classification). So the free magma is not a model of 34889 and no rule set can fix it — it needs the
  quotient carrier of Track C. `smallcheck.py 34889 9 1` (semantic) already showed 2 fails; the deep and
  closure buckets show the same thing at scale.
* **The existential decoder for both-compound laws is still not implemented.** For a law with neither side
  bare, `Extractor.rules` still collapses `modes` to `['free','struct']` (`lform = rform = False`), so
  `lazy`, `vdec` and `exist` are all unreachable and the decoded root-side nodes come only from
  `choices[('RD',)]` (at most two nodes at a time). 23357 / 23653 / 21864 / 24199 need it. I did not
  implement it because no failing instance in *my* laws demanded it and the handover is explicit that a mode
  must be driven by an instance; the next agent should start from
  `python gen/_xt_opdiff.py 21864 --maxsize 7 --gens 2 --extract` and read off the missing shape.
* **Nested-`op` results (chain descent) already work** — `('OP', a, b)` is legal as a result and `val()`'s
  `vdec` mode produces it; `one_rule` only rejects results containing an unresolved placeholder. So the
  handover's item (ii) is not a missing capability of the DSL or of `one_rule`; what is missing is a mode
  that *chooses* to produce a nested-op result at a non-`vdec` node.
* **A defect I did not fix**: `revalidate.py`'s minimiser is quadratic (FIX 5). With `closedform2` counts the
  big laws are now feasible, but a linear-ish minimiser (batch removal, or removing only rules that never
  fired across the *whole* regression pool and re-validating once) would be worth more than any further
  extraction work on 10222 / 12294 / 35836.
