from pathlib import Path
import json
import warnings
warnings.filterwarnings("ignore")

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models" / "v1"
PROCESSED.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- Day 1: load + clean ----------------
attr = pd.read_csv(RAW / "employee_attrition.csv")
perf = pd.read_csv(RAW / "employee_performance.csv")
pro = pd.read_csv(RAW / "employee_performance_pro.csv")
occ = pd.read_csv(RAW / "occupation_data.csv")
ess = pd.read_csv(RAW / "essential_skills.csv")
soft = pd.read_csv(RAW / "software_skills.csv")

# Clean whitespace in string columns
def clean_strings(df):
    df = df.copy()
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype("string").str.strip()
    return df

attr = clean_strings(attr)
perf = clean_strings(perf)
pro = clean_strings(pro)
occ = clean_strings(occ)
ess = clean_strings(ess)
soft = clean_strings(soft)

# Preserve raw data; save processed copies
attr.to_csv(PROCESSED / "employee_attrition_processed.csv", index=False)
perf.to_csv(PROCESSED / "employee_performance_processed.csv", index=False)
pro.to_csv(PROCESSED / "employee_performance_pro_processed.csv", index=False)
occ.to_csv(PROCESSED / "occupation_master.csv", index=False)
ess.to_csv(PROCESSED / "essential_skills_processed.csv", index=False)
soft.to_csv(PROCESSED / "software_skills_processed.csv", index=False)

# Data-quality report
datasets = {
    "employee_attrition": attr,
    "employee_performance": perf,
    "employee_performance_pro": pro,
    "occupation": occ,
    "essential_skills": ess,
    "software_skills": soft,
}
quality = []
for name, df in datasets.items():
    quality.append({
        "dataset": name,
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    })
pd.DataFrame(quality).to_csv(PROCESSED / "data_quality_report.csv", index=False)

# ---------------- Day 2: feature engineering + model ----------------
# Keep a compact, explainable feature set.
features = [
    "Age", "BusinessTravel", "Department", "DistanceFromHome",
    "Education", "EducationField", "EnvironmentSatisfaction",
    "JobInvolvement", "JobLevel", "JobRole", "JobSatisfaction",
    "MonthlyIncome", "NumCompaniesWorked", "OverTime",
    "PercentSalaryHike", "PerformanceRating",
    "RelationshipSatisfaction", "StockOptionLevel",
    "TotalWorkingYears", "TrainingTimesLastYear",
    "WorkLifeBalance", "YearsAtCompany", "YearsInCurrentRole",
    "YearsSinceLastPromotion", "YearsWithCurrManager"
]
X = attr[features].copy()
y = (attr["Attrition"] == "Yes").astype(int)

# Business-motivated engineered features
X["IncomePerYearAtCompany"] = X["MonthlyIncome"] * 12 / (X["YearsAtCompany"] + 1)
X["PromotionGapRatio"] = X["YearsSinceLastPromotion"] / (X["YearsAtCompany"] + 1)
X["ExperienceRatio"] = X["YearsAtCompany"] / (X["TotalWorkingYears"] + 1)
X["SatisfactionIndex"] = (
    X["EnvironmentSatisfaction"] +
    X["JobSatisfaction"] +
    X["RelationshipSatisfaction"] +
    X["WorkLifeBalance"]
) / 4

numeric = X.select_dtypes(include=np.number).columns.tolist()
categorical = [c for c in X.columns if c not in numeric]

preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), numeric),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ]), categorical)
])

model = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)
pipeline = Pipeline([
    ("preprocess", preprocess),
    ("model", model)
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42
)
pipeline.fit(X_train, y_train)
probs = pipeline.predict_proba(X_test)[:, 1]
pred = (probs >= 0.5).astype(int)

metrics = {
    "precision": float(precision_score(y_test, pred, zero_division=0)),
    "recall": float(recall_score(y_test, pred, zero_division=0)),
    "f1": float(f1_score(y_test, pred, zero_division=0)),
    "roc_auc": float(roc_auc_score(y_test, probs)),
    "test_rows": int(len(y_test)),
}
joblib.dump(pipeline, MODEL_DIR / "attrition_pipeline.joblib")
(MODEL_DIR / "metadata.json").write_text(json.dumps({
    "model_name": "Attrition Prediction Model",
    "version": "v1.0",
    "algorithm": "LogisticRegression",
    "features": list(X.columns),
    "metrics": metrics,
}, indent=2), encoding="utf-8")
pd.DataFrame([metrics]).to_csv(PROCESSED / "model_metrics.csv", index=False)

# Score all attrition employees
all_probs = pipeline.predict_proba(X)[:, 1]
scored = attr[["EmployeeNumber", "Department", "JobRole"]].copy()
scored["Attrition_Prob"] = all_probs
scored["Risk"] = pd.cut(
    scored["Attrition_Prob"],
    bins=[-np.inf, 0.30, 0.60, np.inf],
    labels=["LOW", "MEDIUM", "HIGH"]
).astype(str)
scored.to_csv(PROCESSED / "attrition_scores.csv", index=False)

# ---------------- Day 3: engagement + O*NET intelligence ----------------
# Use uploaded HR analysis file when available because it contains engagement fields.
hr_path = RAW / "cleaned_hr_data.csv"
if hr_path.exists():
    hr = clean_strings(pd.read_csv(hr_path))
    if {"DepartmentType", "Engagement Score"}.issubset(hr.columns):
        engagement_summary = (
            hr.groupby("DepartmentType", dropna=False)["Engagement Score"]
              .mean().sort_values().reset_index()
        )
        engagement_summary.columns = ["Department", "AverageEngagement"]
        engagement_summary.to_csv(PROCESSED / "engagement_by_department.csv", index=False)
else:
    engagement_summary = pd.DataFrame(columns=["Department", "AverageEngagement"])

# O*NET role master
role_master = occ[["O*NET-SOC Code", "Title", "Description"]].drop_duplicates()
role_master.to_csv(PROCESSED / "occupation_master.csv", index=False)

# Required role skills: use the most interpretable O*NET element names,
# prioritizing Importance scale where available.
ess2 = ess.copy()
ess2 = ess2[ess2["Scale Name"].eq("Importance")] if "Scale Name" in ess2.columns else ess2
ess2["Data Value"] = pd.to_numeric(ess2["Data Value"], errors="coerce")
required = (
    ess2.dropna(subset=["O*NET-SOC Code", "Element Name", "Data Value"])
        .sort_values(["O*NET-SOC Code", "Data Value"], ascending=[True, False])
        .groupby("O*NET-SOC Code")
        .head(10)
)
required = required[["O*NET-SOC Code", "Title", "Element Name", "Data Value"]]
required.to_csv(PROCESSED / "role_required_skills.csv", index=False)

# Software skills by role
software = soft[["O*NET-SOC Code", "Title", "Workplace Example", "Hot Technology", "In Demand"]].drop_duplicates()
software.to_csv(PROCESSED / "role_software_skills.csv", index=False)

# ---------------- Controlled MVP employee skills ----------------
# There is no trustworthy current-employee-skill dataset in the uploaded files.
# To demonstrate the skill-gap engine without pretending otherwise, create a
# reproducible synthetic table for the first 500 attrition employees.
rng = np.random.default_rng(42)
employee_skills = []
skill_candidates = [
    "Reading Comprehension", "Active Listening", "Critical Thinking",
    "Complex Problem Solving", "Speaking", "Writing",
    "Time Management", "Systems Analysis", "Systems Evaluation",
    "Programming", "Data Analysis", "Project Management"
]
for eid in attr["EmployeeNumber"].head(500):
    k = int(rng.integers(3, 7))
    for skill in rng.choice(skill_candidates, size=k, replace=False):
        employee_skills.append({"EmployeeNumber": int(eid), "CurrentSkill": skill, "Source": "SYNTHETIC_MVP"})
employee_skills = pd.DataFrame(employee_skills)
employee_skills.to_csv(PROCESSED / "employee_skills_mvp_synthetic.csv", index=False)

# For a useful MVP demonstration, map each employee role to its top O*NET elements
# only when the role title exactly matches an O*NET title.
# ---------------- HR Role -> O*NET Role Mapping ----------------
# The HR dataset and O*NET use different occupation names.
# Therefore, we use an explicit controlled mapping instead of
# requiring an exact title match.

hr_to_onet_role = {
    "Sales Executive": "Sales Managers",
    "Research Scientist": "Biological Scientists",
    "Laboratory Technician": "Biological Technicians",
    "Manufacturing Director": "Industrial Production Managers",
    "Healthcare Representative": "Sales Representatives of Services",
    "Manager": "General and Operations Managers",
    "Sales Representative": "Sales Representatives of Services",
    "Research Director": "Natural Sciences Managers",
    "Human Resources": "Human Resources Managers",
}

# Build O*NET title -> required skills dictionary
role_skills_map = (
    required.groupby("Title")["Element Name"]
    .apply(lambda s: list(dict.fromkeys(s.tolist())))
    .to_dict()
)

current_map = employee_skills.groupby("EmployeeNumber")["CurrentSkill"].apply(set).to_dict()
gaps = []
for _, row in scored.head(500).iterrows():
    role = row["JobRole"]

# Convert HR role to the corresponding O*NET occupation
    onet_role = hr_to_onet_role.get(role)

# Retrieve the required O*NET skills
    required_set = set(role_skills_map.get(onet_role, []))
    current_set = current_map.get(int(row["EmployeeNumber"]), set())
    missing = sorted(required_set - current_set)
    gaps.append({
    "EmployeeNumber": int(row["EmployeeNumber"]),
    "JobRole": role,
    "ONETRole": onet_role if onet_role else "UNMAPPED",
    "SkillGap": ", ".join(missing[:10]),
    "SkillGapCount": len(missing),
})
gaps_df = pd.DataFrame(gaps)
gaps_df.to_csv(PROCESSED / "employee_skill_gaps.csv", index=False)

# Organization-wide gap severity
org = {}
for skills in gaps_df["SkillGap"].fillna(""):
    for s in [x.strip() for x in skills.split(",") if x.strip()]:
        org[s] = org.get(s, 0) + 1
org_df = pd.DataFrame(
    [{"Skill": k, "EmployeesMissing": v,
      "Severity": "HIGH" if v >= 100 else ("MEDIUM" if v >= 50 else "LOW")}
     for k, v in sorted(org.items(), key=lambda x: -x[1])]
)
org_df.to_csv(PROCESSED / "organization_skill_gaps.csv", index=False)

# Recommendation engine
recommendation_map = {
    "Programming": "Complete a Python/programming fundamentals course",
    "Data Analysis": "Complete a data analysis course with Python and SQL",
    "Project Management": "Complete a project management fundamentals course",
    "Systems Analysis": "Learn systems analysis and requirements engineering",
    "Systems Evaluation": "Learn systems evaluation and technology assessment",
    "Critical Thinking": "Take a critical-thinking and analytical decision-making course",
    "Complex Problem Solving": "Practice structured problem-solving and case studies",
    "Active Listening": "Take an active listening and communication course",
    "Speaking": "Take a professional communication and presentation course",
    "Writing": "Take a business writing course",
    "Time Management": "Take a time-management and productivity course",
    "Reading Comprehension": "Take a technical reading and comprehension course",
}
recs = []
for _, r in gaps_df.iterrows():
    skills = [s.strip() for s in str(r["SkillGap"]).split(",") if s.strip()]
    rec = recommendation_map.get(skills[0], f"Upskill in {skills[0]}") if skills else "No immediate recommendation"
    recs.append({
        "EmployeeNumber": r["EmployeeNumber"],
        "Recommendation": rec
    })
rec_df = pd.DataFrame(recs)

# Final employee intelligence table
intel = scored.head(500).merge(gaps_df, on=["EmployeeNumber", "JobRole"], how="left")
if hr_path.exists() and {"Employee ID", "Engagement Score"}.issubset(hr.columns):
    # Do not join: Employee ID namespaces are not proven compatible with EmployeeNumber.
    # Instead, leave engagement unmatched and preserve a separate analytics dataset.
    intel["Engagement"] = np.nan
else:
    intel["Engagement"] = np.nan
intel = intel.merge(rec_df, on="EmployeeNumber", how="left")
intel["SkillGap"] = intel["SkillGap"].fillna("")
intel["Recommendation"] = intel["Recommendation"].fillna("No role mapping / skill evidence available")
intel.to_csv(PROCESSED / "employee_intelligence.csv", index=False)

# Project relationship documentation
(ROOT / "docs" / "data_relationships.md").write_text("""# Data Relationships

## Verified relationships

- `occupation_data` ↔ `essential_skills`: **O*NET-SOC Code**
- `occupation_data` ↔ `software_skills`: **O*NET-SOC Code**

## Employee data

The uploaded employee datasets use different ID namespaces:
- attrition: `EmployeeNumber`
- performance: `Employee ID`
- performance_pro: `EmployeeID`
- cleaned HR analysis: `Employee ID`

These IDs were **not proven to refer to the same employees**, so the MVP does not merge them.

## Consequence

The attrition model is evaluated on `employee_attrition.csv`. Engagement and performance datasets are treated as separate analytics sources until a real common employee key is supplied.

The MVP skill table is synthetic and labelled `SYNTHETIC_MVP`; it exists only to demonstrate the skill-gap/recommendation pipeline.
""", encoding="utf-8")

print("Pipeline complete.")
print(json.dumps(metrics, indent=2))
