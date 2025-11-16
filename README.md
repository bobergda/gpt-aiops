# AIOps - Analiza Anomalii z Qwen3:8b

Analiza anomalii CPU/Memory w aplikacjach przy pomocy lokalnego modelu LLM (Qwen3:8b).

## Wymagania

- Python 3.8+
- Ollama (zainstalowana i uruchomiona)
- Model Qwen3:8b w Ollama

## Instalacja

### 1. Zainstaluj Ollama

```bash
curl https://ollama.ai/install.sh | sh
```

### 2. Pobierz model Qwen3:8b

```bash
ollama pull qwen3:8b
```

### 3. Uruchom skrypt instalacyjny

Skrypt `start.sh` automatycznie:
- Sprawdzi wymagania
- Utworzy wirtualne środowisko (venv)
- Zainstaluje zależności Pythona
- Uruchomi aplikację

```bash
./start.sh
```

## Uruchomienie

### Opcja 1: Szybki start (REKOMENDOWANY)

```bash
./start.sh
```

Skrypt automatycznie:
- Sprawdzi wszystkie wymagania
- Utworzy venv (jeśli nie istnieje)
- Zainstaluje zależności
- Wyświetli menu wyboru

### Opcja 2: Manualne uruchomienie

```bash
# Aktywuj venv
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom
python quick_analysis.py
```

### Opcja 3: Szybka analiza (jeden pomiar)

```bash
./start.sh
# Wybierz opcję 1
```

### Opcja 4: Ciągłe monitorowanie (60 sekund)

```bash
./start.sh
# Wybierz opcję 2
```

## Jak to działa

1. **Zbieranie metryk** - Pobiera CPU, pamięć, procesy itp. za pomocą `psutil`
2. **Detekcja anomalii** - Sprawdza czy CPU > 80% lub pamięć > 85%
3. **Analiza LLM** - Wysyła metryki do modelu Qwen2:8b
4. **Opis anomalii** - Model zwraca tekstowy opis przyczyn i rekomendacji

## Personalizacja

### Zmień progi anomalii

```python
analyzer.monitor_continuous(duration_seconds=120, interval_seconds=5)
# oraz
analyzer.is_anomaly(metrics, cpu_threshold=90, mem_threshold=90)
```

### Zmień model

```python
analyzer = AnomalyAnalyzer(model="mistral")  # lub inny model
```

## Struktura projektu

```
aiops/
├── anomaly_analyzer.py    # Główny skrypt monitorowania
├── quick_analysis.py       # Szybka analiza
├── requirements.txt        # Zależności
└── README.md              # Ten plik
```

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# 2. Upewnij się, że Ollama działa z Qwen3:8b
ollama run qwen3:8b
```

### Model nie znaleziony
```bash
# Pobierz model:
ollama pull qwen2:8b

# Lista dostępnych modeli:
ollama list
```

### Wolne działanie
- Zmniejsz `duration_seconds` lub zwiększ `interval_seconds`
- Qwen3:8b powinien być szybki na większości maszyn

## API Ollama

Jeśli chcesz używać Ollama jako API bez tego skryptu:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2:8b",
  "prompt": "Czym jest anomalia CPU?"
}'
```

## Notatki

- Qwen3:8b to nowy model z ulepszoną obsługą języka i rozumowaniem
- Model działa lokalnie, brak wysyłania danych na zewnątrz
- Idealne dla działów AIOps / DevOps
