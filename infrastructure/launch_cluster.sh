#!/bin/bash

# Axiom-Alpha-Research-Lab Master Boot Script
echo "========================================"
echo " Starting Axiom Alpha Infrastructure    "
echo "========================================"

# Determine the role passed as an argument (e.g., ./launch_cluster.sh --data-node)
ROLE=$1

case $ROLE in
  --primary-compute)
    echo "Role: Primary Compute (Deep Learning & MLflow)"
    docker-compose -f docker-compose.yml up -d mlflow-db mlflow-server
    
    # NEW: Wait strictly for the PostgreSQL DB to be ready on port 5432
    # Then wait for the MLflow server to be ready on port 5000
    echo "Waiting for MLflow backend to initialize..."
    ./infrastructure/mlflow/wait-for-it.sh 127.0.0.1:5432 -t 20
    ./infrastructure/mlflow/wait-for-it.sh 127.0.0.1:5000 -t 20

    echo "Structuring MLflow Registries..."
    python infrastructure/mlflow/init_experiments.py
    ;;
    
  --data-node)
    echo "Role: Data Node (kdb+ & Telemetry)"
    docker-compose -f docker-compose.yml up -d mongodb
    echo "MongoDB telemetry running on port 27017."
    
    echo "Starting kdb+ Ticker Plant and RDB..."
    # Starts kdb+ listening on port 5011, loading the RDB script
    q kdb_tick/rdb.q -p 5011 < /dev/null > rdb.log 2>&1 &
    echo "kdb+ RDB running on port 5011."
    ;;
    
  --monitoring-station)
    echo "Role: Live Risk Control (Dashboard)"
    echo "Booting Streamlit PnL Dashboard..."
    # Command to boot your Python dashboard
    # streamlit run ../src/dashboard/app.py
    ;;
    
  *)
    echo "Usage: ./launch_cluster.sh [ --primary-compute | --data-node | --monitoring-station ]"
    exit 1
    ;;
esac

echo "========================================"
echo " Infrastructure successfully initialized. "
echo "========================================"