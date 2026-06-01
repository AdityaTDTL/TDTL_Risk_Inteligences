from __future__ import annotations
import random
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample"
DATA.mkdir(parents=True, exist_ok=True)
random.seed(42)

channels = ["UPI", "IMPS", "NEFT", "Cards", "ATM", "Payment Gateway", "Wallet"]
branches = ["Pune", "Mumbai", "Nagpur", "Nashik", "Delhi", "Bengaluru"]

transactions = []
for i in range(5000):
    declared = f"ACC{random.randint(1000, 1300)}"
    source = declared if random.random() > 0.22 else f"ACC{random.randint(9000, 9050)}"
    transactions.append({
        "transaction_id": f"TX{i:06d}",
        "customer_id": f"CUST{random.randint(1, 1200):05d}",
        "agent_id": f"AG{random.randint(1, 100):04d}",
        "branch": random.choice(branches),
        "amount": round(random.lognormvariate(10.2, 0.8), 2),
        "channel": random.choice(channels),
        "source_account": source,
        "declared_account": declared,
        "bureau_inquiries_7d": random.choices([0,1,2,3,4,5], [40,25,15,10,6,4])[0],
        "gps_mismatch_km": round(max(0, random.gauss(1.2, 1.8)), 2),
        "repeated_source_count": random.choices([0,1,2,3,4,5,8,10], [35,25,15,8,7,5,3,2])[0],
        "employee_override_count": random.choices([0,1,2,3,5], [70,15,8,5,2])[0],
    })
pd.DataFrame(transactions).to_csv(DATA / "transactions.csv", index=False)

collections = []
for i in range(1500):
    collections.append({
        "alert_id": f"COL{i:05d}",
        "month_end_flag": int(random.random() < 0.35),
        "collection_spike_ratio": round(random.uniform(0.8, 4.5), 2),
        "undeclared_source": int(random.random() < 0.28),
        "repeated_source_count": random.randint(0, 10),
        "gps_mismatch_km": round(random.uniform(0, 8), 2),
        "agent_prior_risk": random.randint(0, 100),
    })
pd.DataFrame(collections).to_csv(DATA / "collections.csv", index=False)

employees = []
for i in range(500):
    employees.append({
        "employee_id": f"EMP{i:04d}",
        "override_count_30d": random.randint(0, 15),
        "suspicious_activity_count_30d": random.randint(0, 8),
        "after_hours_activity_count": random.randint(0, 10),
        "repeated_customer_access_count": random.randint(0, 20),
        "maker_checker_violation_count": random.randint(0, 3),
    })
pd.DataFrame(employees).to_csv(DATA / "employees.csv", index=False)

print(f"Demo data generated at {DATA}")
