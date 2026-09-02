# Data Relationships

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
