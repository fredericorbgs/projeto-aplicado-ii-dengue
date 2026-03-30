"""Modulo de coleta de dados (Etapa 1/2).

Nesta disciplina, voce pode:
- baixar boletins manualmente (ou via requests / endpoints) e
- colocar os PDFs em `data/raw/boletins/`

Este script automatiza o passo "carregar PDFs locais" para dentro da estrutura
do repo, garantindo reprodutibilidade do pipeline.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .config import RAW_BOLETINS_DIR


def collect_data(*, input_dir: Path, output_dir: Path = RAW_BOLETINS_DIR, force: bool = False) -> None:
    input_dir = input_dir.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()

    if not input_dir.exists():
        raise FileNotFoundError(f"Diretorio de entrada nao existe: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_paths = [p for p in input_dir.rglob("*.pdf") if p.is_file()]
    if not pdf_paths:
        raise FileNotFoundError(f"Nenhum PDF encontrado em: {input_dir}")

    for pdf in sorted(pdf_paths):
        dst = output_dir / pdf.name
        if dst.exists() and not force:
            continue
        shutil.copy2(str(pdf), str(dst))


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa PDFs locais para data/raw/boletins.")
    parser.add_argument("--input-dir", required=True, help="Diretorio local contendo os boletins (PDFs).")
    parser.add_argument("--output-dir", default=str(RAW_BOLETINS_DIR), help="Destino dentro do repo.")
    parser.add_argument("--force", action="store_true", help="Reescreve arquivos existentes.")
    args = parser.parse_args()

    collect_data(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir),
        force=args.force,
    )


if __name__ == "__main__":
    main()
