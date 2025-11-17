#!/usr/bin/env bash
set -euo pipefail

MODEL=${1:-qwen3:8b}
PROMPT=${2:-"napisz kim jesteś"}

curl http://localhost:11434/api/generate -d "{
  \"model\": \"${MODEL}\",
  \"prompt\": \"${PROMPT}\",
  \"think\": false,
  \"stream\": false
}"