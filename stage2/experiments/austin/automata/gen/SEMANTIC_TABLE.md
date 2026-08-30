# SEMANTIC free-model table — the FIRST thing to check about a law

> ## CORRECTION 2026-08-29 (deep session 8): the Track C inference below is INVALID as stated.
>
> **"Semantic free-model failure ⟹ no rule set can fix it, the carrier must change" does not follow.**
> `freemodel.Free`'s reading search is **incomplete**, so its failures can be ordinary decoder holes.
> Measured: **9663 / 36487 (3 rows) and 12294 (1 row) force NO identity at all** and are Track B — both
> now have validated free-carrier models. They were filed Track C here on 23 and 22 semantic failures.
>
> **The test that actually decides it is `gen/_id_query.py`** (ground congruence closure over hash-consed
> free terms, asserting `RHS(x,y,z) ~ x` over a growing pool, reporting classes whose two smallest members
> are distinct free terms of the same size). **Every merge is a sound consequence of the law, so a hit is a
> proof**, and a miss over a large pool is strong evidence of none. It finds `a*a = b*b` at size 3 for
> 12073 and 27859 unprompted, and 10222's identity at size 9; it finds **0** for 9663, 36487 and 12294
> over 689,386 / 2,209,526 congruence nodes. **~5 s per law**: `python gen/_id_query.py <eq> 3 2 2 5`.
>
> **Run it on every law still filed Track C below before building a carrier for it.** Confirmed Track C so
> far: 12073, 27859, 34889 (squares), 10222/35836 (`(a*a)*((z*a)*a)` is z-independent — and its tag must be
> **unary**, because `K a ◇ (a◇a) = a` makes `K` injective), and 22591 (`a = I3(a)`, proved by hand in
> `gen/P2_EXISTENTIAL_DECODER.md`). **Unchecked and therefore unclassified: 21865, 21866, 24199, 36487's
> partner rows, and every law marked "pending".**

`python smallcheck.py <eq> 9 1` evaluates the law on all 12,167 one-generator terms of size <= 9 in the
SEMANTIC free model (`freemodel.Free`) — the mathematical object, NOT the extracted rule system.
`--closed` does the same in the extracted rule system. The two differ, and the difference decides the track:

* semantic 0 fails, extracted fails  -> the extractor is incomplete. Repairable with rules. TRACK B.
* semantic fails on one-generator terms -> the law derives an identity between distinct free terms.
  NO rule set can fix it; the carrier must change. TRACK C.

Measured 2026-08-29 (deep session 7), open laws only. Column = semantic fails at 1 generator, size <= 9.

| law | fails | class |
| --- | --- | --- |
| 5837 | 0 | EXTRACTOR HOLE (Track B) |
| 6912 | 1 | near-clean, 1-2 instances |
| 8485 | 0 | EXTRACTOR HOLE (Track B) |
| 9663 | 23 | IDENTITY LAW (Track C) |
| 10218 | 0 | EXTRACTOR HOLE (Track B) |
| 10222 | 45 | IDENTITY LAW (Track C) |
| 11081 | 0 | EXTRACTOR HOLE (Track B) |
| 12073 | 23 | IDENTITY LAW (Track C) |
| 12087 | 0 | EXTRACTOR HOLE (Track B) |
| 12234 | 0 | EXTRACTOR HOLE (Track B) |
| 12294 | 22 | IDENTITY LAW (Track C) |
| 12883 | 0 | EXTRACTOR HOLE (Track B) |
| 13764 | 0 | EXTRACTOR HOLE (Track B) |
| 17286 | 0 | EXTRACTOR HOLE (Track B) |
| 21864 | 5 | near-clean, 1-2 instances |
| 21865 | 68 | IDENTITY LAW (Track C) |
| 21866 | 18515 | IDENTITY LAW (Track C) |
| 22591 | 46 | IDENTITY LAW (Track C) |
| 23354 | n/a | pending |
| 23357 | n/a | pending |
| 23653 | n/a | pending |
| 24199 | 230 | IDENTITY LAW (Track C) |
| 24200 | 0 | EXTRACTOR HOLE (Track B) |
| 27859 | 13 | IDENTITY LAW (Track C) |
| 28626 | n/a | pending |
| 32281 | 0 | EXTRACTOR HOLE (Track B) |
| 32294 | 0 | EXTRACTOR HOLE (Track B) |
| 33020 | 0 | EXTRACTOR HOLE (Track B) |
| 34889 | 2 | near-clean, 1-2 instances |
| 35036 | 0 | EXTRACTOR HOLE (Track B) |
| 35836 | 45 | IDENTITY LAW (Track C) |
| 36487 | 23 | IDENTITY LAW (Track C) |
| 36524 | n/a | pending |
| 38316 | n/a | pending |
| 38565 | 0 | EXTRACTOR HOLE (Track B) |
| 39163 | n/a | pending |
| 39214 | 1 | near-clean, 1-2 instances |
| 40037 | 1 | near-clean, 1-2 instances |

## What this changes versus the handover

* **9663 / 36487 (3 rows) are NOT a repair task.** Both fail semantically (23 instances each). The
  handover filed them as "49 rules with a single fuzz failure"; that is the extracted system agreeing with
  a model that is itself wrong. They belong with 12073 / 21865 / 22591 / 27859.
* **10222 / 35836 (2 rows) and 12294 (1 row) likewise fail semantically** (45, 45, 22). Their
  `revalidate.py` timeouts are a separate and smaller problem (below).
* **32281 (3 rows) and 33020 / 12883 (3 rows) are the opposite case**: the semantic model is clean (0 and
  0) while the extracted rule set fails 134 times and wholly. Pure extractor holes. 33020's rows 0012 and
  0054 are **SHIPPED** (2026-08-29).
* **34889 is NOT an extractor hole, and this file used to say it was.** Its two semantic failures are
  genuine and forced: `op((g0*g0), ((g0*((g0*g0)*g0))*(g0*g0))) = g0` is literally
  `L[x := g0, y := g0, z := (g0*g0)]`. The law derives, in three literal instantiations,
  **`(g*g)*(g*g) = g*g` -- every square is idempotent** -- so it is a Track C identity law and wants a
  carrier, not rules. All three rows are **SHIPPED** (2026-08-29) on the E-quotient carrier.

  **The generalisation, and it is the most useful line in this file:** the E-quotient carrier is NOT
  limited to the 12073 / 27859 family. Those two force *all squares equal and idempotent*; 34889 forces
  only *squares are idempotent*, which is strictly weaker -- and collapsing every square to one 0-ary
  constant `E` is nevertheless consistent with it. So for every law still listed above as **near-clean,
  1-2 instances -- 6912 (1), 21864 (5), 39214 (1), 40037 (1) -- derive the forced idempotence or square
  identity BEFORE any further extractor work.** 34889 went from "2 semantic failures" to three accepted
  certificates in about two hours once that question was asked.
  (Not universal: `PLAYBOOK_QUOTIENT.md` §4 proves square collapse forces the trivial magma for 22591, and
  `gen/P2_EXISTENTIAL_DECODER.md` R1 proves 22591 makes *every* element a square, which rules the carrier
  out there. Derive the forced identity first; do not assume either way.)
* **"near-clean, 1-2 instances" IS NOT A CLASS — it is Track C with big witnesses.** Three laws filed in
  that bucket have now been resolved and **all three are Track C identity laws**: 34889 (2 fails) forces
  *every square is idempotent* and shipped 3 rows on the E-quotient carrier; **6912 (1 fail) forces
  `(a*a) = ((a*a)*(a*a))` and then `(b*b) = (a*a)` — ALL SQUARES EQUAL** (mechanically verified,
  `gen/_x6912_derive2.py`), so the free term algebra is refuted over ≥ 2 generators; **39214 (1 fail) is
  6912's dual** and inherits all of it. **A low semantic-failure count means the witnesses are BIG, not
  that the carrier is nearly right.** 6912's 2-generator witnesses need terms of size ≥ 9, which is why
  `smallcheck 6912 5 2` reads 0 fails and `trace.py 6912 --n 400` reads "no failure found" — neither is
  evidence of a working model at this scale.
  **So 21864 (5) and 40037 (1) must get the `gen/_x6912_derive2.py`-style substitution derivation before
  any rule work.** Note the E-quotient is *not* automatic even when a square identity is forced: for 6912
  it is refuted by a forced collision (`op(q,t) = E ⟹ q = t` is forced, and two witnesses of its failure
  are forced too), and for all seven P2 laws substituting every variable by `x` gives `x = W*W`, so
  all-squares-equal trivialises. Derive, then test the carrier; assume neither.
* **21864 vs 24199**: 5 semantic fails against 230. Orientation matters — work the 21864 side.
* **21866 is in a class of its own**: 18,515 fails at one generator and 7,744 at two.

## The `revalidate.py` timeout is NOT an extraction blow-up

Measured directly this session. `Extractor.rules(exist=False)` costs **0.2-0.3 s** on every one of the five
laws whose `revalidate.py` run times out (10222, 36524, 12294, 10218, 8485). What it returns is 83-218
rules, and `Closed.op` is O(rules) with an expensive guard check, so a single deep test costs 25-63 ms and
the full validator (12,167 exhaustive assignments + 3,000 deep + 12,000 fuzz + closure + critical), run
again inside the minimiser and again for `exist=True`, is what runs for 40 minutes.

So do NOT cap `level2` / `cap2` to fix this. Invert the pipeline instead: extract, minimise against a CHEAP
validator, then run the full validator ONCE on the small set. `gen/_orch_minim.py <eq> [N] [--full]`
implements exactly that (bulk-drop the never-fired rules, then validated removal, then the full validator).

| law | extract s | rules extracted | ms per deep test |
| --- | --- | --- | --- |
| 10218 | 0.2 | 140 | 25 |
| 8485 | 0.2 | 83 | 27 |
| 12294 | 0.3 | 218 | 55 |
| 10222 | 0.3 | 168 | 40 |
| 36524 | 0.3 | 112 | 63 |

All five pass 200 deep tests with 0 failures at the full rule set, so the models are plausibly right and
merely enormous.
