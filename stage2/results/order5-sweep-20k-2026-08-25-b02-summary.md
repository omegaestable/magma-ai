# Sweep report: order5-sweep-20k-2026-08-25-b02

- rows: **5000**
- solved: **4922 (98.44%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **78**
- solver-claimed verdicts: {'true': 1045, 'false': 3877}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 2, 2
- seconds: total 38076.1, mean 7.615, p50 0.012, p95 9.372, p99 61.023, slowest solved 285.696

## Route families

- `witness`: 3339
- `completion`: 422
- `singleton`: 315
- `linear`: 307
- `egg_collapse`: 235
- `spine`: 189
- `equational_closure`: 23
- `local_model4`: 12
- `enum_fin3`: 10
- `derived_cp_closure`: 10
- `constancy`: 9
- `constraint_fin8`: 9
- `egg_bootstrap`: 9
- `egg_ladder`: 7
- `lemma_chain`: 7
- `affine`: 4
- `constraint_fin9`: 4
- `universal_identity`: 3
- `constraint_fin6`: 3
- `nested_square_singleton`: 1
- `egg_closure`: 1
- `lemma_bootstrap`: 1
- `tail_square_singleton`: 1
- `rewrite`: 1

## Failure clustering by hypothesis law

- eq1 `24199`: 2 failures
- eq1 `11362`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 70, 'eq1_vars': {3: 77, 2: 1}, 'eq1_ops': {5: 78}}

## Failure ledger

- `order5_39276_24088` [skip, label=unlabelled, 299.999s] eq1 `x = (((y * y) * (x * z)) * y) * x` => eq2 `x = ((x * y) * y) * ((y * x) * x)`
- `order5_15801_22260` [skip, label=unlabelled, 300.001s] eq1 `x = y * (((z * (y * x)) * x) * x)` => eq2 `x = (x * (x * y)) * ((y * x) * x)`
- `order5_10222_26638` [skip, label=unlabelled, 300.0s] eq1 `x = y * ((x * y) * ((z * y) * y))` => eq2 `x = ((x * x) * (y * x)) * (y * x)`
- `order5_41082_1393` [skip, label=unlabelled, 300.002s] eq1 `x = ((((y * y) * z) * x) * x) * z` => eq2 `x = y * (((z * z) * z) * z)`
- `order5_11977_47727` [skip, label=unlabelled, 299.995s] eq1 `x = y * (((x * y) * z) * (y * z))` => eq2 `x * x = (y * (x * x)) * (z * y)`
- `order5_12073_57821` [skip, label=unlabelled, 300.001s] eq1 `x = y * (((y * x) * x) * (z * z))` => eq2 `x * (y * z) = ((x * x) * x) * y`
- `order5_33020_28484` [skip, label=unlabelled, 300.002s] eq1 `x = (y * (((x * y) * z) * x)) * y` => eq2 `x = (((x * y) * y) * z) * (x * y)`
- `order5_9603_2738` [skip, label=unlabelled, 299.994s] eq1 `x = y * ((z * x) * (y * (x * y)))` => eq2 `x = ((y * y) * (x * y)) * z`
- `order5_44534_378` [skip, label=unlabelled, 300.001s] eq1 `x * y = y * ((x * (z * x)) * x)` => eq2 `x * y = (x * y) * y`
- `order5_14047_55788` [skip, label=unlabelled, 299.992s] eq1 `x = y * ((z * ((y * x) * x)) * x)` => eq2 `x * (y * x) = (x * z) * (y * x)`
- `order5_6005_29509` [skip, label=unlabelled, 300.001s] eq1 `x = y * (y * (z * ((x * y) * y)))` => eq2 `x = (y * (x * (y * (y * z)))) * z`
- `order5_27287_15258` [skip, label=unlabelled, 300.0s] eq1 `x = ((y * z) * (z * x)) * (z * x)` => eq2 `x = x * (((x * (y * z)) * y) * x)`
- `order5_7763_53593` [skip, label=unlabelled, 299.992s] eq1 `x = y * (y * ((z * (x * z)) * y))` => eq2 `x * y = (((z * z) * x) * y) * x`
- `order5_43963_60478` [skip, label=unlabelled, 300.001s] eq1 `x * y = z * ((z * y) * (y * x))` => eq2 `(x * y) * z = (x * y) * (z * z)`
- `order5_12820_24879` [skip, label=unlabelled, 300.0s] eq1 `x = y * ((x * (x * (z * z))) * y)` => eq2 `x = (x * (x * (x * y))) * (z * z)`
- `order5_48271_62103` [skip, label=unlabelled, 299.993s] eq1 `x * y = (z * (y * y)) * (y * x)` => eq2 `(x * y) * y = ((y * y) * x) * z`
- `order5_33029_27129` [skip, label=unlabelled, 299.994s] eq1 `x = (y * (((x * y) * z) * z)) * z` => eq2 `x = ((y * z) * (x * x)) * (y * x)`
- `order5_34947_39830` [skip, label=unlabelled, 299.992s] eq1 `x = ((y * y) * ((z * x) * y)) * z` => eq2 `x = (((x * (y * x)) * x) * y) * x`
- `order5_17883_3055` [skip, label=unlabelled, 299.989s] eq1 `x = (x * x) * (y * ((y * z) * z))` => eq2 `x = (((x * x) * y) * x) * x`
- `order5_18263_27751` [skip, label=unlabelled, 299.511s] eq1 `x = (y * y) * (y * ((z * x) * z))` => eq2 `x = ((y * (x * y)) * y) * (y * y)`
- `order5_5604_21379` [skip, label=unlabelled, 300.001s] eq1 `x = x * (x * (y * ((y * z) * y)))` => eq2 `x = (x * (x * y)) * (x * (z * x))`
- `order5_29551_56572` [skip, label=unlabelled, 299.997s] eq1 `x = (y * (x * (z * (y * y)))) * z` => eq2 `x * (x * y) = (z * (x * z)) * x`
- `order5_25178_26211` [skip, label=unlabelled, 300.0s] eq1 `x = (y * (x * (z * z))) * (x * y)` => eq2 `x = (y * ((y * z) * z)) * (y * z)`
- `order5_31267_57107` [skip, label=unlabelled, 299.988s] eq1 `x = (y * ((x * y) * (z * x))) * z` => eq2 `x * (y * z) = (z * (x * z)) * z`
- `order5_40956_60001` [skip, label=unlabelled, 299.999s] eq1 `x = ((((y * x) * z) * y) * z) * z` => eq2 `(x * x) * y = (x * x) * (y * x)`
- `order5_13764_25744` [skip, label=unlabelled, 299.99s] eq1 `x = y * ((x * ((z * y) * y)) * y)` => eq2 `x = (x * ((x * x) * x)) * (x * y)`
- `order5_17637_3521` [skip, label=unlabelled, 300.022s] eq1 `x = (y * z) * (z * (x * (y * y)))` => eq2 `x * y = x * ((y * y) * x)`
- `order5_11082_20489` [skip, label=unlabelled, 300.002s] eq1 `x = y * ((x * (y * x)) * (z * z))` => eq2 `x = (x * x) * (((x * y) * y) * x)`
- `order5_14658_7439` [skip, label=unlabelled, 300.0s] eq1 `x = y * (((x * z) * (z * y)) * y)` => eq2 `x = x * (y * ((y * (z * y)) * x))`
- `order5_13935_60992` [skip, label=unlabelled, 300.002s] eq1 `x = y * ((y * ((z * z) * z)) * x)` => eq2 `(x * x) * y = (z * (z * z)) * y`
- `order5_37736_11802` [skip, label=unlabelled, 299.996s] eq1 `x = ((y * (z * (y * x))) * z) * z` => eq2 `x = x * (((y * y) * x) * (x * z))`
- `order5_24199_22900` [skip, label=unlabelled, 300.004s] eq1 `x = ((y * x) * x) * ((x * z) * y)` => eq2 `x = (y * (z * z)) * ((x * y) * z)`
- `order5_24199_16549` [skip, label=unlabelled, 299.992s] eq1 `x = ((y * x) * x) * ((x * z) * y)` => eq2 `x = y * ((((y * z) * y) * z) * x)`
- `order5_9392_21184` [skip, label=unlabelled, 299.995s] eq1 `x = y * ((x * z) * (z * (x * y)))` => eq2 `x = (y * z) * (((z * z) * z) * z)`
- `order5_18364_26933` [skip, label=unlabelled, 300.0s] eq1 `x = (y * z) * (x * ((x * z) * y))` => eq2 `x = ((y * x) * (z * z)) * (x * z)`
- `order5_33998_36089` [skip, label=unlabelled, 300.001s] eq1 `x = ((y * y) * (x * (x * z))) * z` => eq2 `x = ((y * (z * z)) * (z * y)) * z`
- `order5_7837_46075` [skip, label=unlabelled, 299.996s] eq1 `x = y * (z * ((x * (x * y)) * z))` => eq2 `x * x = (y * z) * (z * (x * y))`
- `order5_31262_32500` [skip, label=unlabelled, 299.993s] eq1 `x = (y * ((x * y) * (y * z))) * y` => eq2 `x = (y * ((z * (y * z)) * x)) * z`
- `order5_7385_5666` [skip, label=unlabelled, 300.004s] eq1 `x = x * (y * ((x * (x * z)) * y))` => eq2 `x = x * (y * (y * ((x * y) * z)))`
- `order5_26646_23156` [skip, label=unlabelled, 299.984s] eq1 `x = ((x * x) * (y * y)) * (x * y)` => eq2 `x = ((x * x) * y) * (z * (z * y))`
- `order5_46500_45202` [skip, label=unlabelled, 300.001s] eq1 `x * y = (z * y) * (x * (y * x))` => eq2 `x * x = y * (((z * z) * y) * y)`
- `order5_30656_31366` [skip, label=unlabelled, 300.001s] eq1 `x = (y * (z * ((x * y) * y))) * z` => eq2 `x = (y * ((y * x) * (x * z))) * y`
- `order5_9345_39992` [skip, label=unlabelled, 299.997s] eq1 `x = y * ((x * y) * (z * (y * y)))` => eq2 `x = (((y * (x * x)) * y) * y) * y`
- `order5_40057_2306` [skip, label=unlabelled, 299.998s] eq1 `x = (((y * (x * z)) * x) * y) * y` => eq2 `x = (y * (x * (y * z))) * x`
- `order5_44539_318` [skip, label=unlabelled, 300.0s] eq1 `x * y = y * ((x * (z * y)) * y)` => eq2 `x * x = y * (z * x)`
- `order5_24606_17288` [skip, label=unlabelled, 299.996s] eq1 `x = ((y * z) * y) * ((z * x) * y)` => eq2 `x = (y * x) * (z * (z * (y * x)))`
- `order5_26403_4924` [skip, label=unlabelled, 300.001s] eq1 `x = (y * ((z * z) * x)) * (x * y)` => eq2 `x = y * (x * (x * (z * (y * z))))`
- `order5_32199_21364` [skip, label=unlabelled, 300.0s] eq1 `x = (y * ((x * (z * z)) * y)) * z` => eq2 `x = (x * (x * x)) * (y * (x * y))`
- `order5_59314_61140` [skip, label=unlabelled, 300.006s] eq1 `(x * y) * x = y * ((x * y) * z)` => eq2 `(x * y) * x = (z * (z * y)) * z`
- `order5_22619_9376` [skip, label=unlabelled, 300.001s] eq1 `x = (y * (y * x)) * ((z * z) * z)` => eq2 `x = y * ((x * z) * (y * (x * z)))`
- `order5_11362_61336` [skip, label=unlabelled, 300.001s] eq1 `x = y * ((z * (x * y)) * (y * z))` => eq2 `(x * y) * z = (x * (x * z)) * x`
- `order5_12900_59583` [skip, label=unlabelled, 299.997s] eq1 `x = y * ((x * (z * (z * x))) * y)` => eq2 `(x * y) * z = x * ((x * z) * y)`
- `order5_36932_59139` [skip, label=unlabelled, 300.0s] eq1 `x = (((y * z) * z) * (x * y)) * z` => eq2 `(x * x) * y = x * ((y * z) * z)`
- `order5_48904_57569` [skip, label=unlabelled, 300.0s] eq1 `x * y = ((y * x) * x) * (y * z)` => eq2 `x * (y * x) = ((y * y) * y) * y`
- `order5_20801_60037` [skip, label=unlabelled, 299.994s] eq1 `x = (y * x) * (((z * z) * z) * y)` => eq2 `(x * x) * y = (y * x) * (x * z)`
- `order5_27280_48050` [skip, label=unlabelled, 300.003s] eq1 `x = ((y * z) * (z * x)) * (x * y)` => eq2 `x * y = (y * (x * z)) * (z * x)`
- `order5_13510_30133` [skip, label=unlabelled, 300.015s] eq1 `x = x * ((x * ((y * z) * z)) * z)` => eq2 `x = (x * (x * ((x * y) * x))) * x`
- `order5_30289_20483` [skip, label=unlabelled, 299.999s] eq1 `x = (x * (y * ((z * z) * x))) * y` => eq2 `x = (x * x) * (((x * x) * y) * x)`
- `order5_20272_59137` [skip, label=unlabelled, 299.996s] eq1 `x = (y * z) * ((z * (x * z)) * y)` => eq2 `(x * x) * y = x * ((y * z) * x)`
- `order5_12854_16451` [skip, label=unlabelled, 300.001s] eq1 `x = y * ((x * (y * (z * y))) * z)` => eq2 `x = y * ((((y * x) * x) * x) * y)`
- `order5_11362_48612` [skip, label=unlabelled, 300.001s] eq1 `x = y * ((z * (x * y)) * (y * z))` => eq2 `x * x = ((y * x) * y) * (y * z)`
- `order5_18527_215` [skip, label=unlabelled, 299.984s] eq1 `x = (y * z) * (z * ((y * x) * y))` => eq2 `x = (x * (y * z)) * y`
- `order5_26291_44760` [skip, label=unlabelled, 300.008s] eq1 `x = (y * ((z * x) * z)) * (z * y)` => eq2 `x * y = z * ((y * (y * x)) * y)`
- `order5_9327_53436` [skip, label=unlabelled, 299.998s] eq1 `x = y * ((x * y) * (x * (z * y)))` => eq2 `x * y = (((z * x) * x) * x) * y`
- `order5_5066_2066` [skip, label=unlabelled, 300.0s] eq1 `x = y * (y * (x * (y * (z * y))))` => eq2 `x = ((x * y) * y) * (z * x)`
- `order5_14873_26998` [skip, label=unlabelled, 299.996s] eq1 `x = y * (((z * x) * (y * z)) * y)` => eq2 `x = ((y * y) * (x * z)) * (y * x)`
- `order5_35036_20547` [skip, label=unlabelled, 300.002s] eq1 `x = ((y * z) * ((x * y) * x)) * y` => eq2 `x = (x * y) * (((x * y) * y) * y)`
- `order5_22446_49455` [skip, label=unlabelled, 300.001s] eq1 `x = (y * (x * x)) * ((x * z) * z)` => eq2 `x * x = (x * (y * (y * z))) * z`
- `order5_15820_51758` [skip, label=unlabelled, 299.996s] eq1 `x = y * (((z * (y * y)) * x) * z)` => eq2 `x * y = ((z * y) * (x * x)) * x`
- `order5_45452_55819` [skip, label=unlabelled, 300.0s] eq1 `x * y = y * (((y * z) * y) * x)` => eq2 `x * (y * x) = (y * y) * (z * z)`
- `order5_15657_53851` [skip, label=unlabelled, 299.98s] eq1 `x = y * (((y * (z * x)) * z) * z)` => eq2 `x * (x * x) = y * (z * (z * y))`
- `order5_37581_5396` [skip, label=unlabelled, 300.0s] eq1 `x = ((y * (y * (z * x))) * z) * y` => eq2 `x = y * (z * (z * (z * (z * x))))`
- `order5_36579_1674` [skip, label=unlabelled, 299.999s] eq1 `x = (((y * x) * z) * (z * x)) * y` => eq2 `x = (x * y) * ((z * z) * z)`
- `order5_34794_35520` [skip, label=unlabelled, 300.001s] eq1 `x = ((y * x) * ((z * x) * y)) * x` => eq2 `x = ((x * (y * z)) * (x * y)) * x`
- `order5_26344_42654` [skip, label=unlabelled, 299.996s] eq1 `x = (y * ((z * y) * y)) * (x * z)` => eq2 `x * y = x * (y * ((x * z) * z))`
- `order5_13566_47051` [skip, label=unlabelled, 300.0s] eq1 `x = x * ((y * ((y * y) * x)) * z)` => eq2 `x * y = (x * y) * ((z * x) * x)`
- `order5_38282_29760` [skip, label=unlabelled, 300.001s] eq1 `x = ((y * ((x * y) * z)) * x) * y` => eq2 `x = (y * (z * (x * (x * y)))) * x`
- `order5_13098_52504` [skip, label=unlabelled, 300.0s] eq1 `x = y * ((z * (x * (x * y))) * y)` => eq2 `x * y = ((y * (z * y)) * y) * z`
