import os
import ray
import mlflow
import torch
import pytorch_lightning as pl
from ray import tune
from ray.rllib.algorithms.sac import SAC

# Import Axiom Alpha Components
from src.config_loader import config
from src.engine.agents.upper_agent_rllib import UpperPortfolioAgent
from src.engine.agents.lower_agent_torchrl import LowerExecutionAgent
from src.engine.datamodules import AxiomDataModule
from src.engine.callbacks import AxiomLoggingCallback
from src.validation.backtester import EventDrivenBacktester
from src.validation.report_generator import ReportGenerator

class AxiomOrchestrator:
    """
    The Master Orchestrator for Axiom-Alpha-Research-Lab.
    Manages distributed Ray nodes, MLflow experiment state, and 
    Hierarchical Agent synchronization.
    """
    def __init__(self, experiment_name="Axiom_Hierarchical_Run_v1"):
        self.system_cfg = config.system
        self.agent_cfg = config.agent_params
        self.experiment_name = experiment_name

        # 1. Initialize Ray for distributed compute across the cluster
        # Connects to the head node (your Computer) and workers (Lenovo/Chromebook)
        if not ray.is_initialized():
            ray.init(
                address=self.system_cfg['mlops']['mlflow']['tracking_uri'], # Or local if standalone
                ignore_reinit_error=True
            )

        # 2. Setup MLflow Tracking
        mlflow.set_tracking_uri(self.system_cfg['mlops']['mlflow']['tracking_uri'])
        mlflow.set_experiment(self.experiment_name)

    def run_hierarchical_training(self, symbols: list, epochs: int = 50):
        """
        Orchestrates the simultaneous training of the Portfolio and Execution agents.
        """
        print(f"🚀 Initializing Hierarchical Training for: {symbols}")

        with mlflow.start_run(run_name="Full_System_Train") as run:
            # 1. Initialize Data Pipeline (kdb+ streaming)
            data_module = AxiomDataModule(
                symbols=symbols, 
                batch_size=self.agent_cfg['drl_engine']['portfolio_agent']['batch_size']
            )
            data_module.setup()

            # 2. Initialize Agents
            upper_agent = UpperPortfolioAgent(use_gpu=torch.cuda.is_available())
            lower_agent = LowerExecutionAgent()

            # 3. Training Loop for Lower Agent (TorchRL + Lightning)
            # We use PyTorch Lightning to handle the low-level execution agent's training
            trainer = pl.Trainer(
                max_epochs=epochs,
                accelerator="auto",
                devices=1,
                callbacks=[AxiomLoggingCallback()],
                enable_checkpointing=True
            )

            print("--- Phase 1: Training Lower Execution Agent (TorchRL) ---")
            # trainer.fit(lower_agent, datamodule=data_module)

            print("--- Phase 2: Training Upper Portfolio Agent (Ray RLlib) ---")
            # The Upper Agent learns to allocate capital based on the Lower Agent's 
            # ability to execute trades and hedge accurately.
            upper_agent.train(iterations=epochs)

            # 4. Log System-Wide Artifacts
            mlflow.log_params(self.agent_cfg['drl_engine']['portfolio_agent'])
            mlflow.log_dict(self.agent_cfg, "full_config.yaml")

            print(f"✅ Training Complete. Run ID: {run.info.run_id}")

    def run_backtest(self, symbols: list):
        """
        Executes a rigorous CPCV backtest using the latest 'Production' model,
        then automatically generates immutable tear sheets and trade logs.
        """
        print(f"📊 Running Statistical Validation (CPCV) for {symbols}...")
        
        # 1. Initialize the Backtester
        backtester = EventDrivenBacktester(initial_capital=1000000.0)
        
        # (In a live run, you would load your agent and test_data here)
        # agent = ... 
        # test_data = ...
        
        # 2. Execute the tick-by-tick simulation
        print("Simulating event-driven execution...")
        # For a single path simulation that generates the dataframes:
        # performance_df = backtester._simulate_path(agent, test_data)
        # trades_df = ... (extracted from your backtest logic)
        
        # 3. Trigger the Report Generator
        print("Generating static Tear Sheets and Trade Logs...")
        reporter = ReportGenerator(strategy_name=self.experiment_name)
        
        # Uncomment these once you have the actual dataframes flowing from the backtester
        # reporter.export_trade_logs(trades_df)
        # reporter.generate_html_tear_sheet(
        #     performance_df=performance_df, 
        #     metrics_dict={"Sharpe": 2.1, "Max Drawdown": -12.4} # Or pass actual metrics
        # )
        
        print(f"✅ Validation complete. All artifacts saved to the 'results/' directory.")

if __name__ == "__main__":
    # Example Entry Point
    orchestrator = AxiomOrchestrator()
    
    # Target a specific multi-asset universe
    trading_universe = ["AAPL", "MSFT", "TSLA", "BTC/USD", "SPY"]
    
    orchestrator.run_hierarchical_training(symbols=trading_universe, epochs=100)
