import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from tdtl_risk_ai.features.feature_builder import build_transaction_matrix
rows = [
    {'amount': 100, 'source_account': 'A', 'declared_account': 'B', 'channel': 'UPI', 'source_lat': 12.9716, 'source_lon': 77.5946, 'declared_lat': 12.9716, 'declared_lon': 77.5946, 'customer_id': 'C1'},
    {'amount': 150, 'source_account': 'A', 'declared_account': 'A', 'channel': 'IMPS', 'source_lat': 13.0, 'source_lon': 77.5, 'declared_lat': 13.0, 'declared_lon': 77.5, 'customer_id': 'C1'},
    {'amount': 200, 'source_account': 'D', 'declared_account': 'D', 'channel': 'NEFT', 'source_lat': 0, 'source_lon': 0, 'declared_lat': 0, 'declared_lon': 0, 'customer_id': 'C2'},
]

df = build_transaction_matrix(rows)
print(df)
