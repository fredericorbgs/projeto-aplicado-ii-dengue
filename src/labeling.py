"""Pseudo-rotulagem para Etapa 3.

Estratégia:
1) Vetoriza `chunk_text` com TF-IDF
2) Agrupa em 5 clusters (KMeans)
3) Extrai termos representativos de cada cluster
4) Faz mapeamento cluster -> label tematico por similaridade com lexicos de dominio
5) Salva `data/processed/labels.csv` e relatorio de rotulagem
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import CHUNKS_DATASET_CSV, LABELS_CSV, PROCESSED_DATA_DIR


LABELS = [
    "cenario_epidemiologico",
    "prevencao_controle_vetorial",
    "orientacoes_clinicas_sintomas",
    "politicas_publicas_campanhas",
    "recomendacoes_operacionais",
]


LABEL_LEXICON: Dict[str, List[str]] = {
    "cenario_epidemiologico": [
        "casos",
        "incidencia",
        "epidemiologica",
        "semana",
        "confirmados",
        "notificados",
        "serie",
        "historica",
        "obitos",
        "letalidade",
    ],
    "prevencao_controle_vetorial": [
        "aedes",
        "vetor",
        "mosquito",
        "controle",
        "combate",
        "criador",
        "eliminacao",
        "proliferacao",
        "prevencao",
    ],
    "orientacoes_clinicas_sintomas": [
        "sintomas",
        "doenca",
        "clinica",
        "atendimento",
        "diagnostico",
        "conduta",
        "chikungunya",
        "zika",
        "dengue",
    ],
    "politicas_publicas_campanhas": [
        "secretaria",
        "ministerio",
        "campanha",
        "covisa",
        "politica",
        "programa",
        "mobilizacao",
        "institucional",
    ],
    "recomendacoes_operacionais": [
        "uvis",
        "coordenadoria",
        "notificacao",
        "investigacao",
        "protocolo",
        "operacional",
        "procedimento",
        "fluxo",
        "residencia",
    ],
}


def _cluster_top_terms(vectorizer: TfidfVectorizer, km: KMeans, top_n: int = 25) -> Dict[int, List[str]]:
    terms = np.array(vectorizer.get_feature_names_out())
    out: Dict[int, List[str]] = {}
    for cluster_id, center in enumerate(km.cluster_centers_):
        top_idx = np.argsort(center)[::-1][:top_n]
        out[cluster_id] = terms[top_idx].tolist()
    return out


def _score_cluster_for_label(cluster_terms: List[str], label: str) -> float:
    lex = set(LABEL_LEXICON[label])
    score = 0.0
    for rank, term in enumerate(cluster_terms):
        if term in lex:
            # peso maior para termos de topo
            score += 1.0 / (rank + 1)
    return score


def _best_cluster_label_mapping(cluster_terms: Dict[int, List[str]]) -> Dict[int, str]:
    cluster_ids = sorted(cluster_terms.keys())
    best_score = -1.0
    best_map: Dict[int, str] = {}

    # Permutacao exata (5! = 120), pequeno e deterministico
    for perm in itertools.permutations(LABELS, len(cluster_ids)):
        cur = 0.0
        for cid, lbl in zip(cluster_ids, perm):
            cur += _score_cluster_for_label(cluster_terms[cid], lbl)
        if cur > best_score:
            best_score = cur
            best_map = {cid: lbl for cid, lbl in zip(cluster_ids, perm)}

    return best_map


def generate_labels(
    *,
    dataset_csv: Path = CHUNKS_DATASET_CSV,
    labels_csv: Path = LABELS_CSV,
    random_state: int = 42,
) -> Dict[str, object]:
    df = pd.read_csv(dataset_csv, encoding="utf-8")
    if "chunk_id" not in df.columns or "chunk_text" not in df.columns:
        raise ValueError("chunks_dataset.csv deve conter `chunk_id` e `chunk_text`.")

    texts = df["chunk_text"].astype(str).tolist()

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        max_features=20000,
    )
    X = vectorizer.fit_transform(texts)

    km = KMeans(n_clusters=5, random_state=random_state, n_init=20)
    clusters = km.fit_predict(X)

    terms = _cluster_top_terms(vectorizer, km, top_n=25)
    cluster_to_label = _best_cluster_label_mapping(terms)

    labels = [cluster_to_label[int(c)] for c in clusters]
    out_df = pd.DataFrame({"chunk_id": df["chunk_id"], "label": labels})
    labels_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(labels_csv, index=False, encoding="utf-8")

    # Artefatos de auditoria da pseudo-rotulagem
    cluster_counts = pd.Series(clusters).value_counts().sort_index().to_dict()
    label_counts = out_df["label"].value_counts().to_dict()
    audit = {
        "n_chunks": int(len(df)),
        "cluster_counts": {str(k): int(v) for k, v in cluster_counts.items()},
        "cluster_top_terms": {str(k): v for k, v in terms.items()},
        "cluster_to_label": {str(k): v for k, v in cluster_to_label.items()},
        "label_counts": {k: int(v) for k, v in label_counts.items()},
        "random_state": random_state,
    }

    report_json = PROCESSED_DATA_DIR / "labeling_report.json"
    report_md = PROCESSED_DATA_DIR / "labeling_report.md"
    report_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Relatorio de Rotulagem (Pseudo-labeling)\n")
    lines.append("- Metodo: TF-IDF + KMeans (5 clusters) + mapeamento para labels tematicos")
    lines.append(f"- Chunks processados: `{audit['n_chunks']}`")
    lines.append(f"- Random state: `{random_state}`")
    lines.append("")
    lines.append("## Mapeamento cluster -> label")
    lines.append("| Cluster | Label | Top termos (amostra) |")
    lines.append("|---:|---|---|")
    for cid in sorted(cluster_to_label.keys()):
        sample_terms = ", ".join(terms[cid][:10])
        lines.append(f"| {cid} | {cluster_to_label[cid]} | {sample_terms} |")
    lines.append("")
    lines.append("## Distribuicao de labels")
    lines.append("| Label | Quantidade |")
    lines.append("|---|---:|")
    for lbl, cnt in sorted(label_counts.items(), key=lambda kv: kv[0]):
        lines.append(f"| {lbl} | {cnt} |")
    report_md.write_text("\n".join(lines), encoding="utf-8")

    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera labels iniciais por pseudo-rotulagem.")
    parser.add_argument("--dataset-csv", default=str(CHUNKS_DATASET_CSV), help="CSV de chunks.")
    parser.add_argument("--labels-csv", default=str(LABELS_CSV), help="Saida labels.csv.")
    parser.add_argument("--random-state", type=int, default=42, help="Seed para KMeans.")
    args = parser.parse_args()

    audit = generate_labels(
        dataset_csv=Path(args.dataset_csv),
        labels_csv=Path(args.labels_csv),
        random_state=args.random_state,
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

