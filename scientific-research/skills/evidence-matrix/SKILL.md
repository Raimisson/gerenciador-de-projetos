---
name: evidence-matrix
description: Constrói matriz comparativa de evidências entre estudos (versão compacta Study | Country | Period | Unit | N | Method | Treatment | Outcome | Estimate | SE/CI | Identification | Page | DOI, e versão detalhada com amostra, desenho institucional, métricas, robustez, limitações e validade externa) e exporta para Markdown, CSV e JSON a partir das fichas de extração. Use para "matriz de evidências", "evidence matrix", "tabela comparativa de estudos", "comparar estudos", "tabela de literatura".
argument-hint: "[--formato md|csv|json] [--detalhada]"
---

# Evidence Matrix

<!-- integrity:start -->
## Regras de integridade (não negociáveis)

1. Não inventar artigos, DOI, autores, periódicos, páginas, datas, URLs, números ou resultados. Memória do modelo não é fonte.
2. Informação não confirmada → "Não foi possível verificar esta informação nas fontes consultadas."
3. Sem evidência quantitativa → "Não foi encontrada evidência quantitativa que permita estimar este parâmetro."
4. Campo ausente → `NR — não reportado`; nunca inferir sem rotular como [INFERÊNCIA].
5. Separar **[FONTE]**, **[AUTORES]** e **[INFERÊNCIA]**.
6. Status: `VERIFIED` · `PARTIALLY_VERIFIED` · `UNVERIFIED` · `CONTRADICTED` · `NOT_REPORTED`.
7. Texto integral prevalece sobre abstract; registrar página/tabela/figura ou declarar que a página não é identificável.

Referência completa: `${CLAUDE_PLUGIN_ROOT}/docs/scientific-method.md`.
<!-- integrity:end -->

## Quando usar

- Há ≥2 fichas de extração e é preciso comparar métodos, amostras, contextos e resultados.
- Preparar tabela de revisão de literatura para o artigo.

## Quando NÃO usar

- Não há extração ainda → `evidence-extraction` primeiro. A matriz **não** é preenchida
  diretamente a partir de abstracts ou memória.

## Inputs esperados

`research/extraction/*.json` (preferível) e `research/sources/sources.json`.

## Formatos

**Compacta** (uma linha por estimativa):

| Study | Country | Period | Unit | N | Method | Treatment | Outcome | Estimate | SE/CI | Identification | Page | DOI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|

**Detalhada** (colunas adicionais): `peer_reviewed`, `access_level`, `data_source`,
`comparison`, `institutional_design`, `metric/unit`, `specification`, `p_value`,
`robustness`, `limitations`, `external_validity_notes`, `excerpt`, `verification_status`.

Templates: `${CLAUDE_PLUGIN_ROOT}/templates/evidence-matrix.md` e `evidence-matrix.csv`.

## Workflow

1. Validar as extrações (`srtool.py validate extraction ...`).
2. Gerar a matriz:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" matrix research/extraction --sources research/sources/sources.json --format md --out research/matrix/evidence-matrix.md
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" matrix research/extraction --sources research/sources/sources.json --format csv --detailed --out research/matrix/evidence-matrix-detailed.csv
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" matrix research/extraction --sources research/sources/sources.json --format json --out research/matrix/evidence-matrix.json
   ```
   Sem Bash: montar a tabela manualmente copiando **exatamente** os valores das fichas.
3. Comparação analítica (texto abaixo da matriz), com rótulos:
   - **Métodos e identificação**: quais estudos identificam efeito causal e sob quais premissas.
   - **Amostras e contextos**: países, períodos, unidades, desenho institucional.
   - **Métricas**: as unidades são comparáveis? (kWh vs. %; elasticidade vs. nível).
   - **Resultados**: direção e magnitude **como reportadas**; não padronizar sem registrar a conversão como [INFERÊNCIA].
   - **Robustez e limitações**.
   - **Validade externa** para o contexto do usuário [INFERÊNCIA].
4. Sinalizar células `NR` que impedem comparação.

## Output esperado

Matriz (MD/CSV/JSON) + texto comparativo com rótulos + lista de lacunas.

## Critérios de qualidade

- Cada célula é idêntica ao valor da ficha (o gerador garante isso).
- Estimativas de unidades diferentes nunca aparecem na mesma coluna sem a unidade.
- Linhas de estudos `abstract_only` e literatura cinzenta identificáveis.

## Situações de falha

- Fichas inválidas → corrigir a extração, não a matriz.
- Estudos incomparáveis → dizer isso explicitamente; não forçar uma "média".
