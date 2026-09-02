from pydantic import BaseModel, Field
from typing import Optional

class AttritionRequest(BaseModel):
    Age: int = Field(ge=18, le=100)
    BusinessTravel: str
    Department: str
    DistanceFromHome: int = Field(ge=0)
    Education: int = Field(ge=1, le=5)
    EducationField: str
    EnvironmentSatisfaction: int = Field(ge=1, le=4)
    JobInvolvement: int = Field(ge=1, le=4)
    JobLevel: int = Field(ge=1)
    JobRole: str
    JobSatisfaction: int = Field(ge=1, le=4)
    MonthlyIncome: float = Field(gt=0)
    NumCompaniesWorked: int = Field(ge=0)
    OverTime: str
    PercentSalaryHike: float = Field(ge=0)
    PerformanceRating: int = Field(ge=1, le=5)
    RelationshipSatisfaction: int = Field(ge=1, le=4)
    StockOptionLevel: int = Field(ge=0)
    TotalWorkingYears: int = Field(ge=0)
    TrainingTimesLastYear: int = Field(ge=0)
    WorkLifeBalance: int = Field(ge=1, le=4)
    YearsAtCompany: int = Field(ge=0)
    YearsInCurrentRole: int = Field(ge=0)
    YearsSinceLastPromotion: int = Field(ge=0)
    YearsWithCurrManager: int = Field(ge=0)
