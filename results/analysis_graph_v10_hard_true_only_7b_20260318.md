# graph_v9 hard TRUE-only analysis

Source run: `results/sim_qwen2.5_7b_graph_v10_hard_true_only_20260318.json`

## Summary

- Total analyzed answers: 74
- Predicted FALSE: 58
- Predicted TRUE: 16
- Correct: 16

### Intended v9 lane counts

- exact_true_pair: 27
- unmatched_by_simple_v9_scan: 20
- C5_family: 9
- C887_lane: 4
- C24_lane: 4
- C41_family: 4
- C4_family: 3
- C13_lane: 3

### Failure mode counts

- misapplied_witness: 54
- followed_positive_lane: 16
- missed_positive_lane: 4

## Per-problem analysis

### hard_0003

- Intended lane: C5_family
- Why v9 supports the answer: E1 is in the right-projection family; graph_v9 should test E2 by the C5 rightmost-variable rule instead of inventing a refutation.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \( x = ((y * y) * z) * x \) matches the C4 source prototype \( x = x * (y * (z * w)) \), where \( w \) can be any variable or constant. Specifically, it matches wit...
- E1: `x = ((y * y) * z) * x`
- E2: `x = x * (((y * x) * x) * x)`

### hard_0007

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = (y * (y * (y * z))) * x) does not imply the equation 2 (x * y = z * (w * (w * y))) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is y...
- E1: `x = (y * (y * (y * z))) * x`
- E2: `x * y = z * (w * (w * y))`

### hard_0013

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x * y = ((z * y) * x) * x\) does not imply the equation \(x * y = y * (y * (y * y))\). This can be shown by a counterexample in the XOR/affine model over \(\mathb...
- E1: `x * y = ((z * y) * x) * x`
- E2: `x * y = y * (y * (y * y))`

### hard_0018

- Intended lane: C887_lane
- Why v9 says this should not be FALSE: E1 and E2 match the exact C887 lane, which graph_v9 marks TRUE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = ((y * x) * y) * (z * z)) does not imply the equation 2 (x = x * (((x * y) * x) * y)) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is...
- E1: `x = ((y * x) * y) * (z * z)`
- E2: `x = x * (((x * y) * x) * y)`

### hard_0023

- Intended lane: C24_lane
- Why v9 says this should not be FALSE: E1 and E2 match the C24 source-to-target lane, which graph_v9 marks TRUE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = (x * y) * (z * z)\) does not imply the equation \(x * x = x * ((y * z) * w)\). This can be verified by considering a counterexample in the XOR/affine model ov...
- E1: `x = (x * y) * (z * z)`
- E2: `x * x = x * ((y * z) * w)`

### hard_0027

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 \( x = x * (y * (x * z)) \) does not imply the equation 2 \( x = ((x * y) * (z * w)) * u \) based on the LEFT PROJECTION witness. LEFT PROJECTION states that an e...
- E1: `x = x * (y * (x * z))`
- E2: `x = ((x * y) * (z * w)) * u`

### hard_0034

- Intended lane: C41_family
- Why v9 says this should not be FALSE: E1 is in the constant-product family; graph_v9 should use the C41 check on whether both sides of E2 contain *.
- Primary failure mode: missed_positive_lane
- Why the answer is wrong: The answer never uses the positive lane that graph_v9 provided for this case and defaults to a generic FALSE story.
- Response excerpt: The equation \(x * y = (y * x) * z\) does not imply \(x * y = z * ((w * y) * y)\) in all magmas.
- E1: `x * y = (y * x) * z`
- E2: `x * y = z * ((w * y) * y)`

### hard_0035

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \( x = x * ((y * z) * (w * u)) \) does not imply the equation \( x = (x * (x * (y * x))) * x \). This can be verified by considering a counterexample in the XOR/aff...
- E1: `x = x * ((y * z) * (w * u))`
- E2: `x = (x * (x * (y * x))) * x`

### hard_0040

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = x * ((y * (z * w)) * w)) does not imply the equation 2 (x * y = (x * (z * w)) * u) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is y...
- E1: `x = x * ((y * (z * w)) * w)`
- E2: `x * y = (x * (z * w)) * u`

### hard_0041

- Intended lane: C5_family
- Why v9 says this should not be FALSE: E1 is in the right-projection family; graph_v9 should test E2 by the C5 rightmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 implies a structure that is not necessarily satisfied by the equation 2. Specifically, we can use the LEFT PROJECTION witness to show this.
- E1: `x = (((y * x) * y) * z) * x`
- E2: `x * y = z * (w * (z * y))`

### hard_0044

- Intended lane: C5_family
- Why v9 says this should not be FALSE: E1 is in the right-projection family; graph_v9 should test E2 by the C5 rightmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = x * ((y * (y * z)) * x)\) does not imply the equation \(x = (((x * y) * x) * x) * x\). This can be verified by considering a counterexample in the XOR/affine...
- E1: `x = (y * (y * z)) * x`
- E2: `x = (((x * y) * x) * x) * x`

### hard_0046

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x * y = y * ((x * y) * z)\) does not imply the equation \(x * x = y * (y * (y * y))\) based on the LEFT PROJECTION witness.
- E1: `x * y = y * ((x * y) * z)`
- E2: `x * x = y * (y * (y * y))`

### hard_0050

- Intended lane: C4_family
- Why v9 says this should not be FALSE: E1 is in the left-projection family; graph_v9 should test E2 by the C4 leftmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 \( x = x * (((y * z) * w) * u) \) does not imply the equation 2 \( x = ((x * x) * (x * y)) * y \) based on the LEFT PROJECTION witness. LEFT PROJECTION states tha...
- E1: `x = x * (((y * z) * w) * u)`
- E2: `x = ((x * x) * (x * y)) * y`

### hard_0052

- Intended lane: C13_lane
- Why v9 says this should not be FALSE: E1 and E2 match the C13 source-to-safe-target lane, which graph_v9 marks TRUE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = (y * x) * (y * x)) does not imply the equation 2 (x = ((x * y) * x) * (z * x)) based on the LEFT PROJECTION witness.
- E1: `x = (y * x) * (y * x)`
- E2: `x = ((x * y) * x) * (z * x)`

### hard_0054

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x * y = ((z * w) * x) * u\) does not imply the equation \(x * (y * y) = (x * x) * x\). This can be verified by considering a counterexample in the XOR/affine mode...
- E1: `x * y = ((z * w) * x) * u`
- E2: `x * (y * y) = (x * x) * x`

### hard_0056

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 \( x = (y * (y * z)) * (w * x) \) does not imply the equation 2 \( x = y * (z * (w * (u * x))) \) based on the LEFT PROJECTION witness. LEFT PROJECTION states tha...
- E1: `x = (y * (y * z)) * (w * x)`
- E2: `x = y * (z * (w * (u * x)))`

### hard_0059

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \( x = ((y * z) * z) * x \) matches the C4 source prototype \( x = x * (y * (z * w)) \), and the equation \( x = x * ((y * (y * x)) * x) \) is a member of the exact...
- E1: `x = ((y * z) * z) * x`
- E2: `x = x * ((y * (y * x)) * x)`

### hard_0060

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = (((y * z) * x) * z) * x) does not imply the equation 2 (x = y * (((x * y) * y) * x)) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is...
- E1: `x = (((y * z) * x) * z) * x`
- E2: `x = y * (((x * y) * y) * x)`

### hard_0061

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \( x = x * (y * (z * (x * y))) \) does not imply the equation \( x = x * (((y * x) * z) * w) \). This can be verified by considering a counterexample in the XOR/aff...
- E1: `x = x * (y * (z * (x * y)))`
- E2: `x = x * (((y * x) * z) * w)`

### hard_0063

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equations match one of the benchmark-hard TRUE pairs: \[ x=((y*z)*w)*x \Rightarrow x=y*((z*(w*u))*x) \] where \( u \) can be any element in the magma, and no renaming is nee...
- E1: `x = ((y * z) * w) * x`
- E2: `x = y * ((z * (w * u)) * x)`

### hard_0064

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = x * ((y * z) * (z * z))\) does not imply the equation \(x = (x * ((y * y) * x)) * x\). This can be verified by considering a counterexample in the XOR/affine...
- E1: `x = x * ((y * z) * (z * z))`
- E2: `x = (x * ((y * y) * x)) * x`

### hard_0065

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \(x = x * (y * (z * y))\) matches the exact C41 source prototype \(x * y = (y * y) * z\), where both sides contain a star operation. Therefore, we need to check if...
- E1: `x = x * (y * (z * y))`
- E2: `x = (x * (x * (x * y))) * x`

### hard_0067

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = (y * (y * x)) * (z * x)) does not imply the equation 2 (x * y = z * (y * (w * y))) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is y...
- E1: `x = (y * (y * x)) * (z * x)`
- E2: `x * y = z * (y * (w * y))`

### hard_0069

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \( x = ((y * y) * z) * x \) matches the C4 source prototype \( x = x * (y * (z * w)) \), and the equation \( x = y * (y * (z * (w * x))) \) is one of the exact C4 r...
- E1: `x = ((y * y) * z) * x`
- E2: `x = y * (y * (z * (w * x)))`

### hard_0070

- Intended lane: C887_lane
- Why v9 supports the answer: E1 and E2 match the exact C887 lane, which graph_v9 marks TRUE.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \( E1 = x = ((y * x) * y) * (z * z) \) can be transformed to match the form of one of the exact C4 source prototypes: - \( x = x * ((y * (x * y)) * z) \) This match...
- E1: `x = ((y * x) * y) * (z * z)`
- E2: `x = x * (((x * y) * x) * y)`

### hard_0075

- Intended lane: C24_lane
- Why v9 says this should not be FALSE: E1 and E2 match the C24 source-to-target lane, which graph_v9 marks TRUE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = (x * y) * (z * z)\) does not imply the equation \(x * x = x * ((y * z) * w)\). This can be verified by considering a counterexample in the XOR/affine model ov...
- E1: `x = (x * y) * (z * z)`
- E2: `x * x = x * ((y * z) * w)`

### hard_0079

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 \( x = x * (y * (x * z)) \) does not imply the equation 2 \( x = ((x * y) * (z * w)) * u \) based on the LEFT PROJECTION witness. LEFT PROJECTION states that an e...
- E1: `x = x * (y * (x * z))`
- E2: `x = ((x * y) * (z * w)) * u`

### hard_0086

- Intended lane: C41_family
- Why v9 says this should not be FALSE: E1 is in the constant-product family; graph_v9 should use the C41 check on whether both sides of E2 contain *.
- Primary failure mode: missed_positive_lane
- Why the answer is wrong: The answer never uses the positive lane that graph_v9 provided for this case and defaults to a generic FALSE story.
- Response excerpt: The equation \(x * y = (y * x) * z\) does not imply \(x * y = z * ((w * y) * y)\) in all magmas.
- E1: `x * y = (y * x) * z`
- E2: `x * y = z * ((w * y) * y)`

### hard_0087

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \( x = x * ((y * z) * (w * u)) \) does not imply the equation \( x = (x * (x * (y * x))) * x \). This can be verified by considering a counterexample in the XOR/aff...
- E1: `x = x * ((y * z) * (w * u))`
- E2: `x = (x * (x * (y * x))) * x`

### hard_0092

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = x * ((y * (z * w)) * w)) does not imply the equation 2 (x * y = (x * (z * w)) * u) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is y...
- E1: `x = x * ((y * (z * w)) * w)`
- E2: `x * y = (x * (z * w)) * u`

### hard_0093

- Intended lane: C5_family
- Why v9 says this should not be FALSE: E1 is in the right-projection family; graph_v9 should test E2 by the C5 rightmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 implies a structure that is not necessarily satisfied by the equation 2. Specifically, we can use the LEFT PROJECTION witness to show this.
- E1: `x = (((y * x) * y) * z) * x`
- E2: `x * y = z * (w * (z * y))`

### hard_0096

- Intended lane: C5_family
- Why v9 says this should not be FALSE: E1 is in the right-projection family; graph_v9 should test E2 by the C5 rightmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = x * ((y * (y * z)) * x)\) does not imply the equation \(x = (((x * y) * x) * x) * x\). This can be verified by considering a counterexample in the XOR/affine...
- E1: `x = (y * (y * z)) * x`
- E2: `x = (((x * y) * x) * x) * x`

### hard_0098

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x * y = y * ((x * y) * z)\) does not imply the equation \(x * x = y * (y * (y * y))\) based on the LEFT PROJECTION witness.
- E1: `x * y = y * ((x * y) * z)`
- E2: `x * x = y * (y * (y * y))`

### hard_0102

- Intended lane: C4_family
- Why v9 says this should not be FALSE: E1 is in the left-projection family; graph_v9 should test E2 by the C4 leftmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 \( x = x * (((y * z) * w) * u) \) does not imply the equation 2 \( x = ((x * x) * (x * y)) * y \) based on the LEFT PROJECTION witness. LEFT PROJECTION states tha...
- E1: `x = x * (((y * z) * w) * u)`
- E2: `x = ((x * x) * (x * y)) * y`

### hard_0104

- Intended lane: C13_lane
- Why v9 says this should not be FALSE: E1 and E2 match the C13 source-to-safe-target lane, which graph_v9 marks TRUE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = (y * x) * (y * x)) does not imply the equation 2 (x = ((x * y) * x) * (z * x)) based on the LEFT PROJECTION witness.
- E1: `x = (y * x) * (y * x)`
- E2: `x = ((x * y) * x) * (z * x)`

### hard_0106

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x * y = ((z * w) * x) * u\) does not imply the equation \(x * (y * y) = (x * x) * x\). This can be verified by considering a counterexample in the XOR/affine mode...
- E1: `x * y = ((z * w) * x) * u`
- E2: `x * (y * y) = (x * x) * x`

### hard_0108

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 \( x = (y * (y * z)) * (w * x) \) does not imply the equation 2 \( x = y * (z * (w * (u * x))) \) based on the LEFT PROJECTION witness. LEFT PROJECTION states tha...
- E1: `x = (y * (y * z)) * (w * x)`
- E2: `x = y * (z * (w * (u * x)))`

### hard_0111

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \( x = ((y * z) * z) * x \) matches the C4 source prototype \( x = x * (y * (z * w)) \), and the equation \( x = x * ((y * (y * x)) * x) \) is a member of the exact...
- E1: `x = ((y * z) * z) * x`
- E2: `x = x * ((y * (y * x)) * x)`

### hard_0112

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = (((y * z) * x) * z) * x) does not imply the equation 2 (x = y * (((x * y) * y) * x)) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is...
- E1: `x = (((y * z) * x) * z) * x`
- E2: `x = y * (((x * y) * y) * x)`

### hard_0113

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \( x = x * (y * (z * (x * y))) \) does not imply the equation \( x = x * (((y * x) * z) * w) \). This can be verified by considering a counterexample in the XOR/aff...
- E1: `x = x * (y * (z * (x * y)))`
- E2: `x = x * (((y * x) * z) * w)`

### hard_0115

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equations match one of the benchmark-hard TRUE pairs: \[ x=((y*z)*w)*x \Rightarrow x=y*((z*(w*u))*x) \] where \( u \) can be any element in the magma, and no renaming is nee...
- E1: `x = ((y * z) * w) * x`
- E2: `x = y * ((z * (w * u)) * x)`

### hard_0116

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = x * ((y * z) * (z * z))\) does not imply the equation \(x = (x * ((y * y) * x)) * x\). This can be verified by considering a counterexample in the XOR/affine...
- E1: `x = x * ((y * z) * (z * z))`
- E2: `x = (x * ((y * y) * x)) * x`

### hard_0117

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \(x = x * (y * (z * y))\) matches the exact C41 source prototype \(x * y = (y * y) * z\), where both sides contain a star operation. Therefore, we need to check if...
- E1: `x = x * (y * (z * y))`
- E2: `x = (x * (x * (x * y))) * x`

### hard_0119

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = (y * (y * x)) * (z * x)) does not imply the equation 2 (x * y = z * (y * (w * y))) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is y...
- E1: `x = (y * (y * x)) * (z * x)`
- E2: `x * y = z * (y * (w * y))`

### hard_0121

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \( x = ((y * y) * z) * x \) matches the C4 source prototype \( x = x * (y * (z * w)) \), and the equation \( x = y * (y * (z * (w * x))) \) is one of the exact C4 r...
- E1: `x = ((y * y) * z) * x`
- E2: `x = y * (y * (z * (w * x)))`

### hard_0122

- Intended lane: C887_lane
- Why v9 supports the answer: E1 and E2 match the exact C887 lane, which graph_v9 marks TRUE.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \( E1 = x = ((y * x) * y) * (z * z) \) can be transformed to match the form of one of the exact C4 source prototypes: - \( x = x * ((y * (x * y)) * z) \) This match...
- E1: `x = ((y * x) * y) * (z * z)`
- E2: `x = x * (((x * y) * x) * y)`

### hard_0127

- Intended lane: C24_lane
- Why v9 says this should not be FALSE: E1 and E2 match the C24 source-to-target lane, which graph_v9 marks TRUE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = (x * y) * (z * z)\) does not imply the equation \(x * x = x * ((y * z) * w)\). This can be verified by considering a counterexample in the XOR/affine model ov...
- E1: `x = (x * y) * (z * z)`
- E2: `x * x = x * ((y * z) * w)`

### hard_0131

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 \( x = x * (y * (x * z)) \) does not imply the equation 2 \( x = ((x * y) * (z * w)) * u \) based on the LEFT PROJECTION witness. LEFT PROJECTION states that an e...
- E1: `x = x * (y * (x * z))`
- E2: `x = ((x * y) * (z * w)) * u`

### hard_0138

- Intended lane: C41_family
- Why v9 says this should not be FALSE: E1 is in the constant-product family; graph_v9 should use the C41 check on whether both sides of E2 contain *.
- Primary failure mode: missed_positive_lane
- Why the answer is wrong: The answer never uses the positive lane that graph_v9 provided for this case and defaults to a generic FALSE story.
- Response excerpt: The equation \(x * y = (y * x) * z\) does not imply \(x * y = z * ((w * y) * y)\) in all magmas.
- E1: `x * y = (y * x) * z`
- E2: `x * y = z * ((w * y) * y)`

### hard_0139

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \( x = x * ((y * z) * (w * u)) \) does not imply the equation \( x = (x * (x * (y * x))) * x \). This can be verified by considering a counterexample in the XOR/aff...
- E1: `x = x * ((y * z) * (w * u))`
- E2: `x = (x * (x * (y * x))) * x`

### hard_0144

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = x * ((y * (z * w)) * w)) does not imply the equation 2 (x * y = (x * (z * w)) * u) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is y...
- E1: `x = x * ((y * (z * w)) * w)`
- E2: `x * y = (x * (z * w)) * u`

### hard_0145

- Intended lane: C5_family
- Why v9 says this should not be FALSE: E1 is in the right-projection family; graph_v9 should test E2 by the C5 rightmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 implies a structure that is not necessarily satisfied by the equation 2. Specifically, we can use the LEFT PROJECTION witness to show this.
- E1: `x = (((y * x) * y) * z) * x`
- E2: `x * y = z * (w * (z * y))`

### hard_0148

- Intended lane: C5_family
- Why v9 says this should not be FALSE: E1 is in the right-projection family; graph_v9 should test E2 by the C5 rightmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = x * ((y * (y * z)) * x)\) does not imply the equation \(x = (((x * y) * x) * x) * x\). This can be verified by considering a counterexample in the XOR/affine...
- E1: `x = (y * (y * z)) * x`
- E2: `x = (((x * y) * x) * x) * x`

### hard_0150

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x * y = y * ((x * y) * z)\) does not imply the equation \(x * x = y * (y * (y * y))\) based on the LEFT PROJECTION witness.
- E1: `x * y = y * ((x * y) * z)`
- E2: `x * x = y * (y * (y * y))`

### hard_0154

- Intended lane: C4_family
- Why v9 says this should not be FALSE: E1 is in the left-projection family; graph_v9 should test E2 by the C4 leftmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 \( x = x * (((y * z) * w) * u) \) does not imply the equation 2 \( x = ((x * x) * (x * y)) * y \) based on the LEFT PROJECTION witness. LEFT PROJECTION states tha...
- E1: `x = x * (((y * z) * w) * u)`
- E2: `x = ((x * x) * (x * y)) * y`

### hard_0156

- Intended lane: C13_lane
- Why v9 says this should not be FALSE: E1 and E2 match the C13 source-to-safe-target lane, which graph_v9 marks TRUE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = (y * x) * (y * x)) does not imply the equation 2 (x = ((x * y) * x) * (z * x)) based on the LEFT PROJECTION witness.
- E1: `x = (y * x) * (y * x)`
- E2: `x = ((x * y) * x) * (z * x)`

### hard_0158

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x * y = ((z * w) * x) * u\) does not imply the equation \(x * (y * y) = (x * x) * x\). This can be verified by considering a counterexample in the XOR/affine mode...
- E1: `x * y = ((z * w) * x) * u`
- E2: `x * (y * y) = (x * x) * x`

### hard_0160

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 \( x = (y * (y * z)) * (w * x) \) does not imply the equation 2 \( x = y * (z * (w * (u * x))) \) based on the LEFT PROJECTION witness. LEFT PROJECTION states tha...
- E1: `x = (y * (y * z)) * (w * x)`
- E2: `x = y * (z * (w * (u * x)))`

### hard_0163

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \( x = ((y * z) * z) * x \) matches the C4 source prototype \( x = x * (y * (z * w)) \), and the equation \( x = x * ((y * (y * x)) * x) \) is a member of the exact...
- E1: `x = ((y * z) * z) * x`
- E2: `x = x * ((y * (y * x)) * x)`

### hard_0164

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = (((y * z) * x) * z) * x) does not imply the equation 2 (x = y * (((x * y) * y) * x)) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is...
- E1: `x = (((y * z) * x) * z) * x`
- E2: `x = y * (((x * y) * y) * x)`

### hard_0165

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \( x = x * (y * (z * (x * y))) \) does not imply the equation \( x = x * (((y * x) * z) * w) \). This can be verified by considering a counterexample in the XOR/aff...
- E1: `x = x * (y * (z * (x * y)))`
- E2: `x = x * (((y * x) * z) * w)`

### hard_0167

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equations match one of the benchmark-hard TRUE pairs: \[ x=((y*z)*w)*x \Rightarrow x=y*((z*(w*u))*x) \] where \( u \) can be any element in the magma, and no renaming is nee...
- E1: `x = ((y * z) * w) * x`
- E2: `x = y * ((z * (w * u)) * x)`

### hard_0168

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = x * ((y * z) * (z * z))\) does not imply the equation \(x = (x * ((y * y) * x)) * x\). This can be verified by considering a counterexample in the XOR/affine...
- E1: `x = x * ((y * z) * (z * z))`
- E2: `x = (x * ((y * y) * x)) * x`

### hard_0169

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \(x = x * (y * (z * y))\) matches the exact C41 source prototype \(x * y = (y * y) * z\), where both sides contain a star operation. Therefore, we need to check if...
- E1: `x = x * (y * (z * y))`
- E2: `x = (x * (x * (x * y))) * x`

### hard_0171

- Intended lane: unmatched_by_simple_v9_scan
- Why v9 says this should not be FALSE: This pair is not obviously captured by the explicit v9 TRUE lanes checked here, so the sheet is effectively silent; the model still should not convert silence into FALSE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = (y * (y * x)) * (z * x)) does not imply the equation 2 (x * y = z * (y * (w * y))) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is y...
- E1: `x = (y * (y * x)) * (z * x)`
- E2: `x * y = z * (y * (w * y))`

### hard_0173

- Intended lane: exact_true_pair
- Why v9 supports the answer: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \( x = ((y * y) * z) * x \) matches the C4 source prototype \( x = x * (y * (z * w)) \), and the equation \( x = y * (y * (z * (w * x))) \) is one of the exact C4 r...
- E1: `x = ((y * y) * z) * x`
- E2: `x = y * (y * (z * (w * x)))`

### hard_0174

- Intended lane: C887_lane
- Why v9 supports the answer: E1 and E2 match the exact C887 lane, which graph_v9 marks TRUE.
- Outcome classification: followed_positive_lane
- Why the answer is acceptable: This answer is correct; the model eventually produced TRUE on a benchmark-TRUE case.
- Response excerpt: The equation \( E1 = x = ((y * x) * y) * (z * z) \) can be transformed to match the form of one of the exact C4 source prototypes: - \( x = x * ((y * (x * y)) * z) \) This match...
- E1: `x = ((y * x) * y) * (z * z)`
- E2: `x = x * (((x * y) * x) * y)`

### hard_0179

- Intended lane: C24_lane
- Why v9 says this should not be FALSE: E1 and E2 match the C24 source-to-target lane, which graph_v9 marks TRUE.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = (x * y) * (z * z)\) does not imply the equation \(x * x = x * ((y * z) * w)\). This can be verified by considering a counterexample in the XOR/affine model ov...
- E1: `x = (x * y) * (z * z)`
- E2: `x * x = x * ((y * z) * w)`

### hard_0183

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 \( x = x * (y * (x * z)) \) does not imply the equation 2 \( x = ((x * y) * (z * w)) * u \) based on the LEFT PROJECTION witness. LEFT PROJECTION states that an e...
- E1: `x = x * (y * (x * z))`
- E2: `x = ((x * y) * (z * w)) * u`

### hard_0190

- Intended lane: C41_family
- Why v9 says this should not be FALSE: E1 is in the constant-product family; graph_v9 should use the C41 check on whether both sides of E2 contain *.
- Primary failure mode: missed_positive_lane
- Why the answer is wrong: The answer never uses the positive lane that graph_v9 provided for this case and defaults to a generic FALSE story.
- Response excerpt: The equation \(x * y = (y * x) * z\) does not imply \(x * y = z * ((w * y) * y)\) in all magmas.
- E1: `x * y = (y * x) * z`
- E2: `x * y = z * ((w * y) * y)`

### hard_0191

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \( x = x * ((y * z) * (w * u)) \) does not imply the equation \( x = (x * (x * (y * x))) * x \). This can be verified by considering a counterexample in the XOR/aff...
- E1: `x = x * ((y * z) * (w * u))`
- E2: `x = (x * (x * (y * x))) * x`

### hard_0196

- Intended lane: exact_true_pair
- Why v9 says this should not be FALSE: This exact hard TRUE pair is explicitly listed in graph_v9, so FALSE means the model ignored a hardcoded TRUE lane.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 (x = x * ((y * (z * w)) * w)) does not imply the equation 2 (x * y = (x * (z * w)) * u) by the LEFT PROJECTION witness. In equation 2, the rightmost variable is y...
- E1: `x = x * ((y * (z * w)) * w)`
- E2: `x * y = (x * (z * w)) * u`

### hard_0197

- Intended lane: C5_family
- Why v9 says this should not be FALSE: E1 is in the right-projection family; graph_v9 should test E2 by the C5 rightmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation 1 implies a structure that is not necessarily satisfied by the equation 2. Specifically, we can use the LEFT PROJECTION witness to show this.
- E1: `x = (((y * x) * y) * z) * x`
- E2: `x * y = z * (w * (z * y))`

### hard_0200

- Intended lane: C5_family
- Why v9 says this should not be FALSE: E1 is in the right-projection family; graph_v9 should test E2 by the C5 rightmost-variable rule instead of inventing a refutation.
- Primary failure mode: misapplied_witness
- Why the answer is wrong: The answer invokes a witness model or parity heuristic, but uses it to reject a pair that is TRUE in the benchmark.
- Response excerpt: The equation \(x = x * ((y * (y * z)) * x)\) does not imply the equation \(x = (((x * y) * x) * x) * x\). This can be verified by considering a counterexample in the XOR/affine...
- E1: `x = (y * (y * z)) * x`
- E2: `x = (((x * y) * x) * x) * x`
