# Metadados

Este documento define o dicionario minimo de metadados para rastreabilidade dos documentos e chunks.

## Nivel documento (boletim)

| Campo | Tipo | Descricao |
|---|---|---|
| `doc_id` | string | Identificador interno derivado do nome do PDF |
| `pdf_filename` | string | Nome original do arquivo PDF |
| `pages` | inteiro | Quantidade de paginas extraidas |
| `token_count` | inteiro | Quantidade de tokens apos limpeza |
| `source_url` | string | URL da fonte oficial (quando aplicavel) |
| `collection_date` | data | Data de coleta/importacao do arquivo |

## Nivel chunk (unidade de modelagem)

| Campo | Tipo | Descricao |
|---|---|---|
| `chunk_id` | string | Identificador da unidade (`doc_id_chunk_XXX`) |
| `doc_id` | string | Chave de relacionamento com documento |
| `chunk_index` | inteiro | Ordem do chunk dentro do documento |
| `start_token` | inteiro | Posicao inicial da janela |
| `end_token` | inteiro | Posicao final da janela |
| `token_count` | inteiro | Tamanho do chunk em tokens |
| `chunk_text` | string | Conteudo textual do chunk |
| `text_md_path` | string | Caminho do arquivo `.md` do chunk |
| `label` | string | Categoria tematica (quando rotulado) |

## Regras de qualidade

1. `doc_id` e `chunk_id` devem ser unicos.
2. `chunk_id` deve existir em `chunks_dataset.csv` para ser rotulado.
3. Nao remover metadados de origem ao atualizar o corpus.
4. Toda mudanca de schema deve ser registrada em commit com justificativa.
