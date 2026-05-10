import pytest
import numpy as np
import pandas as pd
from src.alpha_factory.causal_inference import CausalFilter

def test_deconfounding_math():
    """
    Proves that the causal filter correctly strips out market beta 
    from a correlated feature, leaving only pure, uncorrelated signal.
    """
    np.random.seed(42)
    
    # 1. Simulate a Macroeconomic Confounder (e.g., SPY returns)
    market_proxy = pd.Series(np.random.normal(0, 1, 1000), name="SPY")
    
    # 2. Simulate a feature that is highly polluted by the market + a little pure alpha
    pure_alpha = pd.Series(np.random.normal(0, 0.1, 1000))
    polluted_feature = (1.5 * market_proxy) + pure_alpha
    
    df = pd.DataFrame({'test_feature': polluted_feature})
    
    # 3. Apply the Axiom Deconfounding Filter
    causal_filter = CausalFilter()
    clean_df = causal_filter.apply_deconfounding(df, market_proxy)
    
    # 4. Mathematical Assertion:
    # If deconfounding worked, the covariance between the cleaned feature 
    # and the market proxy MUST be practically zero.
    covar = clean_df['test_feature'].cov(market_proxy)
    
    assert np.isclose(covar, 0.0, atol=1e-10), f"CRITICAL: Deconfounding failed. Residual covariance: {covar}"

def test_spurious_feature_rejection():
    """
    Ensures the causal filter drops features that fail the strict p-value threshold.
    """
    causal_filter = CausalFilter()
    
    # Simulate a target return series
    target_returns = pd.Series(np.random.normal(0, 1, 100))
    
    # Simulate pure noise that has zero causal relationship with the target
    spurious_noise = pd.Series(np.random.normal(0, 1, 100))
    feature_df = pd.DataFrame({'fake_signal': spurious_noise})
    
    # The filter should return an empty list (all features rejected)
    valid_features = causal_filter.filter_spurious_features(target_returns, feature_df)
    
    assert len(valid_features) == 0, "CRITICAL: Spurious feature bypassed the causal filter!"