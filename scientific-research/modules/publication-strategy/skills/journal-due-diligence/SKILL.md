---
name: journal-due-diligence
description: Módulo Publication Strategy — verifica legitimidade e transparência de um periódico (publisher, ISSN, peer review, conselho editorial, indexação em Crossref, DOAJ, COPE, SciELO, Scopus, Web of Science, Redalyc, Latindex, política de arquivamento, DOI, APC, copyright, open access, ética) com evidências datadas e alertas objetivos, seguindo princípios do Think. Check. Submit., sem rotular como predatório apenas pela ausência de uma indexação. Use para "esse periódico é confiável?", "revista predatória?", "due diligence do periódico", "indexação da revista".
argument-hint: "[periódico] [--issn XXXX-XXXX]"
---

# Journal Due Diligence

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

- Antes de incluir um periódico na lista curta; sempre que o periódico for desconhecido ou
  tiver sido contatado por convite não solicitado.

## Quando NÃO usar

- Regras de formatação/submissão → `journal-requirements`.

## Inputs esperados

Nome do periódico; ISSN (impresso/eletrônico) se disponível; site oficial.

## Checklist (cada item: `CONFIRMED` · `NOT_FOUND` · `NOT_VERIFIED` · `NOT_APPLICABLE` + URL + data)

| Item | Onde verificar (fonte preferencial) |
|---|---|
| Publisher identificado e contato | site do periódico/editora |
| ISSN válido e correspondente ao título | ISSN Portal (portal.issn.org) |
| Processo de peer review descrito | site do periódico |
| Conselho editorial com nomes e afiliações verificáveis | site do periódico (+ páginas institucionais dos editores) |
| DOIs registrados (Crossref) | Crossref / resolução de DOIs de artigos recentes |
| DOAJ (se OA) | doaj.org |
| Membro do COPE | publicationethics.org |
| SciELO / Redalyc / Latindex | sites respectivos (relevante para periódicos latino-americanos) |
| Scopus / Web of Science | listas oficiais de títulos indexados |
| Política de arquivamento/preservação (LOCKSS, CLOCKSS, Portico, PMC) | site do periódico / Keepers Registry |
| APC e o que ela cobre; política de isenção | site do periódico |
| Copyright e licença (CC BY etc.) | site do periódico |
| Política de open access / autoarquivamento | site do periódico, Sherpa Romeo (Open Policy Finder) |
| Políticas de ética (conflito de interesse, retratação, uso de IA, dados) | site do periódico |

## Regras de interpretação

- **Ausência de uma indexação isolada não é prova de predatório** (periódicos novos, regionais
  ou de nicho podem não estar em Scopus/WoS). Conclusões exigem **conjunto** de sinais.
- Sinais de alerta objetivos (listar com evidência): ISSN inexistente/de outro título; conselho
  editorial não verificável; promessas de prazos de revisão irrealistas; APC não informada antes
  da submissão; DOIs que não resolvem; site com métricas falsas ou não reconhecidas; convites
  massivos; escopo excessivamente amplo e desconexo.
- **Think. Check. Submit.** (thinkchecksubmit.org): usar as perguntas da iniciativa como roteiro,
  citando-a como fonte do roteiro.
- Resultado: `SEM ALERTAS RELEVANTES` · `ALERTAS A ESCLARECER` · `ALERTAS GRAVES` — sempre
  acompanhado das evidências; nunca "predatório" sem conjunto de evidências documentado.

## Workflow

1. Consultar as fontes oficiais e preencher `research/publication/journals/<slug>/due-diligence.json`
   (schema `due-diligence.schema.json`, template em `templates/`).
2. Validar: `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" validate due-diligence …` (o validador recusa rótulo "predatory" sem ≥3 alertas com evidência).
3. Verificar frescor antes da decisão: `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" freshness …/due-diligence.json --max-age-days 180`.

## Output esperado

Tabela do checklist + alertas objetivos + conclusão qualificada + data de verificação.

## Critérios de qualidade

- Cada item com fonte e data; itens não consultados `NOT_VERIFIED`.
- Linguagem factual; sem difamação.

## Situações de falha

- Fontes bloqueadas → `NOT_VERIFIED`, com a lista de onde o usuário deve conferir.
