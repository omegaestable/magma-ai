# Public Corpus Family Report

## Dataset Policy

- Train corpus: normal, hard1
- Held-out test: hard2, hard3
- Dev ratio: 0.2

## Ranked Families

### rewrite_metatheorem:true:general
- Prompt safe: True
- Aligned problems: 524
- TRUE / FALSE: 524 / 0
- Internal train / dev: 419 / 105
- Samples: ['normal_0001', 'normal_0002', 'normal_0004', 'normal_0005', 'normal_0007']

### small_finite_magma:false:finite
- Prompt safe: True
- Aligned problems: 443
- TRUE / FALSE: 0 / 443
- Internal train / dev: 355 / 88
- Samples: ['normal_0003', 'normal_0006', 'normal_0008', 'normal_0015', 'normal_0016']

### projection_family_counterexamples:false:general
- Prompt safe: True
- Aligned problems: 364
- TRUE / FALSE: 0 / 364
- Internal train / dev: 290 / 74
- Samples: ['normal_0003', 'normal_0006', 'normal_0008', 'normal_0012', 'normal_0020']

### singleton_rewrite:true:general
- Prompt safe: True
- Aligned problems: 243
- TRUE / FALSE: 243 / 0
- Internal train / dev: 187 / 56
- Samples: ['normal_0004', 'normal_0007', 'normal_0009', 'normal_0013', 'normal_0028']

### canonizer_confluence:false:general
- Prompt safe: True
- Aligned problems: 67
- TRUE / FALSE: 0 / 67
- Internal train / dev: 54 / 13
- Samples: ['normal_0014', 'normal_0026', 'normal_0029', 'normal_0045', 'normal_0174']

### closure_transitive
- Prompt safe: False
- Aligned problems: 40
- TRUE / FALSE: 40 / 0
- Internal train / dev: 35 / 5
- Samples: ['normal_0022', 'normal_0083', 'normal_0090', 'normal_0091', 'normal_0099']

### all4x4_table_counterexamples:false:finite
- Prompt safe: True
- Aligned problems: 10
- TRUE / FALSE: 0 / 10
- Internal train / dev: 6 / 4
- Samples: ['normal_0027', 'normal_0295', 'normal_0415', 'normal_0439', 'normal_0512']

### hard_case:false:finite
- Prompt safe: False
- Aligned problems: 3
- TRUE / FALSE: 0 / 3
- Internal train / dev: 2 / 1
- Samples: ['normal_0415', 'normal_0439', 'normal_0878']

### automated_reasoner:true:general
- Prompt safe: False
- Aligned problems: 1
- TRUE / FALSE: 1 / 0
- Internal train / dev: 1 / 0
- Samples: ['normal_0324']

### central_groupoid_counterexamples:false:general
- Prompt safe: True
- Aligned problems: 0
- TRUE / FALSE: 0 / 0
- Internal train / dev: 0 / 0
- Samples: []

### closure_dual
- Prompt safe: False
- Aligned problems: 0
- TRUE / FALSE: 0 / 0
- Internal train / dev: 0 / 0
- Samples: []

### exceptional_hard:false:general
- Prompt safe: True
- Aligned problems: 0
- TRUE / FALSE: 0 / 0
- Internal train / dev: 0 / 0
- Samples: []

### hard_case:false:general
- Prompt safe: False
- Aligned problems: 0
- TRUE / FALSE: 0 / 0
- Internal train / dev: 0 / 0
- Samples: []

### linear_translation:false:finite
- Prompt safe: True
- Aligned problems: 0
- TRUE / FALSE: 0 / 0
- Internal train / dev: 0 / 0
- Samples: []

### modified_lifted_magma:false:general
- Prompt safe: True
- Aligned problems: 0
- TRUE / FALSE: 0 / 0
- Internal train / dev: 0 / 0
- Samples: []

### rewrite_metatheorem:false:general
- Prompt safe: True
- Aligned problems: 0
- TRUE / FALSE: 0 / 0
- Internal train / dev: 0 / 0
- Samples: []

### subgraph_seed:false:general
- Prompt safe: True
- Aligned problems: 0
- TRUE / FALSE: 0 / 0
- Internal train / dev: 0 / 0
- Samples: []

### subgraph_seed:true:general
- Prompt safe: True
- Aligned problems: 0
- TRUE / FALSE: 0 / 0
- Internal train / dev: 0 / 0
- Samples: []

## Ranked Rule Bundles

### closure_guardrails
- Union problems covered: 524
- Prompt-family alignments: 524
- Internal-only alignments: 40
- Prompt evidence families: ['rewrite_metatheorem:true:general']
- Internal-only families: ['closure_transitive']

### fresh_var_true_override
- Union problems covered: 524
- Prompt-family alignments: 524
- Internal-only alignments: 40
- Prompt evidence families: ['rewrite_metatheorem:true:general']
- Internal-only families: ['closure_transitive']

### safe_true_core
- Union problems covered: 524
- Prompt-family alignments: 524
- Internal-only alignments: 0
- Prompt evidence families: ['rewrite_metatheorem:true:general']
- Internal-only families: []

### false_witness_routing
- Union problems covered: 474
- Prompt-family alignments: 807
- Internal-only alignments: 0
- Prompt evidence families: ['projection_family_counterexamples:false:general', 'small_finite_magma:false:finite']
- Internal-only families: []

### finite_witness_core
- Union problems covered: 443
- Prompt-family alignments: 443
- Internal-only alignments: 0
- Prompt evidence families: ['small_finite_magma:false:finite']
- Internal-only families: []

### singleton_shortcut
- Union problems covered: 243
- Prompt-family alignments: 243
- Internal-only alignments: 0
- Prompt evidence families: ['singleton_rewrite:true:general']
- Internal-only families: []

### invariant_false_lane
- Union problems covered: 67
- Prompt-family alignments: 67
- Internal-only alignments: 0
- Prompt evidence families: ['canonizer_confluence:false:general']
- Internal-only families: []

### finite_witness_escalation
- Union problems covered: 10
- Prompt-family alignments: 10
- Internal-only alignments: 0
- Prompt evidence families: ['all4x4_table_counterexamples:false:finite']
- Internal-only families: []
