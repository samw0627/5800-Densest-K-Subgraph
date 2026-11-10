# Dataset: k-Cluster Benchmark Graphs

These are the benchmark graphs for the Densest k-Subgraph (k-cluster) problem, from the [CEDRIC/CNAM k-cluster library](https://cedric.cnam.fr/~lamberta/Library/k-cluster.html). The library also publishes [optimal values](https://cedric.cnam.fr/~lamberta/Library/solutions_k-cluster.html), but they are **not** included in this folder.

All numbers below were computed from the files themselves.

## Contents

- **90 graph files** (`.txt`) and the original `README.txt`.
- Graph sizes n ∈ {40, 80, 100, 120, 140, 160} and target edge densities d ∈ {25%, 50%, 75%}.
- **5 instances** for each (n, d) pair: 6 × 3 × 5 = 90 graphs.
- Each graph gives **3 problem instances**, with k = n/4, n/2 and 3n/4, for **270 problems** in total.

The value of k is **not** stored in the files. You pick it when you build a problem from a graph.

## File naming

Files from different sizes use three different naming schemes:

| n | Pattern | Example | Weight column |
|---|---|---|---|
| 40 | `PB{i}_d{dd}.txt` | `PB3_d025.txt` | `0.500000` |
| 80, 100 | `ALEA{i}n{n}_d{dd}_method2.txt` | `ALEA2n80_d05_method2.txt` | `0.500000` |
| 120, 140, 160 | `PB{i}_n{n}_d{ddd}.txt` | `PB1_n160_d050.txt` | `1` |

- `{i}` is the instance number, 1 to 5.
- The density code is inconsistent. In the first two schemes, 25%, 50% and 75% are written `d025`, `d05` and `d075`. In the third scheme, they're written `d025`, `d050` and `d075`.
- A loader should parse n and d from the filename with a regex for each scheme, or read n from the header (see below).

Mapping to the brief's `kcluster{n}_{density}_{k}_{instance}.dat` names: those names refer to *problems* (graph + k). These files are *graphs*. For example, `kcluster160_050_40_3` is the graph `PB3_n160_d050.txt` with k = 40.

## File format

```
n m
i j w
i j w
...
```

- **Line 1:** `n m`, the number of vertices and the number of edges. There is no k on this line. Some header lines have a trailing space.
- **Lines 2 to m+1:** one undirected edge per line, `i j w`.
  - Vertices are **1-indexed** (1 to n).
  - Every edge has i < j, and each edge is listed once.
  - `w` is a constant: `0.500000` for n ≤ 100 and `1` for n ≥ 120. It carries no information, so **treat every graph as unweighted** and ignore the third column.
- Line endings are Unix (LF).

### Minimal Python loader

```python
def load_graph(path):
    with open(path) as f:
        n, m = map(int, f.readline().split())
        edges = [tuple(int(x) - 1 for x in line.split()[:2])  # convert to 0-indexed
                 for line in f if line.strip()]
    assert len(edges) == m
    return n, edges
```

## Validation checks (all 90 files pass)

- The number of edge lines equals the `m` in the header.
- All vertex indices are in [1, n], and every vertex has degree ≥ 2 (no isolated vertices).
- Every edge has i < j, with no duplicate edges and no self-loops.
- No two files are identical.

## How the graphs were generated

The two size groups appear to come from different generators:

- **n = 40, 80, 100:** the edge count varies between instances. Realized density ranges from 0.231 to 0.279 for d = 25%, 0.487 to 0.537 for d = 50%, and 0.740 to 0.762 for d = 75%. This matches G(n, p), where each edge is included independently with probability d.
- **n = 120, 140, 160:** all 5 instances of each (n, d) have **exactly** the same edge count, round(d · n(n−1)/2). For example, every `n160_d050` graph has 6360 edges. This matches G(n, m), with a fixed number of edges chosen uniformly at random. The 5 instances are still different graphs.

None of the graphs has a planted dense subgraph, so the optimum k-subgraph is only slightly denser than the graph as a whole.

## Summary by group

Each group has 5 instances.

| n | d | Edges m (min to max) | Realized density (mean) | k values |
|---|---|---|---|---|
| 40 | 25% | 180 to 218 | 0.249 | 10, 20, 30 |
| 40 | 50% | 381 to 419 | 0.509 | 10, 20, 30 |
| 40 | 75% | 577 to 588 | 0.747 | 10, 20, 30 |
| 80 | 25% | 769 to 819 | 0.251 | 20, 40, 60 |
| 80 | 50% | 1550 to 1592 | 0.496 | 20, 40, 60 |
| 80 | 75% | 2353 to 2392 | 0.750 | 20, 40, 60 |
| 100 | 25% | 1200 to 1274 | 0.247 | 25, 50, 75 |
| 100 | 50% | 2411 to 2496 | 0.492 | 25, 50, 75 |
| 100 | 75% | 3665 to 3771 | 0.754 | 25, 50, 75 |
| 120 | 25% | 1785 | 0.250 | 30, 60, 90 |
| 120 | 50% | 3570 | 0.500 | 30, 60, 90 |
| 120 | 75% | 5355 | 0.750 | 30, 60, 90 |
| 140 | 25% | 2433 | 0.250 | 35, 70, 105 |
| 140 | 50% | 4865 | 0.500 | 35, 70, 105 |
| 140 | 75% | 7298 | 0.750 | 35, 70, 105 |
| 160 | 25% | 3180 | 0.250 | 40, 80, 120 |
| 160 | 50% | 6360 | 0.500 | 40, 80, 120 |
| 160 | 75% | 9540 | 0.750 | 40, 80, 120 |

## Notes for experiments

- **Brute force is not practical on any of these graphs.** The smallest problem, n = 40 with k = 10, already has C(40, 10) ≈ 8.5 × 10⁸ subsets, and the n = 40, k = 20 problems have about 1.4 × 10¹¹. Use the published optima as ground truth, and test brute force on smaller graphs or subgraphs.
- The published optimum is a count of edges. Some papers report weighted values, which with the 0.5 weight would be half the edge count. Check this when comparing.
- Greedy peeling is likely to do best at k = 3n/4 and to show the largest gaps on the sparse (25%) graphs.

## Per-graph statistics

| n | d | # | File | m | Density | Min deg | Max deg | Avg deg | k = n/4, n/2, 3n/4 |
|---|---|---|---|---|---|---|---|---|---|
| 40 | 25% | 1 | `PB1_d025.txt` | 183 | 0.235 | 4 | 15 | 9.2 | 10, 20, 30 |
| 40 | 25% | 2 | `PB2_d025.txt` | 218 | 0.279 | 7 | 15 | 10.9 | 10, 20, 30 |
| 40 | 25% | 3 | `PB3_d025.txt` | 206 | 0.264 | 5 | 15 | 10.3 | 10, 20, 30 |
| 40 | 25% | 4 | `PB4_d025.txt` | 184 | 0.236 | 3 | 14 | 9.2 | 10, 20, 30 |
| 40 | 25% | 5 | `PB5_d025.txt` | 180 | 0.231 | 2 | 15 | 9.0 | 10, 20, 30 |
| 40 | 50% | 1 | `PB1_d05.txt` | 381 | 0.488 | 12 | 25 | 19.1 | 10, 20, 30 |
| 40 | 50% | 2 | `PB2_d05.txt` | 419 | 0.537 | 15 | 29 | 20.9 | 10, 20, 30 |
| 40 | 50% | 3 | `PB3_d05.txt` | 408 | 0.523 | 15 | 28 | 20.4 | 10, 20, 30 |
| 40 | 50% | 4 | `PB4_d05.txt` | 393 | 0.504 | 12 | 26 | 19.6 | 10, 20, 30 |
| 40 | 50% | 5 | `PB5_d05.txt` | 384 | 0.492 | 12 | 27 | 19.2 | 10, 20, 30 |
| 40 | 75% | 1 | `PB1_d075.txt` | 577 | 0.740 | 23 | 34 | 28.9 | 10, 20, 30 |
| 40 | 75% | 2 | `PB2_d075.txt` | 584 | 0.749 | 23 | 35 | 29.2 | 10, 20, 30 |
| 40 | 75% | 3 | `PB3_d075.txt` | 588 | 0.754 | 22 | 35 | 29.4 | 10, 20, 30 |
| 40 | 75% | 4 | `PB4_d075.txt` | 584 | 0.749 | 23 | 34 | 29.2 | 10, 20, 30 |
| 40 | 75% | 5 | `PB5_d075.txt` | 579 | 0.742 | 24 | 37 | 28.9 | 10, 20, 30 |
| 80 | 25% | 1 | `ALEA1n80_d025_method2.txt` | 788 | 0.249 | 13 | 28 | 19.7 | 20, 40, 60 |
| 80 | 25% | 2 | `ALEA2n80_d025_method2.txt` | 769 | 0.243 | 9 | 28 | 19.2 | 20, 40, 60 |
| 80 | 25% | 3 | `ALEA3n80_d025_method2.txt` | 786 | 0.249 | 10 | 27 | 19.6 | 20, 40, 60 |
| 80 | 25% | 4 | `ALEA4n80_d025_method2.txt` | 809 | 0.256 | 14 | 29 | 20.2 | 20, 40, 60 |
| 80 | 25% | 5 | `ALEA5n80_d025_method2.txt` | 819 | 0.259 | 13 | 28 | 20.5 | 20, 40, 60 |
| 80 | 50% | 1 | `ALEA1n80_d05_method2.txt` | 1556 | 0.492 | 31 | 53 | 38.9 | 20, 40, 60 |
| 80 | 50% | 2 | `ALEA2n80_d05_method2.txt` | 1550 | 0.491 | 27 | 51 | 38.8 | 20, 40, 60 |
| 80 | 50% | 3 | `ALEA3n80_d05_method2.txt` | 1577 | 0.499 | 26 | 48 | 39.4 | 20, 40, 60 |
| 80 | 50% | 4 | `ALEA4n80_d05_method2.txt` | 1563 | 0.495 | 27 | 49 | 39.1 | 20, 40, 60 |
| 80 | 50% | 5 | `ALEA5n80_d05_method2.txt` | 1592 | 0.504 | 29 | 51 | 39.8 | 20, 40, 60 |
| 80 | 75% | 1 | `ALEA1n80_d075_method2.txt` | 2365 | 0.748 | 49 | 68 | 59.1 | 20, 40, 60 |
| 80 | 75% | 2 | `ALEA2n80_d075_method2.txt` | 2361 | 0.747 | 47 | 69 | 59.0 | 20, 40, 60 |
| 80 | 75% | 3 | `ALEA3n80_d075_method2.txt` | 2392 | 0.757 | 50 | 67 | 59.8 | 20, 40, 60 |
| 80 | 75% | 4 | `ALEA4n80_d075_method2.txt` | 2372 | 0.751 | 50 | 70 | 59.3 | 20, 40, 60 |
| 80 | 75% | 5 | `ALEA5n80_d075_method2.txt` | 2353 | 0.745 | 51 | 67 | 58.8 | 20, 40, 60 |
| 100 | 25% | 1 | `ALEA1n100_d025_method2.txt` | 1211 | 0.245 | 15 | 36 | 24.2 | 25, 50, 75 |
| 100 | 25% | 2 | `ALEA2n100_d025_method2.txt` | 1205 | 0.243 | 15 | 36 | 24.1 | 25, 50, 75 |
| 100 | 25% | 3 | `ALEA3n100_d025_method2.txt` | 1234 | 0.249 | 15 | 34 | 24.7 | 25, 50, 75 |
| 100 | 25% | 4 | `ALEA4n100_d025_method2.txt` | 1200 | 0.242 | 15 | 37 | 24.0 | 25, 50, 75 |
| 100 | 25% | 5 | `ALEA5n100_d025_method2.txt` | 1274 | 0.257 | 13 | 36 | 25.5 | 25, 50, 75 |
| 100 | 50% | 1 | `ALEA1n100_d05_method2.txt` | 2417 | 0.488 | 30 | 62 | 48.3 | 25, 50, 75 |
| 100 | 50% | 2 | `ALEA2n100_d05_method2.txt` | 2496 | 0.504 | 39 | 58 | 49.9 | 25, 50, 75 |
| 100 | 50% | 3 | `ALEA3n100_d05_method2.txt` | 2411 | 0.487 | 37 | 60 | 48.2 | 25, 50, 75 |
| 100 | 50% | 4 | `ALEA4n100_d05_method2.txt` | 2422 | 0.489 | 38 | 60 | 48.4 | 25, 50, 75 |
| 100 | 50% | 5 | `ALEA5n100_d05_method2.txt` | 2426 | 0.490 | 35 | 58 | 48.5 | 25, 50, 75 |
| 100 | 75% | 1 | `ALEA1n100_d075_method2.txt` | 3665 | 0.740 | 62 | 82 | 73.3 | 25, 50, 75 |
| 100 | 75% | 2 | `ALEA2n100_d075_method2.txt` | 3700 | 0.747 | 62 | 84 | 74.0 | 25, 50, 75 |
| 100 | 75% | 3 | `ALEA3n100_d075_method2.txt` | 3771 | 0.762 | 63 | 86 | 75.4 | 25, 50, 75 |
| 100 | 75% | 4 | `ALEA4n100_d075_method2.txt` | 3770 | 0.762 | 63 | 88 | 75.4 | 25, 50, 75 |
| 100 | 75% | 5 | `ALEA5n100_d075_method2.txt` | 3760 | 0.760 | 65 | 85 | 75.2 | 25, 50, 75 |
| 120 | 25% | 1 | `PB1_n120_d025.txt` | 1785 | 0.250 | 18 | 41 | 29.8 | 30, 60, 90 |
| 120 | 25% | 2 | `PB2_n120_d025.txt` | 1785 | 0.250 | 18 | 44 | 29.8 | 30, 60, 90 |
| 120 | 25% | 3 | `PB3_n120_d025.txt` | 1785 | 0.250 | 17 | 42 | 29.8 | 30, 60, 90 |
| 120 | 25% | 4 | `PB4_n120_d025.txt` | 1785 | 0.250 | 19 | 42 | 29.8 | 30, 60, 90 |
| 120 | 25% | 5 | `PB5_n120_d025.txt` | 1785 | 0.250 | 17 | 40 | 29.8 | 30, 60, 90 |
| 120 | 50% | 1 | `PB1_n120_d050.txt` | 3570 | 0.500 | 43 | 72 | 59.5 | 30, 60, 90 |
| 120 | 50% | 2 | `PB2_n120_d050.txt` | 3570 | 0.500 | 46 | 77 | 59.5 | 30, 60, 90 |
| 120 | 50% | 3 | `PB3_n120_d050.txt` | 3570 | 0.500 | 47 | 74 | 59.5 | 30, 60, 90 |
| 120 | 50% | 4 | `PB4_n120_d050.txt` | 3570 | 0.500 | 47 | 70 | 59.5 | 30, 60, 90 |
| 120 | 50% | 5 | `PB5_n120_d050.txt` | 3570 | 0.500 | 39 | 72 | 59.5 | 30, 60, 90 |
| 120 | 75% | 1 | `PB1_n120_d075.txt` | 5355 | 0.750 | 76 | 101 | 89.2 | 30, 60, 90 |
| 120 | 75% | 2 | `PB2_n120_d075.txt` | 5355 | 0.750 | 76 | 103 | 89.2 | 30, 60, 90 |
| 120 | 75% | 3 | `PB3_n120_d075.txt` | 5355 | 0.750 | 78 | 101 | 89.2 | 30, 60, 90 |
| 120 | 75% | 4 | `PB4_n120_d075.txt` | 5355 | 0.750 | 80 | 99 | 89.2 | 30, 60, 90 |
| 120 | 75% | 5 | `PB5_n120_d075.txt` | 5355 | 0.750 | 77 | 99 | 89.2 | 30, 60, 90 |
| 140 | 25% | 1 | `PB1_n140_d025.txt` | 2433 | 0.250 | 20 | 47 | 34.8 | 35, 70, 105 |
| 140 | 25% | 2 | `PB2_n140_d025.txt` | 2433 | 0.250 | 24 | 46 | 34.8 | 35, 70, 105 |
| 140 | 25% | 3 | `PB3_n140_d025.txt` | 2433 | 0.250 | 23 | 46 | 34.8 | 35, 70, 105 |
| 140 | 25% | 4 | `PB4_n140_d025.txt` | 2433 | 0.250 | 21 | 46 | 34.8 | 35, 70, 105 |
| 140 | 25% | 5 | `PB5_n140_d025.txt` | 2433 | 0.250 | 22 | 49 | 34.8 | 35, 70, 105 |
| 140 | 50% | 1 | `PB1_n140_d050.txt` | 4865 | 0.500 | 54 | 84 | 69.5 | 35, 70, 105 |
| 140 | 50% | 2 | `PB2_n140_d050.txt` | 4865 | 0.500 | 58 | 83 | 69.5 | 35, 70, 105 |
| 140 | 50% | 3 | `PB3_n140_d050.txt` | 4865 | 0.500 | 56 | 81 | 69.5 | 35, 70, 105 |
| 140 | 50% | 4 | `PB4_n140_d050.txt` | 4865 | 0.500 | 53 | 82 | 69.5 | 35, 70, 105 |
| 140 | 50% | 5 | `PB5_n140_d050.txt` | 4865 | 0.500 | 56 | 81 | 69.5 | 35, 70, 105 |
| 140 | 75% | 1 | `PB1_n140_d075.txt` | 7298 | 0.750 | 89 | 116 | 104.3 | 35, 70, 105 |
| 140 | 75% | 2 | `PB2_n140_d075.txt` | 7298 | 0.750 | 91 | 116 | 104.3 | 35, 70, 105 |
| 140 | 75% | 3 | `PB3_n140_d075.txt` | 7298 | 0.750 | 91 | 115 | 104.3 | 35, 70, 105 |
| 140 | 75% | 4 | `PB4_n140_d075.txt` | 7298 | 0.750 | 91 | 116 | 104.3 | 35, 70, 105 |
| 140 | 75% | 5 | `PB5_n140_d075.txt` | 7298 | 0.750 | 93 | 118 | 104.3 | 35, 70, 105 |
| 160 | 25% | 1 | `PB1_n160_d025.txt` | 3180 | 0.250 | 25 | 57 | 39.8 | 40, 80, 120 |
| 160 | 25% | 2 | `PB2_n160_d025.txt` | 3180 | 0.250 | 26 | 53 | 39.8 | 40, 80, 120 |
| 160 | 25% | 3 | `PB3_n160_d025.txt` | 3180 | 0.250 | 29 | 53 | 39.8 | 40, 80, 120 |
| 160 | 25% | 4 | `PB4_n160_d025.txt` | 3180 | 0.250 | 24 | 54 | 39.8 | 40, 80, 120 |
| 160 | 25% | 5 | `PB5_n160_d025.txt` | 3180 | 0.250 | 25 | 53 | 39.8 | 40, 80, 120 |
| 160 | 50% | 1 | `PB1_n160_d050.txt` | 6360 | 0.500 | 64 | 95 | 79.5 | 40, 80, 120 |
| 160 | 50% | 2 | `PB2_n160_d050.txt` | 6360 | 0.500 | 65 | 96 | 79.5 | 40, 80, 120 |
| 160 | 50% | 3 | `PB3_n160_d050.txt` | 6360 | 0.500 | 63 | 96 | 79.5 | 40, 80, 120 |
| 160 | 50% | 4 | `PB4_n160_d050.txt` | 6360 | 0.500 | 64 | 96 | 79.5 | 40, 80, 120 |
| 160 | 50% | 5 | `PB5_n160_d050.txt` | 6360 | 0.500 | 66 | 97 | 79.5 | 40, 80, 120 |
| 160 | 75% | 1 | `PB1_n160_d075.txt` | 9540 | 0.750 | 106 | 132 | 119.2 | 40, 80, 120 |
| 160 | 75% | 2 | `PB2_n160_d075.txt` | 9540 | 0.750 | 103 | 133 | 119.2 | 40, 80, 120 |
| 160 | 75% | 3 | `PB3_n160_d075.txt` | 9540 | 0.750 | 104 | 132 | 119.2 | 40, 80, 120 |
| 160 | 75% | 4 | `PB4_n160_d075.txt` | 9540 | 0.750 | 104 | 133 | 119.2 | 40, 80, 120 |
| 160 | 75% | 5 | `PB5_n160_d075.txt` | 9540 | 0.750 | 107 | 132 | 119.2 | 40, 80, 120 |
