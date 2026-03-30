# Contexto para Proxima Etapa

Este arquivo consolida o estado atual do projeto e as decisoes tomadas durante a conversa para facilitar retomada.

## 1) Objetivo do projeto (estado atual)

Projeto academico de classificacao textual supervisionada de boletins epidemiologicos de arboviroses (foco em dengue), com pipeline de:

1. coleta/importacao de PDFs;
2. extracao e limpeza de texto;
3. segmentacao em chunks;
4. preparacao de base para rotulagem e treino;
5. avaliacao de modelos de classificacao.

## 2) Fonte principal usada na Etapa 2

- COVISA/SMS-SP (boletins de arboviroses):
  <https://prefeitura.sp.gov.br/web/saude/w/vigilancia_em_saude/boletim_covisa/arboviroses>

Observacao institucional relevante (documentada): priorizar o boletim mais recente; boletins anteriores sao fotografias do momento da publicacao.

## 3) O que foi implementado em codigo

Arquivos em `src/`:

- `config.py`: paths padrao de dados e artefatos.
- `data_collection.py`: importa/copia PDFs para `data/raw/boletins/`.
- `preprocessing.py`: extrai texto (pdfplumber), limpa, tokeniza, chunkiza e gera EDA.
- `modeling.py`: treino supervisionado com TF-IDF + Naive Bayes + Regressao Logistica (quando houver labels).
- `evaluation.py`: calculo de metricas (acuracia, relatorio de classificacao, matriz de confusao).

Dependencias atualizadas em `requirements.txt`:
- `pdfplumber`
- `joblib`

## 4) Artefatos gerados na Etapa 2

Em `data/processed/`:

- `extracted_text/` (texto por documento)
- `chunks/` (texto por chunk)
- `chunks_dataset.csv`
- `eda_summary.md`
- `eda_summary.json`
- `labels.csv` (template)

Resumo EDA gerado:
- 11 PDFs
- 60 chunks
- chunking: `chunk_size=500`, `stride=200`, `min_fill_ratio=0.6`
- tokens por chunk: media 487.62, min 356, max 500
- vocabulario (apos filtragem): 440

## 5) Relatorios e LaTeX (estado atual)

- Etapa 1:
  - `reports/etapa-1/Etapa1.tex`
  - `reports/etapa-1/Etapa1.pdf`
- Etapa 2:
  - `reports/etapa-2/Etapa2.pdf` (mantido conforme ajuste do usuario)
  - `reports/etapa-2/Etapa2_A2_metodologia.tex` (atualizado com conteudo corrigido)
  - `reports/etapa-2/Etapa2_A2_metodologia_body.tex` (versao para inclusao/somatoria no Etapa1.tex)
  - `reports/etapa-2/Etapa2_A2_metodologia.md`

## 6) Documentacao fortalecida

READMEs e docs atualizados com foco academico:

- `README.md`
- `data/README.md`
- `notebooks/README.md`
- `reports/README.md`
- `docs/escopo-projeto.md`
- `docs/metadados.md`
- `docs/cronograma.md`
- `docs/fontes-dados.md`
- `docs/label_schema.md`

## 7) Decisoes importantes desta conversa

1. Manter fontes `.tex` dos relatorios no repositorio.
2. Manter tambem os PDFs finais das etapas em `reports/`.
3. Priorizar organizacao academica (documentacao clara e rastreavel).
4. Pipeline textual orientado a chunks (nao apenas documento inteiro) para melhorar modelagem supervisionada.

## 8) Proxima etapa recomendada (Etapa 3)

### 8.1 Rotulagem

Preencher `data/processed/labels.csv` com:

- `chunk_id`
- `label`

Categorias sugeridas:
- `cenario_epidemiologico`
- `prevencao_controle_vetorial`
- `orientacoes_clinicas_sintomas`
- `politicas_publicas_campanhas`
- `recomendacoes_operacionais`

### 8.2 Treino

Executar:

```bash
python3 -m src.modeling --labels-csv data/processed/labels.csv
```

Saida esperada:
- `data/processed/metrics.json`

### 8.3 Entregavel da Etapa 3

Consolidar no relatorio:
- desempenho por modelo (acuracia e metricas complementares),
- interpretacao dos erros (matriz de confusao),
- discussoes de limitacoes e proximos refinamentos.

## 9) Commits relevantes recentes

- `a81cc1a`: implementacao de pipeline da Etapa 2 + relatorios/artefatos.
- `40021c4`: reforco da documentacao (README/docs) com padrao academico.

## 10) Requisitos formais da Etapa 3 (A3)

Nesta etapa, a entrega deve incluir obrigatoriamente:

1. Metodo analitico definido na etapa anterior aplicado na base escolhida.
2. Medidas de acuracia usando os metodos definidos na etapa anterior.
3. Descricao dos resultados preliminares, com produto gerado e rascunho de modelo de negocios.
4. Esboco de storytelling.

## 11) Checklist para nota maxima (A3)

Use este checklist como guia interno de qualidade para aumentar chance de pontuacao maxima.

### 11.1 Aplicacao do metodo analitico

- [ ] Metodo aplicado de forma consistente com o corpus real (chunks rotulados).
- [ ] Explicitar pipeline usado no treino (TF-IDF, parametros, split estratificado).
- [ ] Comparar baseline e modelo principal de forma objetiva.
- [ ] Demonstrar entendimento tecnico (decisoes justificadas, sem contradicoes com Etapa 2).

### 11.2 Medidas de acuracia

- [ ] Definir acuracia formalmente e mostrar como foi calculada no teste.
- [ ] Incluir metricas complementares (precision, recall, F1, matriz de confusao).
- [ ] Justificar por que metricas macro sao relevantes em possivel desbalanceamento.
- [ ] Relacionar as metricas com qualidade pratica do modelo.

### 11.3 Resultados preliminares + produto + modelo de negocios

- [ ] Apresentar resultado quantitativo por modelo (tabela/figura no relatorio).
- [ ] Descrever um produto preliminar claro (ex.: classificador de trechos de boletim).
- [ ] Desenhar proposta de valor (quem usa, para que usa, qual ganho de tempo/decisao).
- [ ] Rascunhar modelo de negocios coerente (atores, entregavel, viabilidade inicial).

### 11.4 Storytelling

- [ ] Estruturar narrativa: problema -> dados -> metodo -> resultados -> implicacoes.
- [ ] Conectar visualizacoes aos achados (nao apenas listar metricas).
- [ ] Mostrar limites atuais e proxima iteracao da pesquisa.
- [ ] Garantir coerencia entre historia contada e evidencias tecnicas.

## 12) Estrutura recomendada para o relatorio da Etapa 3

1. Resumo executivo (objetivo da etapa e principais resultados).
2. Aplicacao do metodo na base (passo a passo reproducivel).
3. Resultados de desempenho (acuracia + metricas complementares).
4. Analise de erros e limitacoes.
5. Produto preliminar proposto.
6. Rascunho de modelo de negocios.
7. Esboco de storytelling.
8. Consideracoes finais e proximos passos.

