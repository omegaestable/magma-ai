Champion: v13_proof_required
Aggregate: acc=0.450, true_acc=0.833, false_acc=0.067, parse=1.000

Failures:
- normal_balanced20_true10_false10_seed0: acc=0.500, true=0.900, false=0.100
  * normal_0027 gt=False pred=True
    E1: x * y = ((y * x) * x) * x
    E2: x = (x * x) * (y * (y * y))
  * normal_0703 gt=False pred=True
    E1: x * (y * z) = (z * x) * x
    E2: x * y = z * ((w * w) * w)
  * normal_0443 gt=False pred=True
    E1: x * y = ((x * x) * z) * x
    E2: x = (y * z) * ((x * w) * u)
  * normal_0411 gt=False pred=True
    E1: x = ((y * x) * x) * (y * x)
    E2: x = (x * y) * (y * (x * y))
- normal_balanced20_true10_false10_seed1: acc=0.450, true=0.800, false=0.100
  * normal_0357 gt=False pred=True
    E1: x * y = (y * y) * (y * x)
    E2: x = (y * (y * x)) * (z * x)
  * normal_0878 gt=False pred=True
    E1: x = y * ((y * x) * (x * x))
    E2: x = ((x * x) * x) * (x * y)
  * normal_0695 gt=False pred=True
    E1: x * y = z * (w * y)
    E2: x = (y * ((z * w) * w)) * u
  * normal_0803 gt=False pred=True
    E1: x * y = (z * y) * (y * y)
    E2: x * y = (z * (x * y)) * z
- normal_balanced20_true10_false10_seed2: acc=0.400, true=0.800, false=0.000
  * normal_0130 gt=False pred=True
    E1: x = (y * (x * (z * y))) * x
    E2: x = y * ((y * (z * x)) * z)
  * normal_0705 gt=False pred=True
    E1: x * x = ((x * x) * y) * z
    E2: x = (x * (y * y)) * (y * x)
  * normal_0630 gt=False pred=True
    E1: x = x * (x * ((y * z) * w))
    E2: x = ((y * y) * (y * y)) * x
  * normal_0425 gt=False pred=True
    E1: x * (y * z) = (y * y) * x
    E2: x = (y * ((z * y) * y)) * z
