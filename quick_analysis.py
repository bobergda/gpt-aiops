#!/usr/bin/env python3
"""
Quick anomaly analysis - single measurement and LLM assessment
"""

import ollama
import psutil
from datetime import datetime
import time


def get_top_processes(limit: int = 5) -> str:
    """Return the most demanding CPU and memory processes"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by CPU usage first
    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    
    result = "Top processes (CPU):\n"
    for proc in top_cpu:
        result += f"  - {proc['name']}: {proc['cpu_percent']:.1f}% CPU, {proc['memory_percent']:.1f}% MEM\n"
    
    return result


def quick_analyze():
    """Quick analysis of the current system state"""
    
    print("🤖 Quick anomaly analysis\n")
    
    # Gather metrics
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_gb": psutil.virtual_memory().used / (1024**3),
        "memory_total_gb": psutil.virtual_memory().total / (1024**3),
        "cpu_count": psutil.cpu_count(),
        "processes_count": len(psutil.pids())
    }
    
    print("📊 System metrics:")
    print(f"  CPU: {metrics['cpu_percent']:.1f}%")
    print(f"  Memory: {metrics['memory_percent']:.1f}% ({metrics['memory_used_gb']:.2f}GB / {metrics['memory_total_gb']:.2f}GB)")
    print(f"  Processes: {metrics['processes_count']}")
    print(f"  CPU cores: {metrics['cpu_count']}")
    print(f"  Timestamp: {metrics['timestamp']}\n")
    
    # Fetch top processes
    top_processes = get_top_processes(limit=5)
    print("📈 " + top_processes)
    
    # Build prompt
    prompt = f"""Review these system metrics and identify any potential anomalies:

CPU: {metrics['cpu_percent']:.1f}%
Memory: {metrics['memory_percent']:.1f}% ({metrics['memory_used_gb']:.2f}GB / {metrics['memory_total_gb']:.2f}GB)
Number of processes: {metrics['processes_count']}
Number of CPU cores: {metrics['cpu_count']}

{top_processes}

The response should include:
1. Is this an anomaly? (Yes/No)
2. What are the causes?
3. What actions should be taken?

Be concise and direct."""

    print("🔍 LLM analysis (Qwen3:8b):\n")
    print("-" * 60)
    
    try:
        response = ollama.generate(
            model="qwen3:8b",
            prompt=prompt,
            stream=False,
            think=False,
        )
        print(response['response'])

        prompt_tokens = response.get("prompt_eval_count")
        completion_tokens = response.get("eval_count")

        print("\n📈 Query statistics:")
        if prompt_tokens is not None:
            print(f"  Prompt tokens: {prompt_tokens}")
        if completion_tokens is not None:
            print(f"  Completion tokens: {completion_tokens}")
        if prompt_tokens is not None and completion_tokens is not None:
            print(f"  Total tokens: {prompt_tokens + completion_tokens}")

        total_duration = response.get("total_duration")
        eval_duration = response.get("eval_duration")
        load_duration = response.get("load_duration")

        if total_duration:
            print(f"  Total time: {total_duration / 1e9:.2f}s")
        if eval_duration:
            print(f"  Generation time: {eval_duration / 1e9:.2f}s")
        if load_duration:
            print(f"  Model load time: {load_duration / 1e9:.2f}s")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Ollama is running: ollama run qwen3:8b")
    
    print("-" * 60)


if __name__ == "__main__":
    quick_analyze()
