=== VERIFIED WITNESS BRIEF (cycle 19) ===
Use these as external generation cues, not as unconditional rules.
Prefer witnesses that were actually verified on recent false positives.

[1] RP (n=1) :: x*y = y
    E1: x = ((y * y) * z) * (w * x)
    E2: x = x * ((y * y) * (y * y))
    verified fail on normal_0857: assignment x=0, y=1 gives LHS=0 RHS=1

=== END VERIFIED WITNESS BRIEF ===