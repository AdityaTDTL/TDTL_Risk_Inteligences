from pydantic import BaseModel, Field, validator
import phonenumbers

class PhoneSearchRequest(BaseModel):
    phone: str = Field(..., description="Phone number in international format, e.g., '+91 9876543210'")
    transaction_id: str | None = Field(None, description="Optional transaction ID to investigate")

    @validator('phone')
    def validate_phone(cls, v: str) -> str:
        try:
            number = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(number):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            raise ValueError('Invalid phone number format') from e

class CustomerProfile(BaseModel):
    customer_id: str
    customer_name: str
    bureau_score: float | None = None
    city: str | None = None
    kyc_status: str | None = None
    base_risk_band: str | None = None

class TransactionRecord(BaseModel):
    transaction_id: str
    amount: float
    source_account_id: str
    device_id: str
    city: str
    channel: str
    event_time: str
    month_end_spike_flag: bool

class FraudAnalysisResult(BaseModel):
    transaction_id: str
    anomaly_score: float
    fraud_probability: float
    risk_details: dict
    final_risk_score: float
    risk_level: str
    description: str | None = None

class PhoneSearchResponse(BaseModel):
    customer: CustomerProfile
    total_transactions: int
    suspicious_transactions: int
    average_repayment: float | None = None
    current_transaction: TransactionRecord | None = None
    fraud_results: list[FraudAnalysisResult]
    graph_summary: dict
    final_alert: str
