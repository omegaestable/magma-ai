import json

problems = [json.loads(line) for line in open('data/benchmark/hard2_balanced30_true15_false15_rotation0022_20260417_145804.jsonl')]
done_ids = {'hard2_0198','hard2_0182','hard2_0192','hard2_0126','hard2_0150',
            'hard2_0005','hard2_0122','hard2_0127','hard2_0023','hard2_0090',
            'hard2_0110','hard2_0097','hard2_0140','hard2_0014','hard2_0086'}
remaining = [p for p in problems if p['id'] not in done_ids]
rt = sum(1 for p in remaining if p['answer'])
rf = len(remaining) - rt
print(f'Remaining: {len(remaining)} ({rt}T, {rf}F)')
print()
for p in remaining:
    gt = 'T' if p['answer'] else 'F'
    pid = p['id']
    eq1 = p['equation1']
    eq2 = p['equation2']
    print(f'  {pid:>12}  gt={gt}  eq1={eq1}')
    print(f'               eq2={eq2}')
