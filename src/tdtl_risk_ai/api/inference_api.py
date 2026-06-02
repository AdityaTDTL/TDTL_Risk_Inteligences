from __future__ import annotations

from fastapi import FastAPI, APIRouter, HTTPException

from tdtl_risk_ai.api.schemas import (
    TransactionScoreRequest,
    CollectionScoreRequest,
    EmployeeScoreRequest,
    BureauScoreRequest,
    GraphRequest,
    AgenticRequest,
)
from tdtl_risk_ai.schemas.phone_search import (
    PhoneSearchRequest,
    PhoneSearchResponse,
)
from tdtl_risk_ai.features.feature_builder import TransactionFeatures
from tdtl_risk_ai.models.risk_models import HybridRiskScorer
from tdtl_risk_ai.models.graph_models import collusion_indicators
from tdtl_risk_ai.agents.investigation_agents import (
    InvestigationSummaryAgent,
    RuleRecommendationAgent,
)
from tdtl_risk_ai.services.customer_service import CustomerService
from tdtl_risk_ai.services.fraud_analysis_service import FraudAnalysisService

app = FastAPI(title="TDTL Risk Intelligence AI Engine", version="1.0.0")
scorer = HybridRiskScorer()
summary_agent = InvestigationSummaryAgent()
rule_agent = RuleRecommendationAgent()
router = APIRouter()

@app.get("/health")
def health():
    return {"status": "ok", "service": "TDTL Risk Intelligence AI Engine", "version": "1.0.0"}

# Existing endpoints
@router.post("/score/transaction")
def score_transaction(req: TransactionScoreRequest):
    features = TransactionFeatures(**req.model_dump()).to_model_dict()
    result = scorer.score_transaction(features)
    return {"features": features, **result}

@router.post("/score/collection")
def score_collection(req: CollectionScoreRequest):
    return scorer.score_collection(req.model_dump())

@router.post("/score/employee")
def score_employee(req: EmployeeScoreRequest):
    return scorer.score_employee(req.model_dump())

@router.post("/score/bureau")
def score_bureau(req: BureauScoreRequest):
    return scorer.score_bureau(req.model_dump())

@router.post("/graph/collusion")
def graph_collusion(req: GraphRequest):
    return collusion_indicators(req.records)

@router.post("/agentic/investigation-summary")
def investigation_summary(req: AgenticRequest):
    return summary_agent.summarize(req.payload)

@router.post("/agentic/rule-recommendations")
def rule_recommendations(req: AgenticRequest):
    return rule_agent.recommend(req.payload)

# New phone‑search workflow endpoint
@router.post("/search-phone-number", response_model=PhoneSearchResponse)
async def search_phone_number(req: PhoneSearchRequest):
    # 1. Phone validation is handled by the Pydantic schema
    customer = await CustomerService.get_customer_by_phone(req.phone)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    # 2. Fetch all transactions for the customer
    transactions = await CustomerService.get_transactions_by_customer_id(customer.customer_id)
    # 3. If a specific transaction_id is supplied, locate it
    current_tx = None
    if req.transaction_id:
        current_tx = next((t for t in transactions if t.transaction_id == req.transaction_id), None)
        if not current_tx:
            raise HTTPException(status_code=404, detail="Transaction ID not found for this customer")
    # 4. Perform fraud analysis on the transaction list
    fraud_results = await FraudAnalysisService.analyze_transactions(transactions)
    # 5. Assemble response (including the requested transaction if any)
    response = PhoneSearchResponse(
        customer=customer,
        total_transactions=len(transactions),
        suspicious_transactions=len(fraud_results),
        average_repayment=None,
        current_transaction=current_tx,
        fraud_results=fraud_results,
        graph_summary={},
        final_alert="LOW",
    )
    return response

# Additional helper endpoints (optional)
@router.get("/customer-profile/{phone}")
async def get_customer_profile(phone: str):
    customer = await CustomerService.get_customer_by_phone(phone)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/transactions/{customer_id}")
async def get_transactions(customer_id: str):
    return await CustomerService.get_transactions_by_customer_id(customer_id)

@router.post("/fraud-analysis/{transaction_id}")
async def fraud_analysis(transaction_id: str):
    result = await FraudAnalysisService.analyze_transaction_by_id(transaction_id)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result

app.include_router(router)
