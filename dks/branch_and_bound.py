"""Exact Densest k-Subgraph by branch and bound.

Same depth-first enumeration as ``brute_force`` (choose vertices in
increasing order, keep a running edge count), but before expanding a node we
compute an upper bound on the best completion and prune if it cannot beat the
incumbent.

Bound. At a node with chosen set S (inducing e edges), r vertices still to
pick, and candidate set C (vertices after the last chosen one), any completion
T ⊆ C with |T| = r induces

    e + Σ_{c∈T} |N(c) ∩ S| + |E(T)|.

Each edge of E(T) has both ends in T, so |E(T)| = ½ Σ_{c∈T} |N(c) ∩ T|, and
|N(c) ∩ T| ≤ min(r − 1, |N(c) ∩ C|). Hence, with

    f(c) = |N(c) ∩ S| + ½ · min(r − 1, |N(c) ∩ C|),

the completion value is at most e + (sum of the r largest f(c)). We work with
2·f to stay in integers.

Speed-ups that keep the result exact:
  * vertices are relabelled in decreasing-degree order, so dense vertices are
    tried first and good incumbents appear early;
  * the incumbent is seeded with greedy peeling (repeatedly delete a
    minimum-degree vertex), so pruning starts at the root.
"""

from __future__ import annotations

from dataclasses import dataclass

from .graph import Graph


@dataclass
class BnBResult:
    edges: int
    vertices: tuple[int, ...]  # original vertex labels, sorted
    subsets_checked: int       # complete k-subsets whose edge count was computed
    nodes: int                 # search-tree nodes expanded (incl. leaves)


def greedy_peel(g: Graph, k: int) -> tuple[int, list[int]]:
    """Asahiro et al. greedy peeling. Returns (edges, vertices). O(n^2)."""
    alive = (1 << g.n) - 1
    deg = [g.degree(v) for v in range(g.n)]
    present = set(range(g.n))
    edges = g.m
    while len(present) > k:
        v = min(present, key=lambda u: deg[u])
        present.remove(v)
        alive &= ~(1 << v)
        nbrs = g.adj[v] & alive
        edges -= deg[v]
        while nbrs:
            low = nbrs & -nbrs
            deg[low.bit_length() - 1] -= 1
            nbrs ^= low
    return edges, sorted(present)


def branch_and_bound(g: Graph, k: int) -> BnBResult:
    if not 0 <= k <= g.n:
        raise ValueError(f"k must be in [0, {g.n}], got {k}")
    n = g.n

    # Relabel: new index i  ->  original vertex order[i], by decreasing degree.
    order = sorted(range(n), key=lambda v: -g.degree(v))
    pos = {v: i for i, v in enumerate(order)}
    adj = [0] * n
    for i, v in enumerate(order):
        m = g.adj[v]
        while m:
            low = m & -m
            adj[i] |= 1 << pos[low.bit_length() - 1]
            m ^= low

    best_edges, best_orig = greedy_peel(g, k)
    best_set = tuple(sorted(pos[v] for v in best_orig))
    found_better = False
    leaves = 0
    nodes = 0
    chosen: list[int] = []
    full = (1 << n) - 1

    def extend(start: int, mask: int, edges: int, remaining: int) -> None:
        nonlocal best_edges, best_set, leaves, nodes, found_better
        nodes += 1
        if remaining == 1:
            # The bound below computes |N(c) ∩ S| for every candidate c, which is
            # exactly the edge count of each complete subset S ∪ {c}.
            leaves += n - start
        if remaining == 0:
            if k == 0:
                leaves = 1
            if edges > best_edges:
                best_edges, best_set, found_better = edges, tuple(chosen), True
            return

        cand = full & ~((1 << start) - 1)
        two_f = []
        cap = remaining - 1
        for c in range(start, n):
            c_adj = adj[c]
            b = (c_adj & cand).bit_count()
            two_f.append(2 * (c_adj & mask).bit_count() + (b if b < cap else cap))
        two_f.sort(reverse=True)
        if 2 * edges + sum(two_f[:remaining]) <= 2 * best_edges:
            return  # cannot strictly beat the incumbent

        for v in range(start, n - remaining + 1):
            chosen.append(v)
            extend(v + 1, mask | (1 << v), edges + (adj[v] & mask).bit_count(), remaining - 1)
            chosen.pop()

    extend(0, 0, 0, k)
    verts = tuple(sorted(order[i] for i in best_set))
    return BnBResult(best_edges, verts, leaves, nodes)
