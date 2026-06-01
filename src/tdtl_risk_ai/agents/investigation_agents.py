from __future__ import annotations
from datetime import datetime


class InvestigationSummaryAgent:
    def summarize(self, case_payload: dict) -> dict:
        score = case_payload.get("risk_score") or case_payload.get("score") or 0
        entity = case_payload.get("customer_id") or case_payload.get("employee_id") or case_payload.get("agent_id") or "Unknown entity"
        reasons = case_payload.get("reasons") or []
        next_steps = []
        if score >= 85:
            next_steps = ["Immediate senior vigilance review", "Freeze automated clearance", "Collect payment-source evidence", "Audit linked agent/employee actions"]
        elif score >= 70:
            next_steps = ["Assign investigation case", "Verify declared account and customer confirmation", "Review linked transactions"]
        elif score >= 50:
            next_steps = ["Monitor for recurrence", "Request supporting documents if repeated"]
        else:
            next_steps = ["Allow with passive monitoring"]
        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "entity": entity,
            "executive_summary": f"Risk score {score}/100 generated for {entity}. Primary indicators: {', '.join(reasons) if reasons else 'standard monitoring indicators' }.",
            "recommended_next_steps": next_steps,
            "audit_note": "This summary is AI-assisted and must be validated by an authorized risk/vigilance officer before final action.",
        }


class RuleRecommendationAgent:
    def recommend(self, metrics: dict) -> dict:
        recommendations = []
        if metrics.get("month_end_spike_ratio", 1) >= 2.5:
            recommendations.append({"rule": "Trigger collection audit when agency month-end collection ratio exceeds 2.5x normal daily average", "severity": "High"})
        if metrics.get("shared_source_accounts", 0) >= 3:
            recommendations.append({"rule": "Flag repayment source account linked to 3 or more unrelated customers", "severity": "Critical"})
        if metrics.get("bureau_inquiries_7d", 0) >= 4:
            recommendations.append({"rule": "Hold disbursement review when applicant has 4 or more bureau inquiries in 7 days", "severity": "High"})
        if metrics.get("employee_overrides_30d", 0) >= 8:
            recommendations.append({"rule": "Escalate employee review when manual overrides exceed 8 in 30 days", "severity": "High"})
        return {"recommendations": recommendations or [{"rule": "No new rule recommended from supplied metrics", "severity": "Info"}]}
