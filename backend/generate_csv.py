import pandas as pd
import random


def generate_csv_file():
    data = []

    # Configuration
    vendors = ["Alpha Supplies", "Beta Services", "Gamma Corp"]
    gl_codes = [5001, 5002, 6001]
    cost_centers = ["IT", "Finance", "Operations"]

    # --- HELPER: Random Date Generator (Strict YYYY-MM-DD) ---
    def get_random_date(year_month):
        day = random.randint(1, 28)
        return f"{year_month}-{day:02d}"

    # 1. Generate History (Oct, Nov, Dec 2025)
    # 10 transactions per month to build a baseline
    for month in ["2025-10", "2025-11", "2025-12"]:
        for _ in range(10):
            data.append({
                "date": get_random_date(month),
                "vendor": random.choice(vendors),
                "gl_code": random.choice(gl_codes),
                "amount": round(random.uniform(900, 1500), 2),
                "transaction_type": "Invoice",
                "cost_center": random.choice(cost_centers)
            })

    # 2. Generate Current Month (Jan 2026) - Normal Transactions
    # 8 normal transactions
    month = "2026-01"
    for _ in range(8):
        data.append({
            "date": get_random_date(month),
            "vendor": random.choice(vendors),
            "gl_code": random.choice(gl_codes),
            "amount": round(random.uniform(900, 1500), 2),
            "transaction_type": "Invoice",
            "cost_center": random.choice(cost_centers)
        })

    # 3. Insert Specific Anomalies for Testing

    # Anomaly A: Massive Spike (High Risk)
    data.append({
        "date": "2026-01-28",
        "vendor": "Alpha Supplies",
        "gl_code": 5001,
        "amount": 18500.00,  # Huge amount (Anomaly)
        "transaction_type": "Invoice",
        "cost_center": "IT"
    })

    # Anomaly B: New Vendor (Medium Risk)
    data.append({
        "date": "2026-01-29",
        "vendor": "Omega Solutions",  # New Vendor
        "gl_code": 5002,
        "amount": 1100.00,
        "transaction_type": "Invoice",
        "cost_center": "Operations"
    })

    # Anomaly C: Unusual Journal Entry (Medium/High Risk)
    data.append({
        "date": "2026-01-30",
        "vendor": "Beta Services",
        "gl_code": 6001,
        "amount": 4200.00,  # 3x normal amount
        "transaction_type": "Journal",  # Anomalous Type
        "cost_center": "Finance"
    })

    # Save to CSV
    df = pd.DataFrame(data)

    # Explicitly sort by date to keep it organized
    df = df.sort_values("date")

    filename = "test_ledger_upload.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Created '{filename}' with {len(df)} rows.")


if __name__ == "__main__":
    generate_csv_file()