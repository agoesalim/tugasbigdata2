import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path

st.set_page_config(layout="wide", page_title="Smart Farming Dashboard")
st.title("🌾 Smart Village Farming Dashboard - Data Lifecycle Project")

# ---------------------------
# Helpers
# ---------------------------
def find_col(df, keywords):
    cols = df.columns.astype(str)
    cols_lower = [c.lower().strip() for c in cols]
    for kw in [k.lower().strip() for k in keywords]:
        for orig, low in zip(cols, cols_lower):
            if kw in low:
                return orig
    return None

def find_csv():
    # cek beberapa kemungkinan lokasi file
    candidates = [
        "dashboard_ready.csv",
        "data/processed/dashboard_ready.csv",
        "data/processed/dashboard_ready.csv".replace("\\", "/"),
        "dashboard/dashboard_ready.csv",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p

    # fallback: cari file bernama dashboard_ready.csv di repo
    for p in Path(".").rglob("dashboard_ready.csv"):
        return str(p)

    return None

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

# ---------------------------
# Load Data (no blank!)
# ---------------------------
csv_path = find_csv()
if csv_path is None:
    st.error("❌ File 'dashboard_ready.csv' tidak ditemukan di repo.")
    st.info("Pastikan file CSV ada di repo (mis. folder yang sama dengan streamlit_app.py atau data/processed/).")
    st.stop()

st.sidebar.success(f"📄 Data file: {csv_path}")

try:
    df = load_data(csv_path)
except Exception as e:
    st.error("❌ Gagal membaca CSV.")
    st.exception(e)
    st.stop()

if df is None or df.empty:
    st.warning("⚠️ DataFrame kosong. CSV terbaca tapi tidak ada baris data.")
    st.write("Preview df:", df)
    st.stop()

# Debug toggle
debug = st.sidebar.checkbox("Debug mode", value=True)
if debug:
    st.subheader("🔎 Debug Preview")
    st.write("Shape:", df.shape)
    st.write("Columns:", list(df.columns))
    st.dataframe(df.head(20), use_container_width=True)

# Detect columns
col_moisture = find_col(df, ["soil moisture", "moisture"])
col_temp     = find_col(df, ["temperature", "temp"])
col_humidity = find_col(df, ["humidity"])
col_yield    = find_col(df, ["yield"])
col_status   = "Status" if "Status" in df.columns else find_col(df, ["status"])

if debug:
    st.write({
        "moisture": col_moisture,
        "temp": col_temp,
        "humidity": col_humidity,
        "yield": col_yield,
        "status": col_status
    })

# ---------------------------
# Sidebar range (safe)
# ---------------------------
st.sidebar.header("🔧 Filters")
max_idx = len(df) - 1
start, end = st.sidebar.slider("Select Range Index", 0, max_idx, (0, max_idx))
df_view = df.iloc[start:end+1]

# ---------------------------
# Metrics (safe)
# ---------------------------
m1, m2, m3, m4 = st.columns(4)

def metric_last(col, label, fmt):
    if col is None or col not in df.columns:
        return "N/A"
    try:
        v = df[col].dropna().iloc[-1]
        return fmt(v)
    except Exception:
        return "N/A"

m1.metric("Kelembaban", metric_last(col_moisture, "Kelembaban", lambda v: f"{float(v):.1f}%"))
m2.metric("Suhu",       metric_last(col_temp, "Suhu", lambda v: f"{float(v):.1f}°C"))
m3.metric("Yield",      metric_last(col_yield, "Yield", lambda v: f"{float(v):.2f} t/ha"))
m4.metric("Status",     df[col_status].dropna().iloc[-1] if col_status in df.columns and df[col_status].notna().any() else "N/A")

# Alerts summary (kalau kolom ada)
a1, a2 = st.columns(2)
a1.metric("Alert Irigasi", int(df["Irrigation_Needed"].sum()) if "Irrigation_Needed" in df.columns else 0)
a2.metric("Heat Stress", int(df["Heat_Stress"].sum()) if "Heat_Stress" in df.columns else 0)

# ---------------------------
# Charts
# ---------------------------
c1, c2 = st.columns(2)

with c1:
    if col_moisture and col_moisture in df_view.columns:
        fig_line = px.line(df_view, x=df_view.index, y=col_moisture, title="Trend Kelembaban Tanah")
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Kolom kelembaban tidak ditemukan untuk line chart.")

with c2:
    if col_moisture and col_moisture in df.columns and df[col_moisture].notna().any():
        val = float(df[col_moisture].dropna().iloc[-1])
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            title={'text': "Kelembaban Real-time"},
            gauge={'axis': {'range': [0, 100]}}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)
    else:
        st.info("Gauge tidak tampil (kolom kelembaban tidak ada/semua NaN).")

# Correlation heatmap (numeric-only)
num_df = df.select_dtypes(include="number")
if num_df.shape[1] >= 2:
    fig_heatmap = px.imshow(num_df.corr(), title="Korelasi Antar Sensor")
    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.info("Heatmap tidak tampil (kolom numerik kurang dari 2).")

st.caption("Smart Farming Data Dashboard")
