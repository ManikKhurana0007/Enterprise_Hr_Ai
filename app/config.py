from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
MODEL_PATH = ROOT / "models" / "v1" / "attrition_pipeline.joblib"
MODEL_META = ROOT / "models" / "v1" / "metadata.json"
