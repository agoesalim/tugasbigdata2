
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

# Sidebar
st.sidebar.header("🔧 Filters")
date_range = st.sidebar.slider("Select Date Range", 0, len(df)-1, (0, len(df)-1))

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Kelembaban", f"{df['Soil Moisture (%)'].iloc[-1]:.1f}%")
col2.metric("Suhu", f"{df['Temperature (°C)'].iloc[-1]:.1f}°C")
col3.metric("Yield", f"{df['Yield (tons/ha)'].iloc[-1]:.2f} t/ha")
col4.metric("Status", df['Status'].iloc[-1])

# Charts
col1, col2 = st.columns(2)
with col1:
    fig_line = px.line(df.iloc[date_range[0]:date_range[1]], 
                      x=df.index[date_range[0]:date_range[1]], 
                      y='Soil Moisture (%)', 
                      title="Trend Kelembaban Tanah")
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = df['Soil Moisture (%)'].iloc[-1],
        title = {'text': "Kelembaban Real-time"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "green"},
            'steps' : [
                {'range': [0, 30], 'color': 'red'},
                {'range': [30, 60], 'color': 'yellow'},
                {'range': [60, 100], 'color': 'green'}
            ]}
    ))
    st.plotly_chart(fig_gauge)

col1.metric("Alert Irigasi", df['Irrigation_Needed'].sum())
col2.metric("Heat Stress", df['Heat_Stress'].sum())

# Heatmap
fig_heatmap = px.imshow(df[['Soil Moisture (%)','Temperature (°C)','Humidity (%)','Yield (tons/ha)'].corr(), 
                         title="Korelasi Antar Sensor", color_continuous_scale='RdBu_r')
st.plotly_chart(fig_heatmap, use_container_width=True)

st.caption("Data Quality Score: " + str(quality['overall_score']) + "% | NIM: [ISI NIM]")
