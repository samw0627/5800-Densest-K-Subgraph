from pathlib import Path
import networkx as nx

# Locate dataset folder relative to this script
DATASET_DIR = Path(__file__).resolve().parent.parent / "dataset"

def list_datasets():
    """Return a sorted list of dataset filenames."""
    return sorted(
        file.name
        for file in DATASET_DIR.iterdir()
        if file.is_file() and file.suffix in (".txt", ".dat")
    )


def load_graph(filename):
    """Load one dataset file as a NetworkX graph."""
    filepath = DATASET_DIR / filename

    with filepath.open("r") as f:
        n, m = map(int, f.readline().split())

        G = nx.Graph()
        G.add_nodes_from(range(1, n + 1))

        for line in f:
            if not line.strip():
                continue

            u, v, _ = line.split()
            G.add_edge(int(u), int(v))

    if G.number_of_edges() != m:
        raise ValueError(
            f"Expected {m} edges, got {G.number_of_edges()}"
        )

    return G


if __name__ == "__main__":
    datasets = list_datasets()

    print(f"Found {len(datasets)} datasets")

    for i, filename in enumerate(datasets):
        print(i, filename)

    # Load the first dataset
    # G = load_graph(datasets[0])

    # print("Nodes:", G.number_of_nodes())
    # print("Edges:", G.number_of_edges())