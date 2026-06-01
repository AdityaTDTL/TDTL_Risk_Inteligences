# AI Model Architecture

## 1. Transaction Risk Model

Input features:
- Amount
- Channel risk weight
- Undeclared repayment source flag
- Bureau inquiry velocity
- GPS mismatch distance
- Repeated source-account usage
- Employee override count

Output:
- Risk score from 0 to 100
- Risk category: Low, Medium, High, Critical
- Explainability reasons

## 2. Collections Fraud Model

Detects artificial collection spikes, month-end target manipulation, undeclared funding, geo mismatch and agent/agency abnormal behaviour.

## 3. Back-Channel Funding Model

Uses source-account reuse, customer-account mismatch, relationship graph and temporal repayment behaviour to detect temporary funding by third parties.

## 4. Employee Vigilance Model

Uses overrides, after-hours activity, suspicious access, repeated customer profile views and maker-checker violations.

## 5. CIBIL/Bureau Risk Model

Uses inquiry velocity, score deterioration and product-level credit shopping patterns.

## 6. Graph Collusion Model

Builds customer-account-agent-branch relationship graph. Flags:
- One account funding multiple unrelated customers
- One agent linked to suspicious customer cluster
- High centrality account or employee nodes
- Branch-level network anomalies

## 7. Agentic AI Layer

Agents:
- Investigation Summary Agent
- Rule Recommendation Agent
- Transaction Monitoring Agent
- Collections Fraud Agent
- Employee Vigilance Agent
- Bureau Monitoring Agent

The generated outputs should be treated as decision-support, not autonomous final decisions.
