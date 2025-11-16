#!/bin/bash

# AIOps - Start script
# Uruchamia aplikację analizy anomalii z Qwen3:8b

set -e

echo "🤖 AIOps - Analiza Anomalii z Qwen3:8b"
echo "======================================"
echo ""

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Pobranie ścieżki skryptu
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/.venv"

# Sprawdź Python
echo "📍 Sprawdzam Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 nie znaleziony!${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python3 $PYTHON_VERSION${NC}"
echo ""

# Stwórz i aktywuj venv
echo "📍 Sprawdzam wirtualne środowisko (venv)..."
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️  Tworzę wirtualne środowisko...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Wirtualne środowisko utworzone${NC}"
else
    echo -e "${GREEN}✅ Wirtualne środowisko znalezione${NC}"
fi
echo ""

# Aktywuj venv
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✅ Wirtualne środowisko aktywne${NC}"
echo ""

# Sprawdź Ollama
echo "📍 Sprawdzam Ollama..."
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama nie zainstalowana!${NC}"
    echo "Zainstaluj: curl https://ollama.ai/install.sh | sh"
    exit 1
fi
echo -e "${GREEN}✅ Ollama zainstalowana${NC}"
echo ""

# Sprawdź czy Ollama działa
echo "📍 Sprawdzam dostępność Ollama API..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ollama nie jest uruchomiona${NC}"
    echo ""
    echo "Uruchamiam Ollama z modelem qwen3:8b..."
    echo ""
    ollama run qwen3:8b &
    OLLAMA_PID=$!
    sleep 3
    echo -e "${GREEN}✅ Ollama uruchomiona (PID: $OLLAMA_PID)${NC}"
else
    echo -e "${GREEN}✅ Ollama API dostępna${NC}"
fi
echo ""

# Sprawdź model qwen3:8b
echo "📍 Sprawdzam model qwen3:8b..."
if ! ollama list | grep -q "qwen3:8b"; then
    echo -e "${YELLOW}⚠️  Model qwen3:8b nie znaleziony${NC}"
    echo "Pobieranie modelu (może potrwać kilka minut)..."
    ollama pull qwen3:8b
fi
echo -e "${GREEN}✅ Model qwen3:8b dostępny${NC}"
echo ""

# Zainstaluj zależności jeśli potrzebne
echo "📍 Sprawdzam Python dependencje..."
if ! python3 -c "import ollama, psutil" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Instaluję zależności...${NC}"
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
    echo -e "${GREEN}✅ Zależności zainstalowane${NC}"
else
    echo -e "${GREEN}✅ Zależności zainstalowane${NC}"
fi
echo ""

# Menu
echo "Wybierz opcję:"
echo "1) Szybka analiza (1 pomiar)"
echo "2) Ciągłe monitorowanie (60 sekund)"
echo "3) Wyjście"
echo ""

read -p "Opcja [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Uruchamiam szybką analizę..."
        echo ""
        python3 "$SCRIPT_DIR/quick_analysis.py"
        ;;
    2)
        echo ""
        echo "🚀 Uruchamiam monitorowanie..."
        echo ""
        python3 "$SCRIPT_DIR/anomaly_analyzer.py"
        ;;
    3)
        echo "Do widzenia! 👋"
        deactivate
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Nieprawidłowa opcja${NC}"
        deactivate
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Gotowe!${NC}"
