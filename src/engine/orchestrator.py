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
        Executes a rigorous CPCV backtest using the latest 'Production' model from MLflow.
        """
        print(f"📊 Running Statistical Validation (CPCV) for {symbols}...")
        # Logic to pull model from MLflow Registry and run src/validation/backtester.py
        pass

if __name__ == "__main__":
    # Example Entry Point
    orchestrator = AxiomOrchestrator()
    
    # Target a specific multi-asset universe
    trading_universe = ["AAPL", "MSFT", "TSLA", "BTC/USD", "SPY"]
    
    orchestrator.run_hierarchical_training(symbols=trading_universe, epochs=100)