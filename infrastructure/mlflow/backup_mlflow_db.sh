#!/bin/bash

# Axiom-Alpha-Research-Lab: MLflow Database Backup Utility
# This should be run via cronjob weekly on your Primary Compute PC.

BACKUP_DIR="../../data/backups/mlflow"
DATE=$(date +"%Y_%m_%d_%H%M")
BACKUP_FILE="$BACKUP_DIR/mlflow_pg_dump_$DATE.sql"

echo "========================================"
echo " Starting MLflow Metadata Backup        "
echo "========================================"

# Ensure backup directory exists
mkdir -p $BACKUP_DIR

# Use docker exec to run pg_dump inside the postgres container
# Note: 'axiom_mlflow_db' matches the container_name in docker-compose.yml
# 'axiom_ml' and 'mlflow_experiments' match the POSTGRES_USER and POSTGRES_DB
echo "Dumping PostgreSQL database to $BACKUP_FILE..."

docker exec -t axiom_mlflow_db pg_dump -U axiom_ml -d mlflow_experiments -F p > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "✅ Backup Successful: $BACKUP_FILE"
  
  # Optional: Compress the backup to save space
  gzip "$BACKUP_FILE"
  echo "📦 Compressed to: $BACKUP_FILE.gz"
else
  echo "❌ CRITICAL: Backup Failed!"
  exit 1
fi

echo "========================================"