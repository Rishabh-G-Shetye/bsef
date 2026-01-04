from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import pandas as pd
import io
import base64
import json

from generator import generate_synthetic_ledger
from model import AnomalyModel
from llm_explainer import explain_anomalies, generate_batch_summary
from data_ingestion import ingest_dataframe
from pdf_generator import create_audit_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = AnomalyModel()


@app.get("/scan")
def get_scan_results(use_fake: bool = True, use_llm: bool = True):
    if use_fake:
        print("DEBUG: Generating Synthetic Data...")
        df = generate_synthetic_ledger()
    else:
        return {"error": "Use POST for real data"}

    try:
        df = ingest_dataframe(df)
        df = model.detect_anomalies(df)

        if use_llm:
            df = explain_anomalies(df)

        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Server Error: {e}")
        return {"error": str(e)}


@app.post("/scan")
async def scan_uploaded_csv(file: UploadFile = File(...), use_llm: bool = True):
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
        df = ingest_dataframe(df)
        df = model.detect_anomalies(df)
        if use_llm:
            df = explain_anomalies(df)
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}


# ... imports stay same ...

@app.post("/generate_report")
async def generate_report(request: Request):
    """
    Receives current full dataframe, generates summary + PDF.
    """
    try:
        body = await request.json()
        data = body.get("data", [])

        if not data:
            return {"error": "No data provided"}

        df = pd.DataFrame(data)

        # --- NEW: Calculate Metrics ---
        total_tx = len(df)
        risks_df = df[df["status"] == "Risk"]
        total_risk_val = risks_df["amount"].sum() if not risks_df.empty else 0
        # -----------------------------

        # 1. Generate LLM Summary (Only send risks to LLM to save tokens)
        summary = generate_batch_summary(risks_df)

        # 2. Generate PDF (Pass the new metrics!)
        pdf_buffer = create_audit_pdf(risks_df, summary, total_tx, total_risk_val)

        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")

        return {
            "summary": summary,
            "pdf_base64": pdf_base64
        }
    except Exception as e:
        print(f"Report Error: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)