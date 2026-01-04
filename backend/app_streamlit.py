import streamlit as st
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Month-End Auditor | PS04",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ AI Financial Auditor")
st.markdown("### Month-End Close Exception Finder")

# --- SIDEBAR ---
if st.sidebar.button("🧹 Clear/Reset App"):
    st.session_state["data"] = None
    st.rerun()

if "data" not in st.session_state:
    st.session_state["data"] = None

st.sidebar.header("Audit Controls")

# Mode 1: Synthetic
if st.sidebar.button("🚀 Generate & Scan Synthetic Ledger"):
    with st.spinner("Analyzing Oct-Dec History vs Jan Current..."):
        try:
            res = requests.get(f"{API_URL}/scan?use_fake=true&use_llm=true")
            if res.status_code == 200:
                data = res.json()
                st.session_state["data"] = pd.DataFrame(data)
                st.success("Scan Complete")
            else:
                st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"Connection Failed: {e}")

# Mode 2: Upload
uploaded = st.sidebar.file_uploader("Upload GL Export (CSV)")
if uploaded:
    if st.sidebar.button("Scan Uploaded File"):
        with st.spinner("Analyzing uploaded file..."):
            files = {"file": uploaded}
            try:
                res = requests.post(f"{API_URL}/scan?use_llm=true", files=files)
                if res.status_code == 200:
                    st.session_state["data"] = pd.DataFrame(res.json())
                    st.success("Scan Complete")
                else:
                    st.error("Upload failed")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

# --- MAIN DASHBOARD ---
if st.session_state["data"] is not None:
    df = st.session_state["data"]

    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors='coerce')

    # Filter only Risks (High and Medium)
    risks = df[df["status"] == "Risk"].copy()

    # Sort risks by Score Descending (Highest Priority first)
    risks = risks.sort_values("risk_score", ascending=False)

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Transactions", len(df))
    c2.metric("Anomalies Detected", len(risks), delta_color="inverse")
    total_risk_val = risks["amount"].sum() if not risks.empty else 0
    c3.metric("Risk Value Exposure", f"${total_risk_val:,.2f}")

    st.divider()

    if not risks.empty:
        st.subheader("🚨 Priority Exception Queue")

        # Format the table for display
        display_cols = ["severity", "risk_score", "vendor", "gl_code", "amount", "anomaly_reason"]

        # Color code severity in the dataframe display is tricky,
        # so we rely on the string column "severity" we created in model.py

        st.dataframe(
            risks[display_cols].style.format({
                "amount": "${:,.2f}",
                "risk_score": "{:.1%}"
            }),
            use_container_width=True
        )

        st.subheader("📝 Audit Assistant Findings")
        for _, row in risks.iterrows():
            # Color emoji based on severity
            icon = "🔴" if row['severity'] == "High" else "🟡"

            with st.expander(
                    f"{icon} {row['severity']} Risk: {row.get('vendor', 'Unknown')} - ${row.get('amount', 0):,.2f}"):
                st.markdown(f"**Reason:** {row.get('anomaly_reason', 'N/A')}")
                st.markdown(f"**Risk Score:** {row.get('risk_score', 0) * 100:.1f}%")
                st.markdown(f"**GL Code:** {row.get('gl_code', 'N/A')}")
                st.markdown(f"**Month:** {row.get('accounting_month', 'N/A')}")

    else:
        st.success("✅ No material exceptions found in this dataset.")

    with st.expander("View Full Ledger Data (Sorted by Risk)"):
        # Sort full dataset by risk score so users see the 'almost' risks at the top
        sorted_df = df.sort_values("risk_score", ascending=False)
        st.dataframe(sorted_df, use_container_width=True)