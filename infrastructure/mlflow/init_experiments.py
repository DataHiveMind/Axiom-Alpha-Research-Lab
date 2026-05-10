import mlflow
import time
from mlflow.exceptions import MlflowException

# Connect to the local MLflow server running in Docker
MLFLOW_URI = "http://127.0.0.1:5000"
mlflow.set_tracking_uri(MLFLOW_URI)

# Define the standard architecture of your research laboratory
EXPERIMENTS = {
    "Causal_Discovery_Pipelines": "Tracks factor engineering and causal noise filtering.",
    "Upper_Agent_Portfolio_Alloc": "Tracks SAC/PPO agents for dynamic portfolio weighting.",
    "Lower_Agent_Optimal_Hedging": "Tracks execution agents minimizing slippage.",
    "CPCV_Validation_Runs": "Tracks Combinatorial Purged Cross-Validation results."
}

def wait_for_server(retries=10, delay=5):
    """Wait for the MLflow server to become responsive."""
    for i in range(retries):
        try:
            # A simple call to check if the server is up
            mlflow.search_experiments()
            print(f"✅ MLflow server is up at {MLFLOW_URI}")
            return True
        except Exception as e:
            print(f"⏳ Waiting for MLflow server... ({i+1}/{retries})")
            time.sleep(delay)
    raise ConnectionError("CRITICAL: MLflow server failed to respond.")

def initialize_experiments():
    """Create the standardized experiments if they don't already exist."""
    print("Initializing Axiom Alpha Experiment Registries...")
    
    for exp_name, description in EXPERIMENTS.items():
        try:
            # Attempt to create the experiment with metadata tags
            experiment_id = mlflow.create_experiment(
                name=exp_name,
                tags={"description": description, "environment": "Axiom-Cluster"}
            )
            print(f"  [+] Created: {exp_name} (ID: {experiment_id})")
        except MlflowException:
            # Experiment already exists, just fetch it
            exp = mlflow.get_experiment_by_name(exp_name)
            print(f"  [=] Exists: {exp_name} (ID: {exp.experiment_id})")

if __name__ == "__main__":
    wait_for_server()
    initialize_experiments()
    print("✅ MLflow infrastructure successfully structured.")