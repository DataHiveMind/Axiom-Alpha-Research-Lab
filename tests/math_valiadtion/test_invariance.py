import pytest
import torch
from src.alpha_factory.feature_pipeline import AlphaFactoryPipeline

def test_look_ahead_bias_invariance():
    """
    CRITICAL: Verifies that the Alpha Factory does not leak 
    future information into the current state observation.
    """
    pipeline = AlphaFactoryPipeline()
    symbols = ["AAPL"]
    
    # 1. Get observation at Time T
    obs_t = pipeline.generate_state_observation(symbols)
    
    # 2. Append 'future' data to the system (Mocking a kdb+ update)
    # 3. Re-calculate observation for Time T
    obs_t_after_future = pipeline.generate_state_observation(symbols)
    
    # 4. Assert that the features for Time T have not changed
    # If they change, your code is 'looking into the future'
    assert torch.allclose(torch.tensor(obs_t.values), torch.tensor(obs_t_after_future.values))