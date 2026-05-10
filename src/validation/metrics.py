import numpy as np
import scipy.stats as stats

def estimated_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.0) -> float:
    """Calculates annualized Sharpe Ratio assuming daily returns."""
    excess_returns = returns - risk_free_rate
    if np.std(excess_returns) == 0:
        return 0.0
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

def deflated_sharpe_ratio(observed_sr: float, num_trials: int, variance_of_trials: float, sample_length: int) -> float:
    """
    Calculates the Probability that the Sharpe Ratio is true, 
    discounting for Multiple Testing Bias (Selection Bias).
    """
    # Expected Maximum Sharpe Ratio (Euler-Mascheroni approximation)
    expected_max_sr = np.sqrt(variance_of_trials) * ((1 - 0.5772) * stats.norm.ppf(1 - 1/num_trials) + 0.5772 * stats.norm.ppf(1 - 1/(num_trials * np.e)))
    
    # Calculate the probabilistic deflation
    numerator = (observed_sr - expected_max_sr) * np.sqrt(sample_length - 1)
    denominator = np.sqrt(1 - observed_sr * expected_max_sr + (observed_sr**2 + expected_max_sr**2) / 4)
    
    dsr = stats.norm.cdf(numerator / denominator)
    return dsr