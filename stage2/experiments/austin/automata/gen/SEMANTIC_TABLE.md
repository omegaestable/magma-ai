# SEMANTIC free-model table — the FIRST thing to check about a law

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
* **32281 (3 rows), 33020 / 12883 (3 rows), 34889 (3 rows) are the opposite case**: the semantic model is
  clean (0, 0, 2) while the extracted rule set fails 134, wholly, and 192 times. Pure extractor holes.
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
