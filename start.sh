#!/bin/bash

# AIOps - Start script
# Launch the anomaly analysis app with Qwen3:8b

set -e

echo "🤖 AIOps - Anomaly Analysis with Qwen3:8b"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Resolve script path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/.venv"

# Check Python
echo "📍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python3 $PYTHON_VERSION${NC}"
echo ""

# Create/activate venv
echo "📍 Checking virtual environment (venv)..."
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment found${NC}"
fi
echo ""

# Activate venv
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✅ Virtual environment active${NC}"
echo ""

# Check Ollama
echo "📍 Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama not installed!${NC}"
    echo "Install: curl https://ollama.ai/install.sh | sh"
    exit 1
fi
echo -e "${GREEN}✅ Ollama installed${NC}"
echo ""

# Check if Ollama is running
echo "📍 Checking Ollama API..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ollama is not running${NC}"
    echo ""
    echo "Starting Ollama with the qwen3:8b model..."
    echo ""
    ollama run qwen3:8b &
    OLLAMA_PID=$!
    sleep 3
    echo -e "${GREEN}✅ Ollama started (PID: $OLLAMA_PID)${NC}"
else
    echo -e "${GREEN}✅ Ollama API available${NC}"
fi
echo ""

# Check qwen3:8b model
echo "📍 Checking qwen3:8b model..."
if ! ollama list | grep -q "qwen3:8b"; then
    echo -e "${YELLOW}⚠️  qwen3:8b model not found${NC}"
    echo "Downloading model (this may take a few minutes)..."
    ollama pull qwen3:8b
fi
echo -e "${GREEN}✅ qwen3:8b model available${NC}"
echo ""

# Install dependencies if needed
echo "📍 Checking Python dependencies..."
if ! python3 -c "import ollama, psutil" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi
echo ""

# Menu
echo "Choose an option:"
echo "1) Quick analysis (single measurement)"
echo "2) Continuous monitoring (60 seconds)"
echo "Q) Exit"
echo ""

read -p "Option [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Launching quick analysis..."
        echo ""
        python3 "$SCRIPT_DIR/quick_analysis.py"
        ;;
    2)
        echo ""
        echo "🚀 Launching monitoring..."
        echo ""
        python3 "$SCRIPT_DIR/anomaly_analyzer.py"
        ;;
    q|Q)
        echo "Goodbye! 👋"
        deactivate
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid option${NC}"
        deactivate
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Done!${NC}"
