# Enterprise HR AI — Workforce Intelligence & Upskilling Platform

An end-to-end student project that combines:
- employee attrition prediction
- engagement analytics
- O*NET role intelligence
- organization skill-gap analysis
- rule/semantic-style upskilling recommendations
- FastAPI backend
- Streamlit dashboard
- prediction logging and tests

## Important dataset note

The uploaded datasets do **not** share one universal employee identifier.

- `employee_attrition.csv` has `EmployeeNumber` and 1,470 rows.
- `employee_performance.csv` has a different `Employee ID` namespace and 5,000 rows.
- `employee_performance_pro.csv` has another `EmployeeID` namespace and 500 rows.
- O*NET files connect roles through `O*NET-SOC Code`.

Therefore the project does **not** falsely join unrelated employee IDs. The attrition model is trained on the attrition dataset, while O*NET role/skill intelligence is handled as a separate reference layer. A synthetic controlled employee-skills table is generated only for the MVP skill-gap demonstration and is clearly labelled synthetic.

## Project structure

```text
enterprise_hr_ai/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── notebooks/
├── models/
├── app/
├── frontend/
├── tests/
├── docs/
└── requirements.txt
```

## Run

### 1. Create environment

Windows PowerShell:

```powershell
python -m venv venv
.env\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run Day 1–3 pipeline

```powershell
python scripts/build_pipeline.py
```

This creates cleaned data, the attrition model, O*NET role intelligence, synthetic MVP employee skills, skill gaps, recommendations, and the employee intelligence table.

### 3. Start API

```powershell
uvicorn app.main:app --reload
```

API docs:
`http://127.0.0.1:8000/docs`

### 4. Start dashboard

Open a second terminal:

```powershell
streamlit run frontend/dashboard.py
```

## Main API endpoints

- `POST /predict/attrition`
- `GET /dashboard/summary`
- `GET /dashboard/attrition-by-department`
- `GET /dashboard/skill-gaps`
- `GET /dashboard/recommendations`
- `GET /employees/{employee_id}`

## Model evaluation

The pipeline reports:
- Precision
- Recall
- F1
- ROC-AUC

Accuracy is not the primary selection metric because attrition is imbalanced.

## Production-hardening roadmap

After the MVP works:
- MLflow
- Docker
- drift monitoring
- live performance monitoring
- retraining rules
- authentication/authorization
- deployment
