"""Modulo de pre-processamento (Etapa 2).

Responsabilidades:
1) Extrair texto dos PDFs em `input_dir`
2) Limpar e salvar texto por documento em `data/processed/extracted_text/`
3) Tokenizar e gerar chunks (janela por tokens)
4) Salvar:
   - chunks em `data/processed/chunks/` (um .md por chunk)
   - dataset consolidado `data/processed/chunks_dataset.csv`
5) Gerar EDA (estatisticas) em `data/processed/eda_summary.*`
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd

from .config import (
    CHUNKS_DIR,
    CHUNKS_DATASET_CSV,
    EDA_SUMMARY_JSON,
    EDA_SUMMARY_MD,
    EXTRACTED_TEXT_DIR,
    INTERIM_DATA_DIR,
)


PDF_SUFFIXES = {".pdf"}


TOKEN_RE = re.compile(r"\b\w+\b", re.UNICODE)


def _doc_id_from_path(pdf_path: Path) -> str:
    # Ex: "BoletimArbo SE01_16jan26.pdf" -> "BoletimArbo_SE01_16jan26"
    return pdf_path.stem.replace(" ", "_")


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Une hifens de quebra de linha (ex: "transmissao-\ncontinua" -> "transmissaocontinua")
    text = re.sub(r"-\n", "", text)
    # Remove linhas que viram apenas numero (paginas, rodapes etc.)
    text = re.sub(r"(?m)^\s*\d+\s*$", "", text)
    # Normaliza whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    # Normaliza acentos para ASCII (ex.: "incidencia", "transmissao").
    # Isso deixa os artefatos no repo mais portaveis e simplifica comparacoes.
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text


def _tokenize(text: str) -> List[str]:
    # Tokeniza de forma simples para TF-IDF (mantem caracteres acentuados via \w+).
    tokens = [t.lower() for t in TOKEN_RE.findall(text)]
    # Remove tokens puramente numericos e muito curtos.
    tokens = [t for t in tokens if not t.isdigit() and len(t) > 2]
    return tokens


def _chunk_tokens(tokens: List[str], chunk_size: int, stride: int, min_fill_ratio: float) -> List[Tuple[int, int]]:
    """Retorna lista de (start_idx, end_idx) para chunks em janela por tokens."""
    if chunk_size <= 0:
        raise ValueError("chunk_size deve ser > 0")
    if stride <= 0:
        raise ValueError("stride deve ser > 0")
    if not (0 < min_fill_ratio <= 1):
        raise ValueError("min_fill_ratio deve estar em (0, 1]")

    min_len = max(1, int(chunk_size * min_fill_ratio))
    windows: List[Tuple[int, int]] = []

    for start in range(0, len(tokens), stride):
        end = start + chunk_size
        if start >= len(tokens):
            break
        window = tokens[start:end]
        if len(window) >= min_len:
            windows.append((start, start + len(window)))

        # otimiza: se ja passou do fim, nao tem janela adicional
        if end >= len(tokens):
            break

    # remove chunks vazios por seguranca
    windows = [(s, e) for (s, e) in windows if e > s]
    return windows


def _extract_text_from_pdf(pdfplumber_module, pdf_path: Path) -> Tuple[int, str]:
    with pdfplumber_module.open(str(pdf_path)) as pdf:
        pages = len(pdf.pages)
        raw = "".join((page.extract_text() or "") + "\n" for page in pdf.pages)
    cleaned = _clean_text(raw)
    return pages, cleaned


def extract_and_chunk(
    input_dir: Path,
    *,
    chunk_size: int = 500,
    stride: int = 200,
    min_fill_ratio: float = 0.6,
    force: bool = False,
) -> Dict[str, object]:
    """Extrai texto, gera chunks e salva dataset + EDA."""
    try:
        import pdfplumber  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "pdfplumber nao esta disponivel. Adicione-o em requirements.txt e instale o ambiente."
        ) from e

    input_dir = input_dir.expanduser().resolve()
    if not input_dir.exists():
        raise FileNotFoundError(f"Diretorio de entrada nao existe: {input_dir}")

    EXTRACTED_TEXT_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)

    pdf_paths = []
    for p in sorted(input_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() in PDF_SUFFIXES:
            pdf_paths.append(p)

    if not pdf_paths:
        raise FileNotFoundError(f"Nenhum PDF encontrado em: {input_dir}")

    docs_meta: List[Dict[str, object]] = []
    chunks_rows: List[Dict[str, object]] = []
    corpus_counter: Counter = Counter()

    for pdf_path in pdf_paths:
        doc_id = _doc_id_from_path(pdf_path)
        out_text_md = EXTRACTED_TEXT_DIR / f"{doc_id}.md"

        pages = None
        cleaned_text = None
        if out_text_md.exists() and not force:
            cleaned_text = out_text_md.read_text(encoding="utf-8", errors="ignore")
            # Inferimos pages aproximando; para EDA fina recomende reextrair com --force.
            pages = None
        else:
            pages, cleaned_text = _extract_text_from_pdf(pdfplumber, pdf_path)
            out_text_md.write_text(cleaned_text, encoding="utf-8")

        assert cleaned_text is not None
        tokens = _tokenize(cleaned_text)
        doc_word_count = len(tokens)

        docs_meta.append(
            {
                "doc_id": doc_id,
                # Mantemos apenas o nome do arquivo para evitar caminhos absolutos no repo.
                "pdf_filename": pdf_path.name,
                "pages": pages,
                "token_count": doc_word_count,
            }
        )

        windows = _chunk_tokens(tokens, chunk_size=chunk_size, stride=stride, min_fill_ratio=min_fill_ratio)
        for chunk_index, (start_i, end_i) in enumerate(windows):
            chunk_tokens = tokens[start_i:end_i]
            chunk_id = f"{doc_id}_chunk_{chunk_index:03d}"
            chunk_text = " ".join(chunk_tokens)
            corpus_counter.update(chunk_tokens)

            chunk_md_path = CHUNKS_DIR / f"{chunk_id}.md"
            if force or not chunk_md_path.exists():
                chunk_md_path.write_text(chunk_text, encoding="utf-8")

            chunks_rows.append(
                {
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "chunk_index": chunk_index,
                    "start_token": start_i,
                    "end_token": end_i,
                    "token_count": len(chunk_tokens),
                    "text_md_path": str(chunk_md_path),
                    "chunk_text": chunk_text,
                }
            )

    chunks_df = pd.DataFrame(chunks_rows).sort_values(["doc_id", "chunk_index"]).reset_index(drop=True)
    chunks_df.to_csv(CHUNKS_DATASET_CSV, index=False, encoding="utf-8")

    # --- EDA ---
    # Nota: labels ainda nao estao presentes nesta fase, entao EDA aqui e "descritiva" (texto e chunks).
    token_counts = chunks_df["token_count"].to_numpy()
    chunks_count = len(chunks_df)
    docs_count = len(docs_meta)

    vocab_size = len({t for t in corpus_counter.keys()})
    top_terms = corpus_counter.most_common(30)

    eda_summary = {
        # Mantemos apenas o nome da pasta para evitar paths absolutos no repo.
        "input_dir_name": input_dir.name,
        "n_docs": docs_count,
        "n_chunks": chunks_count,
        "chunking": {
            "chunk_size": chunk_size,
            "stride": stride,
            "min_fill_ratio": min_fill_ratio,
        },
        "token_stats": {
            "chunk_token_count": {
                "mean": float(token_counts.mean()) if len(token_counts) else None,
                "min": int(token_counts.min()) if len(token_counts) else None,
                "max": int(token_counts.max()) if len(token_counts) else None,
            },
            "vocab_size_terms": int(vocab_size),
        },
        "top_terms": [{"term": t, "count": c} for t, c in top_terms],
        "docs_meta": docs_meta,
        "generated_at": pd.Timestamp.utcnow().isoformat(),
    }

    EDA_SUMMARY_JSON.write_text(json.dumps(eda_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # Gera um MD simples (para ficar facil de incorporar no PDF final)
    lines: List[str] = []
    lines.append("# EDA - Etapa 2 (Base textual)\n")
    lines.append(f"- Entrada: `{input_dir.name}`")
    lines.append(f"- Documentos (PDF): `{docs_count}`")
    lines.append(f"- Chunks gerados: `{chunks_count}`")
    lines.append(
        f"- Chunking: `chunk_size={chunk_size}`, `stride={stride}`, `min_fill_ratio={min_fill_ratio}`"
    )
    lines.append("")
    lines.append("## Estatisticas de tamanho (tokens)")
    lines.append(
        f"- Tokens por chunk: mean={eda_summary['token_stats']['chunk_token_count']['mean']:.2f}, "
        f"min={eda_summary['token_stats']['chunk_token_count']['min']}, "
        f"max={eda_summary['token_stats']['chunk_token_count']['max']}"
    )
    lines.append(f"- Vocabulario (termos unicos observados): `{vocab_size}`")
    lines.append("")
    lines.append("## Termos mais frequentes (Top 30)")
    lines.append("| Termo | Ocorrencias |")
    lines.append("|---|---:|")
    for item in top_terms:
        lines.append(f"| {item[0]} | {item[1]} |")
    lines.append("")
    lines.append("## Metadados por documento")
    lines.append("| doc_id | pages | token_count |")
    lines.append("|---|---:|---:|")
    for d in docs_meta:
        pages_val = d["pages"] if d["pages"] is not None else "N/A"
        lines.append(f"| {d['doc_id']} | {pages_val} | {d['token_count']} |")

    EDA_SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")

    return eda_summary


def preprocess_data() -> None:
    parser = argparse.ArgumentParser(description="Extrai texto dos PDFs e gera dataset + EDA (Etapa 2).")
    parser.add_argument("--input-dir", required=True, help="Diretorio local contendo os PDFs dos boletins.")
    parser.add_argument("--chunk-size", type=int, default=500, help="Tamanho do chunk em numero de tokens.")
    parser.add_argument("--stride", type=int, default=200, help="Passo (stride) da janela em tokens.")
    parser.add_argument("--min-fill-ratio", type=float, default=0.6, help="Minimo de preenchimento do ultimo chunk.")
    parser.add_argument("--force", action="store_true", help="Reprocessa mesmo se ja existirem artefatos.")

    args = parser.parse_args()
    extract_and_chunk(
        Path(args.input_dir),
        chunk_size=args.chunk_size,
        stride=args.stride,
        min_fill_ratio=args.min_fill_ratio,
        force=args.force,
    )


if __name__ == "__main__":
    preprocess_data()
