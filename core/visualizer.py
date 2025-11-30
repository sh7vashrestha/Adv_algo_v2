import networkx as nx
from pyvis.network import Network
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def visualize_conflict_graph(
    G: nx.Graph,
    out_html="outputs/conflict_graph.html",
    physics=True,
    colors_dict=None  # ✅ Pass result.colors here
):
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#1E1E1E",
        font_color="white",
        notebook=False,
        directed=False,
    )
    net.toggle_physics(physics)

    degrees = dict(G.degree())
    max_deg = max(degrees.values()) if degrees else 1

    # ✅ Build a color palette for timeslot IDs
    cmap = plt.get_cmap("tab20")  # 20 distinct colors
    def get_color(slot):
        if slot is None:
            return "#999999"
        color = mcolors.rgb2hex(cmap(slot % 20))
        return color

    for node in G.nodes():
        # Use timeslot color if available, else fallback to degree
        if colors_dict and node in colors_dict:
            color = get_color(colors_dict[node])
        else:
            deg = degrees.get(node, 0)
            color = "#4DB6AC" if deg < max_deg / 2 else "#FF7043"

        net.add_node(
            node,
            label=node,
            size=10 + 40 * (degrees.get(node, 0) / max_deg),
            color=color,
        )

    for u, v in G.edges():
        net.add_edge(u, v, color="#AAAAAA", width=0.5)

    net.set_options("""
    {
      "nodes": {"shape": "dot", "font": {"color": "white"}},
      "edges": {"color": {"color": "#AAAAAA"}, "smooth": false},
      "physics": {
        "barnesHut": {"gravitationalConstant": -30000, "springLength": 200, "springConstant": 0.03},
        "stabilization": {"iterations": 2000}
      },
      "interaction": {"zoomView": true, "hover": true}
    }
    """)

    os.makedirs(os.path.dirname(out_html), exist_ok=True)
    net.write_html(out_html)
    return out_html