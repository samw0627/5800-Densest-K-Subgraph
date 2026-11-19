from scripts.read_dataset import list_datasets, load_graph

from itertools import combinations

def brute_force(G, k):
    best_nodes = None
    best_edges = -1

    for nodes in combinations(G.nodes(), k):
        H = G.subgraph(nodes)
        edge_count = H.number_of_edges()

        if edge_count > best_edges:
            best_edges = edge_count
            best_nodes = nodes

    return best_nodes, best_edges