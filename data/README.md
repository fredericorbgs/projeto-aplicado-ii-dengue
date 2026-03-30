# Dados

Este diretorio centraliza os insumos, dados intermediarios e artefatos processados do projeto.

## Estrutura

- `raw/`: dados brutos sem alteracao (ex.: PDFs originais).
- `interim/`: saidas intermediarias do pipeline.
- `processed/`: artefatos prontos para analise/modelagem.
- `external/`: dados complementares de fontes externas.

## Convencoes de uso

1. Nao editar manualmente arquivos em `raw/`.
2. Preferir geracao automatica dos artefatos via scripts em `src/`.
3. Registrar no commit a relacao entre dado gerado e script/parametros usados.

## Artefatos esperados em `processed/`

- `extracted_text/`: texto limpo por documento.
- `chunks/`: unidades de texto para rotulagem/modelagem.
- `chunks_dataset.csv`: base consolidada para treino.
- `eda_summary.md` e `eda_summary.json`: resumo da EDA.
- `labels.csv`: rotulos por `chunk_id` (preenchimento manual/supervisionado).
- `metrics.json`: resultado de avaliacao de modelos (apos treino).
