from __future__ import annotations
from pathlib import Path
import json
import joblib

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = ROOT / "model_artifacts"
DATA_DIR = ROOT / "data" / "sample"


def ensure_dirs() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def risk_category(score: float) -> str:
    if score >= 85:
        return "Critical"
    if score >= 70:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


def save_model(obj, name: str) -> Path:
    ensure_dirs()
    path = ARTIFACT_DIR / name
    joblib.dump(obj, path)
    return path


def load_model(name: str):
    return joblib.load(ARTIFACT_DIR / name)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
