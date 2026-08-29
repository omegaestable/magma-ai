# Wave-2 prompt (2026-08-29 afternoon): one law per agent — validate, REPAIR if needed, then prove

Read first, in full: WAVE_PROMPT.md (rules + report format), AGENT_BRIEF.md (method), then your assignment
`gen/prompt2_<eq>.md`, and at least one accepted proof in full (`certs/research_order5_hard_0059.lean` (5295) or
`certs/research_order5_hard_0094.lean` (7701, repaired then proved)).

What wave 1 learned (7 of 10 generated skeletons were FALSE, 4 were repaired by the agent and then ACCEPTED):

1. **Validate before proving, with the strong validator, not `gen/chk<eq>.py 3000`** (too weak; and for
   DUALIZED laws the old chk files test the wrong orientation and print 3000/3000 fails — ignore them). Use:
   ```python
   import closedform as cf, revalidate as rv, smallcheck as sc, leangen
   from freemodel import normalise, catalog; from laws import parse_eq
   cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
   dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
   law = ('x', leangen.dual_pat(orig[1])) if dualized else orig      # the law the skeleton's `op` models
   rules = <the rule list from gen/chk<eq>.py or your repair>
   fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)           # exhaustive small terms + deep + fuzz + closure + critical
   ```
   (`rv.run_tests` returns a list of (assignment, got, kind, seed); empty = validated.) Also run
   `cf.deep_tests` at 20,000 and your own coincidence-targeted instances (x/y/z built from the model's own
   encodings of each other — the holes found so far were ALL of that shape: a variable equal to an encoding
   of another variable's value, nested once or twice, or an encoding whose outer product is itself decoded).
2. **If the skeleton is FALSE, repair it** (the recipe that worked on 38249, 9667, 40057, 7701, 5837, 33020):
   trace the failing instance (`python trace.py <eq>` prints the chain with the rule fired at each product and
   any msr-gate cut), find which product decoded unexpectedly, and add the rule that recovers the payload
   through the occurrence that is provably free (usually: replace the J-shape guard of an existing rule by an
   `op(dec, enc) == target` guard, or add the `u = v`-type case where the outer product of the encoding was
   itself decoded). Re-validate with `rv.run_tests` (0 fails on 3 seeds), emit the repaired skeleton with
   `leangen.emit(EQ, 'gen/rep<eq>', rules_override=rules)` (a tiny script in gen/; do NOT edit leangen.py /
   closedform.py / fuzz.py), then prove. Keep rule sets small (≤ 8 rules; drop rules that never fire on the
   validator). If the repair needs a rule whose result is a nested `op` (the payload is "whatever op u B
   decodes to"), that is allowed — see the 18137 model (`gen/rec18137b.lean`): rules may recurse on a smaller
   pair; gate the call like the others.
3. If a genuine reading needs a nested guard whose pair is NOT below the msr gate (trace.py prints GATE CUT),
   express that guard structurally instead (the shape the encoding must have), as the `~` rules do.
4. Certificates ≤ 20,000 UTF-8 bytes, ≤ 300 s judge time, no `grind`/`native_decide`/`sorry`; namespace and
   final `submission` term exactly as generated. Stop after ~35 judge iterations or ~2 hours and report the exact
   remaining goals (a validated repaired skeleton with a written lemma plan is a useful partial result).
5. Wave rules unchanged: your law only; nothing outside gen/ except `certs/<row id>.lean` copies of ACCEPTED
   files; no batch jobs; one judge call at a time; report in the WAVE_PROMPT.md format (one ROW line per row,
   dual rows included, repaired rule set verbatim under HOLES).
