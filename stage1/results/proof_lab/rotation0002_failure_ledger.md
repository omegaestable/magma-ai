# Seed Failure Analysis

Cheatsheet: cheatsheets/v23.txt
Files analyzed: 2

## sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v23_20260403_130838.json
fails=4

### [1] normal_0884
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = (x * y) * (z * z)
- eq2=x * x = (x * (x * y)) * z

### [2] normal_0335
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (x * (x * y))
- eq2=x = (x * (y * (y * z))) * w

### [3] normal_0618
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['XOR', 'XNOR']
- corrected_certificate=counterexample witness(s): XOR,XNOR
- corrected_proof=FALSE by certificate source: counterexample witness(s): XOR,XNOR
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (y * (z * (z * x)))
- eq2=x = (x * y) * (z * x)

### [4] normal_0301
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample witness(s): T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=(x * y) * y = (y * z) * z
- eq2=x * (y * z) = (z * y) * x

## sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v23_20260403_131453.json
fails=20

### [1] hard3_0128
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * ((x * (y * z)) * y)
- eq2=x = ((x * y) * z) * (y * z)

### [2] hard3_0116
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * ((y * z) * (y * x))
- eq2=x = ((y * (z * y)) * z) * x

### [3] hard3_0180
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * z) * (z * (z * x))
- eq2=x = ((x * x) * (x * x)) * x

### [4] hard3_0153
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (((y * z) * x) * y)
- eq2=x * (y * x) = x * (z * z)

### [5] hard3_0074
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (z * (x * (z * x)))
- eq2=x = (x * (x * x)) * (x * x)

### [6] hard3_0151
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:explicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:explicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (((y * x) * y) * z)
- eq2=(x * x) * x = (x * x) * y

### [7] hard3_0163
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * (x * (x * z))
- eq2=x = y * (y * (z * (z * x)))

### [8] hard3_0383
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x * y = (y * (z * x)) * y
- eq2=x * y = ((y * y) * y) * y

### [9] hard3_0359
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample witness(s): T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = y * ((y * x) * z)
- eq2=x * y = (y * y) * (z * z)

### [10] hard3_0280
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * y) * (y * z)) * x
- eq2=x * y = x * (x * (z * y))

### [11] hard3_0301
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * (x * x)) * y) * z
- eq2=x = x * ((y * y) * z)

### [12] hard3_0253
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * (y * (y * z))) * y
- eq2=x * (x * y) = x * (z * z)

### [13] hard3_0254
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * (z * (x * x))) * x
- eq2=x * x = (y * z) * (x * x)

### [14] hard3_0096
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (z * ((x * w) * x))
- eq2=x = (x * (x * x)) * x

### [15] hard3_0218
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * y) * x) * (z * w)
- eq2=x = x * (y * (z * (w * u)))

### [16] hard3_0017
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (y * (x * x))
- eq2=x = (x * (y * z)) * x

### [17] hard3_0166
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * (x * (z * w))
- eq2=x = ((y * y) * z) * y

### [18] hard3_0113
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:explicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:explicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * ((y * y) * (x * x))
- eq2=x = x * (((y * x) * x) * x)

### [19] hard3_0073
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (z * (x * (y * x)))
- eq2=x = y * (((z * y) * x) * x)

### [20] hard3_0328
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (((x * y) * x) * y) * y
- eq2=x = (x * x) * (y * x)

total_failures=24
