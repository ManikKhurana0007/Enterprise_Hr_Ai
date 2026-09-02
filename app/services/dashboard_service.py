import pandas as pd
from app.config import PROCESSED

def _read(name):
    return pd.read_csv(PROCESSED / name)

def summary():
    scores = _read("attrition_scores.csv")
    metrics = _read("model_metrics.csv").iloc[0].to_dict()
    return {
        "total_employees_scored": int(len(scores)),
        "high_risk_employees": int((scores["Risk"] == "HIGH").sum()),
        "average_attrition_probability": float(scores["Attrition_Prob"].mean()),
        "model_roc_auc": float(metrics["roc_auc"]),
        "model_f1": float(metrics["f1"]),
    }

def attrition_by_department():
    s = _read("attrition_scores.csv")
    out = s.groupby("Department").agg(
        Employees=("EmployeeNumber", "count"),
        AverageRisk=("Attrition_Prob", "mean")
    ).reset_index()
    return out.to_dict(orient="records")

def skill_gaps():
    return _read("organization_skill_gaps.csv").head(50).to_dict(orient="records")

def recommendations():
    cols = ["EmployeeNumber", "JobRole", "Attrition_Prob", "Risk", "SkillGap", "Recommendation"]
    return _read("employee_intelligence.csv")[cols].head(100).to_dict(orient="records")

def employee(employee_id: int):
    df = _read("employee_intelligence.csv")
    row = df[df["EmployeeNumber"] == employee_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()
