import pandas as pd
import numpy as np
from typing import List
from src.config_loader import config

class CausalFilter:
    """
    Decouples exogenous market noise from true alpha signals 
    using statistical thresholding and deconfounding.
    """
    def __init__(self):
        # Pull strict statistical thresholds from your config
        self.significance = config.agent_params['causal_discovery']['significance_level']
        self.penalty = config.agent_params['causal_discovery']['deconfounder_penalty']

    def _granger_causality_check(self, series_a: pd.Series, series_b: pd.Series) -> float:
        """
        Mock implementation of a Granger Causality test.
        In production, replace with `statsmodels.tsa.stattools.grangercausalitytests`.
        Returns a p-value indicating if series_a 'causes' series_b.
        """
        # Placeholder for actual statistical math
        correlation = series_a.corr(series_b)
        pseudo_p_value = np.exp(-abs(correlation) * 10) 
        return pseudo_p_value

    def filter_spurious_features(self, target_returns: pd.Series, feature_df: pd.DataFrame) -> List[str]:
        """
        Scans all engineered features and drops those that do not pass 
        strict causal significance tests against the target returns.
        """
        robust_features = []
        
        for feature_name in feature_df.columns:
            p_value = self._granger_causality_check(feature_df[feature_name], target_returns)
            
            # If the p-value is lower than our strict threshold, the signal is causal
            if p_value < self.significance:
                robust_features.append(feature_name)
            else:
                pass # Spurious correlation detected and rejected
                
        return robust_features

    def apply_deconfounding(self, feature_df: pd.DataFrame, confounder_proxy: pd.Series) -> pd.DataFrame:
        """
        Uses residualization to strip macroeconomic noise (e.g., SPY returns) 
        out of localized alpha features.
        """
        clean_df = pd.DataFrame(index=feature_df.index)
        
        for col in feature_df.columns:
            # Fit a simple linear model: Feature = beta * Confounder + Residual
            # We keep the Residual (the pure, decoupled signal)
            covariance = feature_df[col].cov(confounder_proxy)
            variance = confounder_proxy.var()
            beta = covariance / variance
            
            clean_df[col] = feature_df[col] - (beta * confounder_proxy)
            
        return clean_df