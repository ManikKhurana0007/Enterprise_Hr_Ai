from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

def test_model_artifacts_exist():
    assert (ROOT / "models/v1/attrition_pipeline.joblib").exists()
    assert (ROOT / "models/v1/metadata.json").exists()

def test_attrition_scores():
    df = pd.read_csv(DATA / "attrition_scores.csv")
    assert df["Attrition_Prob"].between(0, 1).all()
    assert set(df["Risk"].unique()) <= {"LOW", "MEDIUM", "HIGH"}

def test_skill_gap_output():
    df = pd.read_csv(DATA / "employee_skill_gaps.csv")
    assert {"EmployeeNumber", "JobRole", "SkillGap", "SkillGapCount"} <= set(df.columns)
