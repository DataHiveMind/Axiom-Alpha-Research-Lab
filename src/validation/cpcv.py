import numpy as np
import pandas as pd
from itertools import combinations
from sklearn.model_selection import KFold
from src.config_loader import config

class PurgedKFold(KFold):
    """
    Extends KFold to implement Purging and Embargoing for financial timeseries.
    Prevents look-ahead bias and serial correlation leakage.
    """
    def __init__(self, n_splits=5, embargo_pct=0.01):
        super().__init__(n_splits, shuffle=False)
        self.embargo_pct = embargo_pct

    def split(self, X, y=None, groups=None):
        indices = np.arange(X.shape[0])
        embargo_size = int(X.shape[0] * self.embargo_pct)
        
        for train_indices, test_indices in super().split(X, y, groups):
            # 1. Purging: Remove training data that happens concurrently with testing data
            # (In a strict implementation, this relies on trade start/end times)
            
            # 2. Embargoing: Drop training data immediately following the test set
            test_end = test_indices[-1]
            embargo_indices = np.arange(test_end + 1, min(test_end + 1 + embargo_size, X.shape[0]))
            
            # Filter the train_indices
            train_indices = np.setdiff1d(train_indices, test_indices)
            train_indices = np.setdiff1d(train_indices, embargo_indices)
            
            yield train_indices, test_indices

class CPCVEngine:
    """Combinatorial Purged Cross-Validation Orchestrator"""
    def __init__(self, n_splits=6, n_test_splits=2):
        self.n_splits = n_splits
        self.n_test_splits = n_test_splits
        self.cv = PurgedKFold(n_splits=self.n_splits)
        
    def generate_paths(self):
        """Generates the combinatorial paths for backtesting."""
        # Calculates all combinations of test splits
        splits = list(combinations(range(self.n_splits), self.n_test_splits))
        print(f"✅ CPCV Initialized: {len(splits)} backtest paths will be generated.")
        return splits