import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces
from src.alpha_factory.feature_pipeline import AlphaFactoryPipeline

class AxiomPortfolioEnv(gym.Env):
    """
    A FinRL-standard portfolio optimization environment.
    Integrates Axiom Alpha Factory features with high-frequency kdb+ data.
    """
    def __init__(self, stock_symbols: list, initial_amount=1000000, transaction_cost_pct=0.001):
        super().__init__()
        self.stock_symbols = stock_symbols
        self.initial_amount = initial_amount
        self.transaction_cost_pct = transaction_cost_pct
        self.factory = AlphaFactoryPipeline()
        
        # State: [Cash, Holdings, Causal Features...]
        # Observation space is dynamic based on the number of features returned by the factory
        self.state_dim = len(stock_symbols) * 10 + 1 # Placeholder estimate
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.state_dim,), dtype=np.float32)
        
        # Action: Portfolio weights (must sum to 1.0)
        self.action_space = spaces.Box(low=0, high=1, shape=(len(stock_symbols),), dtype=np.float32)

    def _get_obs(self):
        # Pull sanitized, causal-filtered features from the Alpha Factory
        observation_df = self.factory.generate_state_observation(self.stock_symbols)
        return observation_df.values.flatten().astype(np.float32)

    def step(self, weights):
        # Normalize weights to ensure they sum to 1.0 (Simple Softmax logic)
        weights = np.exp(weights) / np.sum(np.exp(weights))
        
        # 1. Fetch current price/state
        obs = self._get_obs()
        
        # 2. Calculate Portfolio Return (In a real env, this uses kdb+ historical data)
        # portfolio_return = np.sum(weights * asset_returns)
        reward = 0.0 # Placeholder for risk-adjusted return (Sharpe/Sortino)
        
        return obs, reward, False, False, {}

    def reset(self, seed=None):
        return self._get_obs(), {}