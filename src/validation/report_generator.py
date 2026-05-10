import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime

class ReportGenerator:
    """
    Axiom Alpha: Static Artifact Generator.
    Saves Trade Logs and interactive HTML Tear Sheets to the results/ directory.
    """
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Resolve paths dynamically to the root results/ folder
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.results_dir = self.root_dir / "results"
        
        self.tear_sheets_dir = self.results_dir / "tear_sheets"
        self.figures_dir = self.results_dir / "figures"
        self.logs_dir = self.results_dir / "trade_logs"
        
        # Ensure directories exist
        for d in [self.tear_sheets_dir, self.figures_dir, self.logs_dir]:
            os.makedirs(d, exist_ok=True)

    def export_trade_logs(self, trades_df: pd.DataFrame):
        """Exports the raw execution logs to a CSV for offline auditing."""
        filename = f"{self.strategy_name}_trades_{self.timestamp}.csv"
        filepath = self.logs_dir / filename
        
        trades_df.to_csv(filepath, index=True)
        print(f"📄 Trade log exported: {filepath.relative_to(self.root_dir)}")

    def generate_html_tear_sheet(self, performance_df: pd.DataFrame, metrics_dict: dict):
        """
        Creates an interactive HTML file containing the equity curve, 
        drawdown, and key metrics that can be opened in any browser.
        """
        filename = f"{self.strategy_name}_TearSheet_{self.timestamp}.html"
        filepath = self.tear_sheets_dir / filename

        # Create a dual-axis chart (Equity Curve + Drawdown)
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Equity Curve
        fig.add_trace(
            go.Scatter(x=performance_df.index, y=performance_df['portfolio_value'], 
                       name="Portfolio MTM", line=dict(color="#00ffcc")),
            secondary_y=False,
        )

        # Drawdown Area
        fig.add_trace(
            go.Scatter(x=performance_df.index, y=performance_df['drawdown'] * -100, 
                       name="Drawdown %", fill='tozeroy', 
                       line=dict(color="#ff3366", width=0), opacity=0.3),
            secondary_y=True,
        )

        # Add Title and Metrics to the Chart Layout
        metrics_text = " | ".join([f"{k}: {v:.2f}" for k, v in metrics_dict.items()])
        
        fig.update_layout(
            title_text=f"<b>{self.strategy_name} - Performance Tear Sheet</b><br><sup>{metrics_text}</sup>",
            template="plotly_dark",
            hovermode="x unified"
        )
        fig.update_yaxes(title_text="Portfolio Value ($)", secondary_y=False)
        fig.update_yaxes(title_text="Drawdown (%)", secondary_y=True)

        # Write to standalone HTML file
        fig.write_html(str(filepath))
        print(f"📊 Tear Sheet generated: {filepath.relative_to(self.root_dir)}")