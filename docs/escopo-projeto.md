# Escopo do Projeto

## Tema

Classificacao e monitoramento textual de boletins epidemiologicos sobre dengue/arboviroses para apoio a analise academica em saude publica.

## Problema

Os boletins oficiais sao ricos em informacao, porem extensos e de atualizacao frequente, dificultando consolidacao analitica manual e comparacoes sistematicas.

## Objetivo geral

Desenvolver um pipeline reprodutivel para coleta/importacao, tratamento textual e preparacao de base para classificacao supervisionada.

## Objetivos especificos

1. Organizar corpus oficial com metadados padronizados.
2. Extrair e limpar texto de boletins em PDF.
3. Segmentar documentos em unidades de analise (chunks).
4. Definir categorias tematicas e estrutura de rotulagem.
5. Treinar e comparar modelos supervisionados.
6. Avaliar desempenho com acuracia e metricas complementares.

## Delimitacao

- Foco em boletins epidemiologicos oficiais de arboviroses.
- Escopo inicial de modelagem textual classica (TF-IDF + modelos lineares/probabilisticos).
- Nao inclui deploy de sistema em producao nesta disciplina.

## Entregaveis por etapa

- Etapa 1: escopo, premissas, cronograma e estrutura do projeto.
- Etapa 2: metodologia detalhada + EDA + pipeline de preprocessamento.
- Etapa 3: treino supervisionado e resultados preliminares.
- Etapa 4: consolidacao final e apresentacao.
