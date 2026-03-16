"""Check if benchmark equations can be matched to the 4694 equation list."""
import json

# Load equations - map normalized text to index
eqs_to_idx = {}
with open('data/exports/equations.txt', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        normalized = line.strip().replace('\u25c7', '*').replace(' ', '')
        eqs_to_idx[normalized] = i

def normalize(eq_text):
    return eq_text.replace(' ', '')

def match_eq(eq_text):
    n = normalize(eq_text)
    return eqs_to_idx.get(n)

found_e1 = 0
found_e2 = 0
not_found_e1 = []
not_found_e2 = []

for fname in ['data/benchmark/hard.jsonl', 'data/benchmark/normal.jsonl']:
    with open(fname) as f:
        for line in f:
            d = json.loads(line)
            idx1 = match_eq(d['equation1'])
            idx2 = match_eq(d['equation2'])
            if idx1:
                found_e1 += 1
            else:
                not_found_e1.append(d['equation1'])
            if idx2:
                found_e2 += 1
            else:
                not_found_e2.append(d['equation2'])

print(f"E1 found: {found_e1}, not found: {len(not_found_e1)}")
print(f"E2 found: {found_e2}, not found: {len(not_found_e2)}")
if not_found_e1:
    print(f"Sample E1 not found: {not_found_e1[:5]}")
if not_found_e2:
    print(f"Sample E2 not found: {not_found_e2[:5]}")
