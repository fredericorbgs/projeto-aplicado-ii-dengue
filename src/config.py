"""Configuracoes gerais do projeto."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

# --- Etapa 2: Boletins e artefatos de texto ---
# Observacao: por padrao, o pipeline espera os PDFs em um subdiretorio
# de `data/raw/boletins`. Voces podem gerar os artefatos em `data/processed/`
# rodando os scripts com `--input-dir` apontando para a pasta local de downloads.
RAW_BOLETINS_DIR = RAW_DATA_DIR / "boletins"

# Texto extraido/limpo (um arquivo por boletim)
EXTRACTED_TEXT_DIR = PROCESSED_DATA_DIR / "extracted_text"

# Segmentos (chunks) do texto (um arquivo por chunk) + dataset consolidado
CHUNKS_DIR = PROCESSED_DATA_DIR / "chunks"
CHUNKS_DATASET_CSV = PROCESSED_DATA_DIR / "chunks_dataset.csv"

# Resumo de EDA (estatisticas + vocabulatio top-N)
EDA_SUMMARY_JSON = PROCESSED_DATA_DIR / "eda_summary.json"
EDA_SUMMARY_MD = PROCESSED_DATA_DIR / "eda_summary.md"

# --- Modelagem (quando houver rotulos) ---
LABELS_CSV = PROCESSED_DATA_DIR / "labels.csv"
MODELS_DIR = PROCESSED_DATA_DIR / "models"
METRICS_JSON = PROCESSED_DATA_DIR / "metrics.json"
