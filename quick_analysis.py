#!/usr/bin/env python3
"""
Szybka analiza anomalii - pojedynczy pomiar i analiza LLM
"""

import ollama
import psutil
from datetime import datetime


def quick_analyze():
    """Szybka analiza bieżącego stanu systemu"""
    
    print("🤖 Szybka analiza anomalii\n")
    
    # Zbierz metryki
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_gb": psutil.virtual_memory().used / (1024**3),
        "memory_total_gb": psutil.virtual_memory().total / (1024**3),
        "cpu_count": psutil.cpu_count(),
        "processes_count": len(psutil.pids())
    }
    
    print("📊 Metryki systemowe:")
    print(f"  CPU: {metrics['cpu_percent']:.1f}%")
    print(f"  Memory: {metrics['memory_percent']:.1f}% ({metrics['memory_used_gb']:.2f}GB / {metrics['memory_total_gb']:.2f}GB)")
    print(f"  Procesy: {metrics['processes_count']}")
    print(f"  Rdzenie CPU: {metrics['cpu_count']}")
    print(f"  Czas: {metrics['timestamp']}\n")
    
    # Przygotuj prompt
    prompt = f"""Przeanalizuj te metryki systemowe i zidentyfikuj potencjalne anomalie:

CPU: {metrics['cpu_percent']:.1f}%
Pamięć: {metrics['memory_percent']:.1f}% ({metrics['memory_used_gb']:.2f}GB / {metrics['memory_total_gb']:.2f}GB)
Liczba procesów: {metrics['processes_count']}
Liczba rdzeni CPU: {metrics['cpu_count']}

Odpowiedź powinna zawierać:
1. Czy to jest anomalia? (Tak/Nie)
2. Jakie są przyczyny?
3. Jakie działania podjąć?

Bądź zwięzły i konkretny."""

    print("🔍 Analiza LLM (Qwen2:8b):\n")
    print("-" * 60)
    
    try:
        response = ollama.generate(
            model="qwen3:8b",
            prompt=prompt,
            stream=False
        )
        print(response['response'])
    except Exception as e:
        print(f"❌ Błąd: {e}")
        print("Upewnij się, że Ollama jest uruchomiona: ollama run qwen3:8b")
    
    print("-" * 60)


if __name__ == "__main__":
    quick_analyze()
