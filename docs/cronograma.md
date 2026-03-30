# Cronograma

## Planejamento por etapa

| Etapa | Objetivo principal | Status |
|---|---|---|
| 1 | Escopo, problema, metas e estrutura do repositorio | Concluida |
| 2 | Definicao metodologica, EDA e preprocessamento | Concluida |
| 3 | Rotulagem, treinamento e avaliacao preliminar | Em andamento |
| 4 | Consolidacao final, storytelling e apresentacao | Pendente |

## Marco tecnico atual (apos Etapa 2)

- Pipeline de extracao, limpeza e chunking implementado em `src/`.
- Artefatos de preprocessamento gerados em `data/processed/`.
- Relatorios em LaTeX/PDF versionados em `reports/`.

## Proximas atividades (Etapa 3)

1. Rotular `data/processed/labels.csv`.
2. Executar treino supervisionado e gerar `metrics.json`.
3. Comparar baseline vs modelo principal.
4. Preparar visualizacoes e discussao dos resultados.
