---
name: journal-fit-analysis
description: Módulo Publication Strategy — avalia em detalhe a aderência (journal fit) entre o manuscrito e cada periódico candidato em sete dimensões (Topic, Method, Contribution, Empirical, Audience, Recent Publication e Article-Type Fit), com justificativas verificáveis, fontes e data, e um índice de aderência transparente que NÃO é probabilidade de aceitação. Use para "journal fit", "esse periódico combina com meu artigo?", "comparar revistas", "aderência ao escopo".
argument-hint: "[periódico ou candidates.json] [--manuscrito research/]"
---

# Journal Fit Analysis

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

- Há candidatos (de `journal-search` ou do usuário) e é preciso decidir entre eles com critérios explícitos.

## Quando NÃO usar

- Verificar legitimidade do periódico → `journal-due-diligence`.
- Conferir regras de formatação → `journal-requirements` / `manuscript-compliance`.

## Inputs esperados

Perfil do manuscrito; para cada periódico: *aims & scope* oficial (URL + data), resultado de
`journal-recent-content-analysis` (artigos comparáveis), tipos de artigo aceitos.

## As sete dimensões

| Dimensão | Pergunta | Evidência exigida |
|---|---|---|
| **Topic Fit** | O periódico publica sobre o problema estudado? | trecho do *aims & scope* + artigos sobre o tema |
| **Method Fit** | Publica estudos com metodologia semelhante? | artigos recentes com método comparável (DOI) |
| **Contribution Fit** | O tipo de contribuição (empírica, teórica, política, metodológica) é o que o periódico publica? | *aims & scope* + perfil dos artigos |
| **Empirical Fit** | Tipo de dado, jurisdição e unidade de análise têm precedentes? | artigos com dados/jurisdição/unidade semelhantes |
| **Audience Fit** | Os leitores são o público adequado para os resultados? | descrição de público no site; perfil de autores/artigos |
| **Recent Publication Fit** | Há artigos semelhantes nos últimos 3–5 anos? | tabela de `journal-recent-content-analysis` |
| **Article-Type Fit** | O periódico aceita o tipo de manuscrito produzido? | lista oficial de tipos de artigo |

Classificação de cada dimensão: `STRONG` · `MODERATE` · `WEAK` · `INSUFFICIENT_EVIDENCE`
— cada uma com justificativa e **lista de evidências** (URL/DOI + data). Sem evidência verificável,
a dimensão é `INSUFFICIENT_EVIDENCE`, nunca "presumida".

## Índice de aderência (transparente)

`python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" fit-report research/publication/journals/<slug>/fit.json` calcula o **Journal Fit Index**:
média ponderada (STRONG=2, MODERATE=1, WEAK=0) das dimensões com evidência, reescalada para 0–100,
com a **cobertura** (dimensões avaliadas/7) sempre ao lado. Pesos padrão iguais; pesos
diferentes devem ser declarados no arquivo. O relatório imprime a fórmula e o aviso:
**"índice de aderência — não é probabilidade de aceitação"**. Campos como `probability` ou
`acceptance_chance` são rejeitados pelo validador.

## Workflow

1. Para cada candidato, reunir evidências (não inferir pelo nome do periódico).
2. Preencher `research/publication/journals/<slug>/fit.json`
   (template `${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/templates/journal-fit.json`).
3. Validar e gerar o relatório padronizado (Journal Fit Report):
   `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" validate fit …/fit.json` e `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" fit-report …/fit.json --out …/fit-report.md`.
4. Comparar candidatos: `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" compare research/publication/journals/*/fit.json`.
5. Registrar riscos de desk rejection com base em evidência (ex.: escopo exige dimensão
   internacional; periódico não publica estudos de caso único).

## Output esperado

Journal Fit Report por periódico (campos: JOURNAL, PUBLISHER, AIMS & SCOPE, TOPIC FIT, METHOD FIT,
AUDIENCE FIT, RECENT ARTICLE FIT, ARTICLE TYPE FIT, OPEN ACCESS, APC, INDEXING, REVIEW TIME IF
PUBLISHED, PUBLICATION TIME IF PUBLISHED, KEY REQUIREMENTS, SIMILAR ARTICLES, RISKS, EVIDENCE,
DATE VERIFIED) + tabela comparativa.

## Critérios de qualidade

- Toda classificação com justificativa e evidência datada.
- Dados ausentes → `NOT VERIFIED`; prazos editoriais só se publicados pelo periódico.
- Nenhuma probabilidade de aceitação; índice apresentado como aderência, com cobertura.

## Situações de falha

- *Aims & scope* inacessível → Topic/Contribution/Audience `INSUFFICIENT_EVIDENCE`; avisar.
- Poucos artigos recentes recuperáveis → Recent Publication Fit `INSUFFICIENT_EVIDENCE` (ausência na
  busca não prova ausência no periódico).
