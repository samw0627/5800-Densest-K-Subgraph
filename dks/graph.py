"""Graph representation, loaders, and generators for Densest k-Subgraph.

Vertices are always 0-indexed internally. Adjacency is stored as one integer
bitmask per vertex, so "how many neighbours of v are in set S" is a single
``(adj[v] & S).bit_count()``.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Iterable


@dataclass
class Graph:
    n: int
    edges: list[tuple[int, int]]
    name: str = ""
    adj: list[int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.adj = [0] * self.n
        seen = set()
        clean = []
        for u, v in self.edges:
            if u == v:
                raise ValueError(f"self-loop on vertex {u}")
            if not (0 <= u < self.n and 0 <= v < self.n):
                raise ValueError(f"edge ({u}, {v}) out of range for n={self.n}")
            key = (min(u, v), max(u, v))
            if key in seen:
                continue  # ignore duplicate edges
            seen.add(key)
            clean.append(key)
            self.adj[u] |= 1 << v
            self.adj[v] |= 1 << u
        self.edges = clean

    @property
    def m(self) -> int:
        return len(self.edges)

    def degree(self, v: int) -> int:
        return self.adj[v].bit_count()

    def edges_in(self, vertices: Iterable[int]) -> int:
        """Number of edges induced by a vertex set."""
        mask = 0
        for v in vertices:
            mask |= 1 << v
        total = 0
        m = mask
        while m:
            low = m & -m
            v = low.bit_length() - 1
            total += (self.adj[v] & mask).bit_count()
            m ^= low
        return total // 2


# --------------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------------- #

def load_kcluster(path: str | Path) -> Graph:
    """Load a CNAM k-cluster benchmark file (header ``n m``, 1-indexed edges).

    The third column (constant weight 0.5 or 1) is ignored.
    """
    path = Path(path)
    with path.open() as f:
        n, m = map(int, f.readline().split()[:2])
        edges = []
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                edges.append((int(parts[0]) - 1, int(parts[1]) - 1))
    if len(edges) != m:
        raise ValueError(f"{path.name}: header says {m} edges, found {len(edges)}")
    return Graph(n, edges, name=path.stem)


def load_json_graphs(path: str | Path) -> list[Graph]:
    """Load ``{"graphs": [{"id", "n", "edges": [[u, v], ...]}, ...]}`` (0-indexed)."""
    path = Path(path)
    data = json.loads(path.read_text())
    return [
        Graph(g["n"], [tuple(e) for e in g["edges"]], name=str(g.get("id", i + 1)))
        for i, g in enumerate(data["graphs"])
    ]


# --------------------------------------------------------------------------- #
# Generators
# --------------------------------------------------------------------------- #

def gnp(n: int, p: float, seed: int | None = None) -> Graph:
    """Erdős–Rényi G(n, p)."""
    rng = random.Random(seed)
    edges = [(u, v) for u, v in combinations(range(n), 2) if rng.random() < p]
    return Graph(n, edges, name=f"gnp_n{n}_p{p}")


def planted_clique(n: int, p: float, k: int, seed: int | None = None) -> tuple[Graph, list[int]]:
    """G(n, p) with k random vertices made fully connected.

    Returns the graph and the (sorted) planted vertices. The optimum DkS value
    for this k is exactly C(k, 2).
    """
    rng = random.Random(seed)
    clique = sorted(rng.sample(range(n), k))
    in_clique = set(clique)
    edges = [
        (u, v)
        for u, v in combinations(range(n), 2)
        if (u in in_clique and v in in_clique) or rng.random() < p
    ]
    return Graph(n, edges, name=f"planted_n{n}_p{p}_k{k}"), clique
