# Seed Failure Analysis

Cheatsheet: cheatsheets/v24j.txt
Files analyzed: 7

## sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_20260407_183950.json
fails=19

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

### [5] hard3_0151
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:explicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:explicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (((y * x) * y) * z)
- eq2=(x * x) * x = (x * x) * y

### [6] hard3_0028
- gt=True pred=False
- cause=FN from conservative false default
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=implication true in matrix (matrix:implicit_proof_true)
- corrected_proof=TRUE in Teorth matrix; no finite counterexample exists
- corrected_counterexample=None
- eq1=x = y * ((z * x) * x)
- eq2=x = ((y * z) * w) * (z * x)

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

### [16] hard3_0166
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * (x * (z * w))
- eq2=x = ((y * y) * z) * y

### [17] hard3_0073
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (z * (x * (y * x)))
- eq2=x = y * (((z * y) * x) * x)

### [18] hard3_0033
- gt=True pred=False
- cause=FN from conservative false default
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=implication true in matrix (matrix:implicit_proof_true)
- corrected_proof=TRUE in Teorth matrix; no finite counterexample exists
- corrected_counterexample=None
- eq1=x = (y * x) * (z * x)
- eq2=x * x = ((y * x) * x) * x

### [19] hard3_0328
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (((x * y) * x) * y) * y
- eq2=x = (x * x) * (y * x)

## sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_20260407_195815.json
fails=11

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

### [2] hard3_0153
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (((y * z) * x) * y)
- eq2=x * (y * x) = x * (z * z)

### [3] hard3_0151
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:explicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:explicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (((y * x) * y) * z)
- eq2=(x * x) * x = (x * x) * y

### [4] hard3_0163
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * (x * (x * z))
- eq2=x = y * (y * (z * (z * x)))

### [5] hard3_0359
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample witness(s): T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = y * ((y * x) * z)
- eq2=x * y = (y * y) * (z * z)

### [6] hard3_0301
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * (x * x)) * y) * z
- eq2=x = x * ((y * y) * z)

### [7] hard3_0253
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * (y * (y * z))) * y
- eq2=x * (x * y) = x * (z * z)

### [8] hard3_0254
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * (z * (x * x))) * x
- eq2=x * x = (y * z) * (x * x)

### [9] hard3_0218
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * y) * x) * (z * w)
- eq2=x = x * (y * (z * (w * u)))

### [10] hard3_0166
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * (x * (z * w))
- eq2=x = ((y * y) * z) * y

### [11] hard3_0328
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (((x * y) * x) * y) * y
- eq2=x = (x * x) * (y * x)

## sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced40_true20_false20_rotation0002_20260403_185904_v24j_20260407_201938.json
fails=14

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

### [2] hard3_0153
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (((y * z) * x) * y)
- eq2=x * (y * x) = x * (z * z)

### [3] hard3_0074
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (z * (x * (z * x)))
- eq2=x = (x * (x * x)) * (x * x)

### [4] hard3_0151
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:explicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:explicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (((y * x) * y) * z)
- eq2=(x * x) * x = (x * x) * y

### [5] hard3_0163
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * (x * (x * z))
- eq2=x = y * (y * (z * (z * x)))

### [6] hard3_0383
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x * y = (y * (z * x)) * y
- eq2=x * y = ((y * y) * y) * y

### [7] hard3_0359
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample witness(s): T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = y * ((y * x) * z)
- eq2=x * y = (y * y) * (z * z)

### [8] hard3_0301
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * (x * x)) * y) * z
- eq2=x = x * ((y * y) * z)

### [9] hard3_0253
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * (y * (y * z))) * y
- eq2=x * (x * y) = x * (z * z)

### [10] hard3_0254
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * (z * (x * x))) * x
- eq2=x * x = (y * z) * (x * x)

### [11] hard3_0218
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * y) * x) * (z * w)
- eq2=x = x * (y * (z * (w * u)))

### [12] hard3_0166
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * (x * (z * w))
- eq2=x = ((y * y) * z) * y

### [13] hard3_0127
- gt=True pred=False
- cause=FN from conservative false default
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=implication true in matrix (matrix:implicit_proof_true)
- corrected_proof=TRUE in Teorth matrix; no finite counterexample exists
- corrected_counterexample=None
- eq1=x = y * ((z * w) * (u * x))
- eq2=x * y = ((y * x) * y) * y

### [14] hard3_0328
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (((x * y) * x) * y) * y
- eq2=x = (x * x) * (y * x)

## sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_182607.json
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

## sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_192130.json
fails=20

### [1] normal_0499
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['LP']
- corrected_certificate=counterexample witness(s): LP
- corrected_proof=FALSE by certificate source: counterexample witness(s): LP
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (((x * y) * z) * y) * x
- eq2=x = ((y * z) * z) * (w * x)

### [2] normal_0614
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['LP']
- corrected_certificate=counterexample witness(s): LP
- corrected_proof=FALSE by certificate source: counterexample witness(s): LP
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * ((y * x) * z)) * y
- eq2=x * y = (y * (z * z)) * x

### [3] normal_0245
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['C0']
- corrected_certificate=counterexample witness(s): C0
- corrected_proof=FALSE by certificate source: counterexample witness(s): C0
- corrected_counterexample=exists (see witness/source above)
- eq1=x * y = (x * (y * x)) * z
- eq2=x = (x * (y * y)) * (x * y)

### [4] normal_0063
- gt=True pred=False
- cause=FN from conservative false default
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=implication true in matrix (matrix:implicit_proof_true)
- corrected_proof=TRUE in Teorth matrix; no finite counterexample exists
- corrected_counterexample=None
- eq1=x = ((y * (x * y)) * y) * z
- eq2=x = ((y * z) * x) * (z * z)

### [5] normal_0783
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['C0']
- corrected_certificate=counterexample witness(s): C0,T3L,T3R
- corrected_proof=FALSE by certificate source: counterexample witness(s): C0,T3L,T3R
- corrected_counterexample=exists (see witness/source above)
- eq1=x * (y * x) = z * (y * y)
- eq2=x = (y * z) * ((x * z) * x)

### [6] normal_0979
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['LP']
- corrected_certificate=counterexample witness(s): LP
- corrected_proof=FALSE by certificate source: counterexample witness(s): LP
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * x) * ((x * y) * z)
- eq2=x * y = z * ((w * w) * x)

### [7] normal_0339
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['C0', 'XOR', 'XNOR']
- corrected_certificate=counterexample witness(s): C0,XOR,XNOR,A2,T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): C0,XOR,XNOR,A2,T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = y * (y * (z * z))
- eq2=x = x * ((y * z) * (w * z))

### [8] normal_0581
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['C0']
- corrected_certificate=counterexample witness(s): C0
- corrected_proof=FALSE by certificate source: counterexample witness(s): C0
- corrected_counterexample=exists (see witness/source above)
- eq1=x * y = (z * w) * z
- eq2=x = ((y * (y * y)) * z) * z

### [9] normal_0884
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = (x * y) * (z * z)
- eq2=x * x = (x * (x * y)) * z

### [10] normal_0415
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['RP']
- corrected_certificate=counterexample witness(s): RP
- corrected_proof=FALSE by certificate source: counterexample witness(s): RP
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * ((y * x) * x)
- eq2=(x * y) * y = (y * x) * x

### [11] normal_0388
- gt=False pred=None
- cause=other
- auto_result=None auto_reason=None
- structural_separators=['LP']
- corrected_certificate=counterexample witness(s): LP
- corrected_proof=FALSE by certificate source: counterexample witness(s): LP
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (x * (y * y))
- eq2=x = (((y * z) * x) * x) * y

### [12] normal_0335
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (x * (x * y))
- eq2=x = (x * (y * (y * z))) * w

### [13] normal_0868
- gt=True pred=False
- cause=FN from conservative false default
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=implication true in matrix (matrix:implicit_proof_true)
- corrected_proof=TRUE in Teorth matrix; no finite counterexample exists
- corrected_counterexample=None
- eq1=x = y * ((z * (z * w)) * y)
- eq2=x * y = (y * (x * x)) * y

### [14] normal_0705
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['C0']
- corrected_certificate=counterexample witness(s): C0,T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): C0,T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = ((x * x) * y) * z
- eq2=x = (x * (y * y)) * (y * x)

### [15] normal_0301
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample witness(s): T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=(x * y) * y = (y * z) * z
- eq2=x * (y * z) = (z * y) * x

### [16] normal_0218
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['C0']
- corrected_certificate=counterexample witness(s): C0
- corrected_proof=FALSE by certificate source: counterexample witness(s): C0
- corrected_counterexample=exists (see witness/source above)
- eq1=x * y = (y * z) * (z * w)
- eq2=x = x * ((x * x) * x)

### [17] normal_0220
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['C0']
- corrected_certificate=counterexample witness(s): C0
- corrected_proof=FALSE by certificate source: counterexample witness(s): C0
- corrected_counterexample=exists (see witness/source above)
- eq1=x * y = (z * x) * (w * w)
- eq2=x = y * (y * ((z * y) * w))

### [18] normal_0853
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['C0']
- corrected_certificate=counterexample witness(s): C0
- corrected_proof=FALSE by certificate source: counterexample witness(s): C0
- corrected_counterexample=exists (see witness/source above)
- eq1=x * y = z * (x * (w * x))
- eq2=x = ((y * x) * z) * (x * x)

### [19] normal_0712
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['RP']
- corrected_certificate=counterexample witness(s): RP
- corrected_proof=FALSE by certificate source: counterexample witness(s): RP
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((y * z) * (y * y)) * x
- eq2=x * y = ((y * z) * w) * z

### [20] normal_0601
- gt=True pred=None
- cause=other
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=implication true in matrix (matrix:implicit_proof_true)
- corrected_proof=TRUE in Teorth matrix; no finite counterexample exists
- corrected_counterexample=None
- eq1=x = y * ((z * (z * w)) * x)
- eq2=x * y = (y * (x * x)) * y

## sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_194143.json
fails=5

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

### [5] normal_0600
- gt=True pred=False
- cause=FN from conservative false default
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=implication true in matrix (matrix:implicit_proof_true)
- corrected_proof=TRUE in Teorth matrix; no finite counterexample exists
- corrected_counterexample=None
- eq1=x = (y * y) * (z * (y * w))
- eq2=x = (y * (y * (z * w))) * w

## sim_meta-llama_llama-3.3-70b-instruct_normal_balanced60_true30_false30_rotation0002_20260403_185904_v24j_20260407_202047.json
fails=6

### [1] normal_0752
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['RP']
- corrected_certificate=counterexample witness(s): RP
- corrected_proof=FALSE by certificate source: counterexample witness(s): RP
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (((z * y) * z) * x)
- eq2=x = (y * ((y * y) * x)) * y

### [2] normal_0884
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = (x * y) * (z * z)
- eq2=x * x = (x * (x * y)) * z

### [3] normal_0335
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (x * (x * y))
- eq2=x = (x * (y * (y * z))) * w

### [4] normal_0618
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['XOR', 'XNOR']
- corrected_certificate=counterexample witness(s): XOR,XNOR
- corrected_proof=FALSE by certificate source: counterexample witness(s): XOR,XNOR
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (y * (z * (z * x)))
- eq2=x = (x * y) * (z * x)

### [5] normal_0301
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=none
- corrected_certificate=counterexample witness(s): T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=(x * y) * y = (y * z) * z
- eq2=x * (y * z) = (z * y) * x

### [6] normal_0712
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=None auto_reason=None
- structural_separators=['RP']
- corrected_certificate=counterexample witness(s): RP
- corrected_proof=FALSE by certificate source: counterexample witness(s): RP
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((y * z) * (y * y)) * x
- eq2=x * y = ((y * z) * w) * z

total_failures=79
