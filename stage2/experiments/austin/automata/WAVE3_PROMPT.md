# Wave-3 prompt (2026-08-29 deep session 8) — delta over WAVE_PROMPT.md and WAVE2_PROMPT.md

Read in this order, in full:
1. `WAVE_PROMPT.md`  (wave rules + the verbatim REPORT FORMAT — you must use it)
2. `AGENT_BRIEF.md`  (the method)
3. `gen/PLAYBOOK_PROOF.md`  (the Lean method; **§3 is mandatory if your model has > 8 rules**)
4. `WAVE2_PROMPT.md` (validation-before-proving; banned tokens)
5. one accepted certificate in full: `certs/research_order5_hard_0059.lean` (5295) or
   `certs/research_order5_hard_0001.lean` (24200)

## What is different in wave 3

**W3-1. HARVEST BEFORE YOU GENERATE (rail 47).** Session 7 wrote several proofs that were finished and then
filed as "unshippable" because they were over the 20,000-byte cap or had one sorry left. A proof that is
over the cap is a FINISHED proof, not a failed one. Your FIRST action, before any model work:
```bash
cd stage2/experiments/austin/automata
ls -l gen/*<your eq>*.lean gen/*<your dual eq>*.lean
for f in gen/*<your eq>*.lean; do echo "$f $(wc -c <$f) sorries=$(grep -c sorry $f)"; done
```
Read every one of them. If one is zero-sorry, compile it (`D=<dev dir> bash devlean2.sh <file>` and grep the
output for `error:`) and go straight to squeezing + judging. If one has 1-2 sorries, finish those sorries
rather than starting over.

**W3-2. WRITE AS YOU GO.** Append every finding to `gen/NOTES_<your eq>.md` the moment you have it — the
failing instance, the lemma that worked, the byte count, the exact remaining goal. Do not save findings for
your final report. If you are killed at 80% the next agent must be able to resume from that file.

**W3-3. Decide the track before proving (technique (i)).**
`python smallcheck.py <eq> 9 1` = semantic free model; `--closed` = the extracted rule system.
Semantic 0 fails + extracted fails ⇒ extractor hole, repairable with rules (Track B).
Semantic fails ⇒ no rule set can help; STOP and report — that is a carrier problem, not yours.
`gen/SEMANTIC_TABLE.md` already has this for every open law; re-run it for yours to confirm.

**W3-4. Minimise before you prove, always.** Cost is 530-780 B per rule on top of ~2,171 B of fixed
boilerplate, against a 20,000 B cap. `gen/_orch_minim.py <eq> [N] [--full]` does extract → bulk-drop
never-fired rules → validated removal → full validation. Do this BEFORE writing a single lemma.

**W3-5. Byte tools, in order:** drop dead rules → `gen/PLAYBOOK_PROOF.md` §3 digest (`TRpre` + `Pdig` +
`Wdig`; it took a 24-rule model to 1,913 B) → `python squeeze.py in.lean out.lean --rename`.
**After ANY squeeze you MUST recompile** (`--rename` silently broke a file this session: 0 → 28 errors).
`macro` is a BANNED TOKEN — never define a tactic macro to save bytes.

**W3-6. Validation standard (it has risen four times; a sampler cannot find a cell of measure zero).**
`rv.run_tests(law, rules, [3,4,5], 3000, 12000)` must be EMPTY, then `cf.deep_tests` at 20,000 on >= 3 seeds,
then **the case tree**: enumerate the `2^k` free/decoded combinations of the `k` products in the law's own
evaluation chain and construct one instance per reachable cell by chained encoding (to force `op(a,b)` to
decode, set `b` to the free encoding of the law's RHS with `y := a`; nest for a second). Worked example:
`gen/_x38565_dd.py`. Law 38565 passed 9 seeds of `run_tests` and 13 x 20,000 deep tests and was still FALSE.
**Plus, since 2026-08-29: for each rule, construct an instance that makes it fire at EVERY product of the
law's chain, not only its own.** A rule whose precondition constrains only `a1 v` (or only `u`), with `v`
pinned solely by a recomputation guard, can fire at a different chain product than the one it was extracted
for. Law 40037's model survived `run_tests`, 20,000 x 3 deep tests and a **1,560,896-assignment exhaustive
sweep** and was still false, refuted in Lean. See `gen/LEMMA_LIBRARY.md`.
**And the LEVEL-k DESCENT, which is the strongest oracle known and refutes sets all five others pass**:
build nested encodings so the decoder must descend THREE levels in the same argument (`op x z`, `op x N3`
and `op x (op x N3)` all decoding). `gen/_w3_12087_deep3.py` is the worked script. It took law 12087's
7-rule, 13-rule and 11-rule sets from 0/500 bad at level 1 to **500/500 bad at level 2**. If your model
fails it, no finite rule set works and you need a decoder that RECURSES (`gen/rec18137b.lean` is the
template). **Run it before writing any Lean.**

**W3-7. Prove one general invariant, not a chain of special cases.** When the law's chain has a repeated
variable, look for the freeness lemma first: 24200 shipped on `FREE (a b) : op (op a b) b = J (op a b) b`;
38565 on `FREE2 (a b) : op a (op b a) = J a (op b a)`, which collapsed a 16-cell case tree to 4.

**W3-8. Judging is parallel-safe** (`jlock.py` pins `JUDGE_LEAN_PATH`, caps concurrency at `JUDGE_SLOTS`=5).
Run one judge call at a time yourself; do not worry about the other agents.

**W3-9. Do not edit anything outside `gen/`** except `certs/<row id>.lean` copies of ACCEPTED certificates.
Never touch `certs/ledger.jsonl`, `closedform.py`, `leangen.py`, `freemodel.py`, `squeeze.py`, or any file
belonging to another agent's law. If you need a changed extractor, copy it to `gen/_<eq>_cf.py` first.

**W3-10. Stop conditions.** ~2 hours or ~35 judge calls. A validated model + a written lemma plan + the exact
remaining goal in `gen/NOTES_<eq>.md` is a useful result. A model you PROVED false, with the instance, is
also a useful result — report it and stop; do not try to prove a false law.
