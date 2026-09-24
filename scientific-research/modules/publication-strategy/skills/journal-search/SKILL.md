---
name: journal-search
description: Módulo Publication Strategy — identifica periódicos potencialmente adequados para um manuscrito concluído a partir de título, abstract, keywords, pergunta, metodologia, resultados, contribuição e referências principais, combinando análise de aims & scope, artigos recentes, tipos de artigo, público e métodos publicados, sem se limitar a palavras-chave nem a uma única editora. Use para "onde publicar", "sugerir periódicos", "journal search", "qual revista", "periódicos para submeter".
argument-hint: "[manuscrito.md ou research/] [--areas economia,energia] [--idiomas en,pt]"
---

# Journal Search

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

- O manuscrito está concluído (ou quase) e é preciso montar a lista inicial de periódicos candidatos.
- Após rejeição, para ampliar a lista (acionado por `resubmission-strategy`).

## Quando NÃO usar

- Avaliar a fundo um periódico já escolhido → `journal-fit-analysis`, `journal-due-diligence`, `journal-requirements`.
- O manuscrito ainda não tem pergunta, método e resultados definidos → voltar a `research-project`.

## Inputs esperados

Preferencialmente: título; abstract; keywords; pergunta de pesquisa; metodologia; principais
resultados; contribuição; referências principais. Esses dados ficam no **perfil do manuscrito**
(`research/publication/manuscript-profile.json`), gerado assim:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" init research
python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" profile research/manuscript/manuscript.md --out research/publication/manuscript-profile.json
```

Campos que o script não consegue extrair (contribuição, método, resultados) são completados a
partir do manuscrito e do **Evidence Ledger** existente — não reconstrua a evidência científica.

## Workflow

1. **Perfil do manuscrito**: confirmar com o usuário tipo de artigo (research article, review,
   short communication, policy paper…), público pretendido, restrições (open access, APC, idioma,
   prazo, indexação exigida pelo programa/instituição).
2. **Fontes de candidatos** (usar várias, registrar de onde veio cada candidato):
   | Fonte | Como | Por que |
   |---|---|---|
   | Veículos da literatura citada | `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" venues research/sources/sources.json` | onde o debate já acontece |
   | Veículos de artigos comparáveis recentes | busca por tema+método (Scite, Consensus, Elicit, OpenAlex, WebSearch) filtrando os últimos 3–5 anos | onde trabalhos semelhantes são publicados hoje |
   | Citantes de artigos-chave | forward citation chasing (`citation-chasing`) | periódicos que dialogam com a mesma literatura |
   | Diretórios | DOAJ, SciELO, Redalyc, Latindex, portais de editoras (Elsevier, Springer Nature, Wiley, Taylor & Francis, SAGE, OUP, CUP, MDPI, sociedades científicas) | cobrir editoras e regiões além das óbvias |
   | Indicação do usuário/orientador | registrar como tal | |
3. **Triagem rápida** de cada candidato por *aims & scope* (página oficial, com URL e data) e
   por pelo menos um artigo publicado comparável. Candidato sem *aims & scope* verificado fica
   marcado `NOT VERIFIED` — não é descartado nem aprovado pelo nome.
4. **Lista longa → curta**: 8–15 candidatos na lista longa; 3–6 seguem para
   `journal-fit-analysis` + `journal-recent-content-analysis` + `journal-due-diligence`.
5. Salvar em `research/publication/journals/candidates.json`
   (schema `${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/schemas/journal-candidates.schema.json`)
   e validar: `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" validate candidates research/publication/journals/candidates.json`.

## Output esperado

Tabela: periódico | editora | origem do candidato (evidência) | *aims & scope* (trecho + URL + data
ou NOT VERIFIED) | artigo comparável (DOI) | tipo de artigo aceito | observações | seguir para análise? (sim/não + motivo).

## Critérios de qualidade

- Cada candidato tem pelo menos uma evidência verificável de aderência (trecho de *aims & scope*
  ou artigo publicado com DOI).
- Mais de uma editora/plataforma considerada; periódicos regionais/nacionais relevantes
  (ex.: SciELO) avaliados quando o público-alvo justificar.
- Nenhuma métrica usada como critério principal; nenhuma probabilidade de aceitação.

## Situações de falha

- Sites de editoras inacessíveis → candidatos permanecem `NOT VERIFIED` e a lista é entregue
  como preliminar; pedir ao usuário para colar o *aims & scope* ou tentar outra fonte.
- Filtro por periódico da ferramenta retorna outros periódicos (acontece no Scite) → descartar
  resultados cujo campo *journal* não corresponda exatamente ao periódico.
