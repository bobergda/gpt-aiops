#!/usr/bin/env python3
"""
Quick anomaly analysis - single measurement and LLM assessment
"""

from datetime import datetime
import time
import sys

import ollama
import psutil

DEFAULT_SHOW_THINKING = False
DEFAULT_EGG = True

def gather_process_stats(limit: int | None = None, sample_delay: float = 1.0):
    """Sample processes and return (pid, name, cpu%, mem%) tuples sorted by CPU."""
    processes = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            proc.cpu_percent(None)  # prime baseline
            processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(sample_delay)

    stats = []
    for proc in processes:
        try:
            cpu = proc.cpu_percent(None)
            mem = proc.memory_percent()
            cmdline = " ".join(proc.cmdline()) if proc.cmdline() else ""
            stats.append((proc.info["pid"], proc.info["name"], cpu, mem, cmdline))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    stats.sort(key=lambda item: item[2], reverse=True)
    return stats[:limit] if limit is not None else stats

def get_top_processes(limit: int = 10) -> str:
    """Return the most demanding CPU and memory processes"""
    top_cpu = gather_process_stats(limit=limit)

    result = "Top processes (CPU):\n"
    print("📈 Top processes (CPU):")
    for pid, name, cpu, mem, cmdline in top_cpu:
        result += f"  - {name}: {cpu:.1f}% CPU, {mem:.1f}% MEM\n"
        print(f"  {pid:>6} {name:<25}: {cpu:.1f}% CPU, {mem:.1f}% MEM")
    
    return result


def quick_analyze(show_thinking: bool = DEFAULT_SHOW_THINKING, egg: bool = False):
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
    top_processes = get_top_processes(limit=10)
    
    # Build prompt
    if not egg:
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
    else:
        # Easter egg – prompt w klimacie mema "Intel vs AMD – WINCEJ RDZENIUF"
        prompt = f"""Masz przeanalizować stan systemu na podstawie poniższych danych,
ale forma odpowiedzi ma nawiązywać do kultowego polskiego mema „Intel vs AMD – WINCEJ RDZENIUF”.

Dane systemowe:

CPU: {metrics['cpu_percent']:.1f}%
Pamięć: {metrics['memory_percent']:.1f}% ({metrics['memory_used_gb']:.2f}GB / {metrics['memory_total_gb']:.2f}GB)
Liczba procesów: {metrics['processes_count']}
Liczba rdzeni CPU: {metrics['cpu_count']}

{top_processes}

Twoja odpowiedź ma mieć **dwie części**, napisane po polsku, jedna po drugiej:

---

### 1. Część pierwsza
Napisz rzeczowo, technicznie i profesjonalnie.  
Uwzględnij:
- czy to wygląda na anomalię (Tak/Nie)  
- prawdopodobne przyczyny  
- konkretne rekomendacje  

Styl: analityczny, spokojny, jak korporacyjny inżynier skupiony na metrykach i wykresach.

---

### 2. Część druga
Napisz krótkie podsumowanie w stylu kultowego mema „AMD – WINCEJ RDZENIUF”.

Wymagania:
- luźny, memiczny język  
- celowe zniekształcenia typu: **„WINCEJ RDZENIUF”, „rdzeń dobry, dużo rdzeni lepsze”, „RDZEŃ → RDZEŃ → RDZEŃ”**  
- żart ma odnosić się do realnych danych (np. do liczby rdzeni albo obciążenia CPU)
- przesadzone, śmieszkowe wnioski w stylu „jak coś działa źle → dodaj rdzeni”  

---

Zachowaj tę kolejność i nie używaj żadnych nawiasów ani oznaczeń trybów w samej treści odpowiedzi."""

    print("🔍 LLM analysis (Qwen3:8b):\n")
    print("-" * 60)
    
    try:
        stats = {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_duration": None,
            "eval_duration": None,
            "load_duration": None,
        }

        in_thinking = False  # track when the model is exposing its thought process

        generate_args = {
            "model": "qwen3:8b",
            "prompt": prompt,
            "stream": True,
            "think": show_thinking
        }

        # Stream the response token-by-token for immediate feedback
        for chunk in ollama.generate(**generate_args):
            if show_thinking:
                thinking_text = (
                    chunk.get("thinking")
                    or chunk.get("message", {}).get("thinking")
                )

                if thinking_text:
                    if not in_thinking:
                        print("\n🧠 Model thinking...\n")
                        in_thinking = True
                    print(thinking_text, end="", flush=True)
                    continue

                if in_thinking and chunk.get("response"):
                    print("\n")
                    in_thinking = False

            if chunk.get("response"):
                print(chunk["response"], end="", flush=True)

            if chunk.get("done"):
                stats["prompt_tokens"] = chunk.get("prompt_eval_count")
                stats["completion_tokens"] = chunk.get("eval_count")
                stats["total_duration"] = chunk.get("total_duration")
                stats["eval_duration"] = chunk.get("eval_duration")
                stats["load_duration"] = chunk.get("load_duration")

        if in_thinking:
            print("\n")

        print()

        print("\n📈 Query statistics:")
        if stats["prompt_tokens"] is not None:
            print(f"  Prompt tokens: {stats['prompt_tokens']}")
        if stats["completion_tokens"] is not None:
            print(f"  Completion tokens: {stats['completion_tokens']}")
        if stats["prompt_tokens"] is not None and stats["completion_tokens"] is not None:
            print(f"  Total tokens: {stats['prompt_tokens'] + stats['completion_tokens']}")

        if stats["total_duration"]:
            print(f"  Total time: {stats['total_duration'] / 1e9:.2f}s")
        if stats["eval_duration"]:
            print(f"  Generation time: {stats['eval_duration'] / 1e9:.2f}s")
        if stats["load_duration"]:
            print(f"  Model load time: {stats['load_duration'] / 1e9:.2f}s")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Ollama is running: ollama run qwen3:8b")
    
    print("-" * 60)


if __name__ == "__main__":
    quick_analyze(show_thinking=DEFAULT_SHOW_THINKING, egg=DEFAULT_EGG)
