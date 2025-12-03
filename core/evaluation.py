from __future__ import annotations
from typing import Dict
import pandas as pd

def summarize_conflicts(edges: int, conflicts: int) -> float:
    return 0.0 if edges == 0 else conflicts / edges

def course_sizes(enrollments: pd.DataFrame) -> pd.Series:
    return enrollments.groupby("course_id")["student_id"].nunique().astype(int)

def validate_durations(courses: pd.DataFrame, timeslots: pd.DataFrame, course_period: dict[int, int]) -> pd.DataFrame:
    timeslot_len = timeslots.set_index("timeslot_id")["duration_min"].astype(int)
    valid_ids = set(timeslot_len.index.astype(int))

    rows = []
    for cid, period in course_period.items():
        dur = int(courses.loc[courses["course_id"] == cid, "exam_duration_min"].iloc[0])
        if period not in valid_ids:
            ok = False
            note = f"Invalid period {period} (not in timeslot list)"
        else:
            ok = dur <= int(timeslot_len.loc[period])
            note = "OK" if ok else "Too long"
        rows.append({
            "course_id": str(cid),
            "timeslot_id": int(period),
            "exam_ok": bool(ok),
            "duration_min": int(dur),
            "note": note
        })
    return pd.DataFrame(rows)


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def compare_algorithms(results_dict, outpath="outputs/algorithm_comparison.png"):
    """
    Compare color count, runtime, and conflicts across algorithms.
    Clean and balanced visualization for publication/presentation.
    """

    df = pd.DataFrame(results_dict).T
    df = df.fillna(0)

    plt.figure(figsize=(7, 4.5))
    plt.title("Algorithm Comparison", fontsize=14, weight="bold")

    # Left axis: Colors used
    ax1 = plt.gca()
    ax1.bar(
        df.index,
        df["colors_used"],
        color="#64B5F6",
        width=0.4,
        label="Colors Used",
        align="center",
    )
    ax1.set_ylabel("Colors Used", color="#1565C0", fontsize=11)
    ax1.tick_params(axis="y", labelcolor="#1565C0")
    ax1.set_ylim(0, max(df["colors_used"].max() * 1.2, 5))

    # Right axis: Runtime
    ax2 = ax1.twinx()
    ax2.plot(
        df.index,
        df["runtime"],
        color="#E53935",
        marker="o",
        linewidth=2.5,
        label="Runtime (s)",
    )
    ax2.set_ylabel("Runtime (s)", color="#B71C1C", fontsize=11)
    ax2.tick_params(axis="y", labelcolor="#B71C1C")
    ax2.set_ylim(0, max(df["runtime"].max() * 1.3, 0.1))

    # Add gridlines
    ax1.grid(axis="y", linestyle="--", alpha=0.6)

    # Annotate values
    for i, (algo, row) in enumerate(df.iterrows()):
        ax1.text(i, row["colors_used"] + 1, f"{int(row['colors_used'])}", ha="center", color="#0D47A1", fontsize=10)
        ax2.text(i, row["runtime"] + 0.02 * df["runtime"].max(), f"{row['runtime']:.2f}s", ha="center", color="#C62828", fontsize=9)

    # Legend
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right", frameon=False)

    plt.tight_layout()
    plt.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close()
    return outpath
