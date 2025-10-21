from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import math
import random

import networkx as nx

random.seed(42)

@dataclass
class ScheduleResult:
    colors: Dict[int, int]  # course_id -> period index (starting from 1)
    num_periods: int
    conflicts: int
    algorithm: str

def greedy_coloring(G: nx.Graph) -> ScheduleResult:
    order = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)
    color: Dict[int, int] = {}
    for node in order:
        neighbor_colors = {color.get(nei) for nei in G.neighbors(node) if nei in color}
        c = 1
        while c in neighbor_colors:
            c += 1
        color[node] = c
    return ScheduleResult(color, max(color.values()) if color else 0, _count_conflicts(G, color), "Greedy")

def dsatur_coloring(G: nx.Graph) -> ScheduleResult:
    # DSATUR heuristic
    color: Dict[int, int] = {}
    sat_deg = {v: 0 for v in G.nodes()}
    uncolored = set(G.nodes())

    def saturation(v):
        return len({color.get(u) for u in G.neighbors(v) if u in color})

    while uncolored:
        # pick vertex with highest saturation, ties by degree
        v = max(uncolored, key=lambda x: (saturation(x), G.degree(x)))
        neighbor_colors = {color.get(nei) for nei in G.neighbors(v) if nei in color}
        c = 1
        while c in neighbor_colors:
            c += 1
        color[v] = c
        uncolored.remove(v)
        for u in G.neighbors(v):
            sat_deg[u] = saturation(u)

    return ScheduleResult(color, max(color.values()) if color else 0, _count_conflicts(G, color), "DSATUR")

def simulated_annealing_coloring(
    G: nx.Graph,
    initial: Dict[int, int] | None = None,
    T0: float = 1.0,
    alpha: float = 0.995,
    max_iters: int = 10000,
    max_colors: int | None = None,
) -> ScheduleResult:
    # If no initial coloring, start with greedy
    if initial is None:
        initial = greedy_coloring(G).colors
    current = initial.copy()
    if max_colors is None:
        max_colors = max(current.values())

    def conflicts(coloring):
        return _count_conflicts(G, coloring)

    cur_conf = conflicts(current)
    T = T0

    nodes = list(G.nodes())
    for it in range(max_iters):
        v = random.choice(nodes)
        old_c = current[v]
        # try a new color in [1, max_colors]
        new_c = random.randint(1, max_colors)
        if new_c == old_c:
            continue
        current[v] = new_c
        new_conf = conflicts(current)
        dE = new_conf - cur_conf
        if dE <= 0 or random.random() < math.exp(-dE / max(T, 1e-8)):
            cur_conf = new_conf
        else:
            current[v] = old_c
        T *= alpha
        if cur_conf == 0:
            break

    used = max(current.values()) if current else 0
    return ScheduleResult(current, used, cur_conf, "SimulatedAnnealing")

def _count_conflicts(G: nx.Graph, color: Dict[int, int]) -> int:
    c = 0
    for u, v in G.edges():
        if color.get(u) == color.get(v):
            c += 1
    return c
