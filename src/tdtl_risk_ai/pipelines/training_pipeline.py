from __future__ import annotations
import pandas as pd
from pathlib import Path
from tdtl_risk_ai.features.feature_builder import build_transaction_matrix, build_collection_matrix, build_employee_matrix
from tdtl_risk_ai.models.risk_models import train_isolation_forest
from tdtl_risk_ai.utils.common import DATA_DIR, save_model, ensure_dirs


def train_all(data_dir: Path = DATA_DIR) -> dict:
    ensure_dirs()
    outputs = {}
    tx_path = data_dir / "transactions.csv"
    if tx_path.exists():
        tx = pd.read_csv(tx_path)
        model = train_isolation_forest(build_transaction_matrix(tx))
        outputs["transaction_anomaly_model"] = str(save_model(model, "transaction_anomaly.joblib"))
    coll_path = data_dir / "collections.csv"
    if coll_path.exists():
        coll = pd.read_csv(coll_path)
        model = train_isolation_forest(build_collection_matrix(coll))
        outputs["collection_anomaly_model"] = str(save_model(model, "collection_anomaly.joblib"))
    emp_path = data_dir / "employees.csv"
    if emp_path.exists():
        emp = pd.read_csv(emp_path)
        model = train_isolation_forest(build_employee_matrix(emp))
        outputs["employee_anomaly_model"] = str(save_model(model, "employee_anomaly.joblib"))
    return outputs
