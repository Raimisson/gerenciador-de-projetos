---
name: journal-recent-content-analysis
description: "Publication Strategy: artigos comparáveis publicados pelo periódico nos últimos 3–5 anos (título, autores, DOI, método, relação). Use para \"artigos recentes da revista\", \"o que a revista publicou sobre\"."
argument-hint: "[periódico] [--anos 5] [--manuscrito research/]"
---

# Journal Recent Content Analysis

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

- Para sustentar empiricamente Topic/Method/Empirical/Recent Publication Fit.
- Para citar, na cover letter, o diálogo do manuscrito com o que o periódico publicou (só com artigos verificados).

## Quando NÃO usar

- Busca geral de literatura → `literature-search`.

## Inputs esperados

Nome exato do periódico (e ISSN, se conhecido); perfil do manuscrito; janela (padrão: últimos 5 anos).

## Workflow

1. **Buscar** artigos do periódico na janela com termos do tema e do método (Scite com filtro
   `journal` + `date_from`; OpenAlex `filter=primary_location.source.issn:…,from_publication_date:…`
   via WebFetch; site do periódico; Consensus/Elicit).
2. **Filtrar pelo periódico exato**: ferramentas às vezes retornam outros periódicos com nome
   parecido — descartar e registrar quantos foram descartados.
3. **Classificar a relação** de cada artigo com o manuscrito:
   `mesmo tema e método` · `mesmo tema, outro método` · `mesmo método, outro tema` ·
   `mesmo setor/jurisdição` · `relacionado` · `não comparável`.
   Método: extraído do abstract/texto; se não disponível → `NR — não reportado`.
4. **Registrar a busca** (ferramenta, query, filtros, data, total retornado, descartados) — a
   ausência de artigos semelhantes na busca **não** prova ausência no periódico.
5. Salvar `research/publication/journals/<slug>/recent-content.json` (schema
   `recent-content.schema.json`) e validar: `python3 "${CLAUDE_PLUGIN_ROOT}/modules/publication-strategy/scripts/pubtool.py" validate recent …`.

## Output esperado

| Título | Autores | Ano | DOI | URL | Método | Relação com o manuscrito |
|---|---|---|---|---|---|---|

+ resumo: quantos comparáveis, em quais dimensões, lacunas da busca.

## Critérios de qualidade

- Todos os artigos com DOI/URL recuperados de ferramenta nesta sessão (não de memória).
- Metadados como retornados; método `NR` quando não verificado.
- Janela temporal e data da busca explícitas.

## Situações de falha

- Sem acesso a índice → pedir ao usuário a página de "latest issues"/"articles in press" ou
  deixar Recent Publication Fit como `INSUFFICIENT_EVIDENCE`.
