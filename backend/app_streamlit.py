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

if "data" not in st.session_state:
    st.session_state["data"] = None

st.sidebar.header("Audit Controls")

# Mode 1: Synthetic
if st.sidebar.button("🚀 Generate & Scan Synthetic Ledger"):
    with st.spinner("Generating 3 months of GL data & Detecting Anomalies..."):
        try:
            res = requests.get(f"{API_URL}/scan?use_fake=true&use_llm=true")
            if res.status_code == 200:
                data = res.json()
                if "error" in data:
                    st.error(data["error"])
                else:
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
                    data = res.json()
                    if "error" in data:
                        st.error(data["error"])
                    else:
                        st.session_state["data"] = pd.DataFrame(data)
                        st.success("Scan Complete")
                else:
                    st.error("Upload failed")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

if st.session_state["data"] is not None:
    df = st.session_state["data"]

    # Ensure amount is numeric for calculation
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors='coerce')

    risks = df[df["status"] == "Risk"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Transactions", len(df))
    c2.metric("Anomalies Detected", len(risks), delta_color="inverse")

    total_risk_val = risks["amount"].sum() if not risks.empty else 0
    c3.metric("Risk Value Exposure", f"${total_risk_val:,.2f}")

    st.divider()

    if not risks.empty:
        st.subheader("🚨 High Priority Exceptions")

        # Display nicely formatted table
        display_cols = ["accounting_month", "vendor", "gl_code", "amount", "anomaly_reason"]
        # Ensure cols exist
        display_cols = [c for c in display_cols if c in df.columns]

        st.dataframe(
            risks[display_cols].style.format({"amount": "${:,.2f}"}),
            use_container_width=True
        )

        st.subheader("📝 Audit Assistant Findings")
        for _, row in risks.iterrows():
            with st.expander(f"{row.get('vendor', 'Unknown')} - ${row.get('amount', 0):,.2f}"):
                st.write(f"**Month:** {row.get('accounting_month', 'N/A')}")
                st.write(f"**GL Code:** {row.get('gl_code', 'N/A')}")
                st.info(row.get('anomaly_reason', 'No explanation'))

    else:
        st.success("✅ No material exceptions found in this dataset.")

    with st.expander("View Full Ledger Data"):
        st.dataframe(df)