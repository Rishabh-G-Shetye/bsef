import pandas as pd
import random


def generate_month(month, with_anomalies=False):
    data = []

    # These are the ONLY vendors that should appear
    gl_codes = [5001, 5002, 6001]
    vendors = ["Alpha Supplies", "Beta Services", "Gamma Corp"]
    cost_centers = ["IT", "Finance", "Operations"]

    # Generate 7-10 normal transactions
    normal_count = 7 if with_anomalies else 10

    for _ in range(normal_count):
        data.append({
            "gl_code": random.choice(gl_codes),
            "vendor": random.choice(vendors),
            "amount": round(random.uniform(900, 1500), 2),
            "accounting_month": month,
            "cost_center": random.choice(cost_centers),
            "transaction_type": "Invoice",
            "date": f"{month}-15"
        })

    if not with_anomalies:
        return pd.DataFrame(data)

    # Add the specific anomalies you want
    data.append({
        "gl_code": 5001,
        "vendor": "Alpha Supplies",
        "amount": 15000.00,  # The 10x spike
        "accounting_month": month,
        "cost_center": "IT",
        "transaction_type": "Invoice",
        "date": f"{month}-28"
    })

    # Add Gamma Corp anomaly
    data.append({
        "gl_code": 7200,
        "vendor": "Gamma Corp",
        "amount": 4200.00,
        "accounting_month": month,
        "cost_center": "Finance",
        "transaction_type": "Invoice",
        "date": f"{month}-29"
    })

    return pd.DataFrame(data)


def generate_synthetic_ledger():
    # Generate 3 months
    nov = generate_month("2025-11", with_anomalies=False)
    dec = generate_month("2025-12", with_anomalies=False)
    jan = generate_month("2026-01", with_anomalies=True)

    df = pd.concat([nov, dec, jan], ignore_index=True)
    # Add simple ID
    df['id'] = range(1, len(df) + 1)
    return df