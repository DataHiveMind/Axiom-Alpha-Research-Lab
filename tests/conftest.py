import pytest
import pandas as pd
import numpy as np
import torch

@pytest.fixture
def sample_tick_data():
    """Generates a synthetic price series for testing."""
    dates = pd.date_range(start="2026-01-01", periods=100, freq="1min")
    data = {
        'price': np.linspace(100, 110, 100) + np.random.normal(0, 0.1, 100),
        'size': np.random.randint(10, 100, 100)
    }
    return pd.DataFrame(data, index=dates)

@pytest.fixture
def mock_agent_obs():
    """Returns a dummy tensor matching the DRL agent's expected input."""
    return torch.randn(1, 4) # [Batch, State_Dim]