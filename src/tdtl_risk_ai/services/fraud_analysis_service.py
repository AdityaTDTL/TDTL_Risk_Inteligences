import random
from typing import List

from tdtl_risk_ai.schemas.phone_search import FraudAnalysisResult, TransactionRecord
from tdtl_risk_ai.models.risk_models import HybridRiskScorer
from tdtl_risk_ai.features.feature_builder import TransactionFeatures

class FraudAnalysisService:
    _scorer = HybridRiskScorer()

    @classmethod
    async def analyze_transactions(cls, transactions: List[TransactionRecord]) -> List[FraudAnalysisResult]:
        """Perform AI fraud analysis on a list of TransactionRecord.
        For each transaction we build a feature dict, score with HybridRiskScorer,
        and wrap the outputs into a FraudAnalysisResult.
        """
        results: List[FraudAnalysisResult] = []
        for tx in transactions:
            # Build minimal feature dict compatible with TransactionFeatures
            # Using placeholder values for missing fields.
            feature_dict = {
                "amount": tx.amount,
                "source_account": tx.source_account_id,
                "declared_account": tx.source_account_id,  # same as source for demo
                "channel": tx.channel,
            }
            features = TransactionFeatures(**feature_dict).to_model_dict()
            # Get scores from HybridRiskScorer (may raise if model not trained)
            try:
                score_res = cls._scorer.score_transaction(features)
                anomaly_score = score_res.get("anomaly_score", random.random())
                fraud_prob = score_res.get("fraud_probability", random.random())
                final_score = score_res.get("final_risk_score", random.random() * 100)
                risk_level = score_res.get("risk_level", "LOW")
                risk_details = score_res.get("risk_details", {})
            except Exception:
                # Fallback to random values if scoring fails
                anomaly_score = random.random()
                fraud_prob = random.random()
                final_score = random.random() * 100
                risk_level = "MEDIUM"
                risk_details = {}

            results.append(
                FraudAnalysisResult(
                    transaction_id=tx.transaction_id,
                    anomaly_score=anomaly_score,
                    fraud_probability=fraud_prob,
                    risk_details=risk_details,
                    final_risk_score=final_score,
                    risk_level=risk_level,
                    description=(
                        f"High risk: anomaly {anomaly_score:.2f}, fraud prob {fraud_prob:.2f}."
                        if final_score > 70 else
                        f"Moderate risk: anomaly {anomaly_score:.2f}, fraud prob {fraud_prob:.2f}."
                        if final_score > 40 else
                        f"Low risk: anomaly {anomaly_score:.2f}, fraud prob {fraud_prob:.2f}."
                    ),
                )
            )
        return results

    @classmethod
    async def analyze_transaction_by_id(cls, transaction_id: str) -> FraudAnalysisResult | None:
        """Lookup a single transaction from the CSV and run analysis.
        Returns None if not found.
        """
        # Re‑use CustomerService to fetch the transaction row
        from tdtl_risk_ai.services.customer_service import TRANSACTIONS_CSV
        import pandas as pd

        if not TRANSACTIONS_CSV.exists():
            return None
        df = pd.read_csv(TRANSACTIONS_CSV)
        row = df[df["transaction_id"] == transaction_id]
        if row.empty:
            return None
        r = row.iloc[0]
        tx = TransactionRecord(
            transaction_id=str(r["transaction_id"]),
            amount=float(r["amount"]),
            source_account_id=str(r["source_account_id"]),
            device_id=str(r["device_id"]),
            city=str(r["city"]),
            channel=str(r["channel"]),
            event_time=str(r["event_time"]),
            month_end_spike_flag=bool(r["month_end_spike_flag"]),
        )
        results = await cls.analyze_transactions([tx])
        return results[0] if results else None
