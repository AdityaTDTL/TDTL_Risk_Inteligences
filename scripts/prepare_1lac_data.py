import pandas as pd
from pathlib import Path
import numpy as np

def prepare_data():
    root = Path(__file__).resolve().parents[2]
    src_dir = root / "tdtl-risk-demo-dataset-1lac-plus" / "tdtl_risk_demo_dataset"
    dest_dir = root / "tdtl-risk-ai-engine" / "data" / "sample"
    dest_dir.mkdir(parents=True, exist_ok=True)

    print("Processing transactions...")
    tx_file = src_dir / "transactions" / "transactions_120k.csv"
    if tx_file.exists():
        tx_df = pd.read_csv(tx_file)
        
        # Mapping to required features
        out_tx = pd.DataFrame()
        out_tx["transaction_id"] = tx_df.get("transaction_id", range(len(tx_df)))
        out_tx["customer_id"] = tx_df.get("customer_id", "CUST_UNKNOWN")
        out_tx["amount"] = tx_df.get("amount", 0.0)
        out_tx["channel"] = tx_df.get("channel", "UPI")
        out_tx["source_account"] = tx_df.get("source_account_id", "")
        # Mock declared account based on the boolean match flag
        out_tx["declared_account"] = np.where(tx_df.get("declared_account_match", True), out_tx["source_account"], "ACC_DIFF")
        
        # Add numeric fields that might be missing in original
        out_tx["bureau_inquiries_7d"] = np.random.choice([0,1,2,3], size=len(tx_df), p=[0.7,0.15,0.1,0.05])
        out_tx["gps_mismatch_km"] = np.where(tx_df.get("third_party_pattern_flag", False), np.random.uniform(5, 50, len(tx_df)), 0.0)
        out_tx["repeated_source_count"] = np.random.poisson(0.5, len(tx_df))
        out_tx["employee_override_count"] = np.random.poisson(0.1, len(tx_df))
        
        out_tx.to_csv(dest_dir / "transactions.csv", index=False)
        print(f"Saved {len(out_tx)} transactions.")

    print("Processing collections...")
    coll_file = src_dir / "collections" / "field_visits_50k.csv"
    if coll_file.exists():
        coll_df = pd.read_csv(coll_file)
        out_coll = pd.DataFrame()
        out_coll["alert_id"] = coll_df.get("visit_id", range(len(coll_df)))
        out_coll["month_end_flag"] = np.random.choice([0,1], size=len(coll_df), p=[0.7,0.3])
        out_coll["collection_spike_ratio"] = np.random.uniform(0.5, 3.0, len(coll_df))
        out_coll["undeclared_source"] = np.where(coll_df.get("geo_mismatch_flag", False), 1, 0)
        out_coll["repeated_source_count"] = np.random.poisson(1, len(coll_df))
        out_coll["gps_mismatch_km"] = np.where(coll_df.get("geo_mismatch_flag", False), np.random.uniform(2, 20, len(coll_df)), 0.0)
        out_coll["agent_prior_risk"] = np.random.randint(0, 100, len(coll_df))
        
        out_coll.to_csv(dest_dir / "collections.csv", index=False)
        print(f"Saved {len(out_coll)} collections.")

    print("Processing employees (vigilance)...")
    emp_file = src_dir / "vigilance" / "employee_activity_30k.csv"
    if emp_file.exists():
        emp_df = pd.read_csv(emp_file)
        out_emp = pd.DataFrame()
        out_emp["employee_id"] = emp_df.get("employee_id", range(len(emp_df)))
        out_emp["override_count_30d"] = np.random.poisson(1, len(emp_df))
        out_emp["suspicious_activity_count_30d"] = np.where(emp_df.get("late_night_flag", False), np.random.randint(1, 5, len(emp_df)), 0)
        out_emp["after_hours_activity_count"] = np.where(emp_df.get("late_night_flag", False), 1, 0)
        out_emp["repeated_customer_access_count"] = np.where(emp_df.get("repeated_access_flag", False), np.random.randint(1, 10, len(emp_df)), 0)
        out_emp["maker_checker_violation_count"] = np.random.choice([0, 1, 2], size=len(emp_df), p=[0.9, 0.08, 0.02])
        
        out_emp.to_csv(dest_dir / "employees.csv", index=False)
        print(f"Saved {len(out_emp)} employee records.")

    print("Data preparation complete! You can now run `python scripts/train_all_models.py`.")

if __name__ == "__main__":
    prepare_data()
