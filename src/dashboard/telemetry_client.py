from pymongo import MongoClient, errors
from pymongo.collection import Collection
from datetime import datetime
from typing import Dict, Any, List

# Import our Singleton Config Loader
from src.config_loader import config

class TelemetryClient:
    """
    Axiom-Alpha-Research-Lab: MongoDB Telemetry Logger.
    Handles asynchronous-style logging for execution data and risk metrics
    without blocking the main high-frequency trading loop.
    """
    _instance = None

    def __new__(cls):
        # Singleton pattern ensures we don't open 500 database connections
        if cls._instance is None:
            cls._instance = super(TelemetryClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            # Pull connection details dynamically from config/system.yaml
            mongo_uri = config.system['databases']['mongodb']['uri']
            db_name = config.system['databases']['mongodb']['database_name']
            
            # Initialize connection with a timeout so it doesn't hang the research cluster
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            
            # Verify connection
            self.client.admin.command('ping')
            
            self.db = self.client[db_name]
            
            # Setup Collections
            self.execution_logs: Collection = self.db['execution_logs']
            self.risk_metrics: Collection = self.db['risk_metrics']
            
            print(f"✅ TelemetryClient connected to MongoDB at {mongo_uri}")
            
        except errors.ServerSelectionTimeoutError as err:
            print(f"❌ CRITICAL: Could not connect to MongoDB telemetry server: {err}")
            raise

    def log_execution(self, agent_id: str, ticker: str, action: str, 
                      quantity: float, price: float, metadata: Dict[str, Any] = None):
        """
        Logs a specific trade execution including the agent's internal state/confidence.
        """
        payload = {
            "timestamp": datetime.utcnow(),
            "agent_id": agent_id,
            "ticker": ticker,
            "action": action,        # e.g., "BUY", "SELL", "HOLD"
            "quantity": quantity,
            "execution_price": price,
            "metadata": metadata or {} # Dump the PyTorch agent's confidence/Q-values here
        }
        
        # In a true high-frequency setup, this insert_one would be passed to a 
        # background worker queue (like Celery/Redis) so it doesn't block the thread.
        self.execution_logs.insert_one(payload)

    def log_portfolio_risk(self, timestamp: datetime, total_exposure: float, 
                           current_drawdown: float, sharpe_ratio: float, 
                           causal_signals: Dict[str, float]):
        """
        Logs the macro-level portfolio risk snapshot. This fuels the live Dashboard.
        """
        payload = {
            "timestamp": timestamp,
            "total_exposure": total_exposure,
            "current_drawdown": current_drawdown,
            "rolling_sharpe": sharpe_ratio,
            "active_causal_factors": causal_signals # Dictionary of factors driving the current decision
        }
        self.risk_metrics.insert_one(payload)

    def fetch_recent_risk_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Used by the Streamlit dashboard to pull the latest telemetry."""
        cursor = self.risk_metrics.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return list(cursor)

# Instantiate a global object to be imported by the execution agents
telemetry = TelemetryClient()