"""
room_allocator.py
-----------------
Allocates multiple exams in the same period across different rooms.
 - Allows parallel exams (different courses same period)
 - Avoids reusing rooms in the same timeslot
 - Matches room capacity as best as possible
 - Works with alphanumeric course IDs
"""

import pandas as pd
import numpy as np


def allocate_rooms(
    course_enrollment: dict[str, int],
    timeslots: pd.DataFrame,
    course_period: dict[str, int],
    classrooms: pd.DataFrame,
) -> pd.DataFrame:
    """
    Assign rooms to exams given student counts and period assignments.

    Multiple courses can share the same timeslot (period), but each room can
    only host one exam at that time.
    """
    # Normalize data types
    timeslots["timeslot_id"] = timeslots["timeslot_id"].astype(int)
    classrooms["classroom_id"] = classrooms["classroom_id"].astype(int)
    course_period = {str(k): int(v) for k, v in course_period.items()}
    course_enrollment = {str(k): int(v) for k, v in course_enrollment.items()}

    rng = np.random.default_rng(42)
    valid_periods = set(timeslots["timeslot_id"].astype(int))
    assignments = []

    # Shuffle classrooms globally once
    classrooms = classrooms.sample(frac=1, random_state=42).reset_index(drop=True)
    rooms_sorted = classrooms.sort_values("capacity").reset_index(drop=True)

    # Track rooms already used in each period
    rooms_used = {tid: set() for tid in valid_periods}

    # Build DataFrame for course info
    df_courses = pd.DataFrame(
        [(cid, course_period[cid], course_enrollment.get(cid, 0)) for cid in course_period],
        columns=["course_id", "timeslot_id", "size"],
    )

    # Allocate per timeslot
    for tid, group in df_courses.groupby("timeslot_id"):
        if tid not in valid_periods:
            continue

        # Sort larger exams first (greedy fit)
        group = group.sort_values("size", ascending=False)

        for _, row in group.iterrows():
            cid = str(row["course_id"])
            size = int(row["size"])
            placed = False

            # Try to find the smallest available room >= size
            for _, r in rooms_sorted.iterrows():
                rid = int(r["classroom_id"])
                cap = int(r["capacity"])

                if rid in rooms_used[tid]:
                    continue  # room already booked for this period

                if cap >= size:
                    assignments.append((cid, tid, rid))
                    rooms_used[tid].add(rid)
                    placed = True
                    break

            # If no suitable room found → assign largest available
            if not placed:
                # get largest free room for this period
                free_rooms = [r for r in rooms_sorted["classroom_id"] if r not in rooms_used[tid]]
                if free_rooms:
                    rid = int(free_rooms[-1])
                    assignments.append((cid, tid, rid))
                    rooms_used[tid].add(rid)
                else:
                    # all rooms full → mark as TBD (shouldn't happen if rooms > courses per slot)
                    assignments.append((cid, tid, -1))

    return pd.DataFrame(assignments, columns=["course_id", "timeslot_id", "classroom_id"])
