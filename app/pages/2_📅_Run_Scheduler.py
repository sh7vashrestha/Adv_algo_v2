"""
2_📅_Run_Scheduler.py
--------------------
Stage 2 – Exam Scheduling:
Loads data, builds conflict graph, runs algorithms (Greedy, DSATUR, SA),
allocates rooms, validates durations, exports PDFs, and visualizes results.
"""

import os
import sys
import time
import pandas as pd
import streamlit as st
from datetime import datetime
import networkx as nx

# Ensure access to core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.graph_builder import build_conflict_graph_from_enrollments
from core.scheduler import greedy_coloring, dsatur_coloring, simulated_annealing_coloring
from core.room_allocator import allocate_rooms
from core.evaluation import validate_durations, compare_algorithms
from core.pdf_exporter import export_master_pdf, export_student_pdfs
from core.visualizer import visualize_conflict_graph


# ---------------------------------------------------------------------
# Streamlit setup
# ---------------------------------------------------------------------
st.set_page_config(page_title="📅 Run Scheduler", layout="wide")
st.title("📅 Exam Timetable Scheduler")
st.caption("Stage 2 – Build conflict graph, run scheduling algorithms, visualize, and export outputs.")


# ---------------------------------------------------------------------
# Dataset selection
# ---------------------------------------------------------------------
st.sidebar.header("Dataset Source")
mode = st.sidebar.radio("Choose dataset source:", ["Use latest synthetic dataset", "Upload CSVs manually"])

base_dir = os.path.abspath("data/synthetic")
dataset_dir = None

if mode == "Use latest synthetic dataset":
    subdirs = [os.path.join(base_dir, d) for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if subdirs:
        dataset_dir = max(subdirs, key=os.path.getmtime)
        st.success(f"📂 Loaded latest dataset: `{os.path.basename(dataset_dir)}`")
    else:
        st.error("No synthetic dataset found. Please generate one in Stage 1.")
        st.stop()
else:
    st.sidebar.write("📤 Upload required CSVs:")
    uploaded = {
        "students": st.sidebar.file_uploader("students.csv", type="csv"),
        "courses": st.sidebar.file_uploader("courses.csv", type="csv"),
        "classrooms": st.sidebar.file_uploader("classrooms.csv", type="csv"),
        "timeslots": st.sidebar.file_uploader("timeslots.csv", type="csv"),
        "enrollments": st.sidebar.file_uploader("enrollments.csv", type="csv"),
    }
    if not all(uploaded.values()):
        st.warning("Please upload all required CSVs.")
        st.stop()
    dataset_dir = "uploads"
    os.makedirs(dataset_dir, exist_ok=True)
    for k, file in uploaded.items():
        path = os.path.join(dataset_dir, f"{k}.csv")
        with open(path, "wb") as f:
            f.write(file.getbuffer())
    st.success("✅ All CSVs uploaded successfully.")


# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------
students = pd.read_csv(os.path.join(dataset_dir, "students.csv"))
courses = pd.read_csv(os.path.join(dataset_dir, "courses.csv"))
rooms = pd.read_csv(os.path.join(dataset_dir, "classrooms.csv"))
times = pd.read_csv(os.path.join(dataset_dir, "timeslots.csv"))
enroll = pd.read_csv(os.path.join(dataset_dir, "enrollments.csv"))

# Normalize IDs
for df in [students, courses, rooms, times, enroll]:
    if "course_id" in df.columns:
        df["course_id"] = df["course_id"].astype(str).str.strip().str.upper()
    if "student_id" in df.columns:
        df["student_id"] = df["student_id"].astype(str).str.strip()

st.subheader("📋 Dataset Summary")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Students", len(students))
col2.metric("Courses", len(courses))
col3.metric("Rooms", len(rooms))
col4.metric("Timeslots", len(times))
col5.metric("Enrollments", len(enroll))


# ---------------------------------------------------------------------
# Algorithm Selection
# ---------------------------------------------------------------------
st.subheader("⚙️ Scheduling Algorithm")
algo = st.selectbox(
    "Select algorithm:",
    ["DSATUR", "Greedy", "Simulated Annealing", "Compare All (Greedy vs DSATUR vs SA)"]
)

if algo == "Simulated Annealing" or algo == "Compare All (Greedy vs DSATUR vs SA)":
    T0 = st.number_input("Initial Temperature (T₀)", 0.1, 10.0, 1.0, 0.1)
    alpha = st.number_input("Cooling Rate (α)", 0.5, 0.99, 0.90, 0.01)
    max_iters = st.number_input("Max Iterations", 100, 10000, 2000, 100)


# ---------------------------------------------------------------------
# Run Scheduler
# ---------------------------------------------------------------------
if st.button("🚀 Run Scheduler"):
    start_time = time.time()
    progress = st.progress(0)

    st.write("🔗 Building conflict graph...")
    G = build_conflict_graph_from_enrollments(enroll)
    st.write(f"📊 Graph: {len(G.nodes())} courses, {len(G.edges())} conflicts")

    # Save & visualize graph
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = os.path.join("outputs", timestamp)
    os.makedirs(outdir, exist_ok=True)
    graph_html = os.path.join(outdir, "conflict_graph.html")
    visualize_conflict_graph(G, out_html=graph_html)

    st.markdown(f"📈 [Open Interactive Conflict Graph →](./{graph_html})")

    graph_density = nx.density(G)
    avg_deg = sum(dict(G.degree()).values()) / len(G) if len(G) else 0
    st.info(f"Graph Density: {graph_density:.3f}, Average Degree: {avg_deg:.2f}")
    progress.progress(25)

    algo_results = {}

    def run_and_record(name, func, *args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        runtime = time.time() - t0
        algo_results[name] = {
            "colors_used": len(set(result.colors.values())),
            "runtime": runtime,
            "conflicts": 0,
        }
        return result

    # -----------------------------------------------------------------
    # Run selected / all algorithms
    # -----------------------------------------------------------------
    if algo == "Compare All (Greedy vs DSATUR vs SA)":
        st.write("🧮 Running all algorithms for comparison...")
        greedy_res = run_and_record("Greedy", greedy_coloring, G)
        dsatur_res = run_and_record("DSATUR", dsatur_coloring, G)
        sa_res = run_and_record(
            "Simulated Annealing",
            simulated_annealing_coloring,
            G,
            initial=dsatur_res.colors,
            T0=float(T0),
            alpha=float(alpha),
            max_iters=int(max_iters),
        )
        result = sa_res  # use SA for final schedule
    else:
        if algo == "Greedy":
            result = run_and_record("Greedy", greedy_coloring, G)
        elif algo == "DSATUR":
            result = run_and_record("DSATUR", dsatur_coloring, G)
        else:
            init = dsatur_coloring(G).colors
            result = run_and_record(
                "Simulated Annealing",
                simulated_annealing_coloring,
                G,
                initial=init,
                T0=float(T0),
                alpha=float(alpha),
                max_iters=int(max_iters),
            )

    progress.progress(60)

    # Clamp colors to timeslot range
    max_slot = int(times["timeslot_id"].max())
    for cid in result.colors:
        result.colors[cid] = int(result.colors[cid]) % max_slot + 1

    # Validation
    st.write("✅ Validating durations...")
    valdf = validate_durations(courses, times, result.colors)
    invalid = valdf[valdf["exam_ok"] == False]
    if len(invalid) > 0:
        st.warning(f"{len(invalid)} exams exceed available timeslot duration.")
    progress.progress(75)

    # Room allocation
    st.write("🏫 Allocating rooms...")
    sizes = enroll.groupby("course_id").size()
    room_df = allocate_rooms(sizes.to_dict(), times, result.colors, rooms)
    progress.progress(85)

    # Merge and label rooms
    merged = courses.merge(room_df, on="course_id", how="left")
    merged = merged.merge(times, on="timeslot_id", how="left")
    if {"building_name", "room_number"}.issubset(rooms.columns):
        merged = merged.merge(
            rooms[["classroom_id", "building_name", "room_number"]],
            on="classroom_id", how="left",
        )
        merged["room_label"] = merged["building_name"].astype(str) + " " + merged["room_number"].astype(str)
    else:
        merged["room_label"] = merged["classroom_id"].astype(str)

    # Save outputs
    schedule_csv = os.path.join(outdir, "schedule_generated.csv")
    merged.to_csv(schedule_csv, index=False)

    # Export PDFs
    st.write("🧾 Exporting PDFs...")
    master_pdf = os.path.join(outdir, "Master_Exam_Schedule.pdf")
    student_dir = os.path.join(outdir, "student_pdfs")
    os.makedirs(student_dir, exist_ok=True)

    display_df = merged[["course_id", "course_name", "timeslot_id", "room_label"]]
    export_master_pdf(display_df, times, master_pdf)
    export_student_pdfs(enroll, display_df, times, student_dir, students_df=students)
    progress.progress(95)

    # Comparison visualization
    if len(algo_results) > 1:
        plot_path = os.path.join(outdir, "algorithm_comparison.png")
        compare_algorithms(algo_results, outpath=plot_path)
        st.image(plot_path, caption="Algorithm Comparison (Colors vs Runtime)")
    else:
        only = list(algo_results.keys())[0]
        st.metric("🧮 Colors Used", algo_results[only]["colors_used"])
        st.metric("⚡ Runtime (s)", f"{algo_results[only]['runtime']:.2f}")

    progress.progress(100)
    st.success(f"✅ Scheduling completed in {time.time() - start_time:.2f} seconds.")
    st.write(f"📂 Results saved under `{outdir}`")

    st.download_button(
        "⬇️ Download Master Schedule PDF",
        open(master_pdf, "rb"),
        file_name="Master_Exam_Schedule.pdf",
    )

    st.dataframe(
        merged[["course_id", "course_name", "timeslot_id", "day", "start_time", "end_time", "room_label"]]
    )
