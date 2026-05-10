from src.dashboard.telemetry_client import telemetry
from src.config_loader import config
import pytorch_lightning as pl

class PortfolioAllocationAgent(pl.LightningModule):
    def __init__(self):
        super().__init__()
        # Load hyperparameters directly from the agent_params.yaml
        self.params = config.agent_params['drl_engine']['portfolio_agent']
        
        self.learning_rate = self.params['learning_rate']
        self.batch_size = self.params['batch_size']
        
        # Save hyperparameters to MLflow automatically
        self.save_hyperparameters(self.params)

        print(f"Agent initialized with LR: {self.learning_rate} and Batch Size: {self.batch_size}")

# ... inside your agent's step() function after making a trade ...

# The agent's internal brain state at the moment of the trade
agent_state_dump = {
    "q_value_confidence": 0.87,
    "causal_noise_penalty": -0.04,
    "predicted_slippage_bps": 2.1,
    "market_regime": "high_volatility"
}

# Log the trade to MongoDB for later analysis
telemetry.log_execution(
    agent_id="Lower_Execution_Agent_v2.1",
    ticker="AAPL",
    action="SELL",
    quantity=500,
    price=185.32,
    metadata=agent_state_dump
)