import pandas as pd
import random


def generate_month(month, with_anomalies=False):
    data = []

    gl_codes = [5001, 5002, 6001]
    vendors = ["Alpha Supplies", "Beta Services", "Gamma Corp"]
    cost_centers = ["IT", "Finance", "Operations"]

    # -----------------------------
    # NORMAL TRANSACTIONS
    # -----------------------------
    normal_count = 8 if with_anomalies else 12

    for _ in range(normal_count):
        data.append({
            "gl_code": random.choice(gl_codes),
            "vendor": random.choice(vendors),
            "amount": round(random.uniform(900, 1500), 2),
            "accounting_month": month,
            "cost_center": random.choice(cost_centers),
            "transaction_type": "Invoice",
            "date": f"{month}-{random.randint(1, 28):02d}"
        })

    if not with_anomalies:
        return pd.DataFrame(data)

    # -----------------------------
    # ANOMALIES (JAN 2026)
    # -----------------------------

    # 1. HIGH RISK: Massive Spike (10x)
    data.append({
        "gl_code": 5001,
        "vendor": "Alpha Supplies",
        "amount": 15000.00,
        "accounting_month": month,
        "cost_center": "IT",
        "transaction_type": "Invoice",
        "date": f"{month}-28"
    })

    # 2. HIGH RISK: New GL Code
    data.append({
        "gl_code": 7200,
        "vendor": "Gamma Corp",
        "amount": 4200.00,
        "accounting_month": month,
        "cost_center": "Finance",
        "transaction_type": "Invoice",
        "date": f"{month}-29"
    })

    # 3. MEDIUM RISK: Unusual Journal Entry (Amount is high, but not insane)
    data.append({
        "gl_code": 6001,
        "vendor": "Beta Services",
        "amount": 3500.00,
        "accounting_month": month,
        "cost_center": "Operations",
        "transaction_type": "Journal",  # Anomalous Type
        "date": f"{month}-30"
    })

    # 4. MEDIUM RISK: New Vendor (Amount is normal)
    data.append({
        "gl_code": 5002,
        "vendor": "Delta Inc",  # New Vendor
        "amount": 1100.00,  # Normal Amount
        "accounting_month": month,
        "cost_center": "IT",
        "transaction_type": "Invoice",
        "date": f"{month}-31"
    })

    return pd.DataFrame(data)


def generate_synthetic_ledger():
    # 3 Months of History + 1 Month of Current
    oct_25 = generate_month("2025-10", with_anomalies=False)
    nov_25 = generate_month("2025-11", with_anomalies=False)
    dec_25 = generate_month("2025-12", with_anomalies=False)
    jan_26 = generate_month("2026-01", with_anomalies=True)

    ledger_df = pd.concat([oct_25, nov_25, dec_25, jan_26], ignore_index=True)
    ledger_df['id'] = range(1, len(ledger_df) + 1)

    return ledger_df