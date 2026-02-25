dashboard_code = '''
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Smart Farming Dashboard")
st.title("🌾 Smart Village Farming Dashboard - Data Lifecycle Project")

@st.cache_data
def load_data():
    return pd.read_csv('dashboard_ready.csv')

df = load_data()

# Helper: auto-detect column names
def find_col(df, keywords):
    cols = df.columns.astype(str)
    cols_lower = [c.lower().strip() for c in cols]
    for kw in keywords:
        for orig, low in zip(cols, cols_lower):
            if kw in low:
                return orig
    return None

col_moisture = find_col(df, ["soil moisture","moisture"])
col_temp     = find_col(df, ["temperature","temp"])
col_humidity = find_col(df, ["humidity"])
col_yield    = find_col(df, ["yield"])

# Sidebar
st.sidebar.header("🔧 Filters")
date_range = st.sidebar.slider("Select Range", 0, len(df)-1, (0, len(df)-1))

# Metrics
col1, col2, col3, col4 = st.columns(4)

if col_moisture:
    col1.metric("Kelembaban", f"{df[col_moisture].iloc[-1]:.1f}%")
if col_temp:
    col2.metric("Suhu", f"{df[col_temp].iloc[-1]:.1f}°C")
if col_yield:
    col3.metric("Yield", f"{df[col_yield].iloc[-1]:.2f} t/ha")

col4.metric("Status", df['Status'].iloc[-1])

# Charts
col1, col2 = st.columns(2)

with col1:
    if col_moisture:
        fig_line = px.line(
            df.iloc[date_range[0]:date_range[1]],
            x=df.index[date_range[0]:date_range[1]],
            y=col_moisture,
            title="Trend Kelembaban Tanah"
        )
        st.plotly_chart(fig_line, use_container_width=True)

with col2:
    if col_moisture:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=df[col_moisture].iloc[-1],
            title={'text': "Kelembaban Real-time"},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 30], 'color': 'red'},
                    {'range': [30, 60], 'color': 'yellow'},
                    {'range': [60, 100], 'color': 'green'}
                ]
            }
        ))
        st.plotly_chart(fig_gauge)

# Alert Metrics
col1.metric("Alert Irigasi", df['Irrigation_Needed'].sum())
col2.metric("Heat Stress", df['Heat_Stress'].sum())

# Heatmap korelasi otomatis
num_df = df.select_dtypes(include="number")

if num_df.shape[1] > 1:
    fig_heatmap = px.imshow(
        num_df.corr(),
        title="Korelasi Antar Sensor",
        color_continuous_scale='RdBu_r'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

st.caption("Smart Farming Data Dashboard")
'''
