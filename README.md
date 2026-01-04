# 🛡️ AI Financial Auditor (PS04)

> **Month-End Close Exception Finder** > *An automated "Smoke Alarm" for financial data that detects anomalies, fraud, and accounting errors in seconds.*

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange)

---

## 📖 Project Overview
**Problem Statement 04:** Month-End Close Exception Finder.

In accounting, finding errors in General Ledgers (GL) is like finding a needle in a haystack. Manual audits are slow and prone to human error.

**AI Financial Auditor** solves this by automatically scanning transaction datasets to flag:
1.  **Spikes:** Amounts >3 standard deviations from the norm (Z-Score).
2.  **New Entities:** First-time vendors or new GL codes.
3.  **Anomalies:** Irregular patterns compared to historical monthly data.

It uses **Statistical Models** for detection and **Google Gemini AI** to explain the risk in plain English for auditors.

---

## 🚀 Features
* **Dual Mode:** * **Synthetic Demo:** Generates a 3-month ledger (Nov/Dec/Jan) with hidden anomalies (e.g., a $15k spike from "Alpha Supplies").
    * **Real World:** Upload any CSV export of a General Ledger.
* **Statistical Detection:** Uses Z-Score logic and history lookback to find outliers without training data.
* **LLM Explainability:** Integrates Google Gemini to write "Audit Notes" explaining *why* a transaction was flagged.
* **Interactive Dashboard:** Streamlit UI for auditors to review high-priority risks.

---

## 🛠️ Tech Stack
* **Backend:** FastAPI, Python, Uvicorn
* **Frontend:** Streamlit
* **Data Processing:** Pandas, NumPy
* **AI/LLM:** Google GenAI SDK (Gemini 2.0 Flash)

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/Rishabh-G-Shetye/bsef.git](https://github.com/Rishabh-G-Shetye/bsef.git)
cd bsef