---
name: literature-search
description: "Estratégia de busca bibliográfica reproduzível: sinônimos, strings booleanas por base, execução nos conectores e search log. Use para \"buscar literatura\", \"string de busca\", \"revisão de literatura\"."
argument-hint: "[pergunta ou tema] [--periodo AAAA-AAAA] [--idiomas pt,en]"
---

# Literature Search

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

- Construir ou executar uma busca acadêmica sobre uma pergunta definida.
- Documentar uma busca de forma reproduzível (para artigo, dissertação, revisão).

## Quando NÃO usar

- Partir de um artigo seminal e expandir por citações → `citation-chasing`.
- Relatórios de governo/reguladores/organizações → `grey-literature` / `regulatory-research`.
- Revisão sistemática formal com protocolo e triagem → `systematic-review` (que chama esta skill para a etapa de busca).

## Inputs esperados

Pergunta de pesquisa (idealmente saída de `research-question`); período; idiomas;
tipos de documento; bases desejadas; ferramentas conectadas.

## Detecção de ferramentas e hierarquia

Antes de buscar, liste as ferramentas disponíveis na sessão e informe o usuário:

| Camada | Ferramentas (nomes típicos de ferramenta) | Uso |
|---|---|---|
| 1. Busca acadêmica semântica | Consensus (`…Consensus…search`), Elicit (`…Elicit…search_papers`) | descoberta ampla |
| 2. Índices bibliográficos | Scite (`…Scite…search_literature`), OpenAlex/Semantic Scholar (via `srtool.py` ou WebFetch) | cobertura, metadados, citações |
| 3. Registro de DOI | Crossref (via `srtool.py doi-check` ou WebFetch `api.crossref.org`) | metadados autoritativos |
| 4. Web | WebSearch/WebFetch, Exa, Tavily, Firecrawl | complementar, working papers |
| Biblioteca pessoal | Zotero (MCP comunitário, **somente leitura**) | o que o usuário já tem |

A hierarquia não é rígida: se uma base é claramente mais apropriada (ex.: RePEc para
economia, SciELO para literatura latino-americana), use-a. Detalhes:
`${CLAUDE_PLUGIN_ROOT}/docs/connectors.md`.

**Sem conectores acadêmicos:** use WebSearch/WebFetch e as APIs públicas
(`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" search-openalex "<query>"`). Sem rede:
entregue a estratégia e as strings para o usuário executar e registre que a busca **não
foi executada**.

## Workflow

1. **Conceitos**: separar a pergunta em 2–4 blocos conceituais (ex.: [mecanismo] AND
   [setor] AND [desfecho]).
2. **Vocabulário**: para cada bloco, sinônimos, variantes ortográficas, siglas e termos
   em PT/EN (e ES se relevante); termos controlados quando a base os tiver (JEL, tesauros).
3. **Strings**: montar string mestre e adaptações por base (sintaxe de campo, truncamento,
   proximidade). Ex. Scopus: `TITLE-ABS-KEY(("revenue decoupling" OR decoupl*) AND (utilit*) AND ("energy efficiency" OR "demand-side management"))`.
4. **Teste de sensibilidade**: se o usuário conhecer 2–5 estudos-chave, verifique se a
   string os recupera; ajuste e registre a mudança.
5. **Execução** (se houver ferramenta): para cada base, executar, registrar a contagem
   **exatamente como reportada pela ferramenta** e salvar os registros retornados.
   Não estimar contagens; se a ferramenta não informa total, registre `NR — não reportado`.
6. **Deduplicação** por DOI normalizado e título normalizado
   (`srtool.py dedupe <arquivo>` se disponível).
7. **Registro** em `research/search/search-log.json` (schema
   `${CLAUDE_PLUGIN_ROOT}/schemas/search-log.schema.json`) e resumo em `search-log.md`
   (template `${CLAUDE_PLUGIN_ROOT}/templates/search-log.md`). Validar:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" validate searchlog research/search/search-log.json`.
8. **Registro de fontes candidatas** em `research/sources/sources.json` com
   `metadata_verification.status: UNVERIFIED` até conferência de DOI.

## Output esperado

- Tabela da estratégia (blocos, termos, strings por base).
- Tabela de execução: base | data | query | filtros | período | encontrados | observações.
- Lista de registros (título, autores, ano, veículo, DOI, URL, ferramenta de origem).
- Limitações de cobertura (idiomas, bases não acessadas, paywalls).

## Critérios de qualidade

- Qualquer pessoa consegue repetir a busca a partir do log.
- Cada registro indica de qual ferramenta/base veio.
- Contagens são as reportadas pela ferramenta, nunca estimadas.
- Nenhum registro é incluído "de memória": se o Claude lembra de um estudo relevante,
  ele só entra após ser localizado em uma ferramenta — senão vai para a seção
  "Pistas a verificar" com status `UNVERIFIED`.

## Situações de falha

- Ferramenta retorna erro/limite de uso → registrar no log (`notes`) e seguir para a
  próxima camada; nunca preencher os resultados que faltariam.
- Resultados irrelevantes → refinar string e registrar a versão anterior.
- Zero resultados → dizer isso; "ausência de estudo na busca não prova inexistência".
