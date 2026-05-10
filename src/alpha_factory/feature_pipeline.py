import pandas as pd
from src.alpha_factory.kdb_interface import KDBInterface
from src.alpha_factory.causal_inference import CausalFilter

class AlphaFactoryPipeline:
    """
    The master ingestion pipeline. Orchestrates kdb+ vector math, 
    merges datasets, and applies causal filtering before feeding the DRL agent.
    """
    def __init__(self):
        self.kdb = KDBInterface(mode="hdb") # Use HDB for training, RDB for live
        self.causal_filter = CausalFilter()

    def generate_state_observation(self, symbols: list, market_proxy: str = 'SPY') -> pd.DataFrame:
        """
        Builds the final, sanitized state matrix for the PyTorch agent.
        """
        print(f"[{symbols}] Generating High-Frequency Features via kdb+...")
        
        # 1. kdb+ Vector Math
        vwap_df = self.kdb.get_vwap_bars(symbols, window_minutes=5)
        obi_df = self.kdb.get_order_book_imbalance(symbols)
        
        # Merge raw features
        raw_features = pd.merge(vwap_df, obi_df, on=['sym', 'time'], how='inner')
        
        print("Applying Causal Deconfounding...")
        
        # 2. Extract our macroeconomic proxy (the confounder we want to strip out)
        if market_proxy in symbols:
            proxy_data = raw_features[raw_features['sym'] == market_proxy]['vwap']
        else:
            # Fallback mock data if proxy isn't requested
            proxy_data = pd.Series(0, index=raw_features.index) 
            
        # 3. Apply Causal Math
        # Drop the text/categorical columns before doing matrix math
        math_cols = raw_features.select_dtypes(include=['float64', 'int64']).columns
        
        clean_signals = self.causal_filter.apply_deconfounding(
            feature_df=raw_features[math_cols], 
            confounder_proxy=proxy_data
        )
        
        # 4. Filter out spurious noise
        # Assuming we are predicting the 1-step forward VWAP change
        target = clean_signals['vwap'].shift(-1).fillna(0)
        valid_columns = self.causal_filter.filter_spurious_features(target, clean_signals)
        
        print(f"✅ Factory Complete. Kept {len(valid_columns)}/{len(math_cols)} causal features.")
        return clean_signals[valid_columns]