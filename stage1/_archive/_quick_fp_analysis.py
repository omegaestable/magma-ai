import json

data = [json.loads(l) for l in open('data/benchmark/mixed_hard23_balanced60_true30_false30_rotation0013_20260414_010332.jsonl')]

tns = ['hard3_0041', 'hard3_0125', 'hard3_0217']
fps = ['hard2_0016','hard3_0242','hard2_0172','hard2_0195','hard3_0059',
       'hard3_0264','hard2_0161','hard3_0277','hard2_0125','hard3_0143',
       'hard3_0358','hard2_0102','hard2_0112','hard2_0009','hard2_0096',
       'hard3_0031','hard3_0029','hard2_0067','hard2_0043','hard3_0185','hard3_0339']

print("=== CORRECTLY CAUGHT FALSE (TN) ===")
for d in data:
    if d['id'] in tns:
        print(f"\n{d['id']}:")
        print(f"  eq1: {d['equation1']}")
        print(f"  eq2: {d['equation2']}")

print("\n\n=== FIRST 5 FALSE POSITIVES (missed FALSE) ===")
shown = 0
for d in data:
    if d['id'] in fps and shown < 5:
        print(f"\n{d['id']}:")
        print(f"  eq1: {d['equation1']}")
        print(f"  eq2: {d['equation2']}")
        shown += 1
