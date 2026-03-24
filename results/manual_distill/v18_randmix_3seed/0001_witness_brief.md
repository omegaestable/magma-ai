=== VERIFIED WITNESS BRIEF (cycle 1) ===
Use these as external generation cues, not as unconditional rules.
Prefer witnesses that were actually verified on recent false positives.

[1] C0 (n=3) :: x*y = 0
    E1: x * y = (y * y) * x
    E2: x = x * (y * ((x * x) * y))
    verified fail on normal_0546: assignment x=1, y=0 gives LHS=1 RHS=0
[2] LP (n=3) :: x*y = x
    E1: x = (x * x) * (y * (y * x))
    E2: x = (y * ((x * x) * y)) * x
    verified fail on normal_0915: assignment x=0, y=1 gives LHS=0 RHS=1
[3] AND (n=2) :: x*y = x AND y
    E1: x * y = (y * y) * x
    E2: x = x * (y * ((x * x) * y))
    verified fail on normal_0546: assignment x=1, y=0 gives LHS=1 RHS=0
[4] OR (n=2) :: x*y = x OR y
    E1: x * y = (y * y) * x
    E2: x = x * (y * ((x * x) * y))
    verified fail on normal_0546: assignment x=0, y=1 gives LHS=0 RHS=1
[5] RP (n=2) :: x*y = y
    E1: x * x = (y * (x * z)) * x
    E2: x * y = y * (x * x)
    verified fail on normal_0736: assignment x=0, y=1 gives LHS=1 RHS=0

=== END VERIFIED WITNESS BRIEF ===