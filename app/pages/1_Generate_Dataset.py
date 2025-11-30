from __future__ import annotations
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from datetime import datetime

import streamlit as st
import pandas as pd

from core.data_generator import generate_synthetic_dataset

st.title("Generate Dataset")

with st.form("gen_form"):
    c1, c2, c3, c4 = st.columns(4)
    n_students = c1.number_input("# Students", min_value=100, max_value=200_000, value=10_000, step=100)
    n_courses  = c2.number_input("# Courses", min_value=10, max_value=5_000, value=100, step=10)
    n_rooms    = c3.number_input("# Rooms", min_value=5, max_value=2_000, value=50, step=5)
    n_periods  = c4.number_input("# Periods", min_value=10, max_value=2_000, value=80, step=5)

    c5, c6 = st.columns(2)
    min_c = c5.number_input("Min courses/student", min_value=1, max_value=20, value=3)
    max_c = c6.number_input("Max courses/student", min_value=min_c, max_value=30, value=6)

    submitted = st.form_submit_button("Generate Synthetic Dataset", type="primary")

if submitted:
    with st.spinner("Generating synthetic data (seed=42)..."):
        outdir = generate_synthetic_dataset(
            n_students=int(n_students),
            n_courses=int(n_courses),
            n_rooms=int(n_rooms),
            n_periods=int(n_periods),
            min_courses_per_student=int(min_c),
            max_courses_per_student=int(max_c),
        )
    st.success(f"Dataset saved to `{outdir}`")

    # Preview samples
    def head_csv(path, n=5):
        return pd.read_csv(path).head(n)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("students.csv")
        st.dataframe(head_csv(os.path.join(outdir, "students.csv")))
        st.subheader("courses.csv")
        st.dataframe(head_csv(os.path.join(outdir, "courses.csv")))
        st.subheader("classrooms.csv")
        st.dataframe(head_csv(os.path.join(outdir, "classrooms.csv")))
    with c2:
        st.subheader("timeslots.csv")
        st.dataframe(head_csv(os.path.join(outdir, "timeslots.csv")))
        st.subheader("enrollments.csv")
        st.dataframe(head_csv(os.path.join(outdir, "enrollments.csv")))

    st.info("Toronto .stu file also generated.")
