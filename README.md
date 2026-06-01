# TDTL Risk Intelligence AI Engine

Integration-ready Python/Jupyter AI layer for the TDTL Real-Time Transaction Monitoring, Collections Fraud, Recovery Intelligence and Employee/Channel Vigilance Platform.

## Capabilities

- Real-time transaction risk scoring
- Collections fraud and artificial month-end spike detection
- Back-channel funding detection
- Agent/DSA behaviour risk scoring
- Employee vigilance anomaly scoring
- Bureau/CIBIL inquiry velocity risk
- Graph-based collusion analytics
- Agentic AI investigation summaries and rule recommendations
- FastAPI inference service for Django/React integration
- Jupyter notebooks for training, validation and explainability

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python scripts/generate_demo_data.py
python scripts/train_all_models.py
uvicorn tdtl_risk_ai.api.inference_api:app --host 0.0.0.0 --port 7000 --reload
```

API health check:

```bash
curl http://localhost:7000/health
```

Risk score:

```bash
curl -X POST http://localhost:7000/score/transaction \
  -H "Content-Type: application/json" \
  -d '{"amount":175000,"channel":"UPI","source_account":"ACC999","declared_account":"ACC123","bureau_inquiries_7d":4,"gps_mismatch_km":4.2,"repeated_source_count":8,"employee_override_count":1}'
# Phone Search Endpoint

```bash
curl -X POST http://localhost:7000/search-phone-number \
  -H "Content-Type: application/json" \
  -d '{"phone": "+91 9876543210", "transaction_id": "TX000123"}'
```

## Integration with Django Backend

Set this in the Django backend `.env`:

## Integration with Django Backend

Set this in the Django backend `.env`:

```env
AI_ENGINE_URL=http://localhost:7000
```

Call these endpoints from Django services:

- `POST /score/transaction`
- `POST /score/collection`
- `POST /score/employee`
- `POST /score/bureau`
- `POST /graph/collusion`
- `POST /agentic/investigation-summary`
- `POST /agentic/rule-recommendations`

## Folder Structure

```text
configs/                      Model and feature configuration
notebooks/                    Jupyter training and explainability notebooks
src/tdtl_risk_ai/api/          FastAPI inference layer
src/tdtl_risk_ai/agents/       Agentic AI services
src/tdtl_risk_ai/features/     Feature engineering
src/tdtl_risk_ai/models/       ML and rule-based models
src/tdtl_risk_ai/pipelines/    Training and scoring pipelines
src/tdtl_risk_ai/utils/        IO, logging and common utilities
data/sample/                   Generated demo data
model_artifacts/               Saved sklearn model artifacts
docs/                          Architecture and integration documentation
scripts/                       Data generation and training scripts
tests/                         Basic tests
```
