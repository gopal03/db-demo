#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}=======================================================${NC}"
echo -e "${GREEN}      Starting Database Demo Configurator Portal       ${NC}"
echo -e "${GREEN}=======================================================${NC}"

if [ ! -d ".venv" ]; then
    echo "Creating python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo -e "${GREEN}Launching Configurator UI...${NC}"
streamlit run configurator.py
