#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}=======================================================${NC}"
echo -e "${GREEN}      Starting Spanner Graph Universal Demo Console    ${NC}"
echo -e "${GREEN}=======================================================${NC}"

if [ ! -d ".venv" ]; then
    echo "Creating python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Ensuring dependencies are installed..."
pip install -r requirements.txt --quiet

echo -e "${GREEN}Launching Streamlit App...${NC}"
streamlit run app.py
