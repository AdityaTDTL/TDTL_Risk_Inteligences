from __future__ import annotations

from dataclasses import dataclass
import math
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CHANNEL_WEIGHTS = {
    "UPI": 8,
    "IMPS": 10,
    "NEFT": 5,
    "RTGS": 7,
    "Cards": 6,
    "ATM": 9,
    "Payment Gateway": 8,
    "Wallet": 10,
}

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great‑circle distance between two points on Earth.

    The result is returned in kilometers.
    """
    # Convert degrees to radians
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    earth_radius_km = 6371.0
    return earth_radius_km * c

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class TransactionFeatures:
    amount: float = 0.0
    channel: str = "UPI"
    source_account: str = ""
    declared_account: str = ""
    bureau_inquiries_7d: int = 0
    gps_mismatch_km: float = 0.0
    repeated_source_count: int = 0
    employee_override_count: int = 0
    amount_deviation: float = 0.0  # Relative deviation from median for the customer

    def to_model_dict(self) -> dict:
        """Serialize the feature set into the dictionary expected by the ML models.
        The values are coerced to the correct primitive types used during training.
        """
        undeclared = bool(
            self.source_account and self.declared_account and self.source_account != self.declared_account
        )
        return {
            "amount": float(self.amount or 0),
            "undeclared_source": int(undeclared),
            "bureau_inquiries_7d": int(self.bureau_inquiries_7d or 0),
            "gps_mismatch_km": float(self.gps_mismatch_km or 0),
            "repeated_source_count": int(self.repeated_source_count or 0),
            "employee_override_count": int(self.employee_override_count or 0),
            "channel_risk_weight": CHANNEL_WEIGHTS.get(self.channel, 6),
            "amount_deviation": float(self.amount_deviation or 0),
        }

# ---------------------------------------------------------------------------
# Core Builders
# ---------------------------------------------------------------------------

def _enrich_gps(df: pd.DataFrame) -> pd.DataFrame:
    """Add a column ``gps_mismatch_km`` using the Haversine distance.

    Expected input columns (if present): ``source_lat``, ``source_lon``,
    ``declared_lat`` and ``declared_lon``. Missing columns default to ``0``.
    """
    lat1 = df.get("source_lat", 0).astype(float)
    lon1 = df.get("source_lon", 0).astype(float)
    lat2 = df.get("declared_lat", 0).astype(float)
    lon2 = df.get("declared_lon", 0).astype(float)
    df["gps_mismatch_km"] = [
        haversine(a, b, c, d) for a, b, c, d in zip(lat1, lon1, lat2, lon2)
    ]
    return df


def _add_repeated_source_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate how many times a ``source_account`` appears in the dataset.

    The column ``repeated_source_count`` is derived as ``occurrences - 1`` so that
    a solitary transaction gets a count of ``0``.
    """
    counts = df["source_account"].value_counts()
    df["repeated_source_count"] = df["source_account"].map(counts).fillna(1) - 1
    return df


def _add_amount_deviation(df: pd.DataFrame) -> pd.DataFrame:
    """Add a relative deviation of ``amount`` from the median amount per customer.

    The dataset is expected to contain a ``customer_id`` column. If the column is
    missing the deviation defaults to ``0``.
    """
    if "customer_id" not in df.columns:
        df["amount_deviation"] = 0.0
        return df
    median_per_customer = df.groupby("customer_id")["amount"].transform("median")
    df["median"] = median_per_customer
    # Avoid division by zero – if median is zero we treat deviation as zero.
    df["amount_deviation"] = df.apply(
        lambda row: (row["amount"] - row["median"]) / row["median"] if row["median"] != 0 else 0.0,
        axis=1,
    )
    df.drop(columns=["median"], inplace=True, errors="ignore")
    return df


def build_transaction_matrix(rows: list[dict] | pd.DataFrame) -> pd.DataFrame:
    """Construct the feature matrix expected by the risk scoring model.

    The function is tolerant to missing columns – default values are injected so
    downstream models always receive a consistent schema.
    """
    df = pd.DataFrame(rows)

    # ---------------------------------------------------------------------
    # Basic numeric columns – safe defaults are injected if they are absent.
    # ---------------------------------------------------------------------
    numeric_cols = [
        "amount",
        "bureau_inquiries_7d",
        "gps_mismatch_km",
        "repeated_source_count",
        "employee_override_count",
        "amount_deviation",
    ]
    for col in numeric_cols:
        if col not in df:
            df[col] = 0

    # ---------------------------------------------------------------------
    # Derived columns – undeclared source flag and channel risk weight.
    # ---------------------------------------------------------------------
    if "undeclared_source" not in df:
        df["undeclared_source"] = (
            df.get("source_account", "") != df.get("declared_account", "")
        ).astype(int)
    if "channel_risk_weight" not in df:
        df["channel_risk_weight"] = df.get("channel", "UPI").map(CHANNEL_WEIGHTS).fillna(6)

    # ---------------------------------------------------------------------
    # Enrichment steps – executed only if the required source columns exist.
    # ---------------------------------------------------------------------
    if {"source_lat", "source_lon", "declared_lat", "declared_lon"}.issubset(df.columns):
        df = _enrich_gps(df)
    if "source_account" in df.columns:
        df = _add_repeated_source_counts(df)
    if "customer_id" in df.columns:
        df = _add_amount_deviation(df)

    # ---------------------------------------------------------------------
    # Return the matrix in the precise order expected by the model.
    # ---------------------------------------------------------------------
    ordered = [
        "amount",
        "undeclared_source",
        "bureau_inquiries_7d",
        "gps_mismatch_km",
        "repeated_source_count",
        "employee_override_count",
        "channel_risk_weight",
        "amount_deviation",
    ]
    return df[ordered]


def build_collection_matrix(rows: list[dict] | pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    defaults = {
        "month_end_flag": 0,
        "collection_spike_ratio": 1.0,
        "undeclared_source": 0,
        "repeated_source_count": 0,
        "gps_mismatch_km": 0.0,
        "agent_prior_risk": 0,
    }
    for k, v in defaults.items():
        if k not in df:
            df[k] = v
    return df[list(defaults.keys())]


def build_employee_matrix(rows: list[dict] | pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    defaults = {
        "override_count_30d": 0,
        "suspicious_activity_count_30d": 0,
        "after_hours_activity_count": 0,
        "repeated_customer_access_count": 0,
        "maker_checker_violation_count": 0,
    }
    for k, v in defaults.items():
        if k not in df:
            df[k] = v
    return df[list(defaults.keys())]
