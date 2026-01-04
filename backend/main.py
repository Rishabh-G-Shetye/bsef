from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

# CRITICAL: Make sure this imports from 'generator', not 'loader'
from generator import generate_synthetic_ledger
from model import AnomalyModel
from llm_explainer import explain_anomalies
from data_ingestion import ingest_dataframe

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
        print("DEBUG: Generating Synthetic Data (Alpha/Beta/Gamma)...")  # Check your terminal for this print
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
        print(f"Error in upload: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)