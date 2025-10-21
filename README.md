# Two-Stage Modular Streamlit Exam Scheduler

**Run**
```bash
pip install -r requirements.txt
streamlit run app/streamlit_main.py
```

**Data locations**
- Synthetic datasets: `data/synthetic/<timestamp>/`
- Outputs: `outputs/<timestamp>/`

**Algorithms**
- Greedy coloring
- DSATUR
- Simulated Annealing (on period assignments)

**Exports**
- `schedule_generated.csv` (course, period)
- `rooming_generated.csv` (course, period, room)
- `summary.txt`
- `Master_Exam_Schedule.pdf`
- `student_pdfs/<student_id>.pdf`
