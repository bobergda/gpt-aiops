#!/bin/bash
set -e

BACKUP="$1"

if [ -z "$BACKUP" ]; then
    echo "❌ Użycie: ./restore_ollama.sh <plik-backupu.tar.gz>"
    exit 1
fi

if [ ! -f "$BACKUP" ]; then
    echo "❌ Plik $BACKUP nie istnieje."
    exit 1
fi

# Upewnij się że katalog istnieje
sudo mkdir -p /usr/share/ollama

echo "➡️  Rozpakowuję modele do /usr/share/ollama..."
sudo tar -xvzf "$BACKUP" -C /usr/share/ollama/.ollama

echo "➡️  Ustawiam właściciela na użytkownika ollama..."
sudo chown -R ollama:ollama /usr/share/ollama/.ollama

echo "🔄 Restartuję usługę ollama..."
sudo systemctl restart ollama

echo "✅ Przywracanie zakończone!"
echo "Możesz sprawdzić:  ollama list"

