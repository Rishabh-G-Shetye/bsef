import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    print(f"✅ API Key found: {API_KEY[:5]}******")
else:
    print("❌ API Key NOT found. Check .env file location.")

client = genai.Client(api_key=API_KEY) if API_KEY else None

FALLBACK_CHAIN = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3-flash",
    "gemma-3-12b",
    "gemma-3-1b"
]


def _query_llm_with_fallback(prompt, response_mime_type="application/json"):
    """Internal helper to run the fallback chain."""
    if not client:
        return None

    for model_name in FALLBACK_CHAIN:
        try:
            print(f"🤖 Attempting {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type=response_mime_type,
                    temperature=0.2
                )
            )
            return response.text
        except Exception as e:
            print(f"⚠️ {model_name} failed: {e}")
            continue
    return None


def generate_batch_summary(risk_rows: pd.DataFrame) -> str:
    """
    Generates a text summary and action plan for the entire dataset.
    """
    if risk_rows.empty:
        return "No risks to summarize."

    # Summarize data for prompt (limit to top 10 to save tokens)
    top_risks = risk_rows.head(10).to_dict(orient="records")

    prompt = f"""
    You are a Lead Financial Auditor. 
    Review these high-risk transactions: {top_risks}

    Write an Executive Audit Summary (plain text, no markdown **bolding**).
    Include:
    1. A rundown of the key anomalies found.
    2. Specific recommended actions (e.g., "Contact Vendor X immediately").
    3. A professional closing statement.

    Keep it concise (max 100 words).
    """

    response = _query_llm_with_fallback(prompt, response_mime_type="text/plain")
    return response if response else "Audit summary generation failed."


def batch_analyze_risks(risk_rows: pd.DataFrame) -> dict:
    """Row-by-row analysis returning JSON."""
    if risk_rows.empty:
        return {}

    transactions = []
    for idx, row in risk_rows.iterrows():
        transactions.append({
            "id": str(idx),
            "vendor": row.get("vendor"),
            "amount": row.get("amount"),
            "flag": row.get("anomaly_reason")
        })

    prompt = f"""
    Analyze these transactions: {json.dumps(transactions)}
    For EACH "id", return a JSON object: {{ "id": "Short explanation" }}
    """

    response = _query_llm_with_fallback(prompt, response_mime_type="application/json")
    try:
        return json.loads(response) if response else {}
    except:
        return {}


def explain_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Enriches DataFrame with row-by-row explanations."""
    df = df.copy()
    if "status" not in df.columns: return df

    risk_rows = df[df["status"] == "Risk"]
    if risk_rows.empty: return df

    print(f"🔍 Analyzing {len(risk_rows)} risks...")
    explanations = batch_analyze_risks(risk_rows)

    for idx, row in df.iterrows():
        idx_str = str(idx)
        if idx_str in explanations:
            df.at[idx, "anomaly_reason"] = f"🤖 {explanations[idx_str]}"

    return df