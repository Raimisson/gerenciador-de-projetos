---
name: regulatory-research
description: "Pesquisa regulatória: legislação, normas, AIR, ARR, consultas públicas, decisões e benchmark, separando norma vigente, proposta, interpretação e evidência. Use para \"regulação\", \"AIR\", \"ARR\", \"agência reguladora\"."
argument-hint: "[tema regulatório] [--jurisdicao BR|US|EU|...] [--setor energia|saneamento|...]"
---

# Regulatory Research

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

- Pergunta que envolve regras, reguladores, instrumentos de política ou avaliação de
  política/programa.
- Preparação de AIR/ARR, notas técnicas, artigos em regulação/políticas públicas.

## Quando NÃO usar

- Apenas literatura acadêmica sem componente normativo → `literature-search`.

## Inputs esperados

Tema; jurisdição(ões); setor; período; se é para AIR, ARR, artigo ou parecer.

## Classificação de fontes (obrigatória)

| Código | Categoria | Exemplos | Natureza |
|---|---|---|---|
| `LEG` | Legislação | lei, medida provisória, decreto | norma |
| `REG` | Regulamentação / ato normativo | resolução normativa, portaria, instrução | norma |
| `PROP` | Proposta normativa | minuta em consulta, projeto de lei | **não vigente** |
| `AIR` | Análise de Impacto Regulatório | relatório de AIR | análise *ex ante* |
| `ARR` | Avaliação de Resultado Regulatório | relatório de ARR | avaliação *ex post* |
| `CP` | Consulta/audiência pública | aviso, contribuições, relatório de análise das contribuições | processo |
| `NT` | Nota técnica | notas técnicas de agências/ministérios | análise/interpretação oficial |
| `DEC` | Decisão regulatória | despacho, acórdão, voto | aplicação da norma |
| `GUIDE` | Guideline / manual | guias de AIR, manuais de EM&V | orientação |
| `EVAL` | Relatório de avaliação de programa | avaliações independentes/oficiais | evidência (cinzenta) |
| `GOV` | Documento de governo | planos, relatórios de ministérios | varia |
| `DATA` | Dados oficiais | bases de agências, estatísticas | dados |
| `ACAD` | Literatura acadêmica | artigos revisados por pares | evidência |
| `GREY` | Literatura cinzenta | working papers, think tanks, org. internacionais | evidência não revisada |
| `INTL` | Benchmark internacional | normas/experiências de outras jurisdições | comparação |

E para cada afirmação, a **natureza**:

| Rótulo | Significado |
|---|---|
| **[NORMA VIGENTE]** | texto normativo em vigor na data da consulta (verificar revogações/alterações) |
| **[PROPOSTA]** | minuta, PL, proposta em consulta — não produz efeitos |
| **[INTERPRETAÇÃO]** | leitura do regulador, doutrina, parecer, ou do Claude ([INFERÊNCIA]) |
| **[EVIDÊNCIA EMPÍRICA]** | resultado observado/estimado (ARR, avaliação, artigo) |

## Regras específicas

1. **Vigência**: para `LEG`/`REG`, registrar número, data, ementa, link oficial
   (ex.: planalto.gov.br, gov.br/aneel, diário oficial), data de consulta e status
   (`em vigor` · `alterada` · `revogada` · `não verificada`). Nunca afirmar vigência sem
   checar a fonte oficial; se não conseguir, "Não foi possível verificar esta informação nas fontes consultadas."
2. **Citar o dispositivo exato** (art., §, inciso) — não a norma inteira.
3. **AIR ≠ evidência de impacto observado**: AIR é projeção *ex ante*; ARR/avaliações são *ex post*.
4. **Contribuições em consulta pública** representam posições de partes interessadas,
   não fatos.
5. **Benchmark internacional**: registrar desenho institucional de cada jurisdição antes de
   comparar resultados (validade externa).

## Workflow

1. Delimitar jurisdição, setor, instrumentos e período.
2. Buscar por categoria (sites oficiais primeiro; depois `grey-literature` e
   `literature-search`). Registrar tudo no search log com `database` = portal oficial.
3. Classificar cada documento (código + natureza) em `sources.json`
   (`regulatory.instrument_type`, `regulatory.status`, `regulatory.jurisdiction`).
4. Linha do tempo normativa (quando relevante): proposta → consulta → norma → alterações → ARR.
5. Extrair evidência empírica via `evidence-extraction`; dispositivos normativos via
   ledger com `design_class: normative`.
6. Entregar mapa regulatório + evidência + lacunas.

## Output esperado

- Tabela de fontes: código | documento | emissor | data | status/vigência | dispositivo | link | verificação.
- Linha do tempo normativa.
- Quadro "Norma vigente × Proposta × Interpretação × Evidência empírica".
- Benchmark internacional com desenho institucional.

## Critérios de qualidade

- Nenhuma proposta apresentada como norma vigente.
- Todo dispositivo citado com link oficial e data de consulta.
- Evidência empírica separada das justificativas regulatórias.

## Situações de falha

- Portal oficial inacessível → registrar; não confiar em reprodução não oficial sem sinalizar.
- Norma consolidada indisponível → alertar que alterações posteriores podem não estar refletidas.
