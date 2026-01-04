# 🛡️ AI Financial Auditor (PS04)

> **Month-End Close Exception Finder**
>
> *An intelligent "Smoke Alarm" for financial ledgers that detects anomalies, fraud, and accounting errors using a Hybrid Ensemble Model (Statistics + ML).*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![AI](https://img.shields.io/badge/AI-Hybrid%20Ensemble%20(Z--Score%20%2B%20Isolation%20Forest)-orange)
![GenAI](https://img.shields.io/badge/GenAI-Google%20Gemini%20%2F%20Gemma-purple)

---

## 📖 Project Overview
**Problem Statement 04:** Month-End Close Exception Finder.

In accounting, finding errors in General Ledgers (GL) is manual, slow, and prone to human error. A single wrong entry can delay the entire month-end close process.

**AI Financial Auditor** solves this by automatically scanning transaction datasets to flag:
1.  **Statistical Outliers:** Transactions deviating significantly from historical norms.
2.  **Hidden Patterns:** Uses Unsupervised Machine Learning to find subtle anomalies.
3.  **Contextual Risks:** Uses LLMs to explain *why* a transaction looks suspicious in plain English.

---

## 🚀 Key Features

### 🧠 Hybrid Ensemble Detection Engine
This system does not rely on a single method. It uses a **multi-layer approach** for maximum accuracy:
1.  **Layer 1: Z-Score Statistics:** Detects material deviations ($>3\sigma$) and volatility.
2.  **Layer 2: Isolation Forest (ML):** An unsupervised algorithm that isolates anomalies in high-dimensional space (detecting subtle fraud that rules miss).
3.  **Layer 3: Deterministic Rules:** Instantly flags "New Vendors" and "First-time GL Codes".

### 🤖 Generative AI Copilot
* **LLM Explainer:** Uses **Google Gemini (Flash 2.5)** and **Gemma** to write human-readable "Audit Notes" for every risk (e.g., *"🤖 Amount is normal, but vendor is new"*).
* **Robust Fallback Chain:** Automatically retries across 5 different models if one is rate-limited or unavailable.
* **Smart Summaries:** Generates an Executive Summary of the entire audit for the Controller.

### 📊 Professional Reporting
* **One-Click Audit Report:** Generates a downloadable **PDF Report** with:
    * Executive Summary & Action Plan.
    * Key Metrics (Total Risk Value, Anomaly Count).
    * Detailed Exception Log.
* **Preview Mode:** Review the AI's findings before downloading.

### 🔌 Dual Input Modes
* **Synthetic Demo Mode:** Generates a realistic 4-month ledger (Oct-Jan) with hidden fraud scenarios (e.g., Kickbacks, Duplicate Payments).
* **Real Data Mode:** Upload any standard CSV export from SAP/Oracle/QuickBooks.

---

## 🛠️ Tech Stack
* **Backend:** FastAPI, Uvicorn
* **Frontend:** Streamlit
* **ML/Stats:** Scikit-Learn (Isolation Forest), NumPy, Pandas
* **GenAI:** Google AI SDK (Gemini & Gemma models)
* **Reporting:** ReportLab (PDF Generation)

---

## ⚙️ Installation & Setup

```bash

1. Clone the Repository
git clone [https://github.com/Rishabh-G-Shetye/bsef.git](https://github.com/Rishabh-G-Shetye/bsef.git)
cd bsef

2. Install Dependencies
pip install -r requirements.txt

3. Setup Environment Variables

Create a .env file in the project root:

GEMINI_API_KEY=your_actual_api_key_here

🏃‍♂️ How to Run
Step 1: Start the Backend
uvicorn main:app --reload --port 8001


Backend URL:
http://127.0.0.1:8001

Step 2: Start the Frontend
streamlit run app_streamlit.py


Frontend URL:
http://localhost:8501
📂 Project Structure
bsef/
├── app_streamlit.py    # Frontend dashboard
├── main.py             # Backend API
├── model.py            # Hybrid detection engine
├── generator.py        # Synthetic data generator
├── llm_explainer.py    # Gemini / Gemma integration
├── pdf_generator.py    # PDF reporting
├── data_ingestion.py   # Data cleaning
└── requirements.txt    # Dependencies


🧪 Usage Guide (For Judges)
1. Demo Mode (Recommended)

Click 🚀 Generate & Scan Synthetic Ledger

System generates:

History: Oct–Dec

Current month: Jan

Ensemble detection identifies:

High Risk: Alpha Supplies ($18,500) – Z-Score + Isolation Forest

Medium Risk: Omega Solutions – New Vendor Rule

Click 📝 Draft Audit Report to generate the PDF.