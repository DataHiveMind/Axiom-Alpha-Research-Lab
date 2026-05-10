import pytorch_lightning as pl
import mlflow
from src.dashboard.telemetry_client import telemetry
from research_workspace.notion_integration.metrics_to_notion import push_to_notion

class AxiomLoggingCallback(pl.Callback):
    """
    Automates cross-platform logging: MLflow for research, 
    Notion for sprints, and MongoDB for live telemetry.
    """
    def on_train_epoch_end(self, trainer, pl_module):
        # 1. Pull metrics from the Lightning Module
        metrics = trainer.callback_metrics
        sharpe = metrics.get("train_sharpe", 0.0)
        
        # 2. Log to MLflow (Research Tracking)
        mlflow.log_metric("epoch_sharpe", sharpe.item(), step=trainer.current_epoch)
        
        # 3. Log to MongoDB (Dashboard Telemetry)
        telemetry.log_portfolio_risk(
            timestamp=trainer.current_epoch,
            total_exposure=1.0, 
            current_drawdown=metrics.get("val_drawdown", 0.0),
            sharpe_ratio=sharpe.item(),
            causal_signals={"alpha_1": 0.5} # Dynamic mapping
        )

    def on_fit_end(self, trainer, pl_module):
        # 4. Push final run summary to Notion (Project Management)
        print("Pushing final experiment metrics to Notion...")
        summary = {
            "Model": pl_module.__class__.__name__,
            "Final Sharpe": trainer.callback_metrics.get("val_sharpe", 0.0).item(),
            "MLflow Run ID": mlflow.active_run().info.run_id
        }
        # This script (to be built) bridges the gap to your Notion DB
        push_to_notion(summary)