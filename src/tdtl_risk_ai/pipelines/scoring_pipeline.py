from __future__ import annotations
import pandas as pd
from tdtl_risk_ai.features.feature_builder import TransactionFeatures
from tdtl_risk_ai.models.risk_models import HybridRiskScorer

scorer = HybridRiskScorer()


def score_transactions(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        features = TransactionFeatures(
            amount=row.get("amount", 0),
            channel=row.get("channel", "UPI"),
            source_account=row.get("source_account", ""),
            declared_account=row.get("declared_account", ""),
            bureau_inquiries_7d=row.get("bureau_inquiries_7d", 0),
            gps_mismatch_km=row.get("gps_mismatch_km", 0),
            repeated_source_count=row.get("repeated_source_count", 0),
            employee_override_count=row.get("employee_override_count", 0),
        ).to_model_dict()
        result = scorer.score_transaction(features)
        rows.append({**row.to_dict(), **features, "risk_score": result["score"], "risk_category": result["category"], "risk_reasons": "; ".join(result["reasons"])})
    return pd.DataFrame(rows)
