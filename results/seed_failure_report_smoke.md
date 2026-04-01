# Seed Failure Analysis

Cheatsheet: cheatsheets/v22_witness.txt
Files analyzed: 1

## sim_meta-llama_llama-3.3-70b-instruct_normal_balanced20_true10_false10_seed0_v21f_structural_20260331_204155.json
fails=2

### [1] normal_0458
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=FALSE auto_reason=X
- structural_separators=['XOR', 'XNOR']
- corrected_certificate=counterexample witness(s): XOR,XNOR
- corrected_proof=FALSE by certificate source: counterexample witness(s): XOR,XNOR
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((y * z) * (x * z)) * y
- eq2=x * y = (z * (w * y)) * z

### [2] normal_0197
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=FALSE auto_reason=X
- structural_separators=['XOR', 'XNOR']
- corrected_certificate=counterexample witness(s): XOR,XNOR
- corrected_proof=FALSE by certificate source: counterexample witness(s): XOR,XNOR
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (((y * x) * z) * z)
- eq2=x = y * ((z * y) * (w * u))

total_failures=2
