# Project Brief: Densest k-Subgraph (DkS)

## Overview

This project implements and empirically compares algorithms for the **Densest k-Subgraph problem**. We take an implementation-and-experiments approach rather than a proof-heavy one: the goal is to measure how close practical algorithms get to the true optimum, how fast they run, and where they break down.

**Deliverable:** a 2-page paper, plus being ready to discuss findings and answer questions.

## Problem

Given an undirected graph G = (V, E) and an integer k, find a set S ⊆ V with |S| = k that maximizes the number of edges inside S.

DkS is NP-hard (the maximum clique problem reduces to it), so no polynomial-time exact algorithm is expected unless P = NP. It is also hard to approximate: the best known guarantee is O(n^(1/4+ε)) (Bhaskara et al., 2010). Background reading: *A Survey on the Densest Subgraph Problem and Its Variants* (Lanciano et al.), Section 3.1.1.

## Algorithms

| Algorithm | Role | Notes |
|---|---|---|
| **Brute force** | Exact baseline | Checks all C(n, k) subsets. Only feasible for small graphs (roughly n ≤ 25). Useful for verifying correctness and showing exponential runtime growth. |
| **Greedy peeling** | Main heuristic | Repeatedly remove the lowest-degree vertex until k remain. Runs in near-linear time. Worst-case guarantee is only O(n/k) (Asahiro et al.). |
| **Third algorithm (TBD)** | Comparison point | Candidates: greedy + local search (swap one node in/out while it improves), or an exact integer-programming formulation solved with an off-the-shelf solver. |

Other approaches (SDP relaxations, the Bhaskara et al. algorithm) will be acknowledged in the report but not implemented.

## Datasets

### 1. Benchmark instances with known optima

Source: [k-cluster instances, CEDRIC/CNAM](https://cedric.cnam.fr/~lamberta/Library/k-cluster.html), with published [optimal values](https://cedric.cnam.fr/~lamberta/Library/solutions_k-cluster.html).

- 270 random graphs: n ∈ {40, 80, 100, 120, 140, 160}, edge density ∈ {25%, 50%, 75%}, k ∈ {n/4, n/2, 3n/4}, 5 instances each.
- Filename pattern: `kcluster{n}_{density}_{k}_{instance}.dat`.
- File format: first line `n k m`, then one line per edge `i j 0.500000` with i < j. Nodes are **1-indexed**. Treat each listed pair as an unweighted edge; the 0.5 weight is an artifact of the authors' formulation.
- Published optimum = number of edges in the best k-subset.
- Sanity check: on `kcluster160_050_40_3`, greedy peeling found 537 edges vs. an optimum of 547 (98.2%).

**Caveat:** these graphs have no planted structure, so simple heuristics already land close to optimal. Differences between algorithms may be small; the 25%-density instances may show them more clearly.

### 2. Synthetic graphs with a planted k-clique

- Generate a random graph G(n, p), then make k chosen vertices fully connected.
- A k-clique has the maximum possible C(k, 2) edges, so **the optimum is known exactly at any graph size**. No brute force needed.
- Difficulty knobs: background density p, and clique size k relative to √n. In G(n, 1/2), cliques much smaller than about √n are hard to find; much larger ones are easy.

### 3. Adversarial example (optional)

A small hand-built graph where greedy peeling fails: a dense cluster of moderate-degree vertices plus a few high-degree "decoy" hubs connected to many sparse leaves. Greedy keeps the hubs and discards the real cluster.

## Metrics

- **Approximation ratio:** edges found ÷ optimal edges.
- **Runtime** as n and k grow.
- **Recovery rate** (planted graphs): fraction of trials where the algorithm returns the planted clique.

## Planned Experiments

1. Ratio to optimum on all benchmark instances, broken down by size and density.
2. Planted-clique sweep: recovery rate as k moves across the √n threshold, for a few values of p. Candidate central figure for the paper.
3. Runtime scaling, including brute force on small graphs.
4. (Optional) Adversarial example illustrating greedy's failure mode.

## Phases

1. **Baseline:** data loader, graph generators, brute force, and verification against known optima.
2. **Implement:** greedy peeling and the third algorithm; run experiments.
3. **Visualize and report:** figures, analysis, 2-page paper.

## Team Workflow

- Communication on Discord.
- GitHub: `main` stays stable; everyone works on their own branch and notifies the group before merging.

## Open Questions

- Which third algorithm to implement?
- Ask David whether he recommends additional datasets, especially real-world graphs.
- Implementation language (Python is easiest; brute force may need pruning or a faster language to go beyond n ≈ 25).
