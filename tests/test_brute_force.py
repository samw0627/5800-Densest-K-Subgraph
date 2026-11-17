from itertools import combinations
from math import comb
from pathlib import Path

import pytest

from dks import Graph, brute_force, brute_force_naive, gnp, load_json_graphs, load_kcluster, planted_clique

DATASET = Path(__file__).resolve().parent.parent / "Dataset"


def complete(n):
    return Graph(n, list(combinations(range(n), 2)))


# ----------------------------- hand-checked cases ----------------------------- #

def test_complete_graph():
    assert brute_force(complete(6), 4).edges == comb(4, 2)


def test_empty_graph():
    r = brute_force(Graph(5, []), 3)
    assert r.edges == 0 and r.vertices == (0, 1, 2)


def test_path():
    g = Graph(5, [(0, 1), (1, 2), (2, 3), (3, 4)])
    assert brute_force(g, 3).edges == 2


def test_star():
    g = Graph(6, [(0, i) for i in range(1, 6)])
    r = brute_force(g, 3)
    assert r.edges == 2 and 0 in r.vertices


def test_finds_k4_over_triangle():
    # Triangle on {0,1,2}, K4 on {3,4,5,6}.
    edges = [(0, 1), (0, 2), (1, 2)] + list(combinations(range(3, 7), 2))
    r = brute_force(Graph(7, edges), 4)
    assert r.edges == 6 and r.vertices == (3, 4, 5, 6)


def test_k_zero_and_k_n():
    g = gnp(8, 0.5, seed=1)
    assert brute_force(g, 0) == brute_force_naive(g, 0)
    assert brute_force(g, 0).edges == 0
    assert brute_force(g, g.n).edges == g.m


@pytest.mark.parametrize("k", [-1, 9])
def test_invalid_k(k):
    with pytest.raises(ValueError):
        brute_force(gnp(8, 0.5, seed=1), k)


# ----------------------------- cross-checks ----------------------------------- #

@pytest.mark.parametrize("seed", range(20))
def test_matches_naive_on_random_graphs(seed):
    n = 6 + seed % 7               # n from 6 to 12
    p = (0.2, 0.5, 0.8)[seed % 3]
    g = gnp(n, p, seed=seed)
    for k in range(n + 1):
        fast, slow = brute_force(g, k), brute_force_naive(g, k)
        assert fast.edges == slow.edges
        assert fast.vertices == slow.vertices      # same tie-breaking
        assert g.edges_in(fast.vertices) == fast.edges
        assert fast.subsets_checked == comb(n, k)


@pytest.mark.parametrize("seed", range(5))
def test_planted_clique_optimum(seed):
    k = 6
    g, clique = planted_clique(16, 0.3, k, seed=seed)
    r = brute_force(g, k)
    assert r.edges == comb(k, 2)
    assert g.edges_in(clique) == comb(k, 2)


# ----------------------------- loaders ----------------------------------------- #

def test_load_kcluster():
    g = load_kcluster(DATASET / "PB1_d025.txt")
    assert (g.n, g.m) == (40, 183)
    assert all(0 <= u < v < 40 for u, v in g.edges)


@pytest.mark.skipif(not (DATASET / "graphs-1.json").exists(), reason="graphs-1.json not present")
def test_json_graphs_match_naive():
    for g in load_json_graphs(DATASET / "graphs-1.json"):
        for k in range(g.n + 1):
            assert brute_force(g, k).edges == brute_force_naive(g, k).edges


# ----------------------------- branch and bound -------------------------------- #

from dks import branch_and_bound, greedy_peel  # noqa: E402


@pytest.mark.parametrize("seed", range(20))
def test_bnb_matches_brute_force(seed):
    n = 6 + seed % 9               # n from 6 to 14
    g = gnp(n, (0.2, 0.5, 0.8)[seed % 3], seed=100 + seed)
    for k in range(n + 1):
        r = branch_and_bound(g, k)
        assert r.edges == brute_force(g, k).edges
        assert len(r.vertices) == k and g.edges_in(r.vertices) == r.edges
        assert r.subsets_checked <= comb(n, k)


@pytest.mark.parametrize("seed", range(5))
def test_bnb_planted_clique(seed):
    g, _ = planted_clique(30, 0.3, 8, seed=seed)
    assert branch_and_bound(g, 8).edges == comb(8, 2)


def test_greedy_peel_is_feasible():
    g = gnp(15, 0.5, seed=3)
    e, vs = greedy_peel(g, 6)
    assert len(vs) == 6 and g.edges_in(vs) == e


def test_bnb_on_benchmark_subgraph():
    g = load_kcluster(DATASET / "PB1_d05.txt")
    sub = Graph(14, [(u, v) for u, v in g.edges if v < 14])
    assert branch_and_bound(sub, 7).edges == brute_force(sub, 7).edges
