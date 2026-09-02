import logging
from fastapi import FastAPI, HTTPException
from app.validation.employee_schema import AttritionRequest
from app.services.attrition_service import predict
from app.services.dashboard_service import summary, attrition_by_department, skill_gaps, recommendations, employee

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Enterprise HR AI", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Enterprise HR AI API", "docs": "/docs"}

@app.post("/predict/attrition")
def predict_attrition(payload: AttritionRequest):
    logger.info("Prediction request received")
    result = predict(payload.model_dump())
    logger.info("Prediction completed: %s", result)
    return result

@app.get("/dashboard/summary")
def dashboard_summary():
    return summary()

@app.get("/dashboard/attrition-by-department")
def department_attrition():
    return attrition_by_department()

@app.get("/dashboard/skill-gaps")
def dashboard_skill_gaps():
    return skill_gaps()

@app.get("/dashboard/recommendations")
def dashboard_recommendations():
    return recommendations()

@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    result = employee(employee_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result
