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