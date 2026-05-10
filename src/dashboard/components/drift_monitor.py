import streamlit as st
import numpy as np

def calculate_z_score(current_value: float, expected_mean: float, expected_std: float) -> float:
    """Calculates how many standard deviations the live performance is from expectations."""
    if expected_std == 0:
        return 0.0
    return (current_value - expected_mean) / expected_std

def render_drift_monitor(live_sharpe: float, backtest_mean_sharpe: float, backtest_std_sharpe: float):
    """
    A Streamlit component that evaluates live model decay.
    """
    st.subheader("⚠️ Model Drift & Regime Detection")
    
    # Calculate the statistical deviation
    z_score = calculate_z_score(live_sharpe, backtest_mean_sharpe, backtest_std_sharpe)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Expected Sharpe (CPCV Mean)", f"{backtest_mean_sharpe:.2f}")
        st.metric("Live Rolling Sharpe", f"{live_sharpe:.2f}")
        
    with col2:
        st.metric("Performance Z-Score", f"{z_score:.2f} σ")
        
        # Trigger warnings based on statistical decay
        if z_score < -2.0:
            st.error("🚨 CRITICAL DRIFT DETECTED: Live performance is > 2 standard deviations below backtest expectations. Recommend immediate trading halt and model retraining.")
        elif z_score < -1.0:
            st.warning("⚠️ WARNING: Mild performance decay detected. Monitor execution logic closely.")
        elif z_score > 2.0:
            st.success("📈 OUTPERFORMANCE: Model is performing significantly better than expected. Verify no data leakage in live feed.")
        else:
            st.info("✅ Model behavior is within expected statistical bounds.")