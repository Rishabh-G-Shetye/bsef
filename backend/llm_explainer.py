import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None


def batch_analyze_risks(risk_rows: pd.DataFrame) -> dict:
    if client is None or risk_rows.empty:
        return {}

    try:
        transactions = []
        for idx, row in risk_rows.iterrows():
            transactions.append({
                "id": str(row["id"]),
                "month": row["accounting_month"],
                "vendor": row["vendor"],
                "amount": float(row["amount"]),
                "gl_code": row["gl_code"],
                "technical_flag": row.get("anomaly_reason", "Statistical Outlier")
            })

        prompt = f"""
        You are a Financial Controller. Review these flagged transactions.

        INPUT DATA:
        {json.dumps(transactions)}

        TASK:
        For EACH transaction ID, write a short, professional audit explanation (max 15 words).
        Explain WHY this looks suspicious based on the data provided.

        OUTPUT FORMAT:
        Return ONLY valid JSON.
        {{ "id_value": "explanation string" }}
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )

        return json.loads(response.text)

    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return {}


def explain_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    if "status" not in df.columns:
        return df

    risk_mask = df["status"] == "Risk"
    risk_rows = df[risk_mask]

    if risk_rows.empty:
        return df

    print(f"🤖 Asking Gemini to explain {len(risk_rows)} risks...")
    explanations = batch_analyze_risks(risk_rows)

    for idx, row in df.iterrows():
        if row["status"] == "Risk":
            row_id = str(row["id"])
            if row_id in explanations:
                existing = df.at[idx, "anomaly_reason"]
                ai_text = explanations[row_id]
                df.at[idx, "anomaly_reason"] = f"🤖 {ai_text} | (Tech: {existing})"

    return df