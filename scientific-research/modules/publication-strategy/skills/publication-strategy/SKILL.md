---
name: publication-strategy
description: Módulo Publication Strategy — monta a estratégia de submissão com uma lista curta de periódicos compatíveis, comparados por aderência temática e metodológica, público, características editoriais, requisitos, custos, open access, prazos editoriais publicados, indexação e métricas (sem que métricas substituam a aderência), com NOT VERIFIED onde faltar fonte; ativa o Target Journal Mode após a escolha. Use para "estratégia de publicação", "em qual revista submeter primeiro", "ordem de submissão", "plano de publicação", "target journal".
argument-hint: "[research/] [--restricoes oa,apc-max,indexacao]"
---

# Publication Strategy

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

- Manuscrito concluído (`manuscript-review` feito) e candidatos avaliados; ou para coordenar
  todo o módulo a partir do zero (junto ao subagente `publication-strategist`).

## Quando NÃO usar

- Só checar formatação para um periódico já escolhido → `manuscript-compliance`.

## Inputs esperados

Perfil do manuscrito; candidatos; fit reports; due diligence; requisitos; restrições do autor
(orçamento de APC, exigência de OA, indexação exigida, prazo, idioma).

## Workflow do módulo

```
journal-search → journal-recent-content-analysis → journal-fit-analysis → journal-due-diligence
→ journal-requirements → [publication-strategy: comparação + escolha] → TARGET JOURNAL MODE
→ manuscript-compliance → submission-preparation / cover-letter → pre-submission-audit
→ submissão (pelo autor) → peer-review-response → publicação | resubmission-strategy
```

1. **Tabela comparativa** (`python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" compare research/publication/journals/*/fit.json`) com colunas:
   aderência temática · aderência metodológica · público · características editoriais · requisitos
   críticos · custos (APC) · open access · prazos (só se publicados pelo periódico) · indexação ·
   métricas (se relevantes, com fonte e ano) · alertas de due diligence · índice de aderência e cobertura.
   Qualquer célula sem fonte → `NOT VERIFIED`.
2. **Ordenação proposta** justificada por aderência e restrições do autor — métricas são critério
   secundário e declarado. Nenhuma probabilidade de aceitação, nenhuma "chance".
3. **Riscos de desk rejection** por candidato, baseados em evidência (escopo, tipo de artigo,
   requisitos não atendíveis, custo).
4. **Decisão do autor**. Após a escolha, ativar o **Target Journal Mode**:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" target set research/publication --journal <slug>
   ```
   Nesse modo, todas as recomendações editoriais seguem prioritariamente as regras desse periódico.
   **Limites do modo:** regras editoriais nunca justificam alteração ou omissão seletiva de
   resultados, fabricação de análise ou referência, manipulação de evidência ou exagero de conclusão.
   Desativar: `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" target clear research/publication`.
5. Salvar `research/publication/strategy.md` (template `publication-strategy.md`) e checar a
   linguagem: `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" lint research/publication/strategy.md`.

## Output esperado

Estratégia com lista curta (3–6), tabela comparativa, ordem sugerida com justificativa, riscos,
pendências `NOT VERIFIED`, próximos passos.

## Critérios de qualidade

- Ordem justificada por aderência verificável; métricas nunca como critério único.
- Sem probabilidades; datas de verificação visíveis.

## Situações de falha

- Informação editorial inacessível → estratégia marcada **preliminar** com itens `NOT VERIFIED`.
