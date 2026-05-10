import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_live_performance(df: pd.DataFrame) -> go.Figure:
    """
    Generates a dual-axis Plotly chart showing the Portfolio Equity Curve 
    overlaid with underwater drawdown.
    """
    # Assuming df has 'timestamp', 'portfolio_value', and 'current_drawdown'
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. Equity Curve (Primary Y-Axis)
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['portfolio_value'], 
            name="Portfolio MTM",
            line=dict(color="#00ffcc", width=2)
        ),
        secondary_y=False,
    )

    # 2. Drawdown Area (Secondary Y-Axis)
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['current_drawdown'] * -100, # Convert to negative percentage
            name="Drawdown %",
            fill='tozeroy',
            line=dict(color="#ff3366", width=0),
            opacity=0.3
        ),
        secondary_y=True,
    )

    # Formatting
    fig.update_layout(
        title_text="Live Strategy Execution & Risk",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="Mark to Market ($)", secondary_y=False)
    fig.update_yaxes(title_text="Drawdown (%)", secondary_y=True, showgrid=False)

    return fig