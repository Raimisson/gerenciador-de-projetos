---
name: grey-literature
description: Busca e classifica literatura cinzenta — documentos de governos, agências reguladoras, organizações internacionais (IEA, OCDE, Banco Mundial, BID, CEPAL), think tanks, universidades, working papers (NBER, SSRN, RePEc), avaliações de programas e relatórios técnicos — sem tratá-la como revisada por pares. Use para "literatura cinzenta", "grey literature", "relatórios técnicos", "working papers", "avaliações de programas", "relatório do governo sobre".
argument-hint: "[tema] [--jurisdicoes BR,US,EU] [--organizacoes lista]"
---

# Grey Literature

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

- A pergunta depende de avaliações de programas, relatórios oficiais ou working papers.
- Setores em que a evidência circula fora de periódicos (regulação, energia, saneamento).

## Quando NÃO usar

- Legislação, atos normativos, AIR/ARR, consultas públicas → `regulatory-research`
  (que usa esta skill para a parte de relatórios).
- Artigos acadêmicos revisados por pares → `literature-search`.

## Inputs esperados

Tema/pergunta; jurisdições; organizações de interesse; período; idiomas.

## Ferramentas

Exa, Tavily ou Firecrawl (se instalados), WebSearch/WebFetch. Para working papers:
OpenAlex (tipo `preprint`/`report`), RePEc/IDEAS, SSRN, NBER via WebFetch. Para relatórios
com DOI (ex.: OSTI `10.2172/...`), conferir no Crossref/DataCite.
Sem ferramentas web: pedir ao usuário os documentos e trabalhar sobre eles.

## Classificação obrigatória de cada documento

| Campo | Valores |
|---|---|
| `source_type` | `working_paper` · `official_report` · `regulator_document` · `technical_report` · `program_evaluation` · `international_org_report` · `think_tank_report` · `thesis` · `conference_paper` · `dataset_documentation` · `news` · `blog` · `other` |
| `peer_reviewed` | `false` (padrão para literatura cinzenta) · `true` só com evidência (ex.: versão publicada em periódico — nesse caso cite a versão publicada) · `"unknown"` |
| `issuer` | organização responsável (autoria institucional) |
| `independence` | `independent` · `commissioned_by_interested_party` · `self_evaluation` · `unknown` |
| `version` | rascunho/versão final/data da versão; working papers mudam entre versões |

## Workflow

1. **Mapa de emissores**: listar organizações relevantes por jurisdição/tema
   (ex.: energia no Brasil: ANEEL, EPE, MME, PROCEL; EUA: LBNL, ACEEE, DOE/OSTI; UE: JRC,
   Comissão Europeia; internacionais: IEA, OCDE, Banco Mundial, BID, CEPAL).
2. **Busca por emissor** (`site:` quando suportado) + busca temática geral.
3. **Localizar a versão primária**: preferir o PDF no site do emissor ao repasse
   em notícia/blog. Notícias servem para descoberta; registrar a fonte primária.
4. **Checar publicação posterior**: working paper virou artigo? Se sim, registrar
   ambos e usar a versão publicada para afirmações, anotando diferenças de resultados.
5. **Registrar** no search log (base = site/organização; query; data; contagem) e em
   `sources.json` com os campos acima.
6. **Extração** segue `evidence-extraction` (com `peer_reviewed: false` visível na matriz).

## Output esperado

Tabela: documento | emissor | ano | tipo | peer_reviewed | independência | URL | DOI (se houver) | relevância | status de verificação.

## Critérios de qualidade

- Nenhum documento cinzento rotulado como revisado por pares.
- URL do emissor original (não agregador) sempre que possível; data de acesso registrada.
- Conflitos de interesse (avaliação encomendada pelo próprio programa) sinalizados.

## Situações de falha

- Link quebrado → procurar no arquivo do emissor ou Wayback Machine; se não achar,
  `UNVERIFIED` com a frase padrão de não verificação.
- Documento sem data/autor → `NR — não reportado`; não deduzir pelo contexto.
