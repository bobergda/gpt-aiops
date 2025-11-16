# AIOps - Anomaly Analysis with Qwen3:8b

CPU and memory anomaly detection for local workloads using the Qwen3:8b LLM.

## Requirements

- Python 3.8+
- Ollama (installed and running)
- Qwen3:8b model available in Ollama

## Installation

### 1. Install Ollama

```bash
curl https://ollama.ai/install.sh | sh
```

### 2. Download the Qwen3:8b model

```bash
ollama pull qwen3:8b
```

### 3. Run the setup script

The `start.sh` script automatically:
- Verifies prerequisites
- Creates a virtual environment (venv)
- Installs Python dependencies
- Launches the app

```bash
./start.sh
```

## Running

### Option 1: Quick start (recommended)

```bash
./start.sh
```

The script will:
- Validate requirements
- Create the venv if needed
- Install dependencies
- Show the launcher menu

### Option 2: Manual run

```bash
# Activate the venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch
python quick_analysis.py
```

### Option 3: One-off quick analysis

```bash
./start.sh
# Choose option 1
```

### Option 4: Continuous monitoring (60 seconds)

```bash
./start.sh
# Choose option 2
```

## How It Works

1. **Metric collection** – Gather CPU, memory, and process info via `psutil`.
2. **Anomaly detection** – Flag readings when CPU > 80% or memory > 85%.
3. **LLM analysis** – Send metrics to the Qwen3:8b model for context.
4. **Explanation** – The model describes causes and recommended actions.

## Customization

### Adjust anomaly thresholds

```python
analyzer.monitor_continuous(duration_seconds=120, interval_seconds=5)
# and
analyzer.is_anomaly(metrics, cpu_threshold=90, mem_threshold=90)
```

### Switch models

```python
analyzer = AnomalyAnalyzer(model="mistral")  # or another Ollama model
```

## Project Structure

```
aiops/
├── anomaly_analyzer.py    # Continuous monitoring script
├── quick_analysis.py      # Single-measurement analysis
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Troubleshooting

### "Cannot connect to Ollama"
```bash
ollama run qwen3:8b
```

### Model not found
```bash
ollama pull qwen3:8b
ollama list
```

### Slow performance
- Lower `duration_seconds` or increase `interval_seconds`.
- Qwen3:8b should run smoothly on most modern machines.

## Using the Ollama API Directly

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:8b",
  "prompt": "What is a CPU anomaly?"
}'
```

## Notes

- Qwen3:8b offers improved language understanding and reasoning.
- Everything runs locally; nothing is sent outside your environment.
- Useful for AIOps and DevOps teams needing quick diagnostics.
