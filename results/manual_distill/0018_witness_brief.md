=== VERIFIED WITNESS BRIEF (cycle 18) ===
Use these as external generation cues, not as unconditional rules.
Prefer witnesses that were actually verified on recent false positives.

[1] RP (n=2) :: x*y = y
    E1: x = ((y * x) * x) * (y * x)
    E2: x = (x * y) * (y * (x * y))
    verified fail on normal_0411: assignment x=0, y=1 gives LHS=0 RHS=1
[2] C0 (n=1) :: x*y = 0
    E1: x * y = (y * z) * (z * w)
    E2: x = x * ((x * x) * x)
    verified fail on normal_0218: assignment x=1 gives LHS=1 RHS=0
[3] XNOR (n=1) :: x*y = 1 iff x=y else 0
    E1: x = ((y * x) * x) * (y * x)
    E2: x = (x * y) * (y * (x * y))
    verified fail on normal_0411: assignment x=0, y=1 gives LHS=0 RHS=1
[4] XOR (n=1) :: x*y = (x+y) mod 2
    E1: x = ((y * x) * x) * (y * x)
    E2: x = (x * y) * (y * (x * y))
    verified fail on normal_0411: assignment x=0, y=1 gives LHS=0 RHS=1

=== END VERIFIED WITNESS BRIEF ===