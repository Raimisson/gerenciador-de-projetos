---
name: resubmission-strategy
description: "Publication Strategy: após rejeição, analisa motivos, planeja mudanças e escolhe outro periódico com regras reconsultadas. Use para \"artigo rejeitado\", \"desk rejection\", \"próxima revista\"."
argument-hint: "[carta de decisão] [research/]"
---

# Resubmission Strategy

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

- Rejeição (desk ou após revisão) ou "reject and resubmit".

## Quando NÃO usar

- Major/minor revision no mesmo periódico → `peer-review-response`.

## Inputs esperados

Carta de decisão; pareceres (se houver); estratégia anterior (`strategy.md`, `candidates.json`,
fit reports); manuscrito submetido.

## Workflow

1. **Classificar o motivo** com base no texto da decisão (citar o trecho): escopo/aderência ·
   contribuição insuficiente · método/identificação · dados · apresentação/formatação ·
   extensão · outro. Não especular motivos não escritos.
2. **Separar** o que é melhoria científica legítima (incorporar) do que é preferência daquele
   periódico (não necessariamente transferível).
3. **Plano de alterações** — com a mesma regra de integridade: nenhuma alteração seletiva de resultados.
4. **Próximo periódico**: reutilizar `candidates.json` e fit reports; atualizar o fit à luz do motivo
   da rejeição (ex.: rejeição por escopo → subir o peso de Topic Fit); se necessário, ampliar com
   `journal-search`.
5. **Reconsultar regras** do novo alvo (`journal-requirements`) — regras antigas nunca são assumidas
   válidas — e rodar `manuscript-compliance` + `pre-submission-audit`.
6. Atualizar o Target Journal Mode: `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" target set research/publication --journal <novo-slug>`.
7. Salvar `research/publication/resubmission/plan-<data>.md` (template `resubmission-plan.md`).

## Output esperado

Diagnóstico da decisão (com trechos), plano de alterações, recomendação de periódico (com fit
atualizado e datas), checklist de reformatação.

## Critérios de qualidade

- Motivos baseados no texto da decisão; nada de "provavelmente rejeitaram porque…" sem rótulo [INFERÊNCIA].
- Nenhuma probabilidade de aceitação no novo periódico.

## Situações de falha

- Decisão sem justificativa → registrar e usar só o fit reavaliado; não inventar causa.
