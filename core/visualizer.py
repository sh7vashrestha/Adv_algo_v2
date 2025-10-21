import networkx as nx
from pyvis.network import Network
import os

def visualize_conflict_graph(G: nx.Graph, out_html="outputs/conflict_graph.html", physics=True):
    """
    Creates an interactive HTML visualization of the conflict graph.
    - Nodes = courses
    - Edges = shared students
    """

    net = Network(
        height="750px",
        width="100%",
        bgcolor="#1E1E1E",
        font_color="white",
        notebook=False,
        directed=False,
    )
    net.toggle_physics(physics)

    # Node degrees for sizing
    degrees = dict(G.degree())
    max_deg = max(degrees.values()) if degrees else 1

    for node, deg in degrees.items():
        net.add_node(
            node,
            label=node,
            size=10 + 40 * (deg / max_deg),
            color="#4DB6AC" if deg < max_deg / 2 else "#FF7043",
        )

    for u, v in G.edges():
        net.add_edge(u, v, color="#757575")

    os.makedirs(os.path.dirname(out_html), exist_ok=True)
    
    # ✅ Save HTML safely (no Jupyter rendering)
    net.write_html(out_html)
    
    return out_html
