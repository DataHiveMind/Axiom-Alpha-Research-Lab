import numpy as np
from src.validation.metrics import estimated_sharpe_ratio

def test_sharpe_ratio_zero_volatility():
    """Tests that the engine handles a flat-line PnL without crashing."""
    returns = np.zeros(100)
    assert estimated_sharpe_ratio(returns) == 0.0

def test_sharpe_ratio_known_baseline():
    """Verifies Sharpe calculation against a known sequence."""
    # A sequence with a daily mean return of 0.01% and 0.1% volatility
    returns = np.array([0.001, -0.001, 0.001, -0.001])
    # Standard deviation is non-zero, mean is zero
    sr = estimated_sharpe_ratio(returns)
    assert sr == 0.0