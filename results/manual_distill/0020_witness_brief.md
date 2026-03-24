=== VERIFIED WITNESS BRIEF (cycle 20) ===
Use these as external generation cues, not as unconditional rules.
Prefer witnesses that were actually verified on recent false positives.

[1] C0 (n=4) :: x*y = 0
    E1: x * y = z * (w * y)
    E2: x = (y * ((z * w) * w)) * u
    verified fail on normal_0695: assignment u=0, w=0, x=1, y=0, z=0 gives LHS=1 RHS=0
[2] RP (n=4) :: x*y = y
    E1: x * y = z * (w * y)
    E2: x = (y * ((z * w) * w)) * u
    verified fail on normal_0695: assignment u=0, w=0, x=1, y=0, z=0 gives LHS=1 RHS=0
[3] XNOR (n=4) :: x*y = 1 iff x=y else 0
    E1: x = ((y * z) * (x * z)) * y
    E2: x * y = (z * (w * y)) * z
    verified fail on normal_0458: assignment w=0, x=1, y=0, z=0 gives LHS=0 RHS=1
[4] XOR (n=4) :: x*y = (x+y) mod 2
    E1: x = ((y * z) * (x * z)) * y
    E2: x * y = (z * (w * y)) * z
    verified fail on normal_0458: assignment w=0, x=1, y=0, z=0 gives LHS=1 RHS=0
[5] AND (n=1) :: x*y = x AND y
    E1: x * y = (y * y) * (y * x)
    E2: x = (y * (y * x)) * (z * x)
    verified fail on normal_0357: assignment x=1, y=0, z=0 gives LHS=1 RHS=0

=== END VERIFIED WITNESS BRIEF ===