=== VERIFIED WITNESS BRIEF (cycle 31) ===
Use these as external generation cues, not as unconditional rules.
Prefer witnesses that were actually verified on recent false positives.

[1] C0 (n=1) :: x*y = 0
    E1: x * (x * y) = (x * z) * y
    E2: x = ((x * x) * x) * (y * z)
    verified fail on normal_0790: assignment x=1, y=0, z=0 gives LHS=1 RHS=0
[2] RP (n=1) :: x*y = y
    E1: x * (x * y) = (x * z) * y
    E2: x = ((x * x) * x) * (y * z)
    verified fail on normal_0790: assignment x=0, y=0, z=1 gives LHS=0 RHS=1

=== END VERIFIED WITNESS BRIEF ===