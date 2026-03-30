# Etapa 2 (A2) - Definicao do Metodo Analitico (Metodologia)

## 1. Linguagem de programacao

O projeto sera desenvolvido em **Python** por ser uma linguagem apropriada para pipeline de ciencia de dados e processamento de texto. A decisao e justificada pelas seguintes razoes:

1. Ecossistema maduro para manipulacao de dados (ex.: `pandas` e `numpy`).
2. Suporte direto a tarefas de classificacao textual com `scikit-learn` (TF-IDF, modelos supervisionados e metodos de avaliacao).
3. Facilidade de implementacao reprodutivel (scripts de linha de comando, leitura/escrita de artefatos e configuracao por arquivos).
4. Facilidade para extracao de texto de PDFs (`pdfplumber`) e integracao com o pipeline de limpeza, tokenizacao e chunking.

## 2. Analise exploratoria (EDA) da base de dados

### 2.1 Fonte e formato da base

A base utilizada nesta etapa e composta por boletins epidemiologicos em **PDF** (11 documentos), armazenados localmente e processados pelo pipeline de extracao.

**Fonte dos boletins (coleta):** [Prefeitura de Sao Paulo - COVISA/SMS-SP - Boletim Covisa (Arboviroses Urbanas)](https://prefeitura.sp.gov.br/web/saude/w/vigilancia_em_saude/boletim_covisa/arboviroses).

Observacao do proprio site: recomenda-se utilizar o ultimo boletim publicado, pois boletins anteriores devem ser entendidos como uma fotografia do momento em que foram publicados (nao e recomendada comparacao direta entre anos diferentes com o boletim vigente).

### 2.2 Caracteristicas de tamanho e estrutura textual (estatisticas reais)

O texto extraido foi normalizado, tokenizado e segmentado em *chunks* para permitir rotulagem e modelagem supervisionada.

**Resultados observados na fase de EDA (artefatos em `data/processed/`):**

- Documentos (PDF): `11`
- Chunks gerados: `60`
- Chunking: `chunk_size=500`, `stride=200`, `min_fill_ratio=0.6`
- Tokens por chunk: media `487.62`, minimo `356`, maximo `500`
- Vocabulacao (termos unicos observados apos filtragem): `440`

### 2.3 Termos predominantes e peculiaridades

Os termos mais frequentes (Top 30) confirmam que o corpus e dominado por vocabulario epidemiologico e padroes recorrentes de boletins, como:

- `casos`, `confirmados`, `sinan`, `municipio`, `semana`, `sintomas`, `dengue`
- termos associados a outras arboviroses presentes no mesmo tipo de boletim, como `chikungunya`, alem de termos de contexto como `incidencia`, `transmissao`, `obitos` e `letalidade`.

**Implicacoes para a modelagem:**

1. A recorrencia de termos indica que TF-IDF sera util para diferenciar categorias tematicas a partir de conteudo textual.
2. A homogeneidade de formato (boletins com secoes similares) sugere que o problema pode se beneficiar de rotulagem por trechos (chunks), reduzindo mistura de temas em uma unica amostra.

### 2.4 Ruido e limpeza aplicada

Como boletins em PDF podem gerar ruido de extracao textual, foram aplicadas rotinas de limpeza antes do chunking:

- uniao de hifens de quebra de linha (`-\n`)
- remocao de linhas que viram apenas numeros (paginas/rodapes)
- normalizacao de whitespace (remocao de espacos duplicados e excesso de quebras)

## 3. Tratamento da base (preparacao e treinamento)

O pipeline de tratamento e implementado no modulo `src/preprocessing.py`. Ele gera artefatos de forma clara e organizada em:

- `data/processed/extracted_text/` (um arquivo .md por documento)
- `data/processed/chunks/` (um arquivo .md por chunk)
- `data/processed/chunks_dataset.csv` (dataset consolidado para modelagem)
- `data/processed/eda_summary.*` (resumo estatistico)

### 3.1 Extracao e normalizacao

1. **Extracao de texto**: cada PDF e processado por `pdfplumber` para extrair texto pagina a pagina.
2. **Limpeza**:
   - remocao de linhas numericas isoladas
   - remocao de quebras causadas por hifens de fim de linha
   - normalizacao de whitespace

### 3.2 Tokenizacao e filtragem

Para tornar o texto compativel com vetorizacao TF-IDF, o pipeline:

- tokeniza por expressoes regulares (`\\b\\w+\\b`)
- converte para minusculas
- remove tokens puramente numericos e tokens muito curtos (menor que 3 caracteres)

### 3.3 Segmentacao (chunking) para aprendizado supervisionado

Como os boletins podem conter multiplos assuntos, a segmentacao e feita por janelas de tokens:

- `chunk_size=500` tokens
- `stride=200` tokens
- `min_fill_ratio=0.6` para garantir que chunks finais nao fiquem vazios

Cada amostra de treinamento sera identificada por:

- `chunk_id = doc_id_chunk_XXX`

### 3.4 Dataset final para modelagem

O arquivo `data/processed/chunks_dataset.csv` contem (no minimo):

- `chunk_id`
- `doc_id`
- `chunk_index`
- `token_count`
- `chunk_text`
- `text_md_path`

Quando o grupo definir rotulos (labels) para categorias tematicas, sera criada a tabela `data/processed/labels.csv` com:

- `chunk_id`
- `label`

### 3.5 Vetorizacao e modelos

Conforme descrito na fase analitica:

1. **TF-IDF** como representacao numerica dos textos:
   - `ngram_range=(1,2)` para capturar unigramas e bigramas
   - `min_df=2` e `max_df=0.95` para reduzir termos muito raros e muito comuns
   - `max_features=20000` para limitar dimensionalidade

2. **Modelos supervisionados**:
   - Baseline: `MultinomialNB`
   - Modelo principal: `LogisticRegression` Multiclasse (`multi_class="multinomial"`, `solver="lbfgs"`, `max_iter=2000`)

### 3.6 Preparacao de treino/validacao/teste

Quando houver labels:

1. O dataset rotulado e dividido de forma estratificada (por classe) em treino, validacao e teste final.
2. A validacao e utilizada para orientar escolha/ajuste (por exemplo, parametros do vetor TF-IDF e do modelo, quando aplicavel).
3. O teste final permanece isolado para avaliacao objetiva.

## 4. Bases teoricas dos metodos

### 4.1 TF-IDF

TF-IDF mede a importancia de termos em relacao ao documento e ao corpus:

- **TF (Term Frequency)**: frequencia do termo no documento
- **IDF (Inverse Document Frequency)**: penaliza termos comuns no corpus

Intuicao: termos muito comuns em todo o conjunto carregam pouco poder discriminativo; termos que aparecem relativamente mais em alguns documentos tendem a ser mais informativos para diferenciar categorias.

### 4.2 Naive Bayes Multinomial (baseline)

O Naive Bayes Multinomial e um classificador probabilistico que modela a distribuicao de frequencias de termos. Ele usa a hipotese de independencia condicional entre termos dado a classe.

Apesar dessa hipotese ser simplificadora para linguagem natural, o metodo costuma funcionar bem como baseline em classificacao textual, especialmente quando os dados sao representados por frequencias (ou ponderacoes TF-IDF).

### 4.3 Regressao Logistica Multiclasse (modelo principal)

A Regressao Logistica Multiclasse generaliza o modelo de classificacao para varias classes, usando uma funcao de ativacao do tipo softmax. Assim, o modelo aprende pesos por classe e produz probabilidades:

- maior probabilidade indica a classe prevista

A principal vantagem e o bom equilibrio entre:

- desempenho em texto vetorizado com TF-IDF
- estabilidade do treino
- interpretabilidade relativa via pesos associados aos termos (em n-gramas)

## 5. Definicao e calculo da acuracia

### 5.1 Acuracia (multiclasse)

A acuracia sera calculada no conjunto de teste como:

> acuracia = numero de previsoes corretas / numero total de previsoes

Implementacao: `accuracy_score(y_true, y_pred)` (comparacao direta entre classe real e classe predita).

### 5.2 Avaliacao complementar (para lidar com desbalanceamento)

Embora a acuracia seja a principal medida exigida, a avaliacao sera complementada com:

- `precision`, `recall` e `f1-score` (idealmente com medias macro)
- matriz de confusao para inspecionar onde o modelo erra (quais classes sao mais confundidas)

Essas metricas permitem uma leitura mais robusta em cenarios com possivel desbalanceamento entre categorias tematicas.

### 5.3 Saidas de avaliacao

Quando houver labels:

- os resultados de performance serao gerados e persistidos em `data/processed/metrics.json` pela rotina de modelagem.

