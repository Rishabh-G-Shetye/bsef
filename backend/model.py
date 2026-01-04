import pandas as pd
import numpy as np


class AnomalyModel:

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Initialize defaults
        df["status"] = "OK"
        df["risk_score"] = 0.0
        df["anomaly_reason"] = "None"
        df["severity"] = "Low"

        # Sort by month for history lookup
        if "accounting_month" in df.columns:
            df = df.sort_values("accounting_month")
            months = sorted(df["accounting_month"].unique())
        else:
            return df

        if len(months) < 2:
            return df

        # Define Baseline: Use everything except the very last month for training
        latest_month = months[-1]
        historical = df[df["accounting_month"] != latest_month]

        if historical.empty:
            return df

        # Calculate Baseline Stats (Global Context)
        global_mean = historical["amount"].mean()
        global_std = historical["amount"].std()

        # Get unique sets for O(1) lookup
        historical_vendors = set(historical["vendor"].unique())
        historical_gls = set(historical["gl_code"].unique())

        # FIX 2: Iterate through ALL rows (df.iterrows), not just current.
        # This ensures historical data also gets a score (likely low)
        # so the table looks consistent.
        for idx, row in df.iterrows():

            # 1. CALCULATE Z-SCORE
            z_score = abs(row["amount"] - global_mean) / (global_std + 1e-6)

            # 2. CALCULATE BASE RISK SCORE
            calculated_risk = min(z_score / 4, 1.0)

            reasons = []

            # --- RULE 1: STATISTICAL DEVIATION ---
            if z_score > 3:
                reasons.append(f"Extreme Spike ({round(z_score, 1)}x std dev)")
                calculated_risk = max(calculated_risk, 0.85)
            elif z_score > 2:
                reasons.append(f"Unusual Variance ({round(z_score, 1)}x std dev)")
                calculated_risk = max(calculated_risk, 0.5)
            # FIX 1: Add catch for Medium risks (Gap between 1.6 and 2.0)
            elif z_score > 1.5:
                reasons.append(f"Moderate Deviation ({round(z_score, 1)}x std dev)")
                calculated_risk = max(calculated_risk, 0.45)

            # --- RULE 2: NEW ENTITY DETECTION ---
            # Only apply "New Entity" logic to the LATEST month.
            # (We don't want to flag Oct 2025 as 'New' just because it was the start of data)
            if row["accounting_month"] == latest_month:
                if row["vendor"] not in historical_vendors:
                    reasons.append(f"New Vendor: {row['vendor']}")
                    calculated_risk = max(calculated_risk, 0.6)

                if row["gl_code"] not in historical_gls:
                    reasons.append(f"New GL Code: {row['gl_code']}")
                    calculated_risk = max(calculated_risk, 0.75)

                # Check Unusual Transaction Type
                vendor_history = historical[historical['vendor'] == row['vendor']]
                if not vendor_history.empty:
                    if row['transaction_type'] not in vendor_history['transaction_type'].values:
                        reasons.append(f"Unusual Type '{row['transaction_type']}' for this vendor")
                        calculated_risk = max(calculated_risk, 0.55)

            # 3. ASSIGN FINAL VALUES
            df.at[idx, "risk_score"] = round(calculated_risk, 3)

            if calculated_risk > 0.7:
                df.at[idx, "severity"] = "High"
                df.at[idx, "status"] = "Risk"
            elif calculated_risk > 0.4:
                df.at[idx, "severity"] = "Medium"
                df.at[idx, "status"] = "Risk"
            else:
                df.at[idx, "severity"] = "Low"
                df.at[idx, "status"] = "OK"

            if reasons:
                df.at[idx, "anomaly_reason"] = "; ".join(reasons)

        return df