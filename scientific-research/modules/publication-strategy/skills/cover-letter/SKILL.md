---
name: cover-letter
description: "Publication Strategy: cover letter específica ao periódico, com contribuição e aderência ao escopo, sem elogios genéricos nem \"primeiro estudo\" sem verificação. Use para \"cover letter\", \"carta ao editor\"."
argument-hint: "[periódico-alvo] [research/]"
---

# Cover Letter

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

- Periódico escolhido; manuscrito final ou quase final.

## Quando NÃO usar

- Resposta a revisores → `peer-review-response`.

## Inputs esperados

Manuscrito; ledger; *aims & scope* oficial (trecho + URL + data); requisitos da cover letter
(`requirements.json`); artigos comparáveis verificados do periódico (`recent-content.json`);
nome do editor **apenas se verificado** no site; declarações exigidas na carta.

## Estrutura

1. Saudação (editor verificado ou "Dear Editor").
2. Submissão: título, tipo de artigo.
3. **Problema** (1–2 frases).
4. **Contribuição** e **principais resultados** — com os números exatamente como no manuscrito
   (e rastreáveis ao ledger); linguagem causal calibrada ao desenho.
5. **Relevância para os leitores** e **aderência ao aims & scope** — citando o trecho do escopo e,
   se útil, 1–2 artigos recentes do periódico com os quais o manuscrito dialoga (verificados).
6. **Originalidade** — descrever o que o manuscrito acrescenta **em relação à literatura revisada**;
   "primeiro/inédito/pioneiro" só se houver busca documentada que sustente, e mesmo assim com
   qualificação ("até onde a busca documentada em X alcançou…").
7. Declarações exigidas (originalidade, não submissão simultânea, conflitos, preprint) — confirmadas
   pelos autores.

## Proibições

- Elogios genéricos ("prestigious", "renowned", "leading journal", "prestigiosa revista").
- Probabilidades, promessas ou pressão sobre prazos.
- Números, referências ou dados de autores ausentes do manuscrito/ledger.

## Workflow

1. Rascunhar em `research/publication/submission/<slug>/cover-letter.md` (template `cover-letter.md`).
2. `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" lint research/publication/submission/<slug>/cover-letter.md` e `srtool.py scan` para números.
3. Mostrar ao autor os trechos que exigem confirmação.

## Output esperado

Carta de 1 página + lista de verificações pendentes.

## Critérios de qualidade

- Cada afirmação de resultado rastreável; aderência ao escopo com trecho citado.

## Situações de falha

- *Aims & scope* não verificado → carta marcada rascunho e parágrafo de aderência com `[NOT VERIFIED]`.
