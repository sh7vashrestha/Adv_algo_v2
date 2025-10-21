from __future__ import annotations
import streamlit as st

st.set_page_config(page_title="Exam Scheduler", page_icon="📅", layout="wide")

st.title("Two-Stage Modular Streamlit Exam Scheduler")

st.markdown(
    """
**Stage 1 — Generate Dataset**: Create synthetic students, courses, classrooms, timeslots, and enrollments.

**Stage 2 — Run Scheduler**: Upload CSVs **or** use the latest synthetic dataset, build conflict graph, choose algorithm (Greedy/DSATUR/SA), assign rooms, and export CSV/PDF outputs.

Use the **Pages** sidebar to navigate.
"""
)
