# Seed Failure Analysis

Cheatsheet: cheatsheets/v22_witness.txt
Files analyzed: 4

## sim_paid_normal_seed20260401_v22_witness.json
fails=0

## sim_paid_normal_seed20260402_v22_witness.json
fails=4

### [1] normal_0852
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (y * (x * (y * x)))
- eq2=x = y * ((z * (x * w)) * x)

### [2] normal_0725
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * (y * x)) * (y * z)
- eq2=x = x * (x * (y * (z * w)))

### [3] normal_0012
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample witness(s): A2,T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): A2,T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = (y * (x * y)) * y
- eq2=x * y = z * (z * (y * y))

### [4] normal_0933
- gt=False pred=None
- cause=other
- auto_result=FALSE auto_reason=C0
- structural_separators=['C0']
- corrected_certificate=counterexample witness(s): C0
- corrected_proof=FALSE by certificate source: counterexample witness(s): C0
- corrected_counterexample=exists (see witness/source above)
- eq1=x * y = ((z * y) * y) * x
- eq2=x = y * (((x * z) * w) * w)

## sim_paid_hard3_seed20260401_v22_witness.json
fails=29

### [1] hard3_0059
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample witness(s): T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = (y * z) * w
- eq2=x * (x * y) = (z * x) * y

### [2] hard3_0282
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * y) * (y * z)) * w
- eq2=x = (x * (y * y)) * (y * y)

### [3] hard3_0079
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (z * (z * (z * x)))
- eq2=x = ((y * y) * z) * (x * x)

### [4] hard3_0065
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (y * (x * (x * z)))
- eq2=x * x = (x * x) * y

### [5] hard3_0253
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * (y * (y * z))) * y
- eq2=x * (x * y) = x * (z * z)

### [6] hard3_0217
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * x) * y) * (z * w)
- eq2=x = (x * (y * z)) * y

### [7] hard3_0242
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((y * z) * x) * (x * w)
- eq2=x = ((x * x) * y) * (y * y)

### [8] hard3_0190
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * ((x * x) * y)
- eq2=x * (y * z) = (x * z) * y

### [9] hard3_0016
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (x * (x * x))
- eq2=x * y = (y * y) * (y * y)

### [10] hard3_0200
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * (x * y)) * (z * z)
- eq2=x = (x * (y * x)) * (z * w)

### [11] hard3_0392
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:explicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:explicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x * (x * y) = (x * z) * w
- eq2=x * (y * x) = (x * x) * y

### [12] hard3_0167
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * (x * (z * w))
- eq2=x * y = z * (x * (z * z))

### [13] hard3_0150
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (((y * x) * y) * z)
- eq2=x = x * ((y * (z * w)) * x)

### [14] hard3_0306
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * (y * x)) * z) * w
- eq2=x = x * ((y * z) * (x * w))

### [15] hard3_0057
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample witness(s): T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = (y * z) * z
- eq2=x * x = y * (y * x)

### [16] hard3_0013
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (y * (z * x))
- eq2=x = (((x * x) * x) * x) * x

### [17] hard3_0226
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * y) * z) * (w * z)
- eq2=x = (x * x) * (x * (y * z))

### [18] hard3_0351
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample witness(s): A2
- corrected_proof=FALSE by certificate source: counterexample witness(s): A2
- corrected_counterexample=exists (see witness/source above)
- eq1=x * y = x * (y * (z * x))
- eq2=x * y = x * ((z * y) * w)

### [19] hard3_0342
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = y * (x * (x * z))
- eq2=x * y = (x * z) * (y * y)

### [20] hard3_0012
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (y * (x * x))
- eq2=x * x = (x * y) * (x * x)

### [21] hard3_0017
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (y * (x * x))
- eq2=x = (x * (y * z)) * x

### [22] hard3_0022
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * ((x * y) * z)
- eq2=x * y = x * ((y * x) * y)

### [23] hard3_0108
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * ((y * z) * (z * x))
- eq2=x * (y * x) = x * (z * x)

### [24] hard3_0039
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * (y * x)) * y
- eq2=x = (x * x) * (x * (y * z))

### [25] hard3_0330
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (((x * y) * z) * x) * y
- eq2=x = (x * (y * (x * z))) * w

### [26] hard3_0044
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * y) * z) * w
- eq2=x * y = (x * (z * w)) * w

### [27] hard3_0123
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * ((z * w) * (u * x))
- eq2=x * y = z * (w * y)

### [28] hard3_0300
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * (x * x)) * x) * y
- eq2=x = x * ((y * (z * z)) * x)

### [29] hard3_0097
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (z * ((x * w) * x))
- eq2=x = (y * ((y * z) * y)) * x

## sim_paid_hard3_seed20260402_v22_witness.json
fails=30

### [1] hard3_0086
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (y * ((y * z) * y))
- eq2=x * y = ((x * z) * y) * w

### [2] hard3_0276
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * x) * (y * x)) * z
- eq2=x * y = (x * (y * z)) * w

### [3] hard3_0073
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * (z * (x * (y * x)))
- eq2=x = y * (((z * y) * x) * x)

### [4] hard3_0174
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * y) * (z * (y * x))
- eq2=x = (y * ((x * z) * z)) * x

### [5] hard3_0216
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * x) * y) * (z * z)
- eq2=x * (y * z) = (x * y) * z

### [6] hard3_0045
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((y * x) * y) * x
- eq2=x * (y * z) = y * (x * z)

### [7] hard3_0236
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((y * y) * x) * (x * z)
- eq2=x = (y * x) * ((y * x) * x)

### [8] hard3_0348
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = y * (y * (x * z))
- eq2=x * y = (y * z) * (z * y)

### [9] hard3_0130
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * ((y * (x * x)) * z)
- eq2=x * y = x * ((z * y) * y)

### [10] hard3_0370
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample witness(s): T3L
- corrected_proof=FALSE by certificate source: counterexample witness(s): T3L
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = (y * x) * (z * w)
- eq2=x * y = z * ((x * z) * w)

### [11] hard3_0175
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:explicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:explicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * z) * (x * (z * x))
- eq2=x * y = ((x * x) * y) * y

### [12] hard3_0164
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * (x * (z * x))
- eq2=x = (y * (y * (z * y))) * x

### [13] hard3_0234
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((y * y) * x) * (x * z)
- eq2=x = y * ((y * x) * x)

### [14] hard3_0110
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * ((x * y) * (z * x))
- eq2=x = ((y * (y * x)) * y) * x

### [15] hard3_0372
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x * y = (x * y) * (z * y)
- eq2=x * (y * z) = (x * x) * z

### [16] hard3_0032
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * x) * (x * z)
- eq2=x * y = (x * (z * x)) * y

### [17] hard3_0081
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:explicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:explicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (x * ((y * y) * y))
- eq2=x = x * ((y * (x * x)) * x)

### [18] hard3_0248
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * (y * (x * y))) * y
- eq2=(x * x) * x = (x * x) * y

### [19] hard3_0111
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * ((x * z) * (z * x))
- eq2=x * x = x * ((y * z) * x)

### [20] hard3_0185
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (x * y) * ((y * z) * y)
- eq2=x * y = x * ((z * w) * x)

### [21] hard3_0263
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * ((x * x) * x)) * x
- eq2=x = (((x * x) * x) * y) * x

### [22] hard3_0011
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (x * (y * z))
- eq2=x = ((x * (y * x)) * x) * x

### [23] hard3_0119
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = y * ((z * z) * (x * x))
- eq2=x = x * (((x * y) * y) * x)

### [24] hard3_0180
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * z) * (z * (z * x))
- eq2=x = ((x * x) * (x * x)) * x

### [25] hard3_0080
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * (x * ((x * y) * z))
- eq2=x * y = x * (x * (y * z))

### [26] hard3_0179
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = (y * z) * (z * (x * x))
- eq2=x = (y * ((z * x) * y)) * x

### [27] hard3_0343
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x * x = y * (x * (x * z))
- eq2=x * x = ((y * y) * y) * x

### [28] hard3_0286
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * y) * (z * x)) * y
- eq2=x * y = (x * (z * z)) * x

### [29] hard3_0104
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = x * ((x * y) * (z * y))
- eq2=x * (y * y) = (x * z) * z

### [30] hard3_0275
- gt=False pred=True
- cause=FP from incomplete hard-false coverage
- auto_result=TRUE auto_reason=NONE
- structural_separators=none
- corrected_certificate=counterexample in matrix (matrix:implicit_proof_false)
- corrected_proof=FALSE by certificate source: counterexample in matrix (matrix:implicit_proof_false)
- corrected_counterexample=exists (see witness/source above)
- eq1=x = ((x * x) * (y * x)) * y
- eq2=x * y = (x * (z * z)) * y

total_failures=63
