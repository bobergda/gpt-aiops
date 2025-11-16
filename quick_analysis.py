#!/usr/bin/env python3
"""
Szybka analiza anomalii - pojedynczy pomiar i analiza LLM
"""

import ollama
import psutil
from datetime import datetime
import time


def get_top_processes(limit: int = 5) -> str:
    """Pobierz top procesy zużywające CPU i pamięć"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sortuj po CPU
    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    
    result = "Top procesy (CPU):\n"
    for proc in top_cpu:
        result += f"  - {proc['name']}: {proc['cpu_percent']:.1f}% CPU, {proc['memory_percent']:.1f}% MEM\n"
    
    return result


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
    
    # Pobierz top procesy
    top_processes = get_top_processes(limit=5)
    print("📈 " + top_processes)
    
    # Przygotuj prompt
    prompt = f"""Przeanalizuj te metryki systemowe i zidentyfikuj potencjalne anomalie:

CPU: {metrics['cpu_percent']:.1f}%
Pamięć: {metrics['memory_percent']:.1f}% ({metrics['memory_used_gb']:.2f}GB / {metrics['memory_total_gb']:.2f}GB)
Liczba procesów: {metrics['processes_count']}
Liczba rdzeni CPU: {metrics['cpu_count']}

{top_processes}

Odpowiedź powinna zawierać:
1. Czy to jest anomalia? (Tak/Nie)
2. Jakie są przyczyny?
3. Jakie działania podjąć?

Bądź zwięzły i konkretny."""

    print("🔍 Analiza LLM (Qwen3:8b):\n")
    print("-" * 60)
    
    try:
        response = ollama.generate(
            model="qwen3:8b",
            prompt=prompt,
            stream=False
        )
        print(response['response'])

        prompt_tokens = response.get("prompt_eval_count")
        completion_tokens = response.get("eval_count")

        print("\n📈 Statystyki zapytania:")
        if prompt_tokens is not None:
            print(f"  Tokeny promptu: {prompt_tokens}")
        if completion_tokens is not None:
            print(f"  Tokeny odpowiedzi: {completion_tokens}")
        if prompt_tokens is not None and completion_tokens is not None:
            print(f"  Tokeny łącznie: {prompt_tokens + completion_tokens}")

        total_duration = response.get("total_duration")
        eval_duration = response.get("eval_duration")
        load_duration = response.get("load_duration")

        if total_duration:
            print(f"  Czas całkowity: {total_duration / 1e9:.2f}s")
        if eval_duration:
            print(f"  Czas generowania: {eval_duration / 1e9:.2f}s")
        if load_duration:
            print(f"  Czas ładowania modelu: {load_duration / 1e9:.2f}s")
    except Exception as e:
        print(f"❌ Błąd: {e}")
        print("Upewnij się, że Ollama jest uruchomiona: ollama run qwen3:8b")
    
    print("-" * 60)


if __name__ == "__main__":
    quick_analyze()
