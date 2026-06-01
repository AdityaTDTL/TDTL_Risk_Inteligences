from tdtl_risk_ai.models.risk_models import HybridRiskScorer


def test_transaction_score_high_for_undeclared_repeated_source():
    scorer = HybridRiskScorer()
    result = scorer.score_transaction({
        "amount": 200000,
        "undeclared_source": 1,
        "bureau_inquiries_7d": 4,
        "gps_mismatch_km": 3,
        "repeated_source_count": 5,
        "employee_override_count": 1,
        "channel_risk_weight": 8,
    })
    assert result["score"] >= 70
    assert result["category"] in {"High", "Critical"}
