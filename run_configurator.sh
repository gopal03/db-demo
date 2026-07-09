#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}=======================================================${NC}"
echo -e "${GREEN}      Starting Database Demo Configurator Portal       ${NC}"
echo -e "${GREEN}=======================================================${NC}"

if command -v uv &> /dev/null; then
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment using uv..."
        uv venv .venv
    fi
    source .venv/bin/activate
    echo "Verifying dependencies with uv..."
    uv pip install -r requirements.txt
else
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment using standard python..."
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    echo "Verifying dependencies with pip..."
    pip install -r requirements.txt
fi

echo -e "${GREEN}Launching Configurator UI...${NC}"
streamlit run configurator.py
