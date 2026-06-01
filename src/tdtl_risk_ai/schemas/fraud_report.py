from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class HistoricalBehaviour(BaseModel):
    avg_repayment_amount: float = Field(..., description="Average repayment amount across historical transactions")
    normal_city: str = Field(..., description="Most frequent city in historical transactions")
    normal_device: str = Field(..., description="Most frequent device ID in historical transactions")
    usual_transaction_time: str = Field(..., description="Most frequent transaction hour (e.g., '20:00')")
    normal_source_account: str = Field(..., description="Most frequent source account ID in historical transactions")

class CurrentTransaction(BaseModel):
    transaction_id: str
    amount: float
    city: str
    device_id: str
    transaction_time: str = Field(..., description="Hour portion of event_time, e.g., '02:00'")
    source_account_id: str

class ParameterComparison(BaseModel):
    parameter: str
    historical: str
    current: str
    risk: str

class ComparisonEngine(BaseModel):
    comparisons: List[ParameterComparison]

class RiskFeatures(BaseModel):
    amount_anomaly_risk: str
    device_risk: str
    geo_risk: str
    timing_risk: str
    shared_account_risk: str
    agent_risk: str = Field(default="LOW")

class AIModelResult(BaseModel):
    model_name: str
    result: str
    anomaly_score: Optional[float] = None
    fraud_probability: Optional[float] = None
    details: Optional[Dict] = None

class AIModelResults(BaseModel):
    results: List[AIModelResult]

class RiskScoring(BaseModel):
    final_risk_score: float
    risk_level: str
    fraud_probability: float

class FinalDecision(BaseModel):
    decision: str
    explanation: List[str]
    recommended_action: str

class FraudReportResponse(BaseModel):
    historical_behaviour: HistoricalBehaviour
    current_transaction: CurrentTransaction
    comparison_engine: ComparisonEngine
    risk_features: RiskFeatures
    ai_model_results: AIModelResults
    risk_scoring: RiskScoring
    final_decision: FinalDecision
    alerts: List[str] = []
