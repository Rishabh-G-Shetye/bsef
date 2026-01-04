import streamlit as st
import pandas as pd
import requests
import base64

API_URL = "http://127.0.0.1:8001"

st.set_page_config(page_title="Month-End Auditor | PS04", page_icon="🛡️", layout="wide")
st.markdown("""<style>.stApp { background-color: #0e1117; color: #FFFFFF; }</style>""", unsafe_allow_html=True)

# --- UPDATED TITLE WITH ML BADGE ---
st.title("🛡️ AI Financial Auditor")
st.markdown("### Month-End Close Exception Finder")
st.caption("Powered by: **Hybrid Ensemble (Z-Score + Isolation Forest) & Google Gemini**")
# -----------------------------------

# Session State for Report
if "report_summary" not in st.session_state:
    st.session_state["report_summary"] = ""
if "report_pdf" not in st.session_state:
    st.session_state["report_pdf"] = None

# Clear button
if st.sidebar.button("🧹 Clear/Reset App"):
    st.session_state["data"] = None
    st.session_state["report_summary"] = ""
    st.session_state["report_pdf"] = None
    st.rerun()

if "data" not in st.session_state:
    st.session_state["data"] = None

st.sidebar.header("Audit Controls")

# Mode 1: Synthetic
if st.sidebar.button("🚀 Generate & Scan Synthetic Ledger"):
    with st.spinner("Running Ensemble Model (Stats + ML)..."):
        try:
            res = requests.get(f"{API_URL}/scan?use_fake=true&use_llm=true")
            if res.status_code == 200:
                st.session_state["data"] = pd.DataFrame(res.json())
                st.session_state["report_summary"] = ""
                st.session_state["report_pdf"] = None
                st.success("Analysis Complete")
            else:
                st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"Connection Failed: {e}")

# Mode 2: Upload
uploaded = st.sidebar.file_uploader("Upload GL Export (CSV)")
if uploaded:
    if st.sidebar.button("Scan Uploaded File"):
        with st.spinner("Running Ensemble Model..."):
            files = {"file": uploaded}
            try:
                res = requests.post(f"{API_URL}/scan?use_llm=true", files=files)
                if res.status_code == 200:
                    st.session_state["data"] = pd.DataFrame(res.json())
                    st.session_state["report_summary"] = ""
                    st.session_state["report_pdf"] = None
                    st.success("Analysis Complete")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

if st.session_state["data"] is not None:
    df = st.session_state["data"]
    if "amount" in df.columns: df["amount"] = pd.to_numeric(df["amount"], errors='coerce')

    risks = df[df["status"] == "Risk"].sort_values("risk_score", ascending=False)

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Transactions", len(df))
    c2.metric("Anomalies Detected", len(risks), delta_color="inverse")
    total_risk_val = risks["amount"].sum() if not risks.empty else 0
    c3.metric("Risk Value Exposure", f"${total_risk_val:,.2f}")

    st.divider()

    # Report Gen
    st.subheader("📄 Audit Reporting")
    col_gen, col_preview = st.columns([1, 3])

    with col_gen:
        if st.button("📝 Draft Audit Report"):
            with st.spinner("Consulting AI & Generating PDF..."):
                try:
                    payload = {"data": df.to_dict(orient="records")}
                    res = requests.post(f"{API_URL}/generate_report", json=payload)

                    if res.status_code == 200:
                        result = res.json()
                        st.session_state["report_summary"] = result["summary"]
                        st.session_state["report_pdf"] = result["pdf_base64"]
                    else:
                        st.error("Report generation failed.")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state["report_summary"]:
        with col_preview:
            st.info(f"**AI Executive Summary:**\n\n{st.session_state['report_summary']}")

        if st.session_state["report_pdf"]:
            pdf_data = base64.b64decode(st.session_state["report_pdf"])
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_data,
                file_name="Audit_Exception_Report.pdf",
                mime="application/pdf"
            )

    st.divider()

    # Tables
    if not risks.empty:
        st.subheader("🚨 Priority Exception Queue")
        display_cols = ["severity", "risk_score", "vendor", "gl_code", "amount", "anomaly_reason"]
        st.dataframe(risks[display_cols].style.format({"amount": "${:,.2f}", "risk_score": "{:.1%}"}),
                     use_container_width=True)

        st.subheader("📝 Audit Assistant Findings")
        for _, row in risks.iterrows():
            icon = "🔴" if row['severity'] == "High" else "🟡"
            with st.expander(f"{icon} {row['severity']} Risk: {row.get('vendor')} - ${row.get('amount', 0):,.2f}"):
                st.write(f"**Reason:** {row.get('anomaly_reason')}")

    with st.expander("View Full Ledger Data"):
        st.dataframe(df.sort_values("risk_score", ascending=False), use_container_width=True)