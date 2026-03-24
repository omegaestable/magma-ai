=== VERIFIED WITNESS BRIEF (cycle 21) ===
Use these as external generation cues, not as unconditional rules.
Prefer witnesses that were actually verified on recent false positives.

[1] RP (n=6) :: x*y = y
    E1: x * x = x * (x * (x * x))
    E2: x = x * ((y * (y * z)) * y)
    verified fail on normal_0283: assignment x=0, y=1, z=0 gives LHS=0 RHS=1
[2] XNOR (n=6) :: x*y = 1 iff x=y else 0
    E1: x * x = x * (x * (x * x))
    E2: x = x * ((y * (y * z)) * y)
    verified fail on normal_0283: assignment x=0, y=0, z=1 gives LHS=0 RHS=1
[3] XOR (n=6) :: x*y = (x+y) mod 2
    E1: x * x = x * (x * (x * x))
    E2: x = x * ((y * (y * z)) * y)
    verified fail on normal_0283: assignment x=0, y=0, z=1 gives LHS=0 RHS=1
[4] C0 (n=4) :: x*y = 0
    E1: x * x = x * (x * (x * x))
    E2: x = x * ((y * (y * z)) * y)
    verified fail on normal_0283: assignment x=1, y=0, z=0 gives LHS=1 RHS=0
[5] AND (n=2) :: x*y = x AND y
    E1: x * x = x * (x * (x * x))
    E2: x = x * ((y * (y * z)) * y)
    verified fail on normal_0283: assignment x=1, y=0, z=0 gives LHS=1 RHS=0

=== END VERIFIED WITNESS BRIEF ===