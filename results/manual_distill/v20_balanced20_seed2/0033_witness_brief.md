=== VERIFIED WITNESS BRIEF (cycle 33) ===
Use these as external generation cues, not as unconditional rules.
Prefer witnesses that were actually verified on recent false positives.

[1] RP (n=1) :: x*y = y
    E1: x = y * ((y * x) * x)
    E2: (x * y) * y = (y * x) * x
    verified fail on normal_0415: assignment x=0, y=1 gives LHS=1 RHS=0

=== END VERIFIED WITNESS BRIEF ===