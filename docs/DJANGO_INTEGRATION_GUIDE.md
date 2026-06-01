# Django Integration Guide

## Environment

Add to Django `.env`:

```env
AI_ENGINE_URL=http://localhost:7000
```

## Example Django Service Wrapper

```python
import os
import requests

AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://localhost:7000")

def score_transaction(payload):
    response = requests.post(f"{AI_ENGINE_URL}/score/transaction", json=payload, timeout=8)
    response.raise_for_status()
    return response.json()
```

## Suggested Backend Integration Points

1. On transaction creation: call `/score/transaction` and persist score/category/reasons.
2. On collection alert creation: call `/score/collection`.
3. On employee vigilance event: call `/score/employee`.
4. On loan application bureau inquiry: call `/score/bureau`.
5. On case opening: call `/agentic/investigation-summary`.
6. Nightly: send linked transactions to `/graph/collusion` and create high-risk cases.
