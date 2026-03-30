# Rotulagem (Labels) - Etapa 2

Este arquivo descreve o formato esperado para o CSV de rotulos utilizado na modelagem.

## Arquivo esperado

`data/processed/labels.csv`

## Schema (colunas)

- `chunk_id`: identificador do chunk, no formato `doc_id_chunk_XXX`
- `label`: categoria tematica atribuida ao chunk

## Categorias (sugestao inicial)

Se o grupo mantiver as categorias propostas na Etapa 2 anterior, os labels podem ser:

1. `cenario_epidemiologico`
2. `prevencao_controle_vetorial`
3. `orientacoes_clinicas_sintomas`
4. `politicas_publicas_campanhas`
5. `recomendacoes_operacionais`

## Observacao importante

O treinamento so funciona quando existem linhas em `labels.csv` para `chunk_id` presentes em:

`data/processed/chunks_dataset.csv`

