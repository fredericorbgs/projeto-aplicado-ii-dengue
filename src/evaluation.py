"""Modulo de avaliacao (Etapa 2).

Nesta etapa, a avaliacao e "metodologica": definimos quais metricas serao
calculadas (acuracia, precision, recall, F1 e matriz de confusao) e como
ela sera registrada em saidas versionaveis.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def compute_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    """Calcula metricas padrao para classificacao multiclasse."""
    y_true_arr = np.asarray(y_true, dtype=str)
    y_pred_arr = np.asarray(y_pred, dtype=str)

    acc = accuracy_score(y_true_arr, y_pred_arr)
    report = classification_report(y_true_arr, y_pred_arr, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true_arr, y_pred_arr).tolist()

    return {
        "accuracy": float(acc),
        "classification_report": report,
        "confusion_matrix": cm,
        "n_test_samples": int(len(y_true_arr)),
        "n_classes": int(len(sorted(set(y_true_arr)))),
    }


def evaluate_and_save(
    *,
    y_true: List[str],
    y_pred: List[str],
    output_json: Path,
) -> Dict[str, Any]:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    metrics = compute_metrics(y_true=y_true, y_pred=y_pred)
    output_json.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics


def evaluate_model() -> None:
    raise SystemExit(
        "Este modulo fornece funcoes auxiliares. "
        "Use `src/modeling.py` para treinar e calcular metrics quando houver labels.csv."
    )


if __name__ == "__main__":
    evaluate_model()
