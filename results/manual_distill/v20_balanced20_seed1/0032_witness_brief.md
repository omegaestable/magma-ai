=== VERIFIED WITNESS BRIEF (cycle 32) ===
Use these as external generation cues, not as unconditional rules.
Prefer witnesses that were actually verified on recent false positives.

[1] C0 (n=2) :: x*y = 0
    E1: x * (y * z) = (y * z) * w
    E2: x = (x * x) * (y * (y * y))
    verified fail on normal_0612: assignment x=1, y=0 gives LHS=1 RHS=0
[2] LP (n=1) :: x*y = x
    E1: x * y = x * (x * (x * x))
    E2: x = (((y * z) * w) * u) * x
    verified fail on normal_0799: assignment u=0, w=0, x=0, y=1, z=0 gives LHS=0 RHS=1
[3] RP (n=1) :: x*y = y
    E1: x = (y * (x * (z * y))) * x
    E2: x = y * ((y * (z * x)) * z)
    verified fail on normal_0130: assignment x=0, y=0, z=1 gives LHS=0 RHS=1

=== END VERIFIED WITNESS BRIEF ===