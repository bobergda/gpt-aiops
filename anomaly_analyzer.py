#!/usr/bin/env python3
"""
CPU/Memory anomaly analysis with Qwen3:8b
Collect system metrics and describe anomalies using an LLM
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
        Initialize the anomaly analyzer
        
        Args:
            model: Ollama model name (default: qwen3:8b)
        """
        self.model = model
        self.metrics_history: List[Dict] = []
        
    def collect_metrics(self) -> Dict:
        """Collect CPU and memory metrics"""
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
        Check whether metrics indicate an anomaly
        
        Args:
            metrics: Metrics dictionary
            cpu_threshold: CPU threshold (%)
            mem_threshold: Memory threshold (%)
        
        Returns:
            True if anomaly detected, False otherwise
        """
        return metrics["cpu_percent"] > cpu_threshold or metrics["memory_percent"] > mem_threshold
    
    def analyze_anomaly(self, metrics: Dict) -> Dict:
        """
        Analyze the anomaly with the LLM
        
        Args:
            metrics: Metrics dictionary
            
        Returns:
            Response returned by Ollama
        """
        prompt = f"""Analyze these system metrics and identify potential anomalies:

CPU: {metrics['cpu_percent']:.1f}%
Memory: {metrics['memory_percent']:.1f}% ({metrics['memory_used_gb']:.2f}GB / {metrics['memory_total_gb']:.2f}GB)
Process count: {metrics['processes_count']}
CPU cores: {metrics['cpu_count']}
Timestamp: {metrics['timestamp']}

The response should include:
1. Is this an anomaly? (Yes/No)
2. What are the causes of the high utilization?
3. What actions should be taken?
4. Could this cause performance issues?

Be concise and specific."""

        return ollama.generate(
            model=self.model,
            prompt=prompt,
            stream=False
        )

    @staticmethod
    def print_llm_stats(response: Dict):
        """Display token usage and timing statistics"""
        prompt_tokens = response.get("prompt_eval_count")
        completion_tokens = response.get("eval_count")
        total_duration = response.get("total_duration")
        eval_duration = response.get("eval_duration")
        load_duration = response.get("load_duration")

        print("\n📊 Analysis statistics:")
        if prompt_tokens is not None:
            print(f"  Prompt tokens: {prompt_tokens}")
        if completion_tokens is not None:
            print(f"  Completion tokens: {completion_tokens}")
        if prompt_tokens is not None and completion_tokens is not None:
            print(f"  Total tokens: {prompt_tokens + completion_tokens}")
        if total_duration:
            print(f"  Total time: {total_duration / 1e9:.2f}s")
        if eval_duration:
            print(f"  Generation time: {eval_duration / 1e9:.2f}s")
        if load_duration:
            print(f"  Model load time: {load_duration / 1e9:.2f}s")
    
    def monitor_continuous(self, duration_seconds: int = 60, interval_seconds: int = 10):
        """
        Continuous monitoring and anomaly analysis
        
        Args:
            duration_seconds: Duration of monitoring (seconds)
            interval_seconds: Metric collection interval (seconds)
        """
        print(f"🔍 Starting monitoring for {duration_seconds}s...")
        print(f"   Model: {self.model}")
        print(f"   Interval: {interval_seconds}s\n")
        
        start_time = time.time()
        anomaly_count = 0
        
        while time.time() - start_time < duration_seconds:
            # Gather metrics
            metrics = self.collect_metrics()
            self.metrics_history.append(metrics)
            
            print(f"[{metrics['timestamp']}]")
            print(f"  CPU: {metrics['cpu_percent']:.1f}% | Memory: {metrics['memory_percent']:.1f}%")
            
            # Check anomaly
            if self.is_anomaly(metrics):
                anomaly_count += 1
                print("  ⚠️  ANOMALY DETECTED!")
                print("\n📊 LLM analysis:")
                print("-" * 60)
                
                analysis_response = self.analyze_anomaly(metrics)
                print(analysis_response['response'])
                self.print_llm_stats(analysis_response)
                
                print("-" * 60 + "\n")
            else:
                print("  ✅ Normal status\n")
            
            time.sleep(interval_seconds)
        
        # Summary
        self.print_summary(anomaly_count)
    
    def print_summary(self, anomaly_count: int):
        """Display monitoring session summary"""
        print("\n" + "="*60)
        print("📈 SESSION SUMMARY")
        print("="*60)
        
        if not self.metrics_history:
            print("No data to analyze")
            return
        
        cpu_values = [m["cpu_percent"] for m in self.metrics_history]
        mem_values = [m["memory_percent"] for m in self.metrics_history]
        
        print(f"Measurements collected: {len(self.metrics_history)}")
        print(f"Anomalies detected: {anomaly_count}")
        print(f"\nCPU:")
        print(f"  Average: {sum(cpu_values)/len(cpu_values):.1f}%")
        print(f"  Min: {min(cpu_values):.1f}% | Max: {max(cpu_values):.1f}%")
        print(f"\nMemory:")
        print(f"  Average: {sum(mem_values)/len(mem_values):.1f}%")
        print(f"  Min: {min(mem_values):.1f}% | Max: {max(mem_values):.1f}%")


def main():
    """Main entry point"""
    print("🤖 AIOps - Anomaly Analysis with Qwen3:8b\n")
    
    # Check Ollama availability
    try:
        models = ollama.list()
        print(f"✅ Ollama available")
        print(f"   Models detected: {len(models['models'])}\n")
    except Exception as e:
        print(f"❌ Error: Cannot connect to Ollama: {e}")
        print("   Make sure Ollama is running: ollama run qwen3:8b")
        return
    
    # Create analyzer
    analyzer = AnomalyAnalyzer(model="qwen3:8b")
    
    # Monitor for 60 seconds with a 10-second interval
    analyzer.monitor_continuous(duration_seconds=60, interval_seconds=10)


if __name__ == "__main__":
    main()
