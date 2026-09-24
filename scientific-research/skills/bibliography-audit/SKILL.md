---
name: bibliography-audit
description: "Confere DOI e metadados, detecta duplicatas e referências inventadas e formata ABNT, APA, Chicago ou BibTeX só se verificadas. Use para \"conferir referências\", \"formatar ABNT/APA\", \"gerar BibTeX\"."
argument-hint: "[arquivo de referências .bib/.ris/.md/.json] [--estilo abnt|apa|chicago|bibtex]"
---

# Bibliography Audit

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

- Conferir uma lista de referências (do manuscrito, do Zotero, de um `.bib`).
- Gerar referências formatadas a partir de metadados verificados.

## Quando NÃO usar

- Verificar se as fontes sustentam as frases → `citation-audit`.

## Inputs esperados

Lista de referências (qualquer formato), ou `research/sources/sources.json`; estilo desejado.
Zotero (se conectado via MCP comunitário) é usado **somente para leitura**; qualquer
escrita na biblioteca exige pedido explícito do usuário e confirmação (o hook do plugin
pede confirmação).

## Workflow

1. **Normalizar** a lista em `sources.json` (um registro por referência, `S-…`).
2. **Verificar cada referência**, nesta ordem:
   1. DOI → Crossref/doi.org (`srtool.py doi-check`); comparar título, autores, ano, periódico.
   2. Sem DOI → busca por título exato (Crossref/OpenAlex/Scite); para normas e relatórios,
      o site do emissor.
   3. Registrar `metadata_verification.status`, `checked_against`, `checked_on`, divergências.
3. **Duplicatas**: mesmo DOI, ou título normalizado + ano iguais; versões working paper ×
   publicada (manter ambas ligadas, citar a publicada) — `srtool.py dedupe`.
4. **Sinais de invenção**: DOI inexistente; DOI de outro trabalho; autores/ano/periódico
   incompatíveis; não encontrado em nenhum índice → marcar `POSSIVELMENTE INVENTADA`
   e **não formatar**.
5. **Formatar** somente registros `VERIFIED` (ou `PARTIALLY_VERIFIED` com campos faltantes
   explícitos — nunca preencher volume/páginas de memória):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" format research/sources/sources.json --style abnt
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/srtool.py" format research/sources/sources.json --style bibtex --out refs.bib
   ```
   Estilos: `abnt` (NBR 6023), `apa` (7ª ed.), `chicago` (autor-data), `bibtex`.
   O formatador é simplificado; revise casos especiais (autoria institucional, normas,
   capítulos) manualmente e registre isso.
6. Relatório (template `${CLAUDE_PLUGIN_ROOT}/templates/bibliography-audit-report.md`).

## Output esperado

Tabela: S-id | referência original | status | divergências | ação; referências formatadas
(apenas verificadas); lista de duplicatas; lista de possivelmente inventadas.

## Critérios de qualidade

- Nenhum campo bibliográfico preenchido sem fonte.
- Alterações em relação à referência original listadas campo a campo.

## Situações de falha

- Rede bloqueada/limite de API → `UNVERIFIED`; não formatar como verificada.
- Metadados conflitantes entre bases → registrar ambos; preferir registro do DOI/editor.
