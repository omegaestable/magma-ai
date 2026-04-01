#!/usr/bin/env python3
"""Test the full v22 cheatsheet template rendering."""
import json
import jinja2
from pathlib import Path

template_text = Path("cheatsheets/v22_lookup.txt").read_text(encoding="utf-8")

# Test cases with known answers from v21f examples
test_cases = [
    # Example A from v21f — FALSE via C0
    ("x * y = (y * x) * x", "x = (x * y) * z", False),
    # Example B from v21f — FALSE via LP
    ("x = x * (y * z)", "(x * x) * y = (y * x) * z", False),
    # Example C from v21f — TRUE (no separation)
    ("x = (y * x) * (z * (w * y))", "x = ((y * x) * x) * x", True),
    # Simple TRUE: x = x
    ("x = x * (x * x)", "x = x * (x * x)", True),
    # Gap table pair: Eq321->Eq374
    ("x * y = x * (x * x)", "x * y = (x * x) * y", False),
]

print("Testing v22 cheatsheet rendering ...\n")
for eq1, eq2, expected in test_cases:
    try:
        rendered = jinja2.Template(template_text).render(
            equation1=eq1,
            equation2=eq2,
        )
        # Extract verdict
        verdict = None
        for line in rendered.split('\n'):
            if line.strip().startswith('VERDICT:'):
                v = line.strip().split('VERDICT:')[1].strip()
                verdict = v == 'TRUE'
                break
        
        status = "✓" if verdict == expected else "✗"
        print(f"  {status} E1='{eq1}' E2='{eq2}'")
        print(f"    Expected={expected} Got={verdict}")
        if verdict != expected:
            print(f"    RENDERED OUTPUT:")
            print(rendered)
            print("---")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        break

print("\nDone.")
