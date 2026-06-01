from __future__ import annotations
from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from tdtl_risk_ai.utils.common import risk_category


class HybridRiskScorer:
    """Explainable weighted score used when trained models are unavailable or as policy overlay."""

    def score_transaction(self, payload: dict[str, Any]) -> dict:
        amount = float(payload.get("amount", 0) or 0)
        score = 8
        if amount >= 250000:
            score += 25
        elif amount >= 100000:
            score += 18
        elif amount >= 50000:
            score += 10
        score += 30 if payload.get("undeclared_source") else 0
        score += min(20, int(float(payload.get("gps_mismatch_km", 0)) * 4))
        score += min(24, int(payload.get("bureau_inquiries_7d", 0) or 0) * 8)
        score += min(20, int(payload.get("repeated_source_count", 0) or 0) * 5)
        score += min(16, int(payload.get("employee_override_count", 0) or 0) * 4)
        score += int(payload.get("channel_risk_weight", 0) or 0)
        score = max(0, min(100, score))
        reasons = []
        if payload.get("undeclared_source"):
            reasons.append("Payment source differs from declared customer account")
        if payload.get("bureau_inquiries_7d", 0) >= 3:
            reasons.append("High bureau inquiry velocity in recent window")
        if payload.get("repeated_source_count", 0) >= 3:
            reasons.append("Source account used across multiple repayments")
        if payload.get("gps_mismatch_km", 0) >= 2:
            reasons.append("Field visit/payment geography mismatch")
        return {"score": score, "category": risk_category(score), "reasons": reasons or ["No severe policy breach detected"]}

    def score_collection(self, payload: dict[str, Any]) -> dict:
        score = 10
        score += 20 if payload.get("month_end_flag") else 0
        score += min(25, int(max(0, float(payload.get("collection_spike_ratio", 1)) - 1) * 15))
        score += 25 if payload.get("undeclared_source") else 0
        score += min(20, int(payload.get("repeated_source_count", 0)) * 5)
        score += min(15, int(float(payload.get("gps_mismatch_km", 0)) * 3))
        score += min(20, int(payload.get("agent_prior_risk", 0)) // 5)
        score = min(100, score)
        return {"score": score, "category": risk_category(score), "reasons": ["Collection risk score combines month-end spike, undeclared funding, geo mismatch and agent prior risk"]}

    def score_employee(self, payload: dict[str, Any]) -> dict:
        score = 5
        score += min(24, int(payload.get("override_count_30d", 0)) * 4)
        score += min(24, int(payload.get("suspicious_activity_count_30d", 0)) * 6)
        score += min(15, int(payload.get("after_hours_activity_count", 0)) * 3)
        score += min(18, int(payload.get("repeated_customer_access_count", 0)) * 3)
        score += min(20, int(payload.get("maker_checker_violation_count", 0)) * 10)
        score = min(100, score)
        return {"score": score, "category": risk_category(score), "reasons": ["Employee risk score combines overrides, suspicious activity, after-hours behaviour and maker-checker violations"]}

    def score_bureau(self, payload: dict[str, Any]) -> dict:
        inquiries_24h = int(payload.get("inquiries_24h", 0))
        inquiries_7d = int(payload.get("inquiries_7d", 0))
        score_drop = int(payload.get("score_drop_30d", 0))
        score = min(100, 10 + inquiries_24h * 18 + inquiries_7d * 7 + score_drop // 2)
        return {"score": score, "category": risk_category(score), "reasons": ["Bureau risk uses inquiry velocity and recent score deterioration"]}


def train_isolation_forest(X: pd.DataFrame) -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", IsolationForest(n_estimators=120, contamination=0.08, random_state=42)),
    ]).fit(X)


def anomaly_score(model: Pipeline, X: pd.DataFrame) -> np.ndarray:
    raw = -model.decision_function(X)
    mn, mx = raw.min(), raw.max()
    if mx == mn:
        return np.full(len(raw), 50)
    return ((raw - mn) / (mx - mn) * 100).round(2)


def train_supervised_classifier(X: pd.DataFrame, y: pd.Series) -> RandomForestClassifier:
    clf = RandomForestClassifier(n_estimators=160, max_depth=8, random_state=42, class_weight="balanced")
    clf.fit(X, y)
    return clf
