# Raw campaign archive manifest

Updated: 2026-08-30

The archives below contain ignored output from completed campaigns and the
pre-deadline scratch-tree snapshot. Tracked per-batch Markdown summaries,
aggregate failure ledgers, fixtures, and accepted certificates remain in their
canonical repository locations.

| Archive | Files | Uncompressed bytes | Archive bytes | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `2026-08-25-order4-100k-shards.zip` | 40 | 62,157,789 | 4,127,434 | `d94f4429b6808a9e08dfe94327fd2d50c21459953304e8d3fa02dec9feb6fdbe` |
| `2026-08-26-order4-200k-shards.zip` | 80 | 124,317,076 | 8,255,073 | `27b8cc77d0a56c520d0a395df759ba1754a4836fe6742d14d808158cf7f0190c` |
| `2026-08-27-order4-200k-shards.zip` | 80 | 124,337,022 | 8,269,196 | `34a3e85bda3d8c1810e8702cdb2e1430ca653e48c3d3b7fc54f0403a0b164326` |
| `2026-08-29-order4-400k-shards.zip` | 80 | 249,213,098 | 16,056,949 | `418026a9521e7b730dd4c8c9f7c657a0900536a516abc4bb44180e23ddda6503` |
| `tmp-stage2-smoke-through-2026-08-30.zip` | 21,226 | 122,469,288 | 35,786,384 | `4401f58ffc67d649e40a80152dfa38d3943b6db0d5659eb61c283f72ef9e26ae` |

Recovery:

```powershell
Expand-Archive stage2/results/raw/<archive>.zip stage2/results/raw/restored/<archive>
```
