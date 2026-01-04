import pandas as pd
import numpy as np


class AnomalyModel:

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["status"] = "OK"
        df["risk_score"] = 0.01
        df["anomaly_reason"] = "None"

        # Sort by month to ensure historical context logic works
        if "accounting_month" in df.columns:
            df = df.sort_values("accounting_month")
            months = sorted(df["accounting_month"].unique())
        else:
            return df

        if len(months) < 2:
            return df

        # Compare LATEST month against HISTORY
        latest_month = months[-1]
        historical = df[df["accounting_month"] != latest_month]
        current = df[df["accounting_month"] == latest_month]

        if historical.empty:
            return df

        # Baseline stats
        global_mean = historical["amount"].mean()
        global_std = historical["amount"].std()

        for idx, row in current.iterrows():
            # Z-Score Check
            z_score = abs(row["amount"] - global_mean) / (global_std + 1e-6)

            reasons = []

            # Rule 1: Spike Check
            if z_score > 3:
                reasons.append(f"Amount is {round(z_score, 1)}x standard deviations from norm")
                df.at[idx, "risk_score"] = min(z_score / 5, 1.0)

            # Rule 2: New Vendor Check
            if row["vendor"] not in historical["vendor"].values:
                reasons.append("First time paying this Vendor")
                df.at[idx, "risk_score"] = max(df.at[idx, "risk_score"], 0.8)

            # Rule 3: New GL Code Check
            if row["gl_code"] not in historical["gl_code"].values:
                reasons.append(f"First use of GL Code {row['gl_code']}")
                df.at[idx, "risk_score"] = max(df.at[idx, "risk_score"], 0.8)

            # Finalize Status
            if reasons:
                df.at[idx, "status"] = "Risk"
                df.at[idx, "anomaly_reason"] = "; ".join(reasons)
                if df.at[idx, "risk_score"] < 0.5:
                    df.at[idx, "risk_score"] = 0.7

        return df