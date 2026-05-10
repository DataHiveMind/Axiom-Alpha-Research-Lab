import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard.telemetry_client import telemetry
from src.dashboard.components.pnl_charts import plot_live_performance
from src.dashboard.components.drift_monitor import render_drift_monitor

# Configure the Streamlit Page
st.set_page_config(page_title="Axiom Alpha Control Tower", layout="wide", page_icon="⚡")

st.title("⚡ Axiom Alpha: Live Telemetry Dashboard")

# 1. Fetch Real-Time Data from MongoDB
@st.cache_data(ttl=5) # Refresh data every 5 seconds
def load_risk_data():
    raw_data = telemetry.fetch_recent_risk_metrics(limit=500)
    if not raw_data:
        return pd.DataFrame()
    return pd.DataFrame(raw_data)

df_risk = load_risk_data()

if df_risk.empty:
    st.warning("No telemetry data found. Is the Alpha Factory running?")
    st.stop()

# 2. Top-Level KPIs
col1, col2, col3, col4 = st.columns(4)
current_sharpe = df_risk['rolling_sharpe'].iloc[0]
current_dd = df_risk['current_drawdown'].iloc[0]

col1.metric("Live Sharpe Ratio", f"{current_sharpe:.2f}", delta=f"{current_sharpe - df_risk['rolling_sharpe'].iloc[10]:.2f}")
col2.metric("Max Drawdown", f"{current_dd * 100:.2f}%")
col3.metric("Total Market Exposure", f"{df_risk['total_exposure'].iloc[0] * 100:.1f}%")
col4.metric("Active MLflow Model", "Lower_Agent_v2.1")

st.markdown("---")

# 3. Live PnL & Risk Visualization
st.subheader("Real-Time Risk Decomposition")

fig_sharpe = px.line(df_risk, x='timestamp', y='rolling_sharpe', title="Rolling Sharpe Ratio (Intraday)")
fig_sharpe.add_hline(y=1.5, line_dash="dash", line_color="green", annotation_text="Target")
fig_sharpe.update_layout(template="plotly_dark")

st.plotly_chart(fig_sharpe, use_container_width=True)
st.plotly_chart(plot_live_performance(df_risk), use_container_width=True)

# 4. Agent Brain Inspection (Debugging the DRL Agent)
st.subheader("Agent Execution State")
st.markdown("Inspect the raw Q-Values and causal confidence of the latest trades.")

# Fetch raw execution logs
recent_trades = telemetry.execution_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(10)
trades_df = pd.json_normalize(list(recent_trades))

st.dataframe(trades_df, use_container_width=True)

# Render the Drift Monitor using hardcoded expected metrics from MLflow (or pull dynamically)
render_drift_monitor(
    live_sharpe=current_sharpe, 
    backtest_mean_sharpe=1.85, # Expected from CPCV
    backtest_std_sharpe=0.30
)