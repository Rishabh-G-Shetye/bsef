import pandas as pd


def ingest_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize column names to lowercase
    df.columns = [c.lower() for c in df.columns]

    # Map CSV variations to internal standard
    col_mapping = {
        "transaction_amount": "amount",
        "amt": "amount",
        "cost center": "cost_center",
        "gl code": "gl_code",
        "transaction type": "transaction_type"
    }
    df = df.rename(columns=col_mapping)

    # Required internal schema
    required_cols = {"amount", "vendor", "gl_code"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Create 'id' if missing
    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)

    # Ensure Accounting Month exists (derive from date if missing)
    if "accounting_month" not in df.columns and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["accounting_month"] = df["date"].dt.to_period("M").astype(str)

    return df