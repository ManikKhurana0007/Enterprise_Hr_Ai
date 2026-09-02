import pandas as pd
from app.ml.model_loader import get_model

def predict(payload: dict):
    df = pd.DataFrame([payload])
    df["IncomePerYearAtCompany"] = df["MonthlyIncome"] * 12 / (df["YearsAtCompany"] + 1)
    df["PromotionGapRatio"] = df["YearsSinceLastPromotion"] / (df["YearsAtCompany"] + 1)
    df["ExperienceRatio"] = df["YearsAtCompany"] / (df["TotalWorkingYears"] + 1)
    df["SatisfactionIndex"] = (
        df["EnvironmentSatisfaction"] + df["JobSatisfaction"] +
        df["RelationshipSatisfaction"] + df["WorkLifeBalance"]
    ) / 4

    model = get_model()
    probability = float(model.predict_proba(df)[:, 1][0])
    if probability >= 0.60:
        risk = "HIGH"
    elif probability >= 0.30:
        risk = "MEDIUM"
    else:
        risk = "LOW"
    return {"attrition_probability": probability, "risk_level": risk}
