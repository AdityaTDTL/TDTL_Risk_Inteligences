import pandas as pd
from pathlib import Path
from tdtl_risk_ai.schemas.phone_search import CustomerProfile, TransactionRecord

DATA_ROOT = Path(__file__).resolve().parents[3] / "data"

CUSTOMERS_CSV = DATA_ROOT / "customers.csv"
TRANSACTIONS_CSV = DATA_ROOT / "transactions_120k.csv"

class CustomerService:
    @staticmethod
    async def get_customer_by_phone(phone: str) -> CustomerProfile | None:
        """Lookup a customer by normalized E164 phone number.
        Returns a CustomerProfile pydantic model or None if not found.
        """
        if not CUSTOMERS_CSV.exists():
            return None
        df = pd.read_csv(CUSTOMERS_CSV)
        # Assume column 'phone' stores numbers in E164 format
        row = df[df["phone"] == phone]
        if row.empty:
            return None
        r = row.iloc[0]
        return CustomerProfile(
            customer_id=str(r["customer_id"]),
            customer_name=str(r["customer_name"]),
            bureau_score=r.get("bureau_score"),
            city=r.get("city"),
            kyc_status=r.get("kyc_status"),
            base_risk_band=r.get("base_risk_band"),
        )

    @staticmethod
    async def get_transactions_by_customer_id(customer_id: str) -> list[TransactionRecord]:
        """Return a list of TransactionRecord for the given customer_id.
        Reads from transactions_120k.csv where column 'customer_id' matches.
        """
        if not TRANSACTIONS_CSV.exists():
            return []
        df = pd.read_csv(TRANSACTIONS_CSV)
        df_cust = df[df["customer_id"] == customer_id]
        records = []
        for _, row in df_cust.iterrows():
            records.append(
                TransactionRecord(
                    transaction_id=str(row["transaction_id"]),
                    amount=float(row["amount"]),
                    source_account_id=str(row["source_account_id"]),
                    device_id=str(row["device_id"]),
                    city=str(row["city"]),
                    channel=str(row["channel"]),
                    event_time=str(row["event_time"]),
                    month_end_spike_flag=bool(row["month_end_spike_flag"]),
                )
            )
        return records

