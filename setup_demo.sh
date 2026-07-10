#!/bin/bash
set -e

# Find the active parameters file dynamically
PARAMS_FILE=$(find config/use_cases -name "active_parameters.json" | head -n 1)

if [ -empty ] || [ -z "$PARAMS_FILE" ]; then
    echo "Error: No active configuration found! Please configure your demo using the Configurator Portal first."
    exit 1
fi

echo "=== Phase 1: Provisioning & Compilation ==="
echo "Active parameters found: $PARAMS_FILE"

# Extract database target, use case directory, and project ID using python
PRODUCT=$(python3 -c "import json; print(json.load(open('$PARAMS_FILE'))['target_database'])")
PROJECT_ID=$(python3 -c "import json; print(json.load(open('$PARAMS_FILE'))['project_id'])")
USE_CASE_DIR=$(dirname "$PARAMS_FILE")

echo "Target Product: ${PRODUCT^^}"
echo "Project ID: $PROJECT_ID"
echo "Use Case Folder: $USE_CASE_DIR"

# 1. Provision Infrastructure via Terraform
echo -e "\n---> Step 1: Provisioning ${PRODUCT^^} infrastructure..."
cd "terraform/$PRODUCT"

# Clean up variables and run apply
terraform init
terraform apply -state="state_gaming_analytics.tfstate" -var="project_id=$PROJECT_ID" -auto-approve

# 2. Capture dynamic host IP and save it
echo -e "\n---> Step 2: Extracting dynamic IP address..."
DB_HOST_IP=$(terraform output -json -state="state_gaming_analytics.tfstate" | python3 -c "import sys, json; print(json.load(sys.stdin).get('db_host_ip', {}).get('value', ''))")

cd ../.. # Back to root

if [ -n "$DB_HOST_IP" ]; then
    echo "Dynamic DB Host IP captured: $DB_HOST_IP. Updating parameters file..."
    python3 -c "
import json
data = json.load(open('$PARAMS_FILE'))
data['database_configs']['$PRODUCT']['host'] = '$DB_HOST_IP'
json.dump(data, open('$PARAMS_FILE', 'w'), indent=2)
"
else
    echo "No dynamic host IP found (not required for Spanner/Firestore)."
fi

# 3. Compile DDL Schema
schema_script=".agents/skills/$PRODUCT/step1_schema/scripts/generate_schema.py"
if [ -f "$schema_script" ]; then
    echo -e "\n---> Step 3: Compiling SQL DDL schema..."
    python3 "$schema_script" \
      --config "$USE_CASE_DIR/use_case_config.json" \
      --output-schema "$USE_CASE_DIR/schema.sql" \
      --output-indexes "$USE_CASE_DIR/indexes.sql" \
      --alloydb-columnar "$USE_CASE_DIR/columnar_config.sql"
fi

# 4. Generate Mock Data
data_script=".agents/skills/$PRODUCT/step2_data/scripts/generate_data.py"
if [ -f "$data_script" ]; then
    echo -e "\n---> Step 4: Simulating mock datasets..."
    python3 "$data_script" \
      --config "$USE_CASE_DIR/use_case_config.json" \
      --parameters "$PARAMS_FILE" \
      --output "$USE_CASE_DIR/dummy_data.json"
fi

echo -e "\n======================================================="
echo "  Infrastructure provisioned & parameters updated."
echo "  DDL Schema compiled on disk: $USE_CASE_DIR/schema.sql"
echo "  Mock Data simulated on disk: $USE_CASE_DIR/dummy_data.json"
echo "======================================================="
echo "  Please review the schema and datasets above."
echo "  When ready to execute and launch, run the seed script:"
echo "  ./run_demo.sh"
echo "======================================================="
