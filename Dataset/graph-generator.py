import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path


def gg(path):
    with open(path, "r") as f:
        data = json.load(f)

    graphs = data["graphs"]

    # 3 rows × 4 columns
    fig, axes = plt.subplots(3, 4, figsize=(22, 10))
    axes = axes.flatten()

    for i, graph in enumerate(graphs[:10]):

        G = nx.Graph()
        G.add_nodes_from(range(graph["n"]))
        G.add_edges_from(graph["edges"])

        # Calculate layout
        pos = nx.kamada_kawai_layout(G)

        # Draw graph on corresponding subplot
        nx.draw(
            G,
            pos=pos,
            ax=axes[i],
            with_labels=True,
            node_color="lightblue",
            node_size=350,
            edge_color="gray",
            font_size=9,
            font_weight="bold"
        )

        axes[i].set_title(
            f"{graph.get('id', f'Graph {i+1}')}\n"
            f"n={G.number_of_nodes()}, m={G.number_of_edges()}",
            fontsize=12
        )

    # Hide unused subplots
    for j in range(min(len(graphs), 10), len(axes)):
        axes[j].axis("off")

    plt.tight_layout()
    plt.savefig("all_graphs.png", dpi=300, bbox_inches="tight")
    plt.show()


folder = Path(__file__).resolve().parent
json_path = folder / "graphs-1.json"
gg(json_path)