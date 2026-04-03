# Hard False Family Report

## sim_meta-llama_llama-3.3-70b-instruct_hard_balanced40_true20_false20_rotation0001_20260403_163406_v23_20260403_105851.json
- false_positive_count=18
- primary_family_counts=all4x4_table_counterexamples:13, small_finite_magma:3, canonizer_confluence:1, projection_family_counterexamples:1

### hard_0175
- pair=3926,3920
- primary_family=all4x4_table_counterexamples
- top_scores=all4x4_table_counterexamples:3
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x * y = (x * (y * x)) * z
- eq2=x * y = (x * (x * z)) * x

### hard_0128
- pair=706,860
- primary_family=all4x4_table_counterexamples
- top_scores=all4x4_table_counterexamples:9, small_finite_magma:8, projection_family_counterexamples:5
- feature_flags={'new_vars_in_e2': ['z'], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = y * (y * ((x * y) * x))
- eq2=x = x * ((y * z) * (z * x))

### hard_0125
- pair=907,221
- primary_family=small_finite_magma
- top_scores=all4x4_table_counterexamples:10, hard_case:10, small_finite_magma:10
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = y * ((y * x) * (x * y))
- eq2=x = (y * (x * y)) * x

### hard_0058
- pair=4574,4438
- primary_family=canonizer_confluence
- top_scores=canonizer_confluence:2
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x * (y * z) = (w * w) * z
- eq2=x * (y * x) = (x * z) * x

### hard_0099
- pair=1486,913
- primary_family=all4x4_table_counterexamples
- top_scores=all4x4_table_counterexamples:3, canonizer_confluence:1, central_groupoid_counterexamples:1
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = (y * x) * (x * (z * z))
- eq2=x = y * ((y * x) * (z * y))

### hard_0188
- pair=2089,404
- primary_family=all4x4_table_counterexamples
- top_scores=all4x4_table_counterexamples:3, canonizer_confluence:1, central_groupoid_counterexamples:1
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = ((y * x) * x) * (x * z)
- eq2=x * y = (z * z) * z

### hard_0088
- pair=3290,3264
- primary_family=all4x4_table_counterexamples
- top_scores=all4x4_table_counterexamples:2
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x * x = y * (z * (x * z))
- eq2=x * x = x * (y * (z * x))

### hard_0149
- pair=1480,1882
- primary_family=projection_family_counterexamples
- top_scores=projection_family_counterexamples:5, all4x4_table_counterexamples:3, canonizer_confluence:1
- feature_flags={'new_vars_in_e2': ['w'], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = (y * x) * (x * (x * z))
- eq2=x = (x * (y * z)) * (w * w)

### hard_0189
- pair=2994,2623
- primary_family=all4x4_table_counterexamples
- top_scores=all4x4_table_counterexamples:7, projection_family_counterexamples:5
- feature_flags={'new_vars_in_e2': ['w'], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = ((y * (z * y)) * y) * x
- eq2=x = (y * ((z * w) * y)) * x

### hard_0038
- pair=3919,3330
- primary_family=all4x4_table_counterexamples
- top_scores=all4x4_table_counterexamples:3
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x * y = (x * (x * y)) * z
- eq2=x * y = x * (z * (y * y))

## sim_meta-llama_llama-3.3-70b-instruct_hard3_balanced20_true10_false10_rotation0001_20260403_163406_v23_20260403_110425.json
- false_positive_count=10
- primary_family_counts=small_finite_magma:5, all4x4_table_counterexamples:3, projection_family_counterexamples:2

### hard3_0305
- pair=2864,624
- primary_family=all4x4_table_counterexamples
- top_scores=all4x4_table_counterexamples:3
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = ((x * (y * x)) * x) * z
- eq2=x = x * (x * ((y * y) * z))

### hard3_0110
- pair=885,2939
- primary_family=small_finite_magma
- top_scores=all4x4_table_counterexamples:3, hard_case:3, small_finite_magma:3
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = y * ((x * y) * (z * x))
- eq2=x = ((y * (y * x)) * y) * x

### hard3_0237
- pair=2126,3734
- primary_family=projection_family_counterexamples
- top_scores=projection_family_counterexamples:5, all4x4_table_counterexamples:1, canonizer_confluence:1
- feature_flags={'new_vars_in_e2': ['w'], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = ((y * y) * x) * (x * z)
- eq2=x * y = (x * z) * (x * w)

### hard3_0360
- pair=3490,355
- primary_family=small_finite_magma
- top_scores=small_finite_magma:1
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x * x = y * ((y * z) * w)
- eq2=x * y = z * (w * y)

### hard3_0141
- pair=1085,4093
- primary_family=small_finite_magma
- top_scores=all4x4_table_counterexamples:10, hard_case:10, small_finite_magma:10
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = y * ((x * (y * y)) * x)
- eq2=x * x = ((y * y) * y) * x

### hard3_0103
- pair=827,3332
- primary_family=projection_family_counterexamples
- top_scores=projection_family_counterexamples:5, all4x4_table_counterexamples:2, small_finite_magma:1
- feature_flags={'new_vars_in_e2': ['w'], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = x * ((x * y) * (y * z))
- eq2=x * y = x * (z * (y * w))

### hard3_0130
- pair=1037,3533
- primary_family=all4x4_table_counterexamples
- top_scores=all4x4_table_counterexamples:7, central_groupoid_counterexamples:1, small_finite_magma:1
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = x * ((y * (x * x)) * z)
- eq2=x * y = x * ((z * y) * y)

### hard3_0186
- pair=1663,214
- primary_family=small_finite_magma
- top_scores=small_finite_magma:2
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = (x * y) * ((y * z) * w)
- eq2=x = (x * (y * z)) * x

### hard3_0075
- pair=545,2043
- primary_family=small_finite_magma
- top_scores=all4x4_table_counterexamples:3, hard_case:3, small_finite_magma:3
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = y * (z * (x * (z * x)))
- eq2=x = ((x * x) * y) * (y * x)

### hard3_0234
- pair=2126,124
- primary_family=all4x4_table_counterexamples
- top_scores=all4x4_table_counterexamples:8, hard_case:3, small_finite_magma:3
- feature_flags={'new_vars_in_e2': [], 'lp_obstruction': False, 'rp_obstruction': False}
- eq1=x = ((y * y) * x) * (x * z)
- eq2=x = y * ((y * x) * x)

