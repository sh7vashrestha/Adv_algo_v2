"""
data_generator.py
-----------------
Synthetic dataset generator for the Exam Scheduler system.

Generates:
    - students.csv
    - courses.csv
    - classrooms.csv
    - timeslots.csv
    - enrollments.csv
    - enrollments.stu  (Toronto format)
All saved under /data/synthetic/<timestamp>/
"""

import os
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta


def generate_synthetic_dataset(
    n_students: int = 10000,
    n_courses: int = 100,
    n_rooms: int = 50,
    n_periods: int = 80,
    min_courses_per_student: int = 3,
    max_courses_per_student: int = 6,
    seed: int = 42,
    out_root: str = "data/synthetic",
) -> str:
    """Generate synthetic exam data and save to a timestamped folder."""
    rng = np.random.default_rng(seed)
    fake = Faker()
    Faker.seed(seed)

    # --- Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = os.path.join(out_root, timestamp)
    os.makedirs(outdir, exist_ok=True)

    # ============================================================
    # 🧍 Students
    # ============================================================
    students = pd.DataFrame({
        "student_id": np.arange(1, n_students + 1),
        "first_name": [fake.first_name() for _ in range(n_students)],
        "last_name": [fake.last_name() for _ in range(n_students)],
        "email": [fake.email() for _ in range(n_students)],
        "program_name": rng.choice(
            ["CS", "IT", "SE", "DS", "Math", "Physics", "CyberSec"], size=n_students
        ),
        "year": rng.integers(1, 5, size=n_students),
    })
    students.to_csv(os.path.join(outdir, "students.csv"), index=False)

        # ============================================================
    # 📚 Courses
    # ============================================================
    departments = ["CS", "IT", "SE", "DS", "Math", "PHY", "CYB"]
    dept_codes = {
        "CS": "CS",
        "IT": "IT",
        "SE": "SE",
        "DS": "DS",
        "Math": "MA",
        "PHY": "PH",
        "CYB": "CY"
    }

    # Random department for each course
    dept_choices = rng.choice(departments, size=n_courses)

    # Generate unique, realistic course IDs like "CS0291"
    course_ids = []
    used_ids = set()
    for dept in dept_choices:       
        while True:
            num_code = rng.integers(1000, 4999)
            cid = f"{dept_codes[dept]}{num_code}"
            if cid not in used_ids:
                used_ids.add(cid)
                course_ids.append(cid)
                break


    # Generate realistic course names using Faker
    fake_course_titles = [
        f"{fake.catch_phrase().split()[0]} {fake.word().capitalize()}"
        for _ in range(n_courses)
    ]

    # Combine into DataFrame
    courses = pd.DataFrame({
        "course_id": course_ids,
        "course_name": fake_course_titles,
        "department": dept_choices,
        "credits": rng.integers(2, 5, size=n_courses),
        "description": [fake.sentence(nb_words=10) for _ in range(n_courses)],
        "exam_duration_min": rng.choice(
            [60, 90, 120, 150, 180],
            size=n_courses,
            p=[0.1, 0.2, 0.4, 0.2, 0.1]
        ),
    })
    courses.to_csv(os.path.join(outdir, "courses.csv"), index=False)


    # ============================================================
    # 🏫 Classrooms
    # ============================================================
    classrooms = pd.DataFrame({
        "classroom_id": np.arange(1, n_rooms + 1),
        "building_name": [f"Bldg {fake.random_uppercase_letter()}" for _ in range(n_rooms)],
        "room_number": rng.integers(100, 499, size=n_rooms),
        "capacity": rng.integers(30, 300, size=n_rooms),
        "room_type": rng.choice(
            ["Lecture Hall", "Lab", "Seminar", "Auditorium"], size=n_rooms
        ),
    })
    classrooms.to_csv(os.path.join(outdir, "classrooms.csv"), index=False)

    # ============================================================
    # 🕙 Timeslots — weekdays only (Mon–Fri)
    #  → 2–3 sessions per day between 10:00–15:00
    #  → at least one 180-min exam each day
    #  → start times snapped to :00 or :30
    # ============================================================

    start_date = datetime.now().date()
    timeslot_rows = []
    current_day = start_date
    times_created = 0

    def snap_to_half_hour(minutes):
        """Round minutes to nearest 00 or 30 mark."""
        hh, mm = divmod(minutes, 60)
        if mm < 15:
            mm = 0
        elif mm < 45:
            mm = 30
        else:
            hh += 1
            mm = 0
        return hh * 60 + mm

    while times_created < n_periods:
        # Skip weekends (Saturday=5, Sunday=6)
        if current_day.weekday() >= 5:
            current_day += timedelta(days=1)
            continue

        # 🎯 2–3 sessions per day
        sessions_today = int(rng.integers(2, 4))  # {2, 3}
        daily_slots = []
        start_hour = 10
        latest_end_hour = 15

        # ensure one 180-min duration exists
        has_long_exam = False

        for i in range(sessions_today):
            # Pick duration (force one 180-min per day)
            if not has_long_exam and (i == sessions_today - 1 or rng.random() < 0.3):
                dur = 180
                has_long_exam = True
            else:
                dur = int(rng.choice(
                        [90, 105, 120, 150, 180],
                        p=[0.25, 0.25, 0.2, 0.2, 0.1]
                ))

            earliest_start = start_hour * 60
            latest_start = latest_end_hour * 60 - dur
            if latest_start <= earliest_start:
                break

            start_minute = int(rng.integers(earliest_start, latest_start + 1))
            start_minute = snap_to_half_hour(start_minute)
            end_minute = start_minute + dur

            # ensure exam ends before 15:30 (3:30 PM)
            if end_minute > (latest_end_hour * 60 + 30):
                continue

            daily_slots.append((start_minute, end_minute, dur))

        # guarantee at least one 180-min slot if none was placed
        if not any(d == 180 for _, _, d in daily_slots):
            # insert one at midday if possible
            start_minute = snap_to_half_hour((12 - start_hour) * 60)
            end_minute = start_minute + 180
            if end_minute <= (latest_end_hour * 60 + 30):
                daily_slots.append((start_minute, end_minute, 180))

        # Sort and save for the day
        daily_slots = sorted(daily_slots, key=lambda x: x[0])
        seen = set()
        for start_minute, end_minute, dur in daily_slots:
            if times_created >= n_periods:
                break
            start_time = datetime.combine(current_day, datetime.min.time()) + timedelta(minutes=start_minute)
            end_time = datetime.combine(current_day, datetime.min.time()) + timedelta(minutes=end_minute)
            key = start_time.strftime("%H:%M")
            if key in seen:
                continue
            seen.add(key)
            timeslot_rows.append({
                "timeslot_id": times_created + 1,
                "day": current_day.isoformat(),
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "duration_min": dur,
            })
            times_created += 1

        current_day += timedelta(days=1)

    timeslots = pd.DataFrame(timeslot_rows)
    timeslots.to_csv(os.path.join(outdir, "timeslots.csv"), index=False)


    # ============================================================
    # 🧾 Enrollments (each student takes 3–6 random courses)
    # ============================================================
    enrollment_rows = []
    # group courses by department to reduce global overlap
    dept_groups = {dept: courses[courses["department"] == dept]["course_id"].tolist()
                   for dept in courses["department"].unique()}

    for _, s in students.iterrows():
        dept = s["program_name"]
        n_taken = rng.integers(min_courses_per_student, max_courses_per_student + 1)
        available = dept_groups.get(dept, courses["course_id"].tolist())
        # choose mostly within same dept, small chance cross-dept
        if len(available) >= n_taken:
            enrolled = rng.choice(available, size=n_taken, replace=False)
        else:
            extra = rng.choice(courses["course_id"], size=n_taken - len(available), replace=False)
            enrolled = np.concatenate([available, extra])
        for cid in enrolled:
            enrollment_rows.append((s["student_id"], cid))


    enrollments = pd.DataFrame(enrollment_rows, columns=["student_id", "course_id"])
    enrollments.to_csv(os.path.join(outdir, "enrollments.csv"), index=False)

    # Toronto-style .stu file (one line per student)
    stu_lines = (
        enrollments.groupby("student_id")["course_id"]
        .apply(lambda cids: " ".join(map(str, cids)))
        .tolist()
    )
    with open(os.path.join(outdir, "enrollments.stu"), "w") as f:
        f.write("\n".join(stu_lines))

    print(f"✅ Synthetic dataset created at: {outdir}")
    return outdir


if __name__ == "__main__":
    generate_synthetic_dataset()
