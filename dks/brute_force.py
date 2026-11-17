"""Exact Densest k-Subgraph by exhaustive enumeration.

Every one of the C(n, k) vertex subsets of size k is visited. Subsets are
generated depth-first in lexicographic order, and the induced edge count is
updated incrementally: adding vertex v to a partial set S adds
``|N(v) ∩ S|`` edges, a single bitmask popcount. So each subset costs O(1)
amortised work instead of O(k^2), but the search is still exhaustive -- no
pruning -- and the running time is Θ(C(n, k)).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb

from .graph import Graph


@dataclass
class Result:
    edges: int                 # edges inside the best subset
    vertices: tuple[int, ...]  # the best subset (0-indexed, sorted)
    subsets_checked: int       # always C(n, k) for brute force


def _check_k(g: Graph, k: int) -> None:
    if not 0 <= k <= g.n:
        raise ValueError(f"k must be in [0, {g.n}], got {k}")


def brute_force(g: Graph, k: int) -> Result:
    """Return a k-subset with the maximum number of induced edges.

    Ties are broken by taking the lexicographically smallest subset.
    """
    _check_k(g, k)
    n, adj = g.n, g.adj
    best_edges = -1
    best_set: tuple[int, ...] = ()
    checked = 0
    chosen: list[int] = []

    def extend(start: int, mask: int, edges: int, remaining: int) -> None:
        nonlocal best_edges, best_set, checked
        if remaining == 0:
            checked += 1
            if edges > best_edges:
                best_edges = edges
                best_set = tuple(chosen)
            return
        # Leave room for the remaining vertices: v can go up to n - remaining.
        for v in range(start, n - remaining + 1):
            chosen.append(v)
            extend(v + 1, mask | (1 << v), edges + (adj[v] & mask).bit_count(), remaining - 1)
            chosen.pop()

    extend(0, 0, 0, k)
    return Result(best_edges, best_set, checked)


def brute_force_naive(g: Graph, k: int) -> Result:
    """Reference implementation: itertools.combinations + recount each subset.

    Θ(C(n, k) · k) time. Kept as an independent check on ``brute_force``.
    """
    _check_k(g, k)
    best_edges, best_set = -1, ()
    for subset in combinations(range(g.n), k):
        e = g.edges_in(subset)
        if e > best_edges:
            best_edges, best_set = e, subset
    return Result(best_edges, best_set, comb(g.n, k))
