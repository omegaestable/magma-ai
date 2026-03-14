# Risk Register

1. External competition rules are not archived locally, so some historical README claims could not be verified against organizer text.
2. The hardcoded Hugging Face dataset slug currently returns 404, so the repo cannot automatically fetch the presumed official JSONL files until a current organizer-provided source is confirmed.
3. The local fallback benchmark is useful for offline validation, but it is derived from the checked-in implication matrix and therefore is not a substitute for an external official benchmark split.
4. The current cheatsheet is safer than before, but it has not yet been cross-model benchmarked in this environment because no API evaluation was run.
5. Bucket assignment uses lightweight structural and small-counterexample heuristics; it is useful for debugging, but not a proof taxonomy.
6. The dense matrix is still available in the repo, so future code changes must continue guarding against accidental inference-time lookup leakage.