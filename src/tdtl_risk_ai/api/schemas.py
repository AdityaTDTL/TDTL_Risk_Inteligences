from pydantic import BaseModel, Field
from typing import Any

class TransactionScoreRequest(BaseModel):
    amount: float = 0
    channel: str = "UPI"
    source_account: str = ""
    declared_account: str = ""
    bureau_inquiries_7d: int = 0
    gps_mismatch_km: float = 0
    repeated_source_count: int = 0
    employee_override_count: int = 0

class CollectionScoreRequest(BaseModel):
    month_end_flag: bool = False
    collection_spike_ratio: float = 1.0
    undeclared_source: bool = False
    repeated_source_count: int = 0
    gps_mismatch_km: float = 0
    agent_prior_risk: int = 0

class EmployeeScoreRequest(BaseModel):
    override_count_30d: int = 0
    suspicious_activity_count_30d: int = 0
    after_hours_activity_count: int = 0
    repeated_customer_access_count: int = 0
    maker_checker_violation_count: int = 0

class BureauScoreRequest(BaseModel):
    inquiries_24h: int = 0
    inquiries_7d: int = 0
    score_drop_30d: int = 0

class GraphRequest(BaseModel):
    records: list[dict[str, Any]] = Field(default_factory=list)

class AgenticRequest(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)
