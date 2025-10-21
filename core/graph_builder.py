"""
graph_builder.py
----------------
Builds an exam conflict graph from enrollments.

Each node = course_id
An edge exists between two courses if at least one student is enrolled in both.
Handles alphanumeric IDs (e.g., CS0291) and ensures every course is represented.
"""

import pandas as pd
import networkx as nx


def build_conflict_graph_from_enrollments(enrollments: pd.DataFrame, courses_df: pd.DataFrame | None = None) -> nx.Graph:
    """
    Build a conflict graph from a (student_id, course_id) enrollment dataframe.

    Parameters
    ----------
    enrollments : pd.DataFrame
        Must have columns ['student_id', 'course_id']
    courses_df : pd.DataFrame, optional
        If provided, ensures all courses (even isolated ones) appear as nodes.

    Returns
    -------
    G : nx.Graph
        Undirected graph where nodes are course_ids (strings) and edges represent conflicts.
    """
    G = nx.Graph()

    # --- Normalize IDs ---
    enrollments["course_id"] = enrollments["course_id"].astype(str).str.strip().str.upper()
    enrollments["student_id"] = enrollments["student_id"].astype(str).str.strip()

    # --- Add nodes from enrollments ---
    for cid in enrollments["course_id"].unique():
        G.add_node(cid)

    # --- If a course list is given, ensure all appear (even those with no enrollment overlaps) ---
    if courses_df is not None and "course_id" in courses_df.columns:
        for cid in courses_df["course_id"].astype(str).str.strip().str.upper().unique():
            if cid not in G:
                G.add_node(cid)

    # --- Build conflict pairs efficiently ---
    stu_courses = (
        enrollments.groupby("student_id")["course_id"]
        .apply(list)
        .to_dict()
    )

    # --- Add edges for shared students ---
    for student, courses in stu_courses.items():
        n = len(courses)
        if n < 2:
            continue
        for i in range(n):
            for j in range(i + 1, n):
                a, b = courses[i], courses[j]
                if a != b:
                    G.add_edge(a, b)

    return G


def build_conflict_graph_from_stu_file(stu_path: str, courses_df: pd.DataFrame | None = None) -> nx.Graph:
    """
    Alternate builder from a .stu file (Toronto format).
    Each line = list of course IDs separated by spaces.
    Ensures all courses exist as nodes.
    """
    G = nx.Graph()

    # --- Read .stu file ---
    with open(stu_path, "r") as f:
        for line in f:
            courses = [c.strip().upper() for c in line.strip().split() if c.strip()]
            for c in courses:
                G.add_node(c)
            for i in range(len(courses)):
                for j in range(i + 1, len(courses)):
                    a, b = courses[i], courses[j]
                    if a != b:
                        G.add_edge(a, b)

    # --- Add isolated nodes if course list provided ---
    if courses_df is not None and "course_id" in courses_df.columns:
        for cid in courses_df["course_id"].astype(str).str.strip().str.upper().unique():
            if cid not in G:
                G.add_node(cid)

    return G
