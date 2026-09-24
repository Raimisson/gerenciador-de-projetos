---
name: submission-preparation
description: "Publication Strategy: checklist e arquivos de submissão (title page, versão cega, highlights, declarações) sem inventar dados de autores. Use para \"preparar submissão\", \"checklist de submissão\"."
argument-hint: "[periódico-alvo] [research/]"
---

# Submission Preparation

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

<!-- pubintegrity:start -->
## Regras de integridade editorial (módulo Publication Strategy)

1. **Nunca estimar probabilidade de aceitação** ("X% de chance de aceitação"): não há base publicada para calculá-la. *Journal fit* é avaliação de aderência com critérios e fontes explícitos — nunca probabilidade de publicação.
2. Informação de periódico é **mutável**: registrar URL oficial e data da consulta; reconsultar antes de submeter; sem fonte atual → `NOT VERIFIED`.
3. Não inferir aderência pelo nome do periódico: justificar com *aims & scope* e artigos publicados verificáveis.
4. Não declarar um periódico predatório só pela ausência de uma indexação específica: apresentar evidências e alertas objetivos.
5. Métricas (JIF, CiteScore, quartil) nunca substituem a aderência científica.
6. Regras editoriais **nunca** justificam alterar ou omitir resultados, fabricar análises ou referências, manipular evidência ou exagerar conclusões.
7. Não inventar informações de autores (afiliações, ORCID, financiamento, contribuições, conflitos de interesse).
8. Não afirmar que o trabalho é "o primeiro" ou "inédito" sem verificação documentada.

Referência completa: `${CLAUDE_PLUGIN_ROOT}/docs/publication-strategy.md`.
<!-- pubintegrity:end -->

## Quando usar

- Target Journal Mode ativo (ou periódico escolhido) e requisitos atuais registrados.

## Quando NÃO usar

- Ainda escolhendo periódico → `publication-strategy`.

## Inputs esperados

`target-journal.json`, `requirements.json`, relatório de compliance, manuscrito, ledger e dados
dos autores **fornecidos pelos autores**.

## Workflow

1. Gerar o checklist a partir das regras:
   `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" checklist research/publication/journals/<slug>/requirements.json --out research/publication/submission/<slug>/checklist.md`
   (template `submission-checklist.md`). Cada item: exigência, arquivo, status, fonte.
2. Preparar em `research/publication/submission/<slug>/`:
   | Arquivo | Regras |
   |---|---|
   | `manuscript.md` | versão ajustada às regras (sem mudanças científicas) |
   | `manuscript-blinded.md` | se double-blind: remover nomes, afiliações, agradecimentos identificáveis, autocitações identificáveis conforme o guia |
   | `title-page.md` | autores, afiliações, e-mails, ORCID — **só com dados fornecidos**; lacunas `[AUTORES: preencher]` |
   | `cover-letter.md` | via `cover-letter` |
   | `highlights.md` | derivados do texto, no limite de itens/caracteres; sem exagero causal |
   | `graphical-abstract` | orientar; nunca criar figura com dados não presentes no artigo |
   | `supplementary/` | material suplementar referenciado no texto |
   | `statements.md` | data/code availability, funding, competing interests, CRediT, ethics, consent, uso de IA, acknowledgments — **somente informação dos autores** |
   | `suggested-reviewers.md` | só se o periódico permitir; nomes indicados pelos autores; sem conflitos; nunca inventar contatos |
3. Conferir consistência entre arquivos (título, autores, contagens) e com o ledger (números dos
   highlights/abstract existem no texto e no ledger).
4. Rodar `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" lint` nos textos gerados (probabilidades, "primeiro a…", elogios genéricos).
5. Encaminhar para `pre-submission-audit`.

## Output esperado

Pasta de submissão + checklist com status por item + lista de lacunas que só os autores podem preencher.

## Critérios de qualidade

- Nenhum dado de autor inventado; nenhum número novo em highlights/abstract.
- Declaração de uso de IA redigida conforme a política do periódico, descrevendo o uso real.

## Situações de falha

- Requisito ambíguo → marcar `UNABLE_TO_VERIFY` e sugerir consulta ao editorial office.
