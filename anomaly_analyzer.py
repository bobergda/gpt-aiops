#!/usr/bin/env python3
"""
Analiza anomalii CPU/Memory z użyciem Qwen2:8b model
Zbiera metryki systemowe i opisuje anomalie przy pomocy LLM
"""

import ollama
import psutil
import time
from datetime import datetime
from typing import Dict, List
import json


class AnomalyAnalyzer:
    def __init__(self, model: str = "qwen3:8b"):
        """
        Inicjalizuj analizator anomalii
        
        Args:
            model: Nazwa modelu w Ollama (default: qwen3:8b)
        """
        self.model = model
        self.metrics_history: List[Dict] = []
        
    def collect_metrics(self) -> Dict:
        """Zbierz metryki CPU i pamięci"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "cpu_count": psutil.cpu_count(),
            "processes_count": len(psutil.pids())
        }
    
    def is_anomaly(self, metrics: Dict, cpu_threshold: float = 80, mem_threshold: float = 85) -> bool:
        """
        Sprawdź czy metryki wskazują anomalię
        
        Args:
            metrics: Slownik z metrykami
            cpu_threshold: Próg dla CPU (%)
            mem_threshold: Próg dla pamięci (%)
        
        Returns:
            True jeśli anomalia, False w przeciwnym razie
        """
        return metrics["cpu_percent"] > cpu_threshold or metrics["memory_percent"] > mem_threshold
    
    def analyze_anomaly(self, metrics: Dict) -> Dict:
        """
        Przeanalizuj anomalię przy pomocy LLM
        
        Args:
            metrics: Slownik z metrykami
            
        Returns:
            Odpowiedź zwrócona przez Ollamę
        """
        prompt = f"""Przeanalizuj te metryki systemowe i zidentyfikuj potencjalne anomalie:

CPU: {metrics['cpu_percent']:.1f}%
Pamięć: {metrics['memory_percent']:.1f}% ({metrics['memory_used_gb']:.2f}GB / {metrics['memory_total_gb']:.2f}GB)
Liczba procesów: {metrics['processes_count']}
Liczba rdzeni CPU: {metrics['cpu_count']}
Czas: {metrics['timestamp']}

Odpowiedź powinna zawierać:
1. Czy to jest anomalia? (Tak/Nie)
2. Jakie są przyczyny wysokiego zużycia?
3. Jakie działania podjąć?
4. Czy grozi to problemami wydajności?

Bądź zwięzły i konkretny."""

        return ollama.generate(
            model=self.model,
            prompt=prompt,
            stream=False
        )

    @staticmethod
    def print_llm_stats(response: Dict):
        """Wyświetl statystyki użycia tokenów i czasu"""
        prompt_tokens = response.get("prompt_eval_count")
        completion_tokens = response.get("eval_count")
        total_duration = response.get("total_duration")
        eval_duration = response.get("eval_duration")
        load_duration = response.get("load_duration")

        print("\n📊 Statystyki analizy:")
        if prompt_tokens is not None:
            print(f"  Tokeny promptu: {prompt_tokens}")
        if completion_tokens is not None:
            print(f"  Tokeny odpowiedzi: {completion_tokens}")
        if prompt_tokens is not None and completion_tokens is not None:
            print(f"  Tokeny łącznie: {prompt_tokens + completion_tokens}")
        if total_duration:
            print(f"  Czas całkowity: {total_duration / 1e9:.2f}s")
        if eval_duration:
            print(f"  Czas generowania: {eval_duration / 1e9:.2f}s")
        if load_duration:
            print(f"  Czas ładowania modelu: {load_duration / 1e9:.2f}s")
    
    def monitor_continuous(self, duration_seconds: int = 60, interval_seconds: int = 10):
        """
        Ciągłe monitorowanie i analiza anomalii
        
        Args:
            duration_seconds: Jak długo monitorować (sekundy)
            interval_seconds: Interwał zbierania metryk (sekundy)
        """
        print(f"🔍 Rozpoczynam monitorowanie na {duration_seconds}s...")
        print(f"   Model: {self.model}")
        print(f"   Interwał: {interval_seconds}s\n")
        
        start_time = time.time()
        anomaly_count = 0
        
        while time.time() - start_time < duration_seconds:
            # Zbierz metryki
            metrics = self.collect_metrics()
            self.metrics_history.append(metrics)
            
            print(f"[{metrics['timestamp']}]")
            print(f"  CPU: {metrics['cpu_percent']:.1f}% | Memory: {metrics['memory_percent']:.1f}%")
            
            # Sprawdź anomalię
            if self.is_anomaly(metrics):
                anomaly_count += 1
                print("  ⚠️  ANOMALIA WYKRYTA!")
                print("\n📊 Analiza LLM:")
                print("-" * 60)
                
                analysis_response = self.analyze_anomaly(metrics)
                print(analysis_response['response'])
                self.print_llm_stats(analysis_response)
                
                print("-" * 60 + "\n")
            else:
                print("  ✅ Status normalny\n")
            
            time.sleep(interval_seconds)
        
        # Podsumowanie
        self.print_summary(anomaly_count)
    
    def print_summary(self, anomaly_count: int):
        """Wyświetl podsumowanie sesji monitorowania"""
        print("\n" + "="*60)
        print("📈 PODSUMOWANIE SESJI")
        print("="*60)
        
        if not self.metrics_history:
            print("Brak danych do analizy")
            return
        
        cpu_values = [m["cpu_percent"] for m in self.metrics_history]
        mem_values = [m["memory_percent"] for m in self.metrics_history]
        
        print(f"Liczba pomiarów: {len(self.metrics_history)}")
        print(f"Anomalie wykryte: {anomaly_count}")
        print(f"\nCPU:")
        print(f"  Średnia: {sum(cpu_values)/len(cpu_values):.1f}%")
        print(f"  Min: {min(cpu_values):.1f}% | Max: {max(cpu_values):.1f}%")
        print(f"\nPamięć:")
        print(f"  Średnia: {sum(mem_values)/len(mem_values):.1f}%")
        print(f"  Min: {min(mem_values):.1f}% | Max: {max(mem_values):.1f}%")


def main():
    """Główna funkcja"""
    print("🤖 AIOps - Analiza Anomalii z Qwen2:8b\n")
    
    # Sprawdź dostępność Ollamy
    try:
        models = ollama.list()
        print(f"✅ Ollama dostępna")
        print(f"   Dostępne modele: {len(models['models'])}\n")
    except Exception as e:
        print(f"❌ Błąd: Nie można połączyć się z Ollama: {e}")
        print("   Upewnij się, że Ollama jest uruchomiona: ollama run qwen2:8b")
        return
    
    # Utwórz analizator
    analyzer = AnomalyAnalyzer(model="qwen3:8b")
    
    # Monitoruj przez 60 sekund z interwałem 10 sekund
    analyzer.monitor_continuous(duration_seconds=60, interval_seconds=10)


if __name__ == "__main__":
    main()
