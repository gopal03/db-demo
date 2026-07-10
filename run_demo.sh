#!/bin/bash
set -e

# Find the active parameters file dynamically
PARAMS_FILE=$(find config/use_cases -name "active_parameters.json" | head -n 1)

if [ -empty ] || [ -z "$PARAMS_FILE" ]; then
    echo "Error: No active configuration found! Please run ./setup_demo.sh first."
    exit 1
fi

echo "=== Phase 2: Ingestion & Presentation Launch ==="
echo "Active parameters: $PARAMS_FILE"

PRODUCT=$(python3 -c "import json; print(json.load(open('$PARAMS_FILE'))['target_database'])")

# 1. Run Data Loader to apply schema and upload records
loader_script=".agents/skills/$PRODUCT/step3_load/scripts/load_data.py"
if [ -f "$loader_script" ]; then
    echo -e "\n---> Step 1: Executing schema and uploading records..."
    python3 "$loader_script" --parameters "$PARAMS_FILE"
else
    echo "Error: Loader script '$loader_script' not found!"
    exit 1
fi

# 2. Launch the Demo Explorer console in the background
echo -e "\n---> Step 2: Starting Presentation Dashboard (app.py)..."

# Terminate any running streamlit instances on port 8501 to prevent conflicts
st_pids=$(lsof -t -i:8501 || true)
if [ -n "$st_pids" ]; then
    echo "Clearing stale streamlit instance on port 8501..."
    kill -9 $st_pids || true
fi

# Start app.py in background
nohup streamlit run app.py --server.port 8501 > /tmp/demo_explorer.log 2>&1 &

echo -e "\n======================================================="
echo "  Database schema successfully applied & seeded!"
echo "  Demo Explorer Dashboard is running in the background."
echo "======================================================="
echo "  Local presentation URL: http://localhost:8501"
echo "======================================================="
