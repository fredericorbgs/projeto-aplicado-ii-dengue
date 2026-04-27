# Projeto Aplicado II - Dengue

Projeto academico da disciplina Projeto Aplicado II (UPM), com foco em analise textual e classificacao supervisionada de boletins epidemiologicos sobre dengue/arboviroses.

## Problema de pesquisa

Boletins epidemiologicos oficiais possuem alto valor informacional para vigilancia em saude, mas apresentam:

- volume textual elevado;
- atualizacao frequente;
- formatos heterogeneos para leitura analitica manual.

Este projeto organiza e prepara esse corpus para sustentar analise exploratoria e modelagem de classificacao textual.

## Objetivo geral

Construir um pipeline reprodutivel de ciencia de dados para:

1. coletar/importar boletins oficiais;
2. extrair e tratar o texto;
3. segmentar em unidades analiticas (chunks);
4. estruturar dataset para rotulagem e treinamento;
5. avaliar modelos de classificacao textual.

## Fonte de dados principal

- Boletins COVISA/SMS-SP (arboviroses): <https://prefeitura.sp.gov.br/web/saude/w/vigilancia_em_saude/boletim_covisa/arboviroses>

Detalhes adicionais em `docs/fontes-dados.md`.

## Estrutura do repositorio

```text
.
|-- data/
|   |-- raw/               # insumos originais (PDFs)
|   |-- interim/           # dados intermediarios
|   |-- processed/         # texto extraido, chunks, dataset, EDA
|   |-- external/          # bases externas complementares
|   `-- README.md
|-- docs/
|   |-- escopo-projeto.md
|   |-- fontes-dados.md
|   |-- metadados.md
|   |-- cronograma.md
|   `-- label_schema.md
|-- notebooks/
|   `-- README.md
|-- reports/
|   |-- etapa-1/
|   |-- etapa-2/
|   |-- etapa-3/
|   |-- etapa-4/
|   `-- README.md
|-- references/
|   `-- links-uteis.md
|-- src/
|   |-- config.py          # paths e convencoes
|   |-- data_collection.py # importacao de PDFs para data/raw
|   |-- preprocessing.py   # extracao + limpeza + chunking + EDA
|   |-- labeling.py        # pseudo-rotulagem inicial para etapa 3
|   |-- modeling.py        # TF-IDF + treino supervisionado
|   `-- evaluation.py      # metricas de classificacao
`-- requirements.txt
```

## Fluxo tecnico (etapas 2 e 3)

1. Importar PDFs para o projeto (`src/data_collection.py`).
2. Extrair e limpar texto (`src/preprocessing.py`).
3. Gerar chunks e dataset consolidado (`data/processed/chunks_dataset.csv`).
4. Gerar resumo de EDA (`data/processed/eda_summary.md` e `.json`).
5. Gerar rotulos iniciais em `data/processed/labels.csv` (`src/labeling.py`) e revisar manualmente quando necessario.
6. Treinar e avaliar modelos supervisionados (`src/modeling.py`).

## Como executar

### 1) Ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Importar PDFs para `data/raw/boletins`

```bash
python3 -m src.data_collection --input-dir "/caminho/para/boletins"
```

### 3) Preprocessar e gerar artefatos

```bash
python3 -m src.preprocessing --input-dir "/caminho/para/boletins" --force
```

### 4) Gerar rotulos iniciais (Etapa 3)

```bash
python3 -m src.labeling --dataset-csv data/processed/chunks_dataset.csv --labels-csv data/processed/labels.csv
```

### 5) Treinar modelos (apos gerar/revisar `labels.csv`)

```bash
python3 -m src.modeling --labels-csv data/processed/labels.csv
```

## Entregas academicas

- Etapa 1: definicao de escopo, problema, objetivos e cronograma.
- Etapa 2: definicao metodologica + pipeline implementado + EDA com dados reais.
- Etapa 3: treinamento, resultados preliminares e analise de desempenho.
- Etapa 4: consolidacao final, storytelling e apresentacao.

## Integrantes

- Ana Clara Silva de Souza
- Cid Wallace Araujo de Oliveira
- Eduardo Machado Silva
- Frederico Ripamonte Borges

## Status atual

- Etapa 1: concluida
- Etapa 2: concluida (documentacao + implementacao)
- Etapa 3: em andamento (metodo aplicado, metricas e relatorio preliminar)
