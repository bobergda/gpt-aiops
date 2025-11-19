#!/bin/bash
set -e

BASE="/usr/share/ollama/.ollama/models"

if [ ! -d "$BASE" ]; then
    echo "❌ Nie znaleziono katalogu modeli: $BASE"
    exit 1
fi

echo "📦 Przygotowuję pełny backup katalogu BASE: $BASE"
OUT="ollama-base-full-$(date +%Y%m%d-%H%M%S).tar.gz"

echo "➡️ Tworzę archiwum: $OUT"
sudo tar -cvpzf "$OUT" -C "$(dirname "$BASE")" "$(basename "$BASE")"

echo "✅ Gotowe: $OUT"
