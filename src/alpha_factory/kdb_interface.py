import pykx as kx
import pandas as pd
from pathlib import Path
from src.config_loader import config

class KDBInterface:
    """
    Handles high-performance data streaming between the kdb+ Data Node 
    and the Python ML Compute Node using PyKX.
    """
    def __init__(self, mode="rdb"):
        kdb_host = config.system['databases']['kdb']['host']
        kdb_port = config.system['databases']['kdb'][f"{mode}_port"]
        
        try:
            # Establish synchronous connection to kdb+
            self.q = kx.SyncQConnection(host=kdb_host, port=kdb_port)
            print(f"✅ Connected to kdb+ ({mode}) at {kdb_host}:{kdb_port}")
            
            # Load the vector aggregation scripts into the kdb+ memory space
            q_script_path = Path(__file__).parent / "q_scripts" / "aggregations.q"
            self.q(f"\\l {q_script_path.as_posix()}")
            
        except Exception as e:
            print(f"❌ CRITICAL: Failed to connect to kdb+: {e}")
            raise

    def get_vwap_bars(self, symbols: list, window_minutes: int) -> pd.DataFrame:
        """Executes the kdb+ VWAP function and returns a Pandas DataFrame."""
        sym_str = "`" + "`".join(symbols)
        query = f"calc_vwap_bars[select from trades where sym in {sym_str}; {window_minutes}]"
        
        # Execute the query and instantly convert the kdb+ table to a Pandas DataFrame
        return self.q(query).pd()

    def get_order_book_imbalance(self, symbols: list) -> pd.DataFrame:
        sym_str = "`" + "`".join(symbols)
        query = f"calc_obi[select from quotes where sym in {sym_str}]"
        return self.q(query).pd()