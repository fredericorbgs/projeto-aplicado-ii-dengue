# Fontes de Dados

## Fonte institucional principal
- Ministerio da Saude

## Outras fontes potenciais
- DATASUS
- IBGE
- INMET

## Fonte dos boletins usados no A2 (Etapa 2)

Boletins epidemiologicos (arboviroses urbanas) coletados em:
https://prefeitura.sp.gov.br/web/saude/w/vigilancia_em_saude/boletim_covisa/arboviroses

Observacao do proprio site: recomenda-se utilizar o ultimo boletim publicado, e boletins anteriores devem ser entendidos como uma fotografia do momento em que foram publicados (nao e recomendada comparacao direta entre anos diferentes com o boletim vigente).

## Estrategia de coleta

1. Acesso ao portal oficial da COVISA.
2. Download dos PDFs da serie vigente.
3. Importacao para `data/raw/boletins/`.
4. Processamento via `src/preprocessing.py`.

## Formato e periodicidade observada

- Formato principal: PDF.
- Atualizacao: semanal (boletins urbanos), conforme publicacao institucional.

> Atualizar este documento com links, formatos, periodicidade e estrategia de coleta.
