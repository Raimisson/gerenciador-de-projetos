---
name: systematic-review
description: Apoia revisão sistemática ou estruturada — protocolo, critérios de inclusão/exclusão, registro de triagem (título/resumo e texto completo) com motivos, deduplicação, fluxo inspirado em PRISMA 2020 e checklist de itens reportados, sem afirmar conformidade PRISMA sem verificar todos os requisitos. Use para "revisão sistemática", "scoping review", "triagem", "screening", "critérios de inclusão e exclusão", "fluxograma PRISMA".
argument-hint: "[pergunta] [--tipo sistematica|scoping|estruturada]"
---

# Systematic Review

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

- Revisão com protocolo explícito, busca reproduzível e triagem documentada.
- Scoping review ou revisão estruturada (mais leve) com critérios explícitos.

## Quando NÃO usar

- Revisão narrativa rápida → `literature-search` + `evidence-synthesis`.
- Meta-análise automática — não suportada na v0.1 (ver `evidence-synthesis`, portão de viabilidade).

## Inputs esperados

Pergunta (PICO/PECO/SPIDER adaptado), tipo de revisão, bases, período, idiomas,
número de revisores humanos disponíveis.

## Workflow

1. **Protocolo** (`research/protocol.md`, template
   `${CLAUDE_PLUGIN_ROOT}/templates/research-protocol.md`): objetivos, pergunta,
   critérios de elegibilidade, fontes, estratégia de busca, processo de triagem,
   extração, avaliação de risco de viés, síntese. Sugerir registro (PROSPERO, OSF) quando
   aplicável — o plugin **não** registra nada por conta própria.
2. **Critérios de inclusão/exclusão** (template
   `${CLAUDE_PLUGIN_ROOT}/templates/inclusion-exclusion-criteria.md`): cada critério
   operacional, com código curto (ex.: `EX-OUTCOME` = desfecho não mensurado).
3. **Busca**: acionar `literature-search`, `citation-chasing`, `grey-literature`.
4. **Deduplicação**: por DOI normalizado e título normalizado; registrar contagem removida
   (`srtool.py dedupe`).
5. **Triagem título/resumo** em `research/screening/screening.csv` com colunas:
   `record_id,source_id,title,year,doi,stage,decision,reason_code,reviewer,notes`.
   `decision ∈ {include, exclude, maybe}`; `stage ∈ {title_abstract, full_text}`.
   Claude pode **propor** decisões; em revisão sistemática, recomendar dupla triagem
   humana e registrar o revisor (`reviewer: claude-proposal` vs. nome humano).
6. **Texto completo**: registrar motivo de exclusão por código; registrar quando o texto
   completo não foi obtido (`reason_code: NO-FULLTEXT`).
7. **Fluxo**: preencher `screening` do search log e gerar o fluxo:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" prisma research/search/search-log.json`
   (gera diagrama textual/Markdown com as contagens registradas).
8. **Checklist PRISMA 2020**: marcar item a item como reportado / não reportado / não
   aplicável. Só usar a expressão "conforme PRISMA" se **todos** os itens aplicáveis
   estiverem reportados; caso contrário usar "fluxo inspirado em PRISMA".

## Output esperado

- `protocol.md`, `inclusion-exclusion-criteria.md`, `screening.csv`, search log com
  bloco `screening`, fluxo em Markdown, checklist de itens PRISMA com status.
- Relatório de revisão (template `${CLAUDE_PLUGIN_ROOT}/templates/review-report.md`).

## Critérios de qualidade

- Contagens do fluxo batem (identificados − duplicatas = triados; triados − excluídos = avaliados em texto completo, etc.). O `srtool.py prisma` checa a aritmética.
- Todo excluído em texto completo tem motivo codificado.
- Decisões propostas pelo Claude distinguidas das decisões humanas.

## Situações de falha

- Contagens inconsistentes → não "ajustar" números; apontar a divergência e pedir revisão.
- Texto completo inacessível → registrar; não decidir inclusão final só pelo abstract
  sem sinalizar.
