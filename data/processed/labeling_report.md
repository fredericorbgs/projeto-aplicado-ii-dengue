# Relatorio de Rotulagem (Pseudo-labeling)

- Metodo: TF-IDF + KMeans (5 clusters) + mapeamento para labels tematicos
- Chunks processados: `60`
- Random state: `42`

## Mapeamento cluster -> label
| Cluster | Label | Top termos (amostra) |
|---:|---|---|
| 0 | prevencao_controle_vetorial | partir, online partir, sisden ate, sisden, por, ate sinan, inc, vila, incidencia, inc inc |
| 1 | politicas_publicas_campanhas | cca, vila, autoctones, cci, chikungunya, cca cci, confirmados autoctones, cci cca, cca cca, importados |
| 2 | cenario_epidemiologico | por, partir, sisden ate, online partir, sisden, ate sinan, boletim, urbanas, arboviroses urbanas, arboviroses |
| 3 | orientacoes_clinicas_sintomas | vila, cca, autoctones, zika, confirmados autoctones, cidade, pelo, doenca, amaro, santo amaro |
| 4 | recomendacoes_operacionais | vila, cca, inc, inc inc, por, cci, autoctones, chikungunya, incidencia, importados |

## Distribuicao de labels
| Label | Quantidade |
|---|---:|
| cenario_epidemiologico | 11 |
| orientacoes_clinicas_sintomas | 13 |
| politicas_publicas_campanhas | 17 |
| prevencao_controle_vetorial | 11 |
| recomendacoes_operacionais | 8 |