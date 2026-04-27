"""Modulo de modelagem (Etapas 2 e 3).

Este arquivo implementa o "plano de treinamento" descrito nos relatorios:
- Vetorizacao TF-IDF
- Baseline: Naive Bayes Multinomial
- Modelo principal: Regressao Logistica Multiclasse

Para executar de verdade, e necessario um CSV de rotulos.
Padrao esperado: `data/processed/labels.csv` com as colunas:
- `chunk_id`
- `label`
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from .config import CHUNKS_DATASET_CSV, LABELS_CSV, MODELS_DIR, METRICS_JSON


DEFAULT_LABEL_COLUMN = "label"
DEFAULT_CHUNK_ID_COLUMN = "chunk_id"


def _load_labeled_dataset(labels_csv: Path, dataset_csv: Path) -> pd.DataFrame:
    labels_df = pd.read_csv(labels_csv, encoding="utf-8")
    dataset_df = pd.read_csv(dataset_csv, encoding="utf-8")

    if DEFAULT_CHUNK_ID_COLUMN not in labels_df.columns:
        raise ValueError(f"labels.csv precisa conter coluna `{DEFAULT_CHUNK_ID_COLUMN}`")
    if DEFAULT_LABEL_COLUMN not in labels_df.columns:
        raise ValueError(f"labels.csv precisa conter coluna `{DEFAULT_LABEL_COLUMN}`")
    if "chunk_id" not in dataset_df.columns:
        raise ValueError("dataset_csv precisa conter coluna `chunk_id`")
    if "chunk_text" not in dataset_df.columns:
        raise ValueError("dataset_csv precisa conter coluna `chunk_text`")

    labeled = dataset_df.merge(
        labels_df[[DEFAULT_CHUNK_ID_COLUMN, DEFAULT_LABEL_COLUMN]],
        on=DEFAULT_CHUNK_ID_COLUMN,
        how="inner",
    )

    return labeled


def _build_models() -> Dict[str, Pipeline]:
    # Observacao: TF-IDF sozinho costuma lidar bem com textos em PT.
    # Usamos `ngram_range=(1,2)` para capturar expressoes curtas (melhora sem ficar complexo).
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        max_features=20000,
        stop_words=None,  # mantem tokens do dominio; stopwords podem remover sinal clinico.
    )

    nb = Pipeline(
        steps=[
            ("tfidf", vectorizer),
            ("clf", MultinomialNB(alpha=1.0)),
        ]
    )

    lr = Pipeline(
        steps=[
            ("tfidf", vectorizer),
            (
                "clf",
                LogisticRegression(max_iter=2000, solver="lbfgs"),
            ),
        ]
    )

    return {"naive_bayes_multinomial": nb, "logistic_regression_multiclass": lr}


def train_models(
    *,
    labels_csv: Path,
    dataset_csv: Path = CHUNKS_DATASET_CSV,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42,
    force_train: bool = True,
) -> Dict[str, object]:
    labeled = _load_labeled_dataset(labels_csv, dataset_csv)
    if labeled.empty:
        raise ValueError("Dataset rotulado ficou vazio. Verifique se labels.csv tem chunk_ids existentes.")

    X = labeled["chunk_text"].astype(str)
    y = labeled[DEFAULT_LABEL_COLUMN].astype(str)

    # Split 1: treino vs (val+test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=(test_size + val_size),
        stratify=y,
        random_state=random_state,
    )

    # Split 2: val vs test (a proporcao e relativa ao tamanho temp)
    val_ratio_relative = val_size / (val_size + test_size)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=(1 - val_ratio_relative),
        stratify=y_temp,
        random_state=random_state,
    )

    models = _build_models()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_JSON.parent.mkdir(parents=True, exist_ok=True)

    class_order: List[str] = sorted(set(y_test))

    metrics_summary: Dict[str, object] = {
        "dataset_summary": {
            "n_total_samples": int(len(labeled)),
            "n_train_samples": int(len(X_train)),
            "n_val_samples": int(len(X_val)),
            "n_test_samples": int(len(X_test)),
            "class_order_test": class_order,
        }
    }

    for name, model in models.items():
        # Observacao: por enquanto nao persistimos os modelos (etapa 3 provavelmente exige).
        # Se desejar persistir, podemos adicionar joblib e salvar aqui.
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        metrics_summary[name] = {
            "accuracy": float(acc),
            "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0),
            "confusion_matrix": confusion_matrix(y_test, y_pred, labels=class_order).tolist(),
            "confusion_matrix_labels": class_order,
            "n_test_samples": int(len(y_test)),
            "n_classes": int(len(sorted(set(y_test)))),
        }

    METRICS_JSON.write_text(json.dumps(metrics_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics_summary


def train_model() -> None:
    parser = argparse.ArgumentParser(description="Treina modelos (Etapa 2) quando labels.csv estiver disponivel.")
    parser.add_argument("--labels-csv", default=str(LABELS_CSV), help="Caminho do CSV de rotulos.")
    parser.add_argument("--dataset-csv", default=str(CHUNKS_DATASET_CSV), help="Caminho do dataset de chunks.")
    parser.add_argument("--test-size", type=float, default=0.15, help="Proporcao do teste final.")
    parser.add_argument("--val-size", type=float, default=0.15, help="Proporcao da validacao.")
    parser.add_argument("--random-state", type=int, default=42, help="Seed do split estratificado.")
    args = parser.parse_args()

    metrics = train_models(
        labels_csv=Path(args.labels_csv),
        dataset_csv=Path(args.dataset_csv),
        test_size=args.test_size,
        val_size=args.val_size,
        random_state=args.random_state,
    )
    print("Treinamento concluido. Metricas gravadas em:", METRICS_JSON)
    print(json.dumps(metrics, ensure_ascii=False, indent=2)[:2000])


if __name__ == "__main__":
    train_model()
